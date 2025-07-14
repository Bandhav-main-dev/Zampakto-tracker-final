import streamlit as st
import json
import os
import google.generativeai as genai

# === CONFIG ===
DATA_FILE = os.path.join(os.path.dirname(__file__), "zanpakuto_data.json")
GOOGLE_API_KEY = "AIzaSyBaBnQt9uGLo-C0lw-I2WvZ5mbLWxKVK_8"

# === SETUP ===
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# === LOAD / SAVE ===
def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === GENERATE PRACTICE QUESTIONS ===
def generate_practice_questions(zanpakuto_name, domain, num=3):
    prompt = f"""
    I am building a Bleach-themed skill tracker. Each Zanpakutō represents a skill domain.

    Zanpakutō: {zanpakuto_name}
    Domain: {domain}

    Generate {num} practice questions that help a learner improve in this domain.
    Only return a numbered list of questions.
    """
    try:
        response = model.generate_content(prompt)
        questions = response.text.strip().split("\n")
        cleaned = [q.lstrip("1234567890. ").strip("-• ") for q in questions if q.strip()]
        return cleaned
    except Exception as e:
        st.error(f"❌ Gemini API Error: {e}")
        return []

# === EVALUATE ANSWERS ===
def evaluate_answer(question, answer):
    prompt = f"""
    Question: {question}
    Answer: {answer}

    Evaluate the answer in 1-2 lines. Say if it's correct, partially correct, or incorrect. Give a hint or suggestion if needed.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error evaluating answer: {e}"

# === UI CONFIG ===
st.set_page_config(page_title="🗡️ Zanpakutō Tracker", layout="wide")
st.markdown("""
    <style>
    body {
        background-color: #0f0f0f;
        color: #f1f1f1;
    }
    meter {
        width: 100%;
        height: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# === LOAD DATA ===
data = load_data()
zanpakuto_names = [z["name"] for z in data]

# === SIDEBAR ===
st.sidebar.title("📜 Zanpakutō Navigation")
page = st.sidebar.radio("Select View", ["Zanpakutō Details", "Summary Page"])

# === DETAIL PAGE ===
if page == "Zanpakutō Details":
    selected_name = st.sidebar.radio("Select Zanpakutō", zanpakuto_names)
    selected_zanpakuto = next((z for z in data if z["name"] == selected_name), None)

    if selected_zanpakuto:
        st.markdown(f"""
            <h1 style='text-align: center; color: #ff4b4b;'>🗡️ {selected_zanpakuto['name']} ({selected_zanpakuto['kanji']})</h1>
            <h4 style='text-align: center; color: #facc15;'>Domain: {selected_zanpakuto['domain']}</h4>
            <hr style='border: 1px solid #444;' />
        """, unsafe_allow_html=True)

        st.markdown(f"<p style='text-align:center; font-size:18px;'>{selected_zanpakuto['power']}</p>", unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("### 🔥 Progress")
        st.markdown(f"**Shikai (🟡):** {selected_zanpakuto['shikai_progress']}%")
        st.markdown(f"""
            <meter value="{selected_zanpakuto['shikai_progress']}" min="0" max="100">{selected_zanpakuto['shikai_progress']}%</meter>
        """, unsafe_allow_html=True)

        st.markdown(f"**Bankai (🔴):** {selected_zanpakuto['bankai_progress']}%")
        st.markdown(f"""
            <meter value="{selected_zanpakuto['bankai_progress']}" min="0" max="100">{selected_zanpakuto['bankai_progress']}%</meter>
        """, unsafe_allow_html=True)

        st.markdown(f"**Dangai (⚪):** {selected_zanpakuto['dangai_progress']}%")
        st.markdown(f"""
            <meter value="{selected_zanpakuto['dangai_progress']}" min="0" max="100">{selected_zanpakuto['dangai_progress']}%</meter>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Shikai (Always visible)
        st.markdown("## 📋 Shikai Tasks")
        for i, task in enumerate(selected_zanpakuto["shikai_tasks"]):
            if st.checkbox(f"{i+1}. {task}", key=f"shikai_{i}_{selected_zanpakuto['name']}"):
                selected_zanpakuto["shikai_tasks"].pop(i)
                selected_zanpakuto["shikai_progress"] = min(100, selected_zanpakuto["shikai_progress"] + 20)
                save_data(data)
                st.experimental_rerun()

        if selected_zanpakuto["practise_test_question"]:
            st.markdown("## 🧪 Shikai Practice Questions")
            for i, q in enumerate(selected_zanpakuto["practise_test_question"], 1):
                st.markdown(f"**{i}. {q}**")
                user_answer = st.text_area(f"Your Answer {i}", key=f"answer_{i}")
                if user_answer:
                    feedback = evaluate_answer(q, user_answer)
                    st.markdown(f"🧠 Feedback: _{feedback}_")

        # Bankai
        if selected_zanpakuto.get("shikai_unlocked"):
            if selected_zanpakuto.get("bankai_unlocked"):
                st.markdown("## 📋 Bankai Tasks")
                for i, task in enumerate(selected_zanpakuto["bankai_tasks"]):
                    if st.checkbox(f"{i+1}. {task}", key=f"bankai_{i}_{selected_zanpakuto['name']}"):
                        selected_zanpakuto["bankai_tasks"].pop(i)
                        selected_zanpakuto["bankai_progress"] = min(100, selected_zanpakuto["bankai_progress"] + 20)
                        save_data(data)
                        st.experimental_rerun()

                if selected_zanpakuto["bankai_test_question"]:
                    st.markdown("## 🧪 Bankai Practice Questions")
                    for i, q in enumerate(selected_zanpakuto["bankai_test_question"], 1):
                        st.markdown(f"**{i}. {q}**")
                        user_answer = st.text_area(f"Your Answer (Bankai) {i}", key=f"answer_bankai_{i}")
                        if user_answer:
                            feedback = evaluate_answer(q, user_answer)
                            st.markdown(f"🧠 Feedback: _{feedback}_")

        # Dangai
        if selected_zanpakuto.get("shikai_unlocked") and selected_zanpakuto.get("bankai_unlocked"):
            if selected_zanpakuto.get("dangai_unlocked"):
                st.markdown("## 📋 Dangai Tasks")
                for i, task in enumerate(selected_zanpakuto["dangai_tasks"]):
                    if st.checkbox(f"{i+1}. {task}", key=f"dangai_{i}_{selected_zanpakuto['name']}"):
                        selected_zanpakuto["dangai_tasks"].pop(i)
                        selected_zanpakuto["dangai_progress"] = min(100, selected_zanpakuto["dangai_progress"] + 20)
                        save_data(data)
                        st.experimental_rerun()

                if selected_zanpakuto["dangai_test_question"]:
                    st.markdown("## 🧪 Dangai Practice Questions")
                    for i, q in enumerate(selected_zanpakuto["dangai_test_question"], 1):
                        st.markdown(f"**{i}. {q}**")
                        user_answer = st.text_area(f"Your Answer (Dangai) {i}", key=f"answer_dangai_{i}")
                        if user_answer:
                            feedback = evaluate_answer(q, user_answer)
                            st.markdown(f"🧠 Feedback: _{feedback}_")

        st.markdown("---")
        st.markdown("## ✨ Generate Practice Questions")
        if st.button("⚔️ Invoke Gemini"):
            new_questions = generate_practice_questions(
                selected_zanpakuto["name"],
                selected_zanpakuto["domain"],
                num=3
            )
            if new_questions:
                selected_zanpakuto["practise_test_question"] = new_questions
                save_data(data)
                st.balloons()
                st.success("✅ Practice questions generated and saved!")

    else:
        st.error("Zanpakutō not found.")

# === SUMMARY PAGE ===
elif page == "Summary Page":
    st.title("📊 Zanpakutō Summary Overview")
    st.markdown("This page shows progress for all Zanpakutōs in one view.")

    for z in data:
        st.markdown(f"### 🗡️ {z['name']} ({z['kanji']})")
        st.markdown(f"**Domain:** `{z['domain']}`")
        st.markdown(f"**Power:** {z['power']}")

        st.markdown(f"**Shikai (🟡):** {z['shikai_progress']}%")
        st.markdown(f"<meter value='{z['shikai_progress']}' min='0' max='100'>{z['shikai_progress']}%</meter>", unsafe_allow_html=True)

        st.markdown(f"**Bankai (🔴):** {z['bankai_progress']}%")
        st.markdown(f"<meter value='{z['bankai_progress']}' min='0' max='100'>{z['bankai_progress']}%</meter>", unsafe_allow_html=True)

        st.markdown(f"**Dangai (⚪):** {z['dangai_progress']}%")
        st.markdown(f"<meter value='{z['dangai_progress']}' min='0' max='100'>{z['dangai_progress']}%</meter>", unsafe_allow_html=True)

        if z.get("practise_test_question"):
            st.markdown("**Sample Practice Questions:**")
            for i, q in enumerate(z["practise_test_question"], 1):
                st.markdown(f"- {q}")

        st.markdown("---")