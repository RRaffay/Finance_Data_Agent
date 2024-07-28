import json
import os

EXAMPLE_ANALYSIS_PATH = 'example_data/example_analysis.json'
EXAMPLE_TREE_PATH = 'example_data/example_tree.json'
EXAMPLE_OBJECTIVE_PATH = 'example_data/objective.txt'
EXAMPLE_SYSTEM_MSG_PATH = 'example_data/system_message.txt'


def save_example_data(analysis, tree, objective, repo_overview):
    if not os.path.exists('example_data'):
        os.makedirs('example_data')

    with open(EXAMPLE_ANALYSIS_PATH, 'w') as f:
        json.dump(analysis, f)

    with open(EXAMPLE_TREE_PATH, 'w') as f:
        json.dump(tree, f)

    with open(EXAMPLE_OBJECTIVE_PATH, 'w') as f:
        f.write(objective)

    with open(EXAMPLE_SYSTEM_MSG_PATH, 'w') as f:
        system_message_content = f"""You are a helpful AI. You are given a directory structure of the company files and you need to analyze them based on the objective. Use the tools you have at your disposal to achieve the objective. 

Always explain how you've conducted your analysis: steps taken to get to the answer. If you're making assumptions, state and justify them.

For example, if the user asks for a financial metric, give the result, then outline the files used, the values used from the files, and the calculations performed (if applicable). 

This is the directory structure(Note when specifying a file path, you are supposed to include the root): \n\n{repo_overview}"""
        f.write(system_message_content)


def load_example_data():
    with open(EXAMPLE_ANALYSIS_PATH, 'r') as f:
        analysis = json.load(f)

    with open(EXAMPLE_TREE_PATH, 'r') as f:
        tree = json.load(f)

    with open(EXAMPLE_OBJECTIVE_PATH, 'r') as f:
        objective = f.read()

    with open(EXAMPLE_SYSTEM_MSG_PATH, 'r') as f:
        system_message = f.read()

    return analysis, tree, objective, system_message
