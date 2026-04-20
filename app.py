import streamlit as st
import pandas as pd
from openai import OpenAI
import os
from resume_enhancer import (
    extract_text_from_pdf,
    run_ai_enhancer,
    extract_skills,
    get_relevant_courses,
    get_relevant_jobs,
    calculate_ats_score
)

# Page configuration
st.set_page_config(
    page_title="CareerSeeds | AI Career Assistant",
    page_icon="🌱",
    layout="wide"
)

# Custom Premium CSS (Glassmorphism & Gradients)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f1f5f9;
    }
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        border: none;
        color: white;
        font-weight: 600;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        color: white;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration - Using Environment Variables for Render Compatibility
# On Render, set AIML_API_KEY in Environment Variables
api_key = os.getenv("AIML_API_KEY", "1a63d6d97953468ebfb42bf530d0a4ab") 

client = OpenAI(
    base_url="https://api.aimlapi.com/v1",
    api_key=api_key,
)

# Sidebar Navigation
with st.sidebar:
    st.markdown("<h2 style='color:#38bdf8;'>🌱 CareerSeeds</h2>", unsafe_allow_html=True)
    st.markdown("---")
    choice = st.radio("Navigation", ["🤖 AI Career Chatbot", "📄 Resume Enhancer & ATS"])
    st.markdown("---")
    st.info("CareerSeeds uses AI to help you bloom in your career.")

# --- NAVIGATION LOGIC ---

if choice == "🤖 AI Career Chatbot":
    st.markdown("<h1 class='main-header'>AI Career Assistant</h1>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display Chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything about career paths, skills, or interviews..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consulting career database..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are a professional career counselor at CareerSeeds. You provide encouraging, data-driven, and actionable career advice."}
                        ] + st.session_state.messages
                    )
                    full_response = response.choices[0].message.content
                    st.markdown(full_response)
                except Exception as e:
                    full_response = "Sorry, I'm having trouble connecting right now. Please check your API key."
                    st.error(full_response)
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})

elif choice == "📄 Resume Enhancer & ATS":
    st.markdown("<h1 class='main-header'>Resume Enhancer</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload your Resume (PDF)", type="pdf")
        st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file:
        with st.status("🚀 Processing Resume...", expanded=True) as status:
            st.write("Extracting text...")
            resume_text = extract_text_from_pdf(uploaded_file)
            
            st.write("Analyzing ATS Compatibility...")
            score = calculate_ats_score(resume_text)
            
            st.write("Generating AI Improvements...")
            enhanced_text = run_ai_enhancer(resume_text, client)
            
            st.write("Extracting key skills for recommendations...")
            skills_found = extract_skills(resume_text, client)
            
            status.update(label="Analysis Complete!", state="complete", expanded=False)

        # Dashboard View
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
            st.metric("ATS Compatibility Score", f"{score}%")
            st.progress(score/100)
            st.markdown("</div>", unsafe_allow_html=True)

            # AI Recommendations
            st.subheader("💡 Recommended Courses")
            courses = get_relevant_courses(skills_found, client)
            if courses:
                for course in courses:
                    st.write(f"- {course}")
            else:
                st.write("No specific courses found for your profile.")
            
            st.subheader("💼 Matched Job Openings")
            jobs = get_relevant_jobs(skills_found, client)
            if jobs:
                for job in jobs:
                    st.write(f"- {job}")
            else:
                st.write("No specific job roles found for your profile.")
        
        with col2:
            st.subheader("✨ AI Enhanced Version")
            st.markdown(enhanced_text)
            
            st.download_button(
                label="Download Enhanced Text",
                data=enhanced_text,
                file_name="enhanced_resume.md",
                mime="text/markdown"
            )
