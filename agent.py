# app.py

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

    def __init__(self, dataset):
        self.dataset = dataset
        self.test_architect = create_test_architect()
        self.test_designer=create_test_designer()
        self.test_developer=create_test_development_engineer()
        self.cot1_desc = read_file('prompt/test_plan/test_plan.md')
        self.cot1_out = read_file('prompt/test_plan/test_plan_out.md')
        self.cot2_desc = read_file('prompt/test_design/test_design.md')
        self.cot2_out = read_file('prompt/test_design/test_design_out.md')
        self.cot4_desc = read_file('prompt/test_development/test_develop.md')
        self.cot4_out = read_file('prompt/test_development/test_develop_out.md')

    def stream_run(self):
        """
        一个 generator，用于逐步流式返回每个 Chat/Chunk 的内容
        """
        docs = load_dataset(self.dataset)

        # --------------------------------------------------------------------
        # Cot1 — Test planning
        # --------------------------------------------------------------------
        if 1 in self.DEBUG_RUN:
            print("Step 1: Test planning...")

            step1 = PipelineStep(
                agent=self.test_architect,
                template_text=self.cot1_desc,
                expected_output=self.cot1_out,
                output_file="output/" + docs.dataset_name + "_test_plan.md"
            )

            streaming_output = step1.run(
                srs=docs.srs_text,
                class_diagram=docs.uml_class_text,
                sequence_diagram=docs.uml_sequence_text
            )

            # 每个流式块逐条 yield
            for chunk in streaming_output:
                yield chunk
            # 最终结果在 streaming_output.result
            final1 = streaming_output.result
            # 你也可以 yield final1.raw 或 final1.content

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
            from pathlib import Path

            base = Path('output')

            path = base / (docs.dataset_name+  "testcase.md")

            for module in modules:
                step2_out = step2.run(
                    sut=module.to_json
                )
                for chunk in step2_out:
                    yield chunk
                result = step2_out.result.raw
                write_file(path=path,content=result,overwrite=False)

            print('Cot2 — Test design end')

        if 4 in self.DEBUG_RUN:
            print("Step 4: Test develop...")

            testcase=read_file('output/'+docs.dataset_name+"testcase.md")
            step4 = PipelineStep(
                agent=self.test_developer,
                template_text=self.cot4_desc,
                expected_output=self.cot4_out,
                output_file=''
            )

            step4_output = step4.run(
                TEST_CASES_JSON=testcase,
                class_diagram=docs.uml_class_text,
                ROOT_DIR=r"/home/mgh/dev/data/mate_workplace/stock/backend"
            )
            for chunk in step4_output:
                yield chunk
                print(chunk.content, end="", flush=True)



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
            from pathlib import Path

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








