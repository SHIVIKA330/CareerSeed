import re
import fitz  # PyMuPDF
import pandas as pd
import streamlit as st
from openai import OpenAI
import os

# Initialize Client for AI Enhancement
def run_ai_enhancer(resume_text, client):
    """Uses AIML API (OpenAI compatible) to enhance resume text for ATS."""
    prompt = f"Enhance the following resume text for ATS optimization. Provide clear sections, improve action verbs, and ensure impact-driven bullet points. Maintain the original information but make it professional.\n\nRESUME TEXT:\n{resume_text}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert career coach and ATS optimization specialist."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Enhancement Error: {str(e)}"

def extract_text_from_pdf(pdf_file):
    """Extracts text from uploaded PDF file."""
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"Extraction Error: {str(e)}"

def extract_skills(resume_text, client):
    """Uses AI to extract key skills from the resume."""
    prompt = f"Extract a comma-separated list of the top 5-8 technical skills from this resume. Provide ONLY the skills, no other text.\n\nRESUME:\n{resume_text}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        skills = response.choices[0].message.content.strip().split(',')
        return [s.strip() for s in skills]
    except:
        return ["Python", "JavaScript", "Data Analysis", "SQL", "Machine Learning"] # Fallback

def get_relevant_courses(skills_found, client):
    """Recommends relative courses using AI instead of CSV."""
    skills_str = ", ".join(skills_found)
    prompt = f"Based on these skills: {skills_str}, recommend 5 real and popular online courses (from platforms like Coursera, Udemy, etc.). Provide ONLY a JSON list of course titles with the key 'courses'.\nExample: {{\"courses\": [\"Course 1\", \"Course 2\"]}}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        import json
        data = json.loads(response.choices[0].message.content)
        return data.get("courses", [])
    except:
        return [f"Advanced {skills_found[0]} Certification", f"{skills_found[1]} for Professionals"]

def get_relevant_jobs(skills_found, client):
    """Recommends relevant jobs using AI instead of CSV."""
    skills_str = ", ".join(skills_found)
    prompt = f"Based on these skills: {skills_str}, recommend 5 relevant job roles or specific companies that hire for these skills. Provide ONLY a JSON list of job titles with the key 'jobs'.\nExample: {{\"jobs\": [\"Job 1\", \"Job 2\"]}}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        import json
        data = json.loads(response.choices[0].message.content)
        return data.get("jobs", [])
    except:
        return [f"Senior {skills_found[0]} Developer", f"{skills_found[1]} Systems Architect"]

def calculate_ats_score(resume_text):
    """A simple heuristic for ATS score for demonstration."""
    score = 0
    keywords = ["experience", "education", "skills", "projects", "certifications", "python", "java", "sql"]
    for word in keywords:
        if word in resume_text.lower():
            score += 10
    return min(score + 20, 100) # Base score + matches

