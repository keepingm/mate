# app.py
import json
from pathlib import Path

from agents.test_agent import (
    create_test_architect,
    create_test_designer,
    create_test_development_engineer
)
from piplines.core import PipelineStep
from utils.dataset_utils import load_dataset
from utils.file_utils import read_file
from utils.file_utils import write_file
from utils.memory_utils import Memory


class TestAgentApp:
    DEBUG_RUN = {4}

    def __init__(self, *, dataset_name):
        self.dataset_name = dataset_name
        self.data = load_dataset(dataset_name)
        self.test_architect = create_test_architect()
        self.test_designer=create_test_designer()
        self.test_developer=create_test_development_engineer()
        self.cot1_desc = read_file('prompt/test_plan/test_plan.md')
        self.cot1_out = read_file('prompt/test_plan/test_plan_out.md')
        self.cot2_desc = read_file('prompt/test_design/test_design.md')
        self.cot2_out = read_file('prompt/test_design/test_design_out.md')
        self.cot4_desc = read_file('prompt/test_development/test_develop.md')
        self.cot4_out = read_file('prompt/test_development/test_develop_out.md')

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








