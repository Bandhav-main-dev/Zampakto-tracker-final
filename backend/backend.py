from flask import Flask, request, jsonify
from utils import load_data, save_data, update_progress
from gemini_api import generate_tasks, evaluate_answer

app = Flask(__name__)

@app.route("/zanpakuto", methods=["GET"])
def get_all():
    return jsonify(load_data())

@app.route("/generate_tasks", methods=["POST"])
def generate():
    data = request.json
    domain = data["domain"]
    stage = data["stage"]
    tasks = generate_tasks(domain, stage)
    enriched = [{
        "task": t,
        "answer": "",
        "evaluation": {"score": None, "feedback": ""},
        "completed": False,
        "retry_required": False
    } for t in tasks]
    return jsonify({"tasks": enriched})

@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.json
    task = data["task"]
    answer = data["answer"]
    domain = data["domain"]
    result = evaluate_answer(task, answer, domain)

    result["completed"] = result["score"] >= 7
    result["retry_required"] = not result["completed"]
    return jsonify(result)

@app.route("/update", methods=["POST"])
def update_data():
    updated_data = request.json
    for z in updated_data:
        update_progress(z)
    save_data(updated_data)
    return jsonify({"status": "ok"})

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "zanpakuto backend online"})

if __name__ == "__main__":
    app.run(debug=True)
