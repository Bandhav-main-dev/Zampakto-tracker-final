import streamlit as st
import json
import os
import google.generativeai as genai
import re
from config import ADMIN_PASSWORD

# === MUST BE FIRST ===
st.set_page_config(page_title="Zanpakutō Tracker", layout="wide")

# === CONFIG ===
DATA_FILE = os.path.join(os.path.dirname(__file__), "zanpakuto_data.json")
GOOGLE_API_KEY = "AIzaSyDsiipSZorPJHovyDHLb86XXBx-aYipAMM"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-2.0-flash")

# === BLEACH THEME CSS + GETSUGA TENSHO ANIMATION ===
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
    background-color: #1a1a1a; color: white;
    border: 1px solid #ffd700; border-radius: 6px;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #111111;
    border-right: 2px solid #ffd700;
}

/* Getsuga Tensho Flash */
.getsuga-flash {
    text-align: center;
    font-size: 2em;
    font-weight: bold;
    color: #ffffff;
    padding: 1.5rem;
    margin: 1rem 0;
    border-radius: 12px;
    background: linear-gradient(90deg, #111, #3b82f6, #111);
    box-shadow: 0 0 20px #3b82f6;
    animation: getsuga 1s ease-in-out forwards;
}
@keyframes getsuga {
    0% { opacity: 0; transform: scale(0.3) rotate(-25deg); filter: blur(5px); }
    40% { opacity: 1; transform: scale(1.3) rotate(5deg); filter: blur(0); }
    100% { opacity: 1; transform: scale(1.0) rotate(0deg); }
}
</style>
""", unsafe_allow_html=True)

# === GETSUGA ANIMATION HELPER ===
def getsuga_tensho(level):
    st.markdown(f"""
        <div class="getsuga-flash">
            ⚡ GETSUGA TENSHŌ — {level.upper()} UNLEASHED ⚡
        </div>
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
        getsuga_tensho(level)
        st.markdown(f"##### 🗡️ \"_{zanpakuto['release_command']}_\"")
        st.success(f"🎉 {level.capitalize()} Unlocked!")
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

    z = next((zan for zan in data if zan["name"] == selected), None)
    if z:
        st.markdown(f"### 🗡️ {z['name']} ({z['kanji']}) — *{z['domain']}*")
        st.markdown(f"> {z['power']}")
        col1, col2, col3 = st.columns(3)
        with col1: progress_bar("shikai", z.get("shikai_progress", 0))
        with col2: progress_bar("bankai", z.get("bankai_progress", 0))
        with col3: progress_bar("dangai", z.get("dangai_progress", 0))

# 🔐 Admin Login System
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if page == "Admin Stats" and not st.session_state.admin_authenticated:
    st.markdown("<h2 style='color:#FFD700;'>🔐 Admin Login</h2>", unsafe_allow_html=True)
    password_input = st.text_input("Enter Admin Password", type="password")
    if st.button("Login"):
        if password_input == ADMIN_PASSWORD:
            st.success("Access granted! Welcome, Captain.")
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Wrong password. Access denied.")
            st.rerun()

# === Admin Page UI ===
elif page == "Admin Stats":
    st.markdown("<h1 style='color:#FFD700;'>🧙‍♂️ Admin Zanpakutō Stats</h1>", unsafe_allow_html=True)
    st.markdown("---")

    for z_idx, z in enumerate(data):
        # Create unique key prefix using index and name
        zan_key = f"{z_idx}_" + re.sub(r'\W+', '_', z["name"])

        with st.container():
            st.markdown(f"### 🗡️ {z['name']} ({z['domain']})")
            cols = st.columns(6)

            cols[0].metric("Shikai 🔓", "✅" if z["shikai_unlocked"] else "❌")
            cols[1].progress(z["shikai_progress"] / 100, text=f"{z['shikai_progress']}%")

            cols[2].metric("Bankai 🔓", "✅" if z["bankai_unlocked"] else "❌")
            cols[3].progress(z["bankai_progress"] / 100, text=f"{z['bankai_progress']}%")

            cols[4].metric("Dangai 🔓", "✅" if z["dangai_unlocked"] else "❌")
            cols[5].progress(z["dangai_progress"] / 100, text=f"{z['dangai_progress']}%")

            with st.expander("📜 View Tasks & Status"):
                st.subheader("Shikai Tasks")
                for i, task in enumerate(z["shikai_tasks"]):
                    task_key = re.sub(r'\W+', '_', task['task'])[:40]
                    st.checkbox(
                        f"🔹 {task['task']}",
                        value=task["completed"],
                        disabled=True,
                        key=f"{zan_key}_shikai_{i}_{task_key}"
                    )

                st.subheader("Bankai Tasks")
                for i, task in enumerate(z["bankai_tasks"]):
                    task_key = re.sub(r'\W+', '_', task['task'])[:40]
                    st.checkbox(
                        f"🔸 {task['task']}",
                        value=task["completed"],
                        disabled=True,
                        key=f"{zan_key}_bankai_{i}_{task_key}"
                    )

                st.subheader("Dangai Tasks")
                for i, task in enumerate(z["dangai_tasks"]):
                    task_key = re.sub(r'\W+', '_', task['task'])[:40]
                    st.checkbox(
                        f"🔻 {task['task']}",
                        value=task["completed"],
                        disabled=True,
                        key=f"{zan_key}_dangai_{i}_{task_key}"
                    )

            with st.expander("🛠️ Admin Controls (Unlock Powers)"):
                c1, c2, c3 = st.columns(3)
                z["shikai_unlocked"] = c1.checkbox("Unlock Shikai", value=z["shikai_unlocked"], key=f"{zan_key}_unlock_shikai")
                z["bankai_unlocked"] = c2.checkbox("Unlock Bankai", value=z["bankai_unlocked"], key=f"{zan_key}_unlock_bankai")
                z["dangai_unlocked"] = c3.checkbox("Unlock Dangai", value=z["dangai_unlocked"], key=f"{zan_key}_unlock_dangai")

            st.markdown("---")

    # Save updated data after unlock toggles
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
