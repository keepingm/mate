#!/usr/bin/env python
# src/research_crew/main.py
import os
from pathlib import Path

from dotenv import load_dotenv

# Create output directory if it doesn't exist

os.makedirs('output', exist_ok=True)

CURRENT = Path(__file__).resolve()
ROOT_DIR = CURRENT.parents[2]  # 确保找到根目录
load_dotenv(ROOT_DIR / ".env")
from agent import TestAgentApp
from config import config


# def run():
#     # hone
#     srs = read_file('D:\BJFU\Project\PythonProject\crewai\\test_crew\dataset\hone\docs\PRD.md')
#     class_diagram = read_file('D:\BJFU\Project\PythonProject\crewai\\test_crew\dataset\hone\docs\\UML_class.md')
#     architecture = read_file(
#         'D:\BJFU\Project\PythonProject\crewai\\test_crew\dataset\hone\docs\\architecture_design.md')
#     uml_sequence = read_file('D:\BJFU\Project\PythonProject\crewai\\test_crew\dataset\hone\docs\\UML_sequence.md')
#     # stock
#     # srs = read_file('D:\BJFU\Project\PythonProject\crewai\\test_crew\dataset\stock\SRS.md')
#     # class_diagram = read_file('D:\BJFU\Project\PythonProject\crewai\\test_crew\dataset\stock\Architectural_Views.md')
#     # architecture = read_file('D:\BJFU\Project\PythonProject\crewai\\test_crew\dataset\stock\Architecture_Documentation.md')
#     # uml_sequence = ''
#     # readtime
#     # srs = read_file('D:\BJFU\Project\PythonProject\crewai\\test_crew\dataset\\readtime\docs\\requirements.txt')
#     # class_diagram = read_file('D:\BJFU\Project\PythonProject\crewai\\test_crew\dataset\\readtime\docs\\UML_class.md')
#     # architecture=read_file('D:\BJFU\Project\PythonProject\crewai\\test_crew\dataset\\readtime\docs\\architecture_design.md')
#     # uml_sequence=read_file('D:\BJFU\Project\PythonProject\crewai\\test_crew\dataset\\readtime\docs\\UML_sequence.md')
#     """
#     Run the research crew.
#     """
#     inputs = {
#         'requirement_text': srs,
#         'uml_class': class_diagram,
#         'architecture':architecture,
#         'uml_sequence':uml_sequence,
#         'output':'D:\\BJFU\\Project\\PythonProject\\crewai\\test_crew\\dataset\\hone\\unit_tests'
#     }
#
#     # Create and run the crew
#     crew_instance = TestCrew()  # ← 创建实例
#     result = crew_instance.crew().kickoff(inputs=inputs)
#
#     # Print the result
#     print("\n\n=== FINAL REPORT ===\n\n")
#     print(result.raw)
#     print(f"use ：{result.usage_metrics}")



if __name__ == "__main__":
    app=TestAgentApp(dataset_name='hone')
    for _ in app.stream_run(debug=True):
        pass

