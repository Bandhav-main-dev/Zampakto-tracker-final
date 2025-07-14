import os
import google.generativeai as genai

# Set your API key (or use os.environ)
genai.configure(api_key="AIzaSyBaBnQt9uGLo-C0lw-I2WvZ5mbLWxKVK_8")

model = genai.GenerativeModel("gemini-pro")

def evaluate_answer(task, answer):
    prompt = f"You are an expert teacher. Evaluate this answer to the task: '{task}'\n\nAnswer: {answer}\n\nIs it acceptable? Reply 'Yes' or 'No' with a short reason."
    response = model.generate_content(prompt)
    return response.text



# Load the Gemini model

def generate_practice_questions(zanpakuto_name, domain, num_questions=3):
    prompt = f"""
    I am creating a Bleach-themed learning tracker. Each Zanpakutō represents a skill domain.

    Zanpakutō Name: {zanpakuto_name}
    Domain: {domain}

    Generate {num_questions} domain-specific **practice questions** to help the user master the skills. These questions should be conceptual, technical, or applied. Format them as a plain list.
    """
    response = model.generate_content(prompt)
    questions = response.text.strip().split("\n")

    # Clean list: remove empty lines, prefixes like '1. ', etc.
    return [q.lstrip("1234567890. ").strip("-• ") for q in questions if q.strip()]
