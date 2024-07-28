from flask import request, jsonify, render_template, current_app, send_from_directory
from werkzeug.utils import secure_filename
import os
import zipfile
import json
from flask_app.controllers import analyze_directory_objective, setup_agent_executor, create_directory_tree, create_directory_tree_text, example_agent_setup
from langchain_core.messages import HumanMessage
from flask_app.example_processing import save_example_data, load_example_data

agent_executor = None
thread_id = None

# Ensure the directory for uploaded images exists
if not os.path.exists('uploads/images'):
    os.makedirs('uploads/images')

EXAMPLE_ANALYSIS_PATH = 'example_data/example_analysis.json'
EXAMPLE_TREE_PATH = 'example_data/example_tree.json'


@current_app.route('/')
def index():
    return render_template('index.html')


@current_app.route('/upload', methods=['POST'])
def upload_file():
    global agent_executor, thread_id
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(current_app.config['UPLOAD_FOLDER'])

        extracted_dir = os.path.join(
            current_app.config['UPLOAD_FOLDER'], os.path.splitext(filename)[0])

        objective = request.form.get('objective', '')

        agent_executor, thread_id = setup_agent_executor(objective)

        # File analysis flag is used to determine if the file level analysis should be conducted
        # repo_overview_json = create_directory_tree(
        #     extracted_dir, file_analysis=True)

        with open('example_data/SaaSCO_Tree.json', 'r') as f:
            repo_overview_json = json.load(f)

        # Read text from example_data/ChipCo.txt and save as chipco_text
        with open('example_data/SaaSCo.txt', 'r') as f:
            chipco_text = f.read()
        repo_overview_text = chipco_text

        # repo_overview_text = create_directory_tree_text(
        #     extracted_dir, file_analysis=True)

        directory_analysis = analyze_directory_objective(
            repo_overview_text, objective, agent_executor, thread_id)

        # Save processed data for an example including objective
        save_example_data(directory_analysis, repo_overview_json,
                          objective, repo_overview_text)

        return jsonify({"analysis": directory_analysis, "tree": repo_overview_json})


@current_app.route('/ask', methods=['POST'])
def ask_question():
    global agent_executor, thread_id
    if not agent_executor or not thread_id:
        return "Session not initialized"

    question = request.json.get('question', '')
    question += "\n Return how you've conducted your analysis: steps taken to get to the answer. If you're making assumptions, state and justify them."

    response = agent_executor.invoke({"messages": [HumanMessage(content=question)]}, config={
                                     "configurable": {"thread_id": thread_id}})

    follow_up_analysis = str(response["messages"][-1].content)

    return jsonify({"response": follow_up_analysis})


@current_app.route('/images')
def get_images():
    images_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
    images = [f for f in os.listdir(images_dir) if os.path.isfile(
        os.path.join(images_dir, f))]
    return jsonify(images)


@current_app.route('/images/<filename>')
def uploaded_file(filename):
    images_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
    return send_from_directory(images_dir, filename)


@current_app.route('/example', methods=['GET'])
def get_example():
    analysis, tree, objective, system_message = load_example_data()

    # Setup a new agent with the loaded objective
    global agent_executor, thread_id
    agent_executor, thread_id = setup_agent_executor(objective)
    example_agent_setup(system_message, agent_executor, thread_id)

    return jsonify({"analysis": analysis, "tree": tree, "objective": objective})
