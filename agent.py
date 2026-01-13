# app.py
import json
from pathlib import Path

from agents.test_agent import (
    create_test_architect,
    create_test_designer,
    create_test_development_engineer,
    create_test_debugger
)
from piplines.core import PipelineStep
from utils.dataset_utils import load_dataset
from utils.file_utils import read_file
from utils.file_utils import write_file
from utils.memory_utils import Memory


class TestAgentApp:
    DEBUG_RUN = {4, 5}

    def __init__(self, *, dataset_name):
        self.dataset_name = dataset_name
        self.data = load_dataset(dataset_name)
        self.test_architect = create_test_architect()
        self.test_designer=create_test_designer()
        self.test_developer=create_test_development_engineer()
        self.test_debugger=create_test_debugger()
        self.cot1_desc = read_file('prompt/test_plan/test_plan.md')
        self.cot1_out = read_file('prompt/test_plan/test_plan_out.md')
        self.cot2_desc = read_file('prompt/test_design/test_design.md')
        self.cot2_out = read_file('prompt/test_design/test_design_out.md')
        self.cot4_desc = read_file('prompt/test_development/test_develop.md')
        self.cot4_out = read_file('prompt/test_development/test_develop_out.md')
        self.cot5_desc=read_file('prompt/test_debugger/test_debug.md')
        self.cot5_out=read_file('prompt/test_debugger/test_debug_out.md')

    def _pack_msg(self, type_str, data):
        """辅助函数：将数据打包成 JSON 行"""
        return json.dumps({
            "type": type_str,
            "data": data
        }, ensure_ascii=False) + "\n"

    def stream_run(self, debug):
        print(self.data.dataset_name)
        print(self.data.dataset_root)
        # 定义阶段索引映射 (对应前端 stages 数组的下标)
        # ['测试计划', '测试设计', '测试评审', '测试开发', '测试运行']
        STAGE_PLAN = 0
        STAGE_DESIGN = 1
        STAGE_REVIEW = 2
        STAGE_DEV = 3
        STAGE_RUN = 4


        # --------------------------------------------------------------------
        # Cot1 — Test planning (测试计划)
        # --------------------------------------------------------------------
        if 1 in self.DEBUG_RUN:
            if not debug:
                yield self._pack_msg("stage", {"index": STAGE_PLAN, "name": "测试计划"})

            step1 = PipelineStep(
                agent=self.test_architect,
                template_text=self.cot1_desc,
                expected_output=self.cot1_out,
                output_file="memory/working_memory/test_plan.json"
            )

            streaming_output = step1.run(
                srs=self.data.srs,
                class_diagram=self.data.uml_class,
                sequence_diagram=self.data.uml_sequence
            )

            for chunk in streaming_output:
                # 【关键】发送内容块信号. 注意：需要取 chunk.content
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if debug:
                    print(chunk.content, end="", flush=True)
                else:
                    yield self._pack_msg("content", content)
            # 如果需要保留结果供后续使用
            final1 = streaming_output.result

        # load working memory
        memory = Memory('memory/working_memory/test_plan.json')
        modules = memory.modules
        # --------------------------------------------------------------------
        # Cot2 — Test design (测试设计)
        # --------------------------------------------------------------------
        if 2 in self.DEBUG_RUN:
            # 【关键】发送阶段切换信号 -> 切换到第二个页签/进度
            yield self._pack_msg("stage", {"index": STAGE_DESIGN, "name": "测试设计"})

            step2 = PipelineStep(
                agent=self.test_designer,
                template_text=self.cot2_desc,
                expected_output=self.cot2_out,
                output_file=''
            )
            for module in modules:
                # 这里可能需要在内容里加个标题，说明正在设计哪个模块
                yield self._pack_msg("content",
                                     f"\n\n**正在设计模块: {module.name if hasattr(module, 'name') else '...'}**\n\n")

                step2_out = step2.run(sut=module.to_json)
                for chunk in step2_out:
                    content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                    if debug:
                        print(chunk.content, end="", flush=True)
                    else:
                        yield self._pack_msg("content", content)
                result = step2_out.result.raw
                write_file(path='memory/working_memory/test_case_' + module.name+'.md', content=result, overwrite=False)

        # --------------------------------------------------------------------
        # 跳过阶段 3 (测试评审) 的处理
        # --------------------------------------------------------------------
        # 如果这里没有实际逻辑，但你想让进度条跳过，可以发一个空信号，或者直接进入阶段4

        # --------------------------------------------------------------------
        # Cot4 — Test develop (测试开发)
        # --------------------------------------------------------------------
        if 4 in self.DEBUG_RUN:
            # 【关键】发送阶段切换信号 -> 对应前端 index 3
            yield self._pack_msg("stage", {"index": STAGE_DEV, "name": "测试开发"})
            step4 = PipelineStep(
                agent=self.test_developer,
                template_text=self.cot4_desc,
                expected_output=self.cot4_out,
                output_file=''
            )
            for module in modules:
                testcase = read_file('memory/working_memory/test_case_' + module.name + ".md")
                step4_output = step4.run(
                    language=self.data.language,
                    available_tools=self.tools_prompt(self.data.language),
                    TEST_CASES_JSON=testcase,
                    class_diagram=self.data.uml_class,
                    ROOT_DIR=self.data.sut_root
                )
                for chunk in step4_output:
                    content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                    if debug:
                        print(chunk.content, end="", flush=True)
                    else:
                        yield self._pack_msg("content", content)

        # --------------------------------------------------------------------
        # Cot5 — Test run (测试运行)
        # --------------------------------------------------------------------
        if 5 in self.DEBUG_RUN:
            yield self._pack_msg("stage", {"index": STAGE_DEV, "name": "测试开发"})
            step5 = PipelineStep(
                agent=self.test_debugger,
                template_text=self.cot5_desc,
                expected_output=self.cot5_out,
                output_file='output/'+self.data.dataset_name+'_test_report.md'
            )
            test_suit=read_file('memory/working_memory/generatedTest.txt')
            step5_output=step5.run(
                test_suit=test_suit,
                ROOT_DIR=self.data.sut_root
            )
            for chunk in step5_output:
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if debug:
                    print(chunk.content, end="", flush=True)
                else:
                    yield self._pack_msg("content", content)



    def run(self):
        print("\nStarting TestAgent Pipeline...\n")
        # load dataset
        docs=load_dataset(self.dataset)

        # --------------------------------------------------------------------
        # Cot1 — Test planning
        # --------------------------------------------------------------------
        if 1 in self.DEBUG_RUN:
            print("Step 1: Test planning...")

            step1 = PipelineStep(
                agent=self.test_architect,
                template_text=self.cot1_desc,
                expected_output=self.cot1_out,
                output_file="output/"+docs.dataset_name+"_test_plan.md"
            )

            step1_output = step1.run(
                srs=docs.srs_text,
                class_diagram=docs.uml_class_text,
                sequence_diagram=docs.uml_sequence_text
            )

            # 实时处理流式输出
            for chunk in step1_output:
                print(chunk.content, end="", flush=True)

            # 获取最终结果
            result = step1_output.result
            # print(f"\nFinal Step 1 Output: {result}")

            # print('test_planning:' + step1_output)

        # --------------------------------------------------------------------
        # Cot2 — Test design....
        # --------------------------------------------------------------------
        if 2 in self.DEBUG_RUN:
            memory = Memory('memory/test_plan.json')
            modules = memory.modules
            cot2_outs=[]
            step2 = PipelineStep(
                agent=self.test_designer,
                template_text=self.cot2_desc,
                expected_output=self.cot2_out,
                output_file=''
            )


            base = Path('output')

            path = base / (docs.dataset_name+  "testcase.md")

            for module in modules:
                step2_out = step2.run(
                    sut=module.to_json
                )
                for chunk in step2_out:
                    print(chunk.content, end="", flush=True)
                result = step2_out.result.raw
                write_file(path=path,content=result,overwrite=False)

            print('Cot2 — Test design end')

        # --------------------------------------------------------------------
        # Cot4 — Test planning
        # --------------------------------------------------------------------
        if 4 in self.DEBUG_RUN:
            print("Step 4: Test develop...")

            testcase=read_file(r'D:\BJFU\Project\PythonProject\crewai\test_crew\src\test_crew\output\stocktestcase.md')
            step4 = PipelineStep(
                agent=self.test_developer,
                template_text=self.cot4_desc,
                expected_output=self.cot4_out,
                output_file=''
            )

            step4_output = step4.run(
                TEST_CASES_JSON=testcase,
                class_diagram=docs.uml_class_text,
                ROOT_DIR=r"D:\BJFU\Project\PythonProject\crewai\test_crew\dataset\stock\backend"
            )

            print('test_case:' + step4_output)

    def tools_prompt(self,language):
        if language == 'python':
            return """
        ---

### ✅ 针对 **Python 项目**

1. **编写测试用例**  
   - 所有测试代码必须写入 `{{ROOT_DIR}}/tests/` 目录下。
   - 文件命名格式为：`test_<被测模块名>.py`（例如：被测模块为 `utils.py`，则测试文件为 `test_utils.py`）。
   - 你可以根据逻辑相关性，将多个测试函数组织在同一个测试文件中。

2. **写入测试文件**  
   - 使用工具 `write_code_file` 将测试代码写入指定路径。

3. **检索源码定义**  
   - 如需查看被测函数或类的实现细节，请使用 `code_search` 工具进行关键词或符号检索。

4. **运行与验证测试**  
   - 必须调用 `run_project_generated_tests` 工具执行你编写的测试。
   - 若出现 `ImportError`、语法错误或其他运行时异常，请立即修正测试代码并重新运行。
   - **注意**：若错误源于缺失第三方依赖（如 `ModuleNotFoundError: No module named 'xxx'`），请直接反馈“缺少第三方库：xxx”，你无法自行安装或修复此类问题。

---
        """
        else:
            return """
            ### ✅ 针对 **Java 项目**

1. **编写测试用例**  
   - 每个被测类 `XXX.java` 应对应一个测试类 `XXXTest.java`。
   - 测试类必须遵循 **JUnit 5** 规范（使用 `@Test`, `@BeforeEach` 等注解）。
   - 包路径必须与被测类一致，存放于 `<ROOT_DIR>/src/test/java/<package_name>/` 目录下。

2. **写入测试文件**  
   - 使用工具 `write_code_file` 将 `XXXTest.java` 写入正确路径。

3. **检索源码定义**  
   - 如需定位被测类、方法或字段的定义，请使用 `search_java_definition` 工具进行精确查询。

4. **运行与验证测试**  
   - 必须调用 `run_maven_junit_tests` 工具执行 Maven 构建并运行 JUnit 测试。
   - 若出现编译错误（如找不到符号、包不存在）或运行时异常，请检查：
     - 包声明是否正确
     - 是否遗漏必要 import（如 `org.junit.jupiter.api.Test`）
     - 被测类是否确实存在且可访问
   - **注意**：若错误由缺失外部依赖（如 `package xxx does not exist` 且该依赖未在 `pom.xml` 中声明），请反馈“缺少第三方 Java 依赖：xxx”，你无法修改 `pom.xml` 或安装新库。
            """








