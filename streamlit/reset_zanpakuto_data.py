import json

DATA_FILE = "/workspaces/Zampakto-tracker-final/streamlit/zanpakuto_data.json"

def reset_progress(zanpakuto):
    for level in ["shikai", "bankai", "dangai"]:
        zanpakuto[f"{level}_progress"] = 0
        zanpakuto[f"{level}_unlocked"] = False
        zanpakuto[f"{level}_test_passed"] = False

        for task in zanpakuto.get(f"{level}_tasks", []):
            task["completed"] = False

    return zanpakuto

def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for z in data:
        reset_progress(z)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ Zanpakutō progress has been reset.")

if __name__ == "__main__":
    main()
