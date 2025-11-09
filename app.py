# app.py
import streamlit as st
import json
from review_engine import review_code

st.set_page_config(page_title="AI Code Reviewer", page_icon="🤖", layout="wide")

st.title("🤖 AI Code Reviewer")
st.write("Upload your code file or paste code below to get AI-powered review insights.")

# Sidebar
st.sidebar.header("Configuration")
language = st.sidebar.selectbox("Select Language", ["python", "javascript", "java", "c++", "c#", "html", "go"])
filename = st.sidebar.text_input("Filename", value="main.py")

# Upload or paste code
uploaded_file = st.file_uploader("📤 Upload your code file", type=["py", "js", "java", "cpp", "cs", "html", "go"])
code_input = ""

if uploaded_file is not None:
    code_input = uploaded_file.read().decode("utf-8")
else:
    code_input = st.text_area("Or paste your code here:", height=250)

# Review Button
if st.button("🔍 Review Code"):
    if not code_input.strip():
        st.warning("Please upload or paste some code first.")
    else:
        with st.spinner("Reviewing your code with AI... ⏳"):
            result = review_code(code_input, filename=filename, language=language)
            st.success("✅ Review Complete!")

            # Handle structured vs raw output
            if "error" in result and result["error"] != "Invalid JSON format after cleaning. Model returned non-JSON text.":
                st.error(result["error"])
            elif "raw_response" in result:
                st.write("### 📝 Raw Response")
                st.code(result["raw_response"], language="json")
            else:
                # Display the structured review in nice sections
                st.subheader("📋 Summary")
                st.write(result.get("summary", "N/A"))

                st.subheader("🐞 Issues")
                st.json(result.get("issues", []))

                st.subheader("⚙️ Improvements")
                st.json(result.get("improvements", []))

                st.subheader("🚀 Performance Suggestions")
                st.json(result.get("performance", []))

                st.subheader("🔒 Security Concerns")
                st.json(result.get("security", []))

                st.subheader("🧩 Refactored Code")
                refactor = result.get("refactor", {})
                if isinstance(refactor, dict) and "code" in refactor:
                    st.code(refactor["code"], language=language)
                else:
                    st.write(refactor)
