import streamlit as st
import os
import sys

# Add app folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import processing and LLM functions
from app.ingestion import process_pdf
from app.llm_agent import process_query
from app.arxiv_lookup import search_arxiv
# Streamlit config
st.set_page_config(page_title="Enterprise Doc AI Agent", layout="wide")
st.title("📄 Enterprise Document Q&A AI Agent")

# Initialize session state for uploaded files
if "pdf_files" not in st.session_state:
    st.session_state.pdf_files = []

# --- Upload PDFs ---
st.sidebar.header("📤 Upload PDF Documents")
uploaded_files = st.sidebar.file_uploader(
    "Upload one or more PDF files", 
    type=["pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        file_path = f"./data/sample_papers/{file.name}"

        # ✅ Only process if not already processed
        if file_path not in st.session_state.pdf_files:
            with st.spinner(f"Processing {file.name}..."):
                with open(file_path, "wb") as f:
                    f.write(file.read())
                process_pdf(file_path)
                st.session_state.pdf_files.append(file_path)
                st.sidebar.success(f"{file.name} processed ✅")


#---lookup__-                
st.sidebar.header("🔍 Arxiv Paper Lookup")
search_query = st.sidebar.text_input("Describe a paper (e.g., 'diffusion model for image generation')")

if st.sidebar.button("Search Arxiv"):
    with st.spinner("🔍 Searching Arxiv..."):
        result = search_arxiv(search_query)

        if result and "error" not in result:
            st.sidebar.success("✅ Paper Found!")

            # Display in Main Area
            st.markdown(f"### 📄 {result['title']}")
            st.markdown(f"**👤 Authors:** {result['authors']}")
            st.markdown(f"**📅 Published:** {result['published']}")
            st.markdown("**📝 Abstract:**")
            st.markdown(result['summary'])
            st.markdown(f"📄 [View Full Paper]({result['arxiv_url']}) &nbsp;|&nbsp; 🔗 [Download PDF]({result['pdf_url']})")

            # Short Sidebar View
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 📄 Top Result")
            st.sidebar.markdown(f"**Title:** {result['title']}")
            st.sidebar.markdown(f"[📄 PDF Link]({result['pdf_url']})")

        elif result and "error" in result:
            st.sidebar.error(f"❌ Error: {result['error']}")
        else:
            st.sidebar.warning("⚠️ No results found.")

# --- Query Section ---
st.header("💬 Ask a Question About Your Uploaded Papers")

query_text = st.text_area("Enter your question")

# --- Submit Query ---
if st.button("Submit Query"):
    if not query_text:
        st.warning("⚠️ Please enter a question.")
    elif not st.session_state.pdf_files:
        st.warning("⚠️ Please upload at least one PDF.")
    else:
        with st.spinner("🤖 Thinking..."):
            result = process_query(query_text)
            st.success("✅ Response")
            st.markdown(result)
            st.write(result)
