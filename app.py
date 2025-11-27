# app.py

import os
import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic

from prompts import BASE_SYSTEM_PROMPT, build_user_prompt

# Load ANTHROPIC_API_KEY
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

st.set_page_config(page_title="AI Code Reviewer", layout="wide")
st.title("🧠 AI Code Reviewer")
st.write("Paste your code, select what kind of review you want, and click **Run Review**.")

# Make sure key exists
if not api_key:
    st.error("Your ANTHROPIC_API_KEY is missing from your .env file.")
    st.stop()

# Create underlying LLM client (Anthropic / Claude under the hood)
client = Anthropic(api_key=api_key)

# Sidebar — Settings
st.sidebar.header("Review Settings")

# You can later swap this model without changing the UI branding
MODEL_ID = "claude-sonnet-4-5-20250929"

max_tokens = st.sidebar.slider(
    "Max response length (tokens)",
    min_value=256, max_value=4096, value=2000, step=256,
)

# Main UI
code = st.text_area(
    "Your code:",
    height=300,
    placeholder="Paste your Python (or any language) code here...",
)

st.subheader("What should the AI focus on?")

check_bugs = st.checkbox("Find bugs / logical errors", value=True)
check_refactor = st.checkbox("Refactor / readability suggestions", value=True)
check_performance = st.checkbox("Performance improvements")
check_complexity = st.checkbox("Time & space complexity analysis")
check_tests = st.checkbox("Generate example unit tests")

review_types = []
if check_bugs:
    review_types.append("bugs and logical errors")
if check_refactor:
    review_types.append("refactoring and readability")
if check_performance:
    review_types.append("performance improvements")
if check_complexity:
    review_types.append("time and space complexity analysis")
if check_tests:
    review_types.append("example unit tests")

run = st.button("🚀 Run Review")

# LLM call
if run:
    if not code.strip():
        st.error("Please paste some code first.")
    elif not review_types:
        st.error("Please select at least one review option.")
    else:
        with st.spinner("Running your AI code review..."):
            try:
                user_prompt = build_user_prompt(code, review_types)

                response = client.messages.create(
                    model=MODEL_ID,
                    max_tokens=max_tokens,
                    system=BASE_SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_prompt}],
                )

                output = response.content[0].text

                st.subheader("🔍 Review Result")
                st.markdown(output)

            except Exception as e:
                st.error(f"Review engine error: {e}")
