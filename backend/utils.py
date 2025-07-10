import json

DATA_FILE = "zanpakuto_data.json"

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def calculate_progress(tasks):
    total = len(tasks)
    if total == 0:
        return 0
    completed = sum(1 for t in tasks if t.get("completed"))
    return int((completed / total) * 100)

def update_progress(zanpakuto):
    zanpakuto["shikai_progress"] = calculate_progress(zanpakuto.get("shikai_tasks", []))
    zanpakuto["bankai_progress"] = calculate_progress(zanpakuto.get("bankai_tasks", []))
    zanpakuto["dangai_progress"] = calculate_progress(zanpakuto.get("dangai_tasks", []))
    
    zanpakuto["shikai_unlocked"] = zanpakuto["shikai_progress"] == 100
    zanpakuto["bankai_unlocked"] = zanpakuto["bankai_progress"] == 100
    zanpakuto["dangai_unlocked"] = zanpakuto.get("dangai_progress", 0) == 100
    
