import fnmatch
import json
import os
import py_compile
import subprocess
import sys
import traceback
from typing import Optional, Type, List, Literal, Dict, Any

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class RunProjectTestsInput(BaseModel):
    """运行项目级生成测试的输入参数。"""
    project_root: str = Field(..., description="项目根目录（cwd 与 PYTHONPATH 基准）")
    tests_dir: str = Field(..., description="生成测试用例所在目录（相对 project_root 或绝对路径）")

    # 选择性运行：三种方式，任选其一或组合
    include_patterns: List[str] = Field(
        default_factory=lambda: ["test_*.py", "*_test.py"],
        description="包含的文件名通配模式列表（fnmatch），如 ['test_*.py']"
    )
    exclude_patterns: List[str] = Field(
        default_factory=list,
        description="排除的文件名通配模式列表，如 ['test_flaky_*']"
    )
    include_keywords: List[str] = Field(
        default_factory=list,
        description="文件路径包含这些关键字才会被选中（AND 关系）"
    )
    selected_files: List[str] = Field(
        default_factory=list,
        description="显式指定要跑的测试文件（相对 tests_dir 或绝对路径）。不为空则优先使用它。"
    )

    runner: Literal["pytest", "unittest", "auto"] = Field(
        "auto",
        description="运行器：pytest / unittest / auto（优先 pytest，如果不可用则 unittest）"
    )
    python_executable: str = Field(
        sys.executable,
        description="Python 解释器路径（默认当前解释器）"
    )
    timeout_sec: int = Field(60, description="执行超时（秒）")

    # pytest 参数
    pytest_extra_args: List[str] = Field(
        default_factory=lambda: ["-q", "--maxfail=1", "-s"],
        description="额外 pytest 参数，例如 ['-q','--maxfail=1','-s']"
    )
    # unittest 参数
    unittest_pattern: str = Field(
        "test*.py",
        description="unittest discover 的 pattern（当 runner=unittest 时使用）"
    )

    # 导包相关
    extra_pythonpath: Optional[str] = Field(
        None,
        description="额外 PYTHONPATH（os.pathsep 分隔多个路径）"
    )

    # 语法检查开关
    precheck_syntax: bool = Field(True, description="是否在运行前对选中的文件做语法检查")

    # 输出控制
    verbose: bool = Field(True, description="是否输出更详细的摘要")


class RunProjectGeneratedTestsTool(BaseTool):
    name: str = "run_project_generated_tests"
    description: str = (
        "Selectively run agent-generated Python tests already written into project directory. "
        "Supports file pattern/keyword selection, syntax precheck, and returns detailed errors."
    )
    args_schema: Type[BaseModel] = RunProjectTestsInput

    def _abs_tests_dir(self, project_root: str, tests_dir: str) -> str:
        if os.path.isabs(tests_dir):
            return tests_dir
        return os.path.abspath(os.path.join(project_root, tests_dir))

    def _prepare_env(self, project_root: str, extra_pythonpath: Optional[str]) -> Dict[str, str]:
        env = os.environ.copy()
        project_root_abs = os.path.abspath(project_root)

        parts = [project_root_abs]
        if extra_pythonpath:
            parts.extend([p for p in extra_pythonpath.split(os.pathsep) if p.strip()])

        old = env.get("PYTHONPATH", "")
        if old:
            parts.append(old)

        env["PYTHONPATH"] = os.pathsep.join(parts)
        return env

    def _select_files(
        self,
        tests_dir_abs: str,
        include_patterns: List[str],
        exclude_patterns: List[str],
        include_keywords: List[str],
        selected_files: List[str],
    ) -> List[str]:
        # 如果显式指定 files，优先用它
        if selected_files:
            out = []
            for f in selected_files:
                path = f
                if not os.path.isabs(path):
                    path = os.path.join(tests_dir_abs, f)
                path = os.path.abspath(path)
                if os.path.isfile(path):
                    out.append(path)
            return sorted(list(dict.fromkeys(out)))

        # 否则扫描目录
        all_py = []
        for root, _, files in os.walk(tests_dir_abs):
            for name in files:
                if not name.endswith(".py"):
                    continue
                full = os.path.abspath(os.path.join(root, name))
                all_py.append(full)

        def match_any(name: str, patterns: List[str]) -> bool:
            return any(fnmatch.fnmatch(name, p) for p in patterns)

        chosen = []
        for f in all_py:
            base = os.path.basename(f)
            rel = os.path.relpath(f, tests_dir_abs)

            if include_patterns and not match_any(base, include_patterns):
                continue
            if exclude_patterns and match_any(base, exclude_patterns):
                continue
            if include_keywords:
                if not all(k in rel for k in include_keywords):
                    continue
            chosen.append(f)

        return sorted(chosen)

    def _detect_runner(self, runner: str, python_executable: str, env: Dict[str, str], cwd: str) -> str:
        if runner != "auto":
            return runner
        # 优先尝试 pytest 是否可用
        try:
            p = subprocess.run(
                [python_executable, "-m", "pytest", "--version"],
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if p.returncode == 0:
                return "pytest"
        except Exception:
            pass
        return "unittest"

    def _syntax_check(self, files: List[str]) -> List[Dict[str, Any]]:
        errors = []
        for f in files:
            try:
                py_compile.compile(f, doraise=True)
            except py_compile.PyCompileError as e:
                errors.append({
                    "file": f,
                    "error_type": "SyntaxError",
                    "message": str(e),
                })
        return errors

    def _run(
        self,
        project_root: str,
        tests_dir: str,
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
        include_keywords: List[str] = None,
        selected_files: List[str] = None,
        runner: str = "auto",
        python_executable: str = sys.executable,
        timeout_sec: int = 60,
        pytest_extra_args: List[str] = None,
        unittest_pattern: str = "test*.py",
        extra_pythonpath: Optional[str] = None,
        precheck_syntax: bool = True,
        verbose: bool = True,
    ) -> str:
        include_patterns = include_patterns or ["test_*.py", "*_test.py"]
        exclude_patterns = exclude_patterns or []
        include_keywords = include_keywords or []
        selected_files = selected_files or []
        pytest_extra_args = pytest_extra_args or ["-q", "--maxfail=1", "-s"]

        res: Dict[str, Any] = {
            "ok": False,
            "project_root": os.path.abspath(project_root),
            "tests_dir": tests_dir,
            "runner": None,
            "selected_count": 0,
            "selected_files": [],
            "phase": None,  # selection | syntax_check | test_run | tool_error
            "syntax_errors": [],
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "error_type": None,
            "summary": "",
        }

        try:
            project_root_abs = os.path.abspath(project_root)
            tests_dir_abs = self._abs_tests_dir(project_root_abs, tests_dir)

            res["phase"] = "selection"
            if not os.path.isdir(tests_dir_abs):
                res["error_type"] = "PathError"
                res["summary"] = f"tests_dir not found: {tests_dir_abs}"
                return json.dumps(res, ensure_ascii=False, indent=2)

            selected = self._select_files(
                tests_dir_abs,
                include_patterns,
                exclude_patterns,
                include_keywords,
                selected_files,
            )
            res["selected_count"] = len(selected)
            res["selected_files"] = selected

            if not selected:
                res["ok"] = True
                res["summary"] = "No test files selected (nothing to run)."
                return json.dumps(res, ensure_ascii=False, indent=2)

            env = self._prepare_env(project_root_abs, extra_pythonpath)
            runner_use = self._detect_runner(runner, python_executable, env, project_root_abs)
            res["runner"] = runner_use

            # 语法预检查（可选）
            if precheck_syntax:
                res["phase"] = "syntax_check"
                syn_errs = self._syntax_check(selected)
                res["syntax_errors"] = syn_errs
                if syn_errs:
                    res["ok"] = False
                    res["error_type"] = "SyntaxError"
                    res["summary"] = f"Syntax check failed for {len(syn_errs)} file(s)."
                    return json.dumps(res, ensure_ascii=False, indent=2)

            # 运行测试
            res["phase"] = "test_run"
            if runner_use == "pytest":
                # 直接把选中的文件列表传给 pytest
                cmd = [python_executable, "-m", "pytest", *pytest_extra_args, *selected]
            else:
                # unittest discover 只能按目录+pattern，没法精确到“文件集合”
                # 做法：如果用户显式 selected_files，则逐个文件运行；否则 discover
                if selected_files:
                    cmd = [python_executable, "-m", "unittest", *selected]
                else:
                    cmd = [python_executable, "-m", "unittest", "discover", "-s", tests_dir_abs, "-p", unittest_pattern]

            proc = subprocess.run(
                cmd,
                cwd=project_root_abs,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
            )

            res["exit_code"] = proc.returncode
            res["stdout"] = proc.stdout or ""
            res["stderr"] = proc.stderr or ""

            if proc.returncode == 0:
                res["ok"] = True
                res["summary"] = "Selected tests passed."
                return json.dumps(res, ensure_ascii=False, indent=2)

            # 错误分类
            combined = (res["stdout"] + "\n" + res["stderr"]).lower()
            if "modulenotfounderror" in combined or "importerror" in combined:
                res["error_type"] = "ImportError"
                res["summary"] = "Import failed (ModuleNotFoundError/ImportError)."
            elif "assertionerror" in combined or "failed" in combined:
                res["error_type"] = "TestFailure"
                res["summary"] = "Tests failed (assertion failure)."
            else:
                res["error_type"] = "RuntimeError"
                res["summary"] = "Tests errored during execution."

            return json.dumps(res, ensure_ascii=False, indent=2)

        except subprocess.TimeoutExpired as e:
            res["ok"] = False
            res["phase"] = "test_run"
            res["error_type"] = "TimeoutError"
            res["summary"] = f"Test execution exceeded timeout ({timeout_sec}s)."
            res["stdout"] = (e.stdout or "") if hasattr(e, "stdout") else ""
            res["stderr"] = (e.stderr or "") if hasattr(e, "stderr") else ""
            return json.dumps(res, ensure_ascii=False, indent=2)

        except Exception:
            res["ok"] = False
            res["phase"] = "tool_error"
            res["error_type"] = "ToolError"
            res["summary"] = "Tool crashed unexpectedly."
            res["stderr"] = traceback.format_exc()
            return json.dumps(res, ensure_ascii=False, indent=2)
