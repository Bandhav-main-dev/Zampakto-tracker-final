import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_tasks(domain, stage):
    prompt = f"Generate 3 tasks to master {domain} at the {stage} level."
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return [t.strip() for t in response.text.strip().split("\n") if t.strip()]

def evaluate_answer(task, answer, domain):
    model = genai.GenerativeModel("gemini-pro")
    eval_prompt = f"""
You are a mentor evaluating a student's task for domain: {domain}.
Task: {task}
Answer: {answer}
Give score (1–10), then reasoning. Output JSON format:
{{
  "score": int,
  "feedback": "..."
}}
"""
    response = model.generate_content(eval_prompt)
    return eval(response.text.strip())
