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
section[data-testid="stSidebar"] {
    background-color: #111111;
    border-right: 2px solid #ffd700;
}
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
def unlock_animation(zanpakuto):
    st.markdown("""
    <style>
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
    .release {
        font-size: 32px;
        font-weight: bold;
        color: gold;
        text-shadow: 0 0 10px #FFD700, 0 0 20px #FFA500;
        animation: fadein 2s ease-in-out;
    }
    .name {
        font-size: 40px;
        color: white;
        font-weight: bold;
        text-shadow: 0 0 10px #fff, 0 0 20px #f0f;
    }
    @keyframes fadein {
        from { opacity: 0; transform: scale(0.5); }
        to { opacity: 1; transform: scale(1); }
    }
    </style>
    """, unsafe_allow_html=True)

    with st.spinner("Spiritual Pressure Rising..."):
        st.sleep(2)

    st.markdown('<div class="centered">', unsafe_allow_html=True)
    st.markdown(f'<div class="release">"{zanpakuto["release_command"]}"</div>', unsafe_allow_html=True)
    st.sleep(1.5)
    st.markdown(f'<div class="name">{zanpakuto["name"]} — {zanpakuto["kanji"]}</div>', unsafe_allow_html=True)
    st.image("assets/spirit_burst.gif", caption="Bankai Release!", use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.balloons()
    st.toast(f"{zanpakuto['name']} Unlocked!", icon="⚔️")

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
            <div style="font-weight:600; color: {hex_color};">{label.capitalize()} - {percent}%</div>
            <div style="background-color:#2e2e2e; border-radius:6px; height:26px; overflow:hidden;">
                <div style="width:{percent}%; background-color:{hex_color}; color:{text_color}; text-align:center; line-height:26px; height:26px;">
                    {percent}%
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# === AI EVALUATION ===
def evaluate_answer(question, answer):
    prompt = f"Question: {question}\nAnswer: {answer}\n\nEvaluate the answer briefly."
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
    keys = {
        "tasks": f"{level}_tasks",
        "progress": f"{level}_progress",
        "unlocked": f"{level}_unlocked",
        "test": f"{level}_test_question",
        "passed": f"{level}_test_passed"
    }

    changed = False
    if zanpakuto.get(keys["unlocked"]):
        st.success(f"✅ {level.capitalize()} already unlocked!")
        progress_bar(level, 100)
        return 100, changed

    tasks = zanpakuto.get(keys["tasks"], [])
    for idx, task in enumerate(tasks):
        key = f"{zanpakuto['name']}_{level}_{idx}"
        checked = st.checkbox(task["task"], value=task.get("completed", False), key=key)
        if checked != task.get("completed", False):
            task["completed"] = checked
            changed = True

    task_done = sum(1 for t in tasks if t.get("completed"))
    task_progress = int((task_done / len(tasks)) * 90) if tasks else 0

    questions = zanpakuto.get(keys["test"], [])
    score = 0

    if questions:
        st.markdown(f"### 🧪 {level.capitalize()} Test Questions")
        for i, q in enumerate(questions, 1):
            st.markdown(f"**{i}. {q}**")
            ans_key = f"answer_{zanpakuto['name']}_{level}_{i}"
            ans = st.text_area("Your Answer", key=ans_key)
            if ans.strip():
                fb_key = f"feedback_{zanpakuto['name']}_{level}_{i}"
                if fb_key not in st.session_state:
                    with st.spinner("AI Evaluating..."):
                        feedback = evaluate_answer(q, ans)
                        st.session_state[fb_key] = feedback
                st.markdown(f"🧠 Feedback: _{st.session_state[fb_key]}_")
                if any(word in st.session_state[fb_key].lower() for word in ["correct", "good", "right", "accurate"]):
                    score += 1

        passed = score >= len(questions) // 2 + 1
        if passed != zanpakuto.get(keys["passed"], False):
            zanpakuto[keys["passed"]] = passed
            changed = True
        if passed:
            st.markdown(f'<div class="spiritual-slash">{level.capitalize()} Test Passed!</div>', unsafe_allow_html=True)

    total = min(task_progress + (10 if zanpakuto.get(keys["passed"]) else 0), 100)
    if zanpakuto.get(keys["progress"], 0) != total:
        zanpakuto[keys["progress"]] = total
        changed = True

    progress_bar(level, total)

    if total == 100 and not zanpakuto.get(keys["unlocked"]):
        zanpakuto[keys["unlocked"]] = True
        getsuga_tensho(level)
        st.markdown(f"##### 🗡️ \"_{zanpakuto['release_command']}_\"")
        st.success(f"🎉 {level.capitalize()} Unlocked!")
        changed = True

    if changed:
        save_data(data)

    return total, changed

def reset_zanpakuto_progress(data):
    for z in data:
        for lvl in ["shikai", "bankai", "dangai"]:
            z[f"{lvl}_unlocked"] = False
            z[f"{lvl}_progress"] = 0
            z[f"{lvl}_test_passed"] = False
            for task in z.get(f"{lvl}_tasks", []):
                task["completed"] = False

def render_admin_dashboard(data):
    import re

    st.markdown("## ⚙️ Manage Zanpakutōs")
    st.markdown("---")

    # === Add New Zanpakutō ===
    with st.expander("➕ Add New Zanpakutō"):
        name = st.text_input("Zanpakutō Name")
        kanji = st.text_input("Kanji")
        domain = st.text_input("Skill Domain")
        release = st.text_input("Release Command")
        power = st.text_area("Power Description")

        if st.button("Add Zanpakutō"):
            if name and kanji and domain and release and power:
                if any(z["name"].lower() == name.lower() for z in data):
                    st.warning("Zanpakutō already exists!")
                else:
                    new_z = {
                        "name": name,
                        "kanji": kanji,
                        "domain": domain,
                        "release_command": release,
                        "power": power,
                        "shikai_unlocked": False,
                        "bankai_unlocked": False,
                        "dangai_unlocked": False,
                        "shikai_progress": 0,
                        "bankai_progress": 0,
                        "dangai_progress": 0,
                        "shikai_tasks": [],
                        "bankai_tasks": [],
                        "dangai_tasks": [],
                        "shikai_test_question": [],
                        "bankai_test_question": [],
                        "dangai_test_question": [],
                        "shikai_test_passed": False,
                        "bankai_test_passed": False,
                        "dangai_test_passed": False,
                        "notes": ""
                    }
                    data.append(new_z)
                    save_data(data)
                    st.success(f"✅ {name} added!")
                    st.experimental_rerun()
            else:
                st.warning("Fill in all fields before adding.")

    # === Remove Existing Zanpakutō ===
    with st.expander("🗑️ Remove Existing Zanpakutō"):
        names = [z["name"] for z in data]
        selected_remove = st.selectbox("Select to Remove", names)
        if st.button("Remove Zanpakutō"):
            data[:] = [z for z in data if z["name"] != selected_remove]
            save_data(data)
            st.success(f"🗑️ Removed {selected_remove}")
            st.experimental_rerun()

    st.markdown("---")

    # === Existing Zanpakutō Stats and Controls ===
    for z_idx, z in enumerate(data):
        zan_key = f"{z_idx}_" + re.sub(r'\W+', '_', z["name"])

        st.markdown(f"### 🗡️ {z['name']} ({z['domain']})")
        cols = st.columns(6)
        cols[0].metric("Shikai 🔓", "✅" if z["shikai_unlocked"] else "❌")
        cols[1].progress(z["shikai_progress"] / 100, text=f"{z['shikai_progress']}%")

        cols[2].metric("Bankai 🔓", "✅" if z["bankai_unlocked"] else "❌")
        cols[3].progress(z["bankai_progress"] / 100, text=f"{z['bankai_progress']}%")

        cols[4].metric("Dangai 🔓", "✅" if z["dangai_unlocked"] else "❌")
        cols[5].progress(z["dangai_progress"] / 100, text=f"{z['dangai_progress']}%")

        with st.expander("📜 View Tasks & Status"):
            for level in ["shikai", "bankai", "dangai"]:
                st.subheader(f"{level.capitalize()} Tasks")
                for i, task in enumerate(z[f"{level}_tasks"]):
                    task_key = re.sub(r'\W+', '_', task['task'])[:40]
                    st.checkbox(
                        f"{'🔹🔸🔻'[(['shikai','bankai','dangai'].index(level))]} {task['task']}",
                        value=task["completed"],
                        disabled=True,
                        key=f"{zan_key}_{level}_{i}_{task_key}"
                    )

        with st.expander("🛠️ Admin Controls (Unlock Powers)"):
            c1, c2, c3 = st.columns(3)
            z["shikai_unlocked"] = c1.checkbox("Unlock Shikai", value=z["shikai_unlocked"], key=f"{zan_key}_unlock_shikai")
            z["bankai_unlocked"] = c2.checkbox("Unlock Bankai", value=z["bankai_unlocked"], key=f"{zan_key}_unlock_bankai")
            z["dangai_unlocked"] = c3.checkbox("Unlock Dangai", value=z["dangai_unlocked"], key=f"{zan_key}_unlock_dangai")

        st.markdown("---")

    save_data(data)


# === MAIN LOGIC: Streamlit Page Routing and Handling ===

# Load Zanpakutō data
data = load_data()
zanpakuto_names = [z["name"] for z in data]

# Sidebar Navigation
page = st.sidebar.radio("🔽 Navigation", ["Zanpakutō Details", "Summary Page", "Admin Stats"])

# === Zanpakutō Details Page ===
if page == "Zanpakutō Details":
    selected_name = st.sidebar.selectbox("Select Zanpakutō", zanpakuto_names)
    z = next((z for z in data if z["name"] == selected_name), None)

    if z:
        st.markdown(f"### 🗡️ {z['name']} ({z['kanji']})")
        st.markdown(f"**Domain:** {z['domain']} — _{z['power']}_")
        st.markdown("---")

        total_changed = False

        # === SHIKAI TASKS ===
        prev_shikai = z.get("shikai_unlocked", False)
        _, changed = handle_tasks(z, "shikai", data)
        total_changed |= changed

        if not prev_shikai and z["shikai_unlocked"]:
            unlock_animation(z)

        # === BANKAI TASKS ===
        if z.get("shikai_unlocked"):
            prev_bankai = z.get("bankai_unlocked", False)
            _, changed = handle_tasks(z, "bankai", data)
            total_changed |= changed

            if not prev_bankai and z["bankai_unlocked"]:
                unlock_animation(z)
        else:
            st.info("🔒 Unlock Shikai first to access Bankai tasks.")

        # === DANGAI TASKS ===
        if z.get("bankai_unlocked"):
            prev_dangai = z.get("dangai_unlocked", False)
            _, changed = handle_tasks(z, "dangai", data)
            total_changed |= changed

            if not prev_dangai and z["dangai_unlocked"]:
                unlock_animation(z)
        elif z.get("shikai_unlocked"):
            st.info("🔒 Unlock Bankai first to access Dangai tasks.")

        if total_changed:
            save_data(data)

# === Summary Page ===
elif page == "Summary Page":
    st.title("📊 Zanpakutō Summary")
    selected = st.selectbox("View Summary of", zanpakuto_names)
    z = next((zan for zan in data if zan["name"] == selected), None)

    if z:
        st.markdown(f"### 🗡️ {z['name']} ({z['kanji']}) — *{z['domain']}*")
        st.markdown(f"> {z['power']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            progress_bar("shikai", z.get("shikai_progress", 0))
        with col2:
            progress_bar("bankai", z.get("bankai_progress", 0))
        with col3:
            progress_bar("dangai", z.get("dangai_progress", 0))

# === Admin Page (Login & Stats) ===
elif page == "Admin Stats":
    st.markdown("<h1 style='color:#FFD700;'>🧙‍♂️ Admin Zanpakutō Stats</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # Handle login state
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    # Show login if not authenticated
    if not st.session_state.admin_authenticated:
        st.markdown("<h2 style='color:#FFD700;'>🔐 Admin Login</h2>", unsafe_allow_html=True)
        password_input = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if password_input == ADMIN_PASSWORD:
                st.success("Access granted! Welcome, Captain.")
                st.session_state.admin_authenticated = True
                st.experimental_rerun()
            else:
                st.error("Wrong password. Access denied.")
                st.rerun()
    else:
        # Admin dashboard after login (delegated code handles metrics + controls)
        render_admin_dashboard(data)
