from crewai import Agent
from crewai import LLM

from tools.code_search import CodeSearchTool,SearchJavaCodeTool
from tools.run_py_test import RunProjectGeneratedTestsTool
from tools.write_python_file import WriteCodeFileTool
from tools.run_junit_tests import MavenJUnitTool
from config import config

llm = LLM(
    model=config.config['llm']['model'],
    api_key=config.config['llm']['api_key'],
    base_url=config.config['llm']['base_url']
)


def create_test_architect():
    return Agent(
        role="Test Architect",
        goal="""
            Unit testing of the entire system is difficult, as you need to break it down into several functional modules. 
            Each functional module contains several features, and each feature contains several methods. 
            They have dependencies and work together to complete a set of functional requirements. 
            The partitioned features will serve as the smallest unit of work, and testers will generate unit tests for all methods in a feature each time, ensuring that each feature is independent and contains sufficient contextual information. 
            Output the divided functional modules as the test plan.
        """,
        backstory="A testing architect who excels in breaking down the entire project and specifying testing plans based on the principle of high cohesion and low coupling.",
        llm=llm
    )


def create_test_designer():
    return Agent(
        role="Test Designer",
        goal="Design comprehensive unit test cases based on requirement descriptions, which are described in text form and do not rely on programming languages.",
        backstory="An experienced software testing engineer designs diverse and sufficient test cases for each functional requirement in the requirements document.",
        llm=llm
    )


def create_test_development_engineer():
    return Agent(
        role="Test Development Engineer",
        goal="Develop text unit test cases into automated code, using Junit or UnitTest frameworks to ensure that the code is compiled correctly, and use a range of tools to assist you in coding.",
        backstory="Experienced test and development engineer, skilled in developing test cases into test code based on text test cases and project code structures written by testers, proficient in Junit and UnitTest frameworks.",
        llm=llm,
        tools=[CodeSearchTool(), RunProjectGeneratedTestsTool(), WriteCodeFileTool(),MavenJUnitTool(),SearchJavaCodeTool()]
    )

def create_test_debugger():
    return Agent(
        role="Test Debugger",
        goal="Run test cases, provide test reports, and provide effective feedback for test cases that fail to run.",
        backstory="""
        You are a senior testing and debugging engineer with years of experience in software testing and debugging 
        You have been working in complex systems and high reliability software projects for a long time, 
        familiar with the complete process from unit testing to system testing, especially skilled in executing test cases, 
        analyzing failure reasons, locating defect root causes, and structuring the results into reproducible and traceable test reports.
        """,
        llm=llm,
        tools=[CodeSearchTool(), RunProjectGeneratedTestsTool(),MavenJUnitTool(),SearchJavaCodeTool()]
    )


