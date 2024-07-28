import os
from collections import defaultdict
from anytree import Node, RenderTree
from anytree.exporter import JsonExporter
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import chat_agent_executor
import uuid
from flask_app.agent_utils import chart_generation, file_analysis, financial_calculator

load_dotenv()


def analyze_file(file_path):
    file_name = os.path.basename(file_path)
    loader = UnstructuredFileLoader(file_path)

    try:
        docs = loader.load()
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return "Error parsing file"

    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])

    context = format_docs(docs)
    llm = ChatOpenAI()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a financial analyst. You will be given a file name and the contents of the file. Your job is describe in 20 words what useful information can this file provide. Note that the description may be used to search for this file."),
        ("user", "{file_name} \n {input}")
    ])
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    analysis = chain.invoke({"input": context, "file_name": file_name})

    return analysis


def analyze_directory_objective(repo_overview, objective, agent_executor, thread_id):
    system_message_content = f"""You are a helpful AI. You are given a directory structure of the company files and you need to analyze them based on the objective. Use the tools you have at your disposal to achieve the objective. 

Always explain how you've conducted your analysis: steps taken to get to the answer. If you're making assumptions, state and justify them.

For example, if the user asks for a financial metric, give the result, then outline the files used, the values used from the files, and the calculations performed (if applicable). 

This is the directory structure(Note when specifying a file path, you are supposed to include the root): \n\n{repo_overview}"""
    human_message_content = f"This is the objective: {objective}" + \
        " Keep response to a maximum of a 100 words."

    response = agent_executor.invoke(
        {"messages": [SystemMessage(content=system_message_content), HumanMessage(
            content=human_message_content)]},
        config={"configurable": {"thread_id": thread_id}}
    )
    analysis = str(response["messages"][-1].content)

    return analysis


def example_agent_setup(system_message, agent_executor, thread_id):
    system_message_content = system_message

    human_message_content = f"Say Hi!"

    response = agent_executor.invoke(
        {"messages": [SystemMessage(content=system_message_content), HumanMessage(
            content=human_message_content)]},
        config={"configurable": {"thread_id": thread_id}}
    )
    analysis = str(response["messages"][-1].content)

    return analysis


def setup_agent_executor(objective):
    tools = [file_analysis, chart_generation, financial_calculator]
    model = ChatOpenAI(model='gpt-4o')
    memory = SqliteSaver.from_conn_string(":memory:")
    agent_executor = chat_agent_executor.create_tool_calling_executor(
        model, tools, checkpointer=memory)
    thread_id = str(uuid.uuid4())
    return agent_executor, thread_id


def create_directory_tree(start_path, file_analysis=False):
    file_type_count = defaultdict(int)
    ALLOWED_EXTENSIONS = {'.csv', '.xls', '.xlsx',
                          '.pdf', '.doc', '.docx', '.txt', '.md'}

    def add_nodes(parent_node, path, file_analysis=file_analysis):
        for entry in os.scandir(path):
            if entry.is_file():
                file_type = os.path.splitext(entry.path)[1].lower()
                if file_type in ALLOWED_EXTENSIONS:
                    file_type_count[file_type] += 1
                    if file_analysis:
                        file_analysis = analyze_file(entry.path)
                        Node(entry.name, parent=parent_node,
                             file_analysis=file_analysis)
                    else:
                        Node(entry.name, parent=parent_node)
            else:
                child_node = Node(entry.name, parent=parent_node)
                add_nodes(child_node, entry.path, file_analysis=file_analysis)

    root_node = Node(os.path.basename(start_path.rstrip('/')))
    add_nodes(root_node, start_path, file_analysis=file_analysis)

    metadata_node = Node("metadata", parent=root_node)
    for file_type, count in file_type_count.items():
        Node(f"{file_type}: {count}", parent=metadata_node)

    exporter = JsonExporter()
    repo_overview_json = exporter.export(root_node)

    return repo_overview_json


def create_directory_tree_text(start_path, file_analysis=False):
    file_type_count = defaultdict(int)
    ALLOWED_EXTENSIONS = {'.csv', '.xls', '.xlsx',
                          '.pdf', '.doc', '.docx', '.txt', '.md'}

    def add_nodes(parent_node, path, file_analysis=file_analysis):
        for entry in os.scandir(path):
            if entry.is_file():
                file_type = os.path.splitext(entry.path)[1].lower()
                if file_type in ALLOWED_EXTENSIONS:
                    file_type_count[file_type] += 1
                    file_name = f"{entry.name} (Path: {entry.path})"
                    if file_analysis:
                        analysis_result = analyze_file(entry.path)
                        Node(f"{file_name} (Content Summary: {analysis_result})",
                             parent=parent_node)
                    else:
                        Node(file_name, parent=parent_node)
            elif entry.is_dir():
                child_node = Node(entry.name, parent=parent_node)
                add_nodes(child_node, entry.path, file_analysis=file_analysis)

    root_node = Node(os.path.basename(start_path.rstrip('/')))
    add_nodes(root_node, start_path, file_analysis=file_analysis)

    metadata_node = Node("metadata", parent=root_node)
    for file_type, count in file_type_count.items():
        Node(f"{file_type}: {count}", parent=metadata_node)

    # Generate and print the textual representation of the directory tree
    tree_representation = ""
    for pre, fill, node in RenderTree(root_node):
        tree_representation += f"{pre}{node.name}.\n"

    return tree_representation
