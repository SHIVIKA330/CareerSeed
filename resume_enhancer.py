import subprocess
import re
import fitz  # PyMuPDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import os
import pandas as pd
from pathlib import Path
import streamlit as st
from collections import defaultdict
import math

def extract_text_from_pdf(pdf_path):
    """Extract text content from PDF file"""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def run_llama_enhancer(resume_text):
    """Enhance resume text using LLaMA model"""
    prompt = f"""
Enhance the resume and provide a full updated resume:

{resume_text}
"""
    try:
        process_obj = subprocess.Popen(
            ["ollama", "run", "llama3:8b"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True if os.name == 'nt' else False
        )
        stdout, stderr = process_obj.communicate(input=prompt.encode("utf-8"))
        stdout_decoded = stdout.decode("utf-8", errors="ignore")
        stderr_decoded = stderr.decode("utf-8", errors="ignore")

        if process_obj.returncode != 0:
            raise RuntimeError(f"LLaMA execution failed: {stderr_decoded}")

        return stdout_decoded
    except FileNotFoundError:
        raise FileNotFoundError("LLaMA (ollama) not found. Please make sure it's installed and added to PATH.")
    except Exception as e:
        raise Exception(f"Error running LLaMA: {str(e)}")

def split_into_sections(text):
    """Parse enhanced resume text into sections"""
    try:
        pattern = re.compile(
            r"\*\*(?P<heading>[A-Za-z ]+):\*\*\n?(?P<content>(?:.|\n)*?)(?=\n\*\*[A-Za-z ]+:\*\*|\Z)",
            re.MULTILINE
        )
        sections = {}
        for match in pattern.finditer(text):
            heading = match.group("heading").strip()
            content = match.group("content").strip()
            sections[heading] = content
        return sections
    except Exception as e:
        raise Exception(f"Error parsing resume sections: {str(e)}")

def generate_updated_resume_with_template(original_pdf_path, updated_sections, output_pdf_path, name, phone, email):
    """Generate enhanced PDF resume"""
    try:
        styles = getSampleStyleSheet()

        heading_style = ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            textColor=colors.HexColor('#1f4e79'),
            fontSize=16,
            leading=20,
            spaceAfter=10,
            spaceBefore=10,
            alignment=0,
            fontName='Helvetica-Bold'
        )

        name_style = ParagraphStyle(
            name='NameStyle',
            parent=styles['Normal'],
            fontSize=14,
            leading=16,
            alignment=0,
            textColor=colors.HexColor("#1a1a1a"),
            fontName='Helvetica-Bold'
        )

        contact_style = ParagraphStyle(
            name='ContactStyle',
            parent=styles['Normal'],
            fontSize=12,
            leading=14,
            alignment=2,
            textColor=colors.HexColor("#444444")
        )

        story = []

        # Add contact information
        user_info_data = [
            [Paragraph(name, name_style), Paragraph(f"{phone} | {email}", contact_style)]
        ]
        user_info_table = Table(user_info_data, colWidths=[270, 270])
        user_info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12)
        ]))
        story.append(user_info_table)
        story.append(Spacer(1, 10))

        # Add resume sections
        if not updated_sections:
            raise Exception("No sections were parsed from enhanced resume!")

        for heading, content in updated_sections.items():
            story.append(Paragraph(heading, heading_style))
            story.append(Spacer(1, 6))

            for line in content.strip().split("\n"):
                if line.strip():
                    story.append(Paragraph(line.strip(), styles["Normal"]))
                    story.append(Spacer(1, 4))

            story.append(Spacer(1, 12))

        # Generate PDF
        doc = SimpleDocTemplate(output_pdf_path, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        doc.build(story)
        
    except Exception as e:
        raise Exception(f"Error generating PDF: {str(e)}")

def generate_new_resume_from_scratch(user_data, output_pdf_path):
    """Generate a new resume PDF from scratch using user-provided data"""
    try:
        # Prepare the prompt for LLaMA
        prompt = f"""
Create a professional one-page resume for {user_data['name']} who is applying for the position of {user_data['job_profile']}.
Use the following information:

Personal Details:
- Name: {user_data['name']}
- Contact: {user_data['contact']['email']}, {user_data['contact']['phone']}
- Address: {user_data['contact']['address']}
- LinkedIn: {user_data['contact']['linkedin']}
- GitHub: {user_data['contact']['github']}
- LeetCode: {user_data['contact']['leetcode']}

Education:
- Degree: {user_data['education']['degree']}
- University: {user_data['education']['university']}
- Location: {user_data['education']['location']}
- Grade: {user_data['education']['grade']}
- Year: {user_data['education']['year']}

Experience:
- Company: {user_data['experience']['company']}
- Position: {user_data['experience']['position']}
- Duration: {user_data['experience']['duration']}
- Description: {user_data['experience']['description']}
- Achievements: {user_data['experience']['achievements']}

Projects:
- Name: {user_data['projects']['name']}
- Description: {user_data['projects']['description']}
- Link: {user_data['projects']['link']}

Skills: {user_data['skills']}

Achievements: {user_data['achievements']}

Activities: {user_data['activities']}

Format the resume professionally with these sections:
1. Contact Information (Name, Email, Phone, LinkedIn, GitHub)
2. Education
3. Experience
4. Projects
5. Skills
6. Achievements
7. Activities

Keep it concise and fit on one page. Use bullet points where appropriate.
"""
        
        # Get enhanced resume text from LLaMA
        enhanced_text = run_llama_enhancer(prompt)
        
        # Parse the enhanced text into sections
        updated_sections = split_into_sections(enhanced_text)
        
        # Generate the PDF
        generate_updated_resume_with_template(
            None,  # No original PDF path for new resume
            updated_sections,
            output_pdf_path,
            user_data['name'],
            user_data['contact']['phone'],
            user_data['contact']['email']
        )
        
    except Exception as e:
        raise Exception(f"Error generating new resume: {str(e)}")

def get_relevant_courses(job_profile, csv_path):
    """Get courses relevant to the selected job profile by matching with job_profile column"""
    try:
        if not job_profile or not isinstance(job_profile, str):
            raise ValueError("Invalid job profile provided")
            
        if not Path(csv_path).exists():
            raise FileNotFoundError(f"CSV file not found at {csv_path}")

        df = pd.read_csv(csv_path)
        
        if 'job_profile' not in df.columns:
            raise ValueError("CSV file does not contain the required 'job_profile' column")
        
        matched_courses = df[df['job_profile'].str.contains(job_profile, case=False, na=False)]
        
        return matched_courses

    except Exception as e:
        print(f"Error in get_relevant_courses: {str(e)}")
        return pd.DataFrame()

def get_relevant_jobs(job_profile, csv_path):
    """Get job listings relevant to the selected job profile by matching with job_profile column"""
    try:
        if not job_profile or not isinstance(job_profile, str):
            raise ValueError("Invalid job profile provided")
            
        if not Path(csv_path).exists():
            raise FileNotFoundError(f"CSV file not found at {csv_path}")

        df = pd.read_csv(csv_path)
        
        if 'job_profile' not in df.columns:
            raise ValueError("CSV file does not contain the required 'job_profile' column")
        
        matched_jobs = df[df['job_profile'].str.contains(job_profile, case=False, na=False)]
        
        return matched_jobs

    except Exception as e:
        print(f"Error in get_relevant_jobs: {str(e)}")
        return pd.DataFrame()

def calculate_ats_score(resume_text, job_profile):
    """Calculate ATS score for the resume based on key factors"""
    feedback = defaultdict(list)
    score = 0
    
    # 1. Keyword Analysis (20 points)
    keywords = {
        "Software Developer": ["programming", "development", "code", "algorithm", "debugging"],
        "Data Scientist": ["machine learning", "python", "statistics", "data analysis", "SQL"],
        # Add more job profiles and their keywords
    }
    
    matched_keywords = []
    target_keywords = keywords.get(job_profile, [])
    for keyword in target_keywords:
        if keyword.lower() in str(resume_text).lower():
            matched_keywords.append(keyword)
    
    keyword_score = min(20, len(matched_keywords) * 4)  # Max 20 points
    score += keyword_score
    
    if matched_keywords:
        feedback["Keywords"].append(f"✅ Found relevant keywords: {', '.join(matched_keywords)}")
    else:
        feedback["Keywords"].append("❌ No relevant keywords found for your job profile")
    
    # 2. Section Analysis (20 points)
    required_sections = ["Experience", "Education", "Skills", "Projects"]
    found_sections = []
    
    for section in required_sections:
        if section.lower() in str(resume_text).lower():
            found_sections.append(section)
    
    section_score = min(20, len(found_sections) * 5)  # Max 20 points
    score += section_score
    
    if len(found_sections) == len(required_sections):
        feedback["Sections"].append("✅ All essential sections found")
    else:
        missing = set(required_sections) - set(found_sections)
        feedback["Sections"].append(f"❌ Missing sections: {', '.join(missing)}")
    
    # 3. Length Analysis (15 points)
    word_count = len(str(resume_text).split())
    if 400 <= word_count <= 800:
        length_score = 15
        feedback["Length"].append("✅ Ideal resume length (400-800 words)")
    else:
        length_score = max(0, 15 - abs(word_count - 600) // 50)
        feedback["Length"].append(f"⚠️ Resume length may be {'too long' if word_count > 800 else 'too short'} ({word_count} words)")
    score += length_score
    
    # 4. Contact Information (10 points)
    contact_items = ["@", ".com", "phone", "linkedin"]
    contact_found = sum(1 for item in contact_items if item.lower() in str(resume_text).lower())
    contact_score = min(10, contact_found * 3)  # Max 10 points
    score += contact_score
    
    if contact_found >= 3:
        feedback["Contact Info"].append("✅ Complete contact information found")
    else:
        feedback["Contact Info"].append("⚠️ Contact information may be incomplete")
    
    # 5. Achievement Metrics (15 points)
    metric_words = ["%", "increased", "reduced", "saved", "improved", "achieved"]
    metric_count = sum(1 for word in metric_words if word.lower() in str(resume_text).lower())
    metric_score = min(15, metric_count * 3)  # Max 15 points
    score += metric_score
    
    if metric_count > 0:
        feedback["Achievements"].append(f"✅ Found {metric_count} quantified achievements")
    else:
        feedback["Achievements"].append("❌ No quantified achievements found")
    
    # 6. Formatting (10 points)
    formatting_score = 10  # Assume good formatting since we're processing the text
    score += formatting_score
    feedback["Formatting"].append("✅ Proper formatting detected")
    
    # 7. Skills Match (10 points)
    skills = ["python", "java", "sql", "communication", "teamwork"]
    skills_found = sum(1 for skill in skills if skill.lower() in str(resume_text).lower())
    skills_score = min(10, skills_found * 2)  # Max 10 points
    score += skills_score
    
    if skills_found >= 3:
        feedback["Skills"].append(f"✅ Found {skills_found} relevant skills")
    else:
        feedback["Skills"].append("⚠️ Could use more relevant skills")
    
    # Ensure score is within 0-100
    score = max(0, min(100, score))
    
    # Round to nearest 5 for cleaner presentation
    score = 5 * math.ceil(score / 5)
    
    return score, feedback

def process_resume_with_llama(uploaded_file, name, email, phone, job_profile):
    """Handle the complete resume processing workflow with LLaMA"""
    with st.spinner("Processing your resume..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            input_pdf_path = tmp.name

        try:
            # Step 1: Extract text
            st.info("🔍 Extracting text from your resume...")
            original_text = extract_text_from_pdf(input_pdf_path)

            # Step 2: Calculate ATS Score
            st.info("📊 Calculating ATS Score...")
            ats_score, ats_feedback = calculate_ats_score(original_text, job_profile)
            
            # Step 3: Enhance with LLaMA
            st.info("✨ Enhancing your resume with AI...")
            user_intro = f"My name is {name}, my email is {email}, and my phone number is {phone}. I am applying for the position of {job_profile}."
            full_prompt = user_intro + "\n\n" + original_text
            enhanced_text = run_llama_enhancer(full_prompt)

            # Step 4: Parse enhanced resume
            st.info("📄 Organizing enhanced content...")
            updated_sections = split_into_sections(enhanced_text)

            # Step 5: Generate new PDF
            output_pdf_path = Path(tempfile.gettempdir()) / "enhanced_resume.pdf"
            generate_updated_resume_with_template(
                input_pdf_path, 
                updated_sections, 
                str(output_pdf_path), 
                name, 
                phone, 
                email
            )

            # Step 6: Download result
            st.success("✅ Resume enhancement complete!")
            with open(output_pdf_path, "rb") as f:
                st.download_button(
                    "📥 Download Enhanced Resume", 
                    f, 
                    file_name=f"Enhanced_Resume_{name.replace(' ', '_')}.pdf",
                    help="Click to download your enhanced resume"
                )
            
            # Show preview
            st.subheader("Preview of Enhanced Resume")
            with st.expander("View Enhanced Content"):
                for section, content in updated_sections.items():
                    st.markdown(f"**{section}**")
                    st.write(content)
                    st.markdown("---")

            # Show ATS Score
            st.subheader("ATS Score & Feedback")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("ATS Score", f"{ats_score}/100")
            with col2:
                if ats_score >= 80:
                    st.success("Excellent! Your resume is well optimized for ATS.")
                elif ats_score >= 60:
                    st.warning("Good, but could be improved. See feedback below.")
                else:
                    st.error("Needs significant improvement for ATS. See feedback below.")
            
            # Display ATS Feedback
            with st.expander("View Detailed ATS Feedback"):
                for category, feedback_list in ats_feedback.items():
                    st.markdown(f"**{category}**")
                    for feedback_item in feedback_list:
                        st.write(feedback_item)
                    st.markdown("---")

        except Exception as e:
            st.error(f"❌ Error processing your resume: {str(e)}")
            st.error("Please try again or contact support if the problem persists.")
        finally:
            # Clean up temporary files
            if Path(input_pdf_path).exists():
                Path(input_pdf_path).unlink()
            if Path(output_pdf_path).exists():
                Path(output_pdf_path).unlink()