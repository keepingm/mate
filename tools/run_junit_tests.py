import subprocess
import os
import re
from datetime import datetime
from typing import Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field



# 1. 定义输入参数 Schema (保持不变)
class MavenJUnitToolInput(BaseModel):
    project_path: str = Field(
        ...,
        description="Java 项目的根目录路径（必须包含 pom.xml 文件）。"
    )
    test_selection: Optional[str] = Field(
        None,
        description="可选。指定要运行的测试类或方法（Maven -Dtest 语法）。如 'MyTest' 或 'MyTest#method'。留空则运行全部。"
    )


# 2. 定义带日志功能的工具类
class MavenJUnitTool(BaseTool):
    name: str = "run_maven_junit_tests"
    description: str = (
        "运行 Java Maven 项目中的 JUnit 5 测试。"
        "支持指定特定类或方法。"
        "执行结果会自动保存到本地 log 目录中，并将摘要返回给 Agent。"
    )
    args_schema: Type[BaseModel] = MavenJUnitToolInput

    def _run(self, project_path: str, test_selection: Optional[str] = None) -> str:
        # --- 路径检查 ---
        if not os.path.exists(project_path):
            return f"Error: Project path '{project_path}' does not exist."

        pom_path = os.path.join(project_path, "pom.xml")
        if not os.path.exists(pom_path):
            return f"Error: No 'pom.xml' found in '{project_path}'."

        # --- 构建命令 ---
        # 自动检测操作系统使用 mvn 还是 mvn.cmd (Windows兼容性)
        mvn_cmd = "mvn.cmd" if os.name == 'nt' else "mvn"
        command = [mvn_cmd, "test"]

        # 用于生成文件名的标签
        selection_tag = "all_tests"

        if test_selection:
            command.append(f"-Dtest={test_selection}")
            # 清理文件名中的特殊字符
            selection_tag = re.sub(r'[^a-zA-Z0-9_\-]', '_', test_selection)

        try:
            # --- 执行命令 ---
            print(f"Executing: {' '.join(command)} in {project_path}")
            result = subprocess.run(
                command,
                cwd=project_path,
                capture_output=True,
                text=True,
                check=False,
                encoding='utf-8',  # 强制 utf-8 防止乱码
                errors='replace'
            )

            # --- 组合输出内容 ---
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            output_lines = []
            output_lines.append(f"=== Execution Timestamp: {timestamp} ===")
            output_lines.append(f"=== Command: {' '.join(command)} ===")
            output_lines.append(f"=== Exit Code: {result.returncode} ===")
            output_lines.append("\n--- STDOUT ---")
            output_lines.append(result.stdout)

            if result.stderr:
                output_lines.append("\n--- STDERR ---")
                output_lines.append(result.stderr)

            full_log_content = "\n".join(output_lines)

            # --- 日志记录逻辑 (核心修改) ---
            # 1. 创建 log 目录 (如果不存在)
            log_dir = os.path.join(os.getcwd(), "log")
            os.makedirs(log_dir, exist_ok=True)

            # 2. 生成带时间戳的文件名
            # 格式: test_run_[ClassName]_[YYYYMMDD_HHMMSS].log
            file_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"test_run_{selection_tag}_{file_time}.log"
            log_file_path = os.path.join(log_dir, log_filename)

            # 3. 写入文件
            with open(log_file_path, "w", encoding="utf-8") as f:
                f.write(full_log_content)

            # --- 返回给 Agent 的信息 ---
            # 提示 Agent 日志已保存，并返回部分关键信息，避免 Token 溢出
            summary = (
                f"Maven Execution Finished (Exit Code: {result.returncode}).\n"
                f"Full logs saved to: {log_file_path}\n\n"
                f"--- Output Snippet (Last 2000 chars) ---\n"
                f"{result.stdout[-2000:] if result.stdout else 'No output captured.'}"
            )

            return summary

        except FileNotFoundError:
            return f"Error: '{mvn_cmd}' not found. Please ensure Maven is installed and in system PATH."
        except Exception as e:
            return f"Error executing Maven tests: {str(e)}"

if __name__ == '__main__':
    tool = MavenJUnitTool()

    # ==========================================
    target_project_path = '/home/mgh/dev/data/dataset/exam/examSystem'

    test_class_name = "ExamServiceImplTest"

    print("\n" + "=" * 50)
    print(f"▶️ 场景 2: 运行特定测试类 '{test_class_name}'")
    print("=" * 50)

    result_specific = tool._run(project_path=target_project_path, test_selection=test_class_name)
    print("工具返回结果:\n", result_specific)