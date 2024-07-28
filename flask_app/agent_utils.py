from typing import TypedDict, Dict
from langchain_core.tools import tool
from typing import Annotated
from langchain_openai import ChatOpenAI
from langchain.pydantic_v1 import BaseModel, Field
from langchain_experimental.utilities import PythonREPL
from langgraph.prebuilt import chat_agent_executor
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


repl = PythonREPL()
load_dotenv()


class ChartGenerator(BaseModel):
    instructions: str = Field(
        description="Instructions to generate the chart. Instructions should be clear and concise. Provide the numbers to generate the chart and any other calculations")


@tool("chart_generation", args_schema=ChartGenerator, return_direct=True)
def chart_generation(instructions: str) -> str:
    # Do not remove this docstring
    "Use this to provide instructions to generate a chart. The instructions must be clear and concise. All relevant numbers and calculations must be provided. If the chart is generated successfully, return value will be 'Image saved'. If the chart is not generated, return value will be the error message."

    @tool
    def python_repl(
        code: Annotated[str,
                        "The python code to execute to generate your chart and perform calculations."]
    ):
        """Use this to execute python code. This will return the output of the code"""
        try:
            result = repl.run(code)
        except Exception as e:
            return f"Failed to execute. Error: {repr(e)}"
        result_ret = f"Code:\n```python\n{code}\n```\nStdout: {result}"
        return result_ret

    tools = [python_repl]
    llm = ChatOpenAI(model="gpt-4")

    system_message = """You are a helpful AI assistant, collaborating with other assistants. Your job is to generate a chart based on the instructions provided. Use your tools to generate the chart.
    
Use a non-interactive backend. For example, (matplotlib.use('Agg')). Do not view the chart. This is to make sure we avoid this error: NSWindow should only be instantiated on the main thread! Do not start Matplotlib GUI.
    
Save the image to the 'uploads/images' folder with an appropriate name. Add citation to chart if present. Attempt at least 2 times to generate the chart. 

If you are unable to generate the chart, provide the error message. If you are able to generate the chart and save the image, return Image saved."""

    human_message = instructions

    tools = [python_repl]
    agent_executor = chat_agent_executor.create_tool_calling_executor(
        llm, tools)
    response = agent_executor.invoke(
        {"messages": [SystemMessage(
            content=system_message), HumanMessage(content=human_message)]}
    )
    return response["messages"][-1].content


class FileAnalyzer(BaseModel):
    file_path: str = Field(
        description="Path of the file to analyze. Has to be with respect to the root directory.")
    objective: str = Field(
        description="Objective of the analysis. More precise the objective, better the analysis.")


@tool("file_analysis", args_schema=FileAnalyzer, return_direct=True)
def file_analysis(file_path: str, objective: str) -> str:
    # Do not remove this docstring
    "Use this tool to analyze a file with a given objective. If the file is not parsed correctly, it will return an error message."

    try:

        @tool
        def get_file_content(file_path: Annotated[str, "Path of the file to analyze. Has to be with respect to the root directory."]):
            """Use this tool to get the content of the file. This will return the content of the file."""
            try:
                loader = UnstructuredFileLoader(file_path)
                docs = loader.load()
                context = "\n\n".join([d.page_content for d in docs])

                if ".xlsx" in file_path and len(context.splitlines()) > 200:
                    warning = "WARNING: Content length is longer than recommended for emulating in python using StringIO. Read file directly in python code from file path."
                    context_with_warning = f"{warning}\n\n{context}"
                    return context_with_warning

                return context
            except Exception as e:
                print(f"Error parsing file {file_path}: {e}")
                return "Error retrieving file content."

        @tool
        def python_repl(
            code: Annotated[str,
                            "The python code to perform calculations. To access the output, you must add a print statement."]
        ):
            """Use this to execute python code where you need to perform calculations. To access the output, you must add a print statement. Not using print statement will not return any output."""
            try:
                result = repl.run(code)
            except Exception as e:
                return f"Failed to execute. Error: {repr(e)}"

            if result == "":
                result = "No output from the code. Please add a print statement to get the output."

            result = f"Code:\n```python\n{code}\n```\nStdout: {result}"
            return result

        llm = ChatOpenAI(model='gpt-4o')

        tools = [python_repl, get_file_content]
        agent_executor = chat_agent_executor.create_tool_calling_executor(
            llm, tools)

        system_message = "You are a helpful AI. You will be given a file path. Your job is to analyze the file to achieve the objective. Use your tools to achieve the objective. Be as precise as possible when analyzing the file. Always cite what information you've used and what process you've followed to get the result. If you're making assumptions, state and justify them. If you're dealing with an excel file with a high volume of numerical data, return calculate this using the financial calculator."

        human_message = f"Objective: {objective}. \nFile Path:{file_path}"

        response = agent_executor.invoke(
            {"messages": [SystemMessage(
                content=system_message), HumanMessage(content=human_message)]}
        )

        if response["messages"][-1].content == "":
            return "Error retrieving file content."

        return response["messages"][-1].content
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return f"Error analyzing file {e}"


class FinancialCalculator(BaseModel):
    file_path: str = Field(
        description="Path of the file to analyze. Has to be with respect to the root directory.")

    metric: str = Field(
        description="Financial Metric to be calculated.")

    context: str = Field(
        description="Context of the analysis. This will help the tool to better understand the analysis."
    )


@tool("financial_calculator", args_schema=FinancialCalculator, return_direct=True)
def financial_calculator(file_path: str, metric: str, context: str) -> str:
    # Do not remove this docstring
    "Use this tool to calculate financial metrics."

    try:
        @tool
        def get_file_content(file_path: Annotated[str, "Path of the file to analyze. Has to be with respect to the root directory."]):
            """Use this tool to get the content of the file. This will return the content of the file."""
            try:
                loader = UnstructuredFileLoader(file_path)
                docs = loader.load()
                context = "\n\n".join([d.page_content for d in docs])

                if ".xlsx" in file_path and len(context.splitlines()) > 200:
                    warning = "WARNING: Content length is longer than recommended for emulating in python using StringIO. Read file directly in python code from file path."
                    context_with_warning = f"{warning}\n\n{context}"
                    return context_with_warning

                return context

            except Exception as e:
                print(f"Error parsing file {file_path}: {e}")
                return "Error retrieving file content."

        @tool("python_repl")
        def python_repl(
            code: Annotated[str,
                            "The python code to perform calculations. To access the output, you must add a print statement."]
        ):
            """Use this to execute python code where you need to perform calculations. To access the output, you must add a print statement. Not using print statement will not return any output."""
            try:
                result = repl.run(code)
            except Exception as e:
                return f"Failed to execute. Error: {repr(e)}"

            if result == "":
                result = "No output from the code. Please add a print statement to get the output."

            result = f"Code:\n```python\n{code}\n```\nStdout: {result}"
            return result

        llm = ChatOpenAI(model='gpt-4o')

        tools = [python_repl, get_file_content]
        agent_executor = chat_agent_executor.create_tool_calling_executor(
            llm, tools)

        system_message = """You are a helpful AI that specializes in financial analysis. Your job is to calculate a financial metric. You will be given file file. Use your tools to get the content of the file and perform any calculations needed. 
        
        Always cite what information you've used. Always outline the process you've followed to get the result. If you're making assumptions, state and justify them.
        
        If you're dealing with an excel file with a high volume of numerical data, use the python_repl tool to read and analyze the data.
        """

        human_message = f"Metric: {metric}. \n\nFile:\n{file_path}.\n\nContext: {context}"

        response = agent_executor.invoke(
            {"messages": [SystemMessage(
                content=system_message), HumanMessage(content=human_message)]}
        )

        if response["messages"][-1].content == "":
            return "Error retrieving file content."

        return response["messages"][-1].content
    except Exception as e:
        print(f"Error parsing file: {e}")
        return f"Error analyzing file {e}"
