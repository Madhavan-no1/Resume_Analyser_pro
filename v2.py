import streamlit as st
import google.generativeai as genai
from pathlib import Path
import io
from docx import Document
import PyPDF2
from PIL import Image
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import random

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Gemini model
def initialize_model():
    return genai.GenerativeModel('gemini-pro')

def initialize_vision_model():
    return genai.GenerativeModel('gemini-pro-vision')

# Function to analyze resume
def analyze_resume(file):
    text = ""
    if file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    
    prompt = f"""
    Analyze the following resume and provide:
    1. Skills identified
    2. Areas for improvement
    3. Career path suggestions
    4. Resume formatting feedback
    
    Resume text:
    {text}
    """
    
    model = initialize_model()
    response = model.generate_content(prompt)
    return response.text

# Function to get skill recommendations and learning resources
def get_skill_recommendations(skill):
    model = initialize_model()
    prompt = f"""
    For the skill '{skill}', provide:
    1. Best online learning platforms (with direct links)
    2. Free resources (with direct links)
    3. Paid courses (with direct links)
    4. Estimated time to learn
    5. Career opportunities
    Format the response in markdown with clear headings and bullet points.
    """
    response = model.generate_content(prompt)
    return response.text

# Function to search jobs
def search_jobs(query, location):
    linkedin_url = f"https://www.linkedin.com/jobs/search?keywords={query}&location={location}"
    naukri_url = f"https://www.naukri.com/jobs-in-{location}?keyword={query}"
    return linkedin_url, naukri_url

# Function to get career psychology insights
def get_career_psychology_insights():
    model = initialize_model()
    prompt = """
    Provide insights on career psychology for students and job seekers. Include:
    1. Understanding personal strengths and weaknesses
    2. Dealing with career uncertainty
    3. Building resilience in job search
    4. Overcoming imposter syndrome
    5. Work-life balance expectations
    Format the response in markdown with clear headings and bullet points.
    """
    response = model.generate_content(prompt)
    return response.text

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: white;
    }
    .user-message {
        background-color: rgba(25, 25, 112, 0.7);
    }
    .bot-message {
        background-color: rgba(178, 34, 34, 0.7);
    }
    .sidebar .sidebar-content {
        background-color: rgba(255, 255, 255, 0.1);
    }
    .stButton>button {
        background-color: #fdbb2d;
        color: #1a2a6c;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.2);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Main app
def main():
    st.title("🚀 Career Development Assistant")
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Chat"

    # Navigation
    tabs = ["Chat", "Resume Analysis", "Skill Development", "Job Search", "Career Psychology"]
    st.session_state.current_tab = st.tabs(tabs)

    # Chat Tab
    with st.session_state.current_tab[0]:
        st.subheader("💬 Career Chat Assistant")
        
        user_input = st.text_input("Ask anything about careers, skills, or job roles:")
        
        if st.button("Send"):
            if user_input:
                model = initialize_model()
                prompt = f"""
                You are a career development assistant. Provide helpful advice about:
                - Career paths
                - Job roles and responsibilities
                - Required skills
                - Industry trends
                - Professional development
                
                Question: {user_input}
                """
                response = model.generate_content(prompt)
                st.session_state.chat_history.append(("user", user_input))
                st.session_state.chat_history.append(("bot", response.text))
        
        # Display chat history
        for role, text in st.session_state.chat_history:
            div_class = "user-message" if role == "user" else "bot-message"
            st.markdown(f'<div class="chat-message {div_class}">{text}</div>', unsafe_allow_html=True)

    # Resume Analysis Tab
    with st.session_state.current_tab[1]:
        st.subheader("📄 Resume Analyzer")
        
        uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
        
        if uploaded_file and st.button("Analyze Resume"):
            with st.spinner("Analyzing your resume..."):
                analysis = analyze_resume(uploaded_file)
                st.markdown(analysis)

    # Skill Development Tab
    with st.session_state.current_tab[2]:
        st.subheader("🎯 Skill Development Resources")
        
        skill = st.text_input("Enter a skill you want to learn:")
        if skill and st.button("Get Resources"):
            with st.spinner("Finding learning resources..."):
                recommendations = get_skill_recommendations(skill)
                st.markdown(recommendations)

    # Job Search Tab
    with st.session_state.current_tab[3]:
        st.subheader("🔍 Job Search")
        
        job_title = st.text_input("Enter job title or keywords:")
        location = st.text_input("Location:")
        
        if st.button("Search Jobs"):
            linkedin_url, naukri_url = search_jobs(job_title, location)
            st.markdown(f"[View Jobs on LinkedIn]({linkedin_url})")
            st.markdown(f"[View Jobs on Naukri]({naukri_url})")
            
            # Additional job search tips
            model = initialize_model()
            prompt = f"""
            Provide job search tips and interview preparation advice for the role of {job_title}.
            Include:
            1. Key skills required
            2. Common interview questions
            3. Salary range
            4. Industry trends
            Format the response in markdown with clear headings and bullet points.
            """
            tips = model.generate_content(prompt)
            st.markdown(tips.text)

    # Career Psychology Tab
    with st.session_state.current_tab[4]:
        st.subheader("🧠 Career Psychology Insights")
        
        if st.button("Get Career Psychology Insights"):
            with st.spinner("Generating insights..."):
                insights = get_career_psychology_insights()
                st.markdown(insights)
# Load CSS
def load_css(css_path):
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Call the function to load the CSS
load_css("styles.css")  # If the file is in the same directory
# Or use: load_css("assets/styles.css") if stored in an "assets" folder

if __name__ == "__main__":
    main()