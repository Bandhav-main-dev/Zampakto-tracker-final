import streamlit as st
import json
import os
import google.generativeai as genai

# === MUST BE FIRST ===
st.set_page_config(page_title="Zanpakutō Tracker", layout="wide")

# === CONFIG ===
DATA_FILE = os.path.join(os.path.dirname(__file__), "zanpakuto_data.json")
GOOGLE_API_KEY = "AIzaSyDsiipSZorPJHovyDHLb86XXBx-aYipAMM"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-2.0-flash")

# === BLEACH THEME CSS + ANIMATION ===
st.markdown("""
<style>
body { background-color: #0a0a0a; color: #f1f1f1; }

h1,h2,h3,h4 { color: #ffd700; font-weight: bold; }

.stButton button {
    background-color: #ef4444; color: white;
    border: none; border-radius: 8px;
    padding: 0.5em 1.2em; font-weight: bold;
}
.stButton button:hover {
    background-color: #facc15; color: black;
}

textarea, input {
    background-color: #1f1f1f; color: white;
    border: 1px solid #ffd700; border-radius: 6px;
}

/* Sidebar dark background */
section[data-testid="stSidebar"] {
    background-color: #121212;
    border-right: 1px solid #444;
}

.spiritual-slash {
    position: relative;
    text-align: center;
    font-size: 2em;
    font-weight: bold;
    color: #fff;
    background: linear-gradient(90deg, #ef4444, #facc15, #fff);
    padding: 1rem 2rem;
    margin: 1rem 0;
    border-radius: 12px;
    box-shadow: 0 0 15px #facc15;
    animation: slashFlash 1s ease-out forwards;
}

@keyframes slashFlash {
    0% { opacity: 0; transform: scale(0.5) rotate(-15deg); filter: blur(4px); }
    50% { opacity: 1; transform: scale(1.2) rotate(3deg); filter: blur(0px); }
    100% { opacity: 1; transform: scale(1.0) rotate(0deg); }
}

@keyframes braveUnlock {
    0% {
        transform: scale(0.8);
        opacity: 0;
        filter: brightness(0.4) blur(4px);
    }
    40% {
        transform: scale(1.05);
        opacity: 1;
        filter: brightness(1.4) blur(0px);
        border: 4px solid gold;
        box-shadow: 0 0 40px gold;
    }
    100% {
        transform: scale(1);
        filter: brightness(1);
    }
}

.brave-unlock {
    font-size: 2.4rem;
    text-align: center;
    margin-top: 20px;
    padding: 1.5rem 2rem;
    color: #fff;
    border: 3px solid #FFD700;
    border-radius: 16px;
    background: linear-gradient(90deg, #000000, #FFD70022, #000000);
    box-shadow: 0 0 30px #FFD70066;
    animation: braveUnlock 1.6s ease-out;
}
</style>
""", unsafe_allow_html=True)

# === LOAD / SAVE ===
def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === PROGRESS BAR ===
def progress_bar(label, percent):
    color_map = {
        "shikai": "#facc15",
        "bankai": "#ef4444",
        "dangai": "#e5e7eb"
    }
    hex_color = color_map.get(label.lower(), "#3b82f6")
    text_color = "#000000" if label.lower() == "dangai" else "#ffffff"

    st.markdown(f"""
        <div style="margin-bottom:10px;">
            <div style="font-weight:600;">{label.capitalize()} - {percent}%</div>
            <div style="background-color:#2e2e2e; border-radius:5px; height:24px; overflow:hidden;">
                <div style="width:{percent}%; background-color:{hex_color}; color:{text_color}; text-align:center; line-height:24px; height:24px;">
                    {percent}%
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# === AI EVALUATION ===
def evaluate_answer(question, answer):
    prompt = f"Question: {question}\nAnswer: {answer}\n\nEvaluate the answer in 1-2 lines."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ AI Error: {e}"

# === UNLOCK EFFECT ===
def reiatsu_burst(level):
    emoji_map = {
        "shikai": "🟡",
        "bankai": "🔴",
        "dangai": "⚪"
    }
    reiatsu = emoji_map.get(level.lower(), "✨")
    st.markdown(f"#### {reiatsu * 20}")

# === TASK HANDLER ===
def handle_tasks(zanpakuto, level, data):
    tasks_key = f"{level}_tasks"
    progress_key = f"{level}_progress"
    unlocked_key = f"{level}_unlocked"
    test_question_key = f"{level}_test_question"
    test_passed_key = f"{level}_test_passed"

    changed = False
    if zanpakuto.get(unlocked_key):
        st.success(f"✅ {level.capitalize()} already unlocked!")
        progress_bar(level, 100)
        return 100, changed

    tasks = zanpakuto.get(tasks_key, [])
    for idx, task in enumerate(tasks):
        key = f"{zanpakuto['name']}_{level}_{idx}"
        checked = st.checkbox(task["task"], value=task.get("completed", False), key=key)
        if checked != task.get("completed", False):
            task["completed"] = checked
            changed = True

    completed_count = sum(1 for t in tasks if t.get("completed"))
    task_progress = int((completed_count / len(tasks)) * 90) if tasks else 0

    test_questions = zanpakuto.get(test_question_key, [])
    test_score = 0

    if test_questions:
        st.markdown(f"### 🧪 {level.capitalize()} Test Questions")
        for i, q in enumerate(test_questions, 1):
            st.markdown(f"**{i}. {q}**")
            ans_key = f"answer_{zanpakuto['name']}_{level}_{i}"
            ans = st.text_area("Your Answer", key=ans_key)
            if ans.strip():
                feedback_key = f"feedback_{zanpakuto['name']}_{level}_{i}"
                if feedback_key not in st.session_state:
                    with st.spinner("AI Evaluating..."):
                        feedback = evaluate_answer(q, ans)
                        st.session_state[feedback_key] = feedback
                st.markdown(f"🧠 Feedback: _{st.session_state[feedback_key]}_")
                if any(w in st.session_state[feedback_key].lower() for w in ["correct", "good", "right", "accurate"]):
                    test_score += 1

        passed_now = test_score >= len(test_questions) // 2 + 1
        if passed_now != zanpakuto.get(test_passed_key, False):
            zanpakuto[test_passed_key] = passed_now
            changed = True
        if passed_now:
            st.markdown(f'<div class="spiritual-slash">{level.capitalize()} Test Passed!</div>', unsafe_allow_html=True)

    total_progress = min(task_progress + (10 if zanpakuto.get(test_passed_key) else 0), 100)
    if zanpakuto.get(progress_key, 0) != total_progress:
        zanpakuto[progress_key] = total_progress
        changed = True

    progress_bar(level, total_progress)

    if total_progress == 100 and not zanpakuto.get(unlocked_key):
        zanpakuto[unlocked_key] = True
        reiatsu_burst(level)
        st.markdown(f'<div class="brave-unlock">🔥 {level.capitalize()} Awakened! 🔥</div>', unsafe_allow_html=True)
        st.markdown(f"##### 🗡️ \"_{zanpakuto['release_command']}_\"")
        changed = True

    if changed:
        save_data(data)

    return total_progress, changed

def reset_zanpakuto_progress(data):
    for z in data:
        for level in ["shikai", "bankai", "dangai"]:
            z[f"{level}_unlocked"] = False
            z[f"{level}_progress"] = 0
            z[f"{level}_test_passed"] = False
            for task in z.get(f"{level}_tasks", []):
                task["completed"] = False

# === MAIN LOGIC ===
data = load_data()
zanpakuto_names = [z["name"] for z in data]
page = st.sidebar.radio("🔽 Navigation", ["Zanpakutō Details", "Summary Page", "Admin Stats"])

if page == "Zanpakutō Details":
    selected_name = st.sidebar.selectbox("Select Zanpakutō", zanpakuto_names)
    z = next((x for x in data if x["name"] == selected_name), None)

    if z:
        st.markdown(f"### 🗡️ {z['name']} ({z['kanji']})")
        st.markdown(f"**Domain:** {z['domain']} — _{z['power']}_")
        st.markdown("---")

        total_changed = False

        # Shikai
        _, changed = handle_tasks(z, "shikai", data)
        total_changed |= changed

        # Bankai
        if z.get("shikai_unlocked"):
            _, changed = handle_tasks(z, "bankai", data)
            total_changed |= changed
        else:
            st.info("🔒 Unlock Shikai first to see Bankai tasks.")

        # Dangai
        if z.get("bankai_unlocked"):
            _, changed = handle_tasks(z, "dangai", data)
            total_changed |= changed
        elif z.get("shikai_unlocked"):
            st.info("🔒 Unlock Bankai first to see Dangai tasks.")

        if total_changed:
            save_data(data)

elif page == "Summary Page":
    st.title("📊 Zanpakutō Summary")
    selected = st.selectbox("View Summary of", zanpakuto_names)
    for z in data:
        if z["name"] == selected:
            st.markdown(f"### 🗡️ {z['name']} ({z['kanji']}) — *{z['domain']}*")
            st.markdown(f"> {z['power']}")
            col1, col2, col3 = st.columns(3)
            with col1: progress_bar("shikai", z.get("shikai_progress", 0))
            with col2: progress_bar("bankai", z.get("bankai_progress", 0))
            with col3: progress_bar("dangai", z.get("dangai_progress", 0))

elif page == "Admin Stats":
    st.title("🛡️ Admin Dashboard")
    total_completed = 0
    for z in data:
        completed = sum(
            sum(1 for t in z.get(level+"_tasks", []) if t.get("completed", False))
            for level in ["shikai", "bankai", "dangai"]
        )
        total_completed += completed
        st.markdown(f"🔹 {z['name']}: **{completed}** tasks completed")
    st.markdown("---")
    st.markdown(f"**📈 Total Completed Tasks Across All Zanpakutō: {total_completed}**")

    st.markdown("## 🔄 Reset Zanpakutō Progress")

    reset_pass = st.text_input("Enter Admin Password to Reset:", type="password")

    if st.button("🗑️ Reset All Progress"):
        if reset_pass == "Bankai7241":  # ← change this to your preferred password
            reset_zanpakuto_progress(data)
            save_data(data)
            st.success("✅ All progress has been reset!")
        else:
            st.error("❌ Incorrect password.")

