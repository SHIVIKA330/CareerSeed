import streamlit as st
import tempfile
from pathlib import Path
import pandas as pd
from resume_enhancer import (
    extract_text_from_pdf,
    run_llama_enhancer,
    split_into_sections,
    generate_updated_resume_with_template,
    generate_new_resume_from_scratch,
    get_relevant_courses,
    get_relevant_jobs,
    calculate_ats_score
)
from openai import OpenAI

# Initialize OpenAI client
chat_client = OpenAI(
    base_url="https://api.aimlapi.com/v1",
    api_key="1a63d6d97953468ebfb42bf530d0a4ab",    
)

def career_chatbot(prompt, chat_history=None):
    """Function to interact with OpenAI chatbot"""
    try:
        messages = [{"role": "system", "content": "You are CareerSeed AI, a helpful career assistant that provides resume advice, job search tips, and career guidance. Be professional but friendly."}]
        
        if chat_history:
            messages.extend(chat_history)
            
        messages.append({"role": "user", "content": prompt})
        
        response = chat_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

st.title("🌱 CareerSeed : Grow Your Career")

# Add chatbot to sidebar
with st.sidebar:
    st.header("💬 CareerSeed AI Assistant")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about careers, resumes, or jobs..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = career_chatbot(prompt, st.session_state.messages[:-1])
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Main application - User choice
st.subheader("What would you like to do?")
option = st.radio("Choose an option:", 
                 ["Create a new resume from scratch", "Enhance my existing resume"],
                 key="main_option_radio")

if option == "Create a new resume from scratch":
    # Collect all details for new resume
    st.subheader("Step 1: Enter Your Personal Details")
    
    name = st.text_input("👤 Full Name*", key="name_input")
    address = st.text_input("🏠 Address", key="address_input")
    email = st.text_input("📧 Email ID*", key="email_input")
    phone = st.text_input("📱 Phone Number (10 digits only)*", max_chars=10, key="phone_input")
    linkedin = st.text_input("📈 LinkedIn Profile URL", key="linkedin_input")
    github = st.text_input("🤖 GitHub Profile URL", key="github_input")
    leetcode = st.text_input("🤔 LeetCode Profile URL", key="leetcode_input")

    # Education details
    st.subheader("Step 2: Enter Your Education Details")
    degree_program = st.text_input("🎓 Degree/Program*", key="degree_input")
    university = st.text_input("🏫 University Name*", key="university_input")
    location = st.text_input("📍 Location", key="location_input")
    grade = st.text_input("📚 Grade/GPA", key="grade_input")
    year = st.text_input("📆 Year of Graduation*", key="year_input")

    # Experience details
    st.subheader("Step 3: Enter Your Experience Details")
    company = st.text_input("🏢 Company Name", key="company_input")
    position = st.text_input("📈 Position", key="position_input")
    duration = st.text_input("🕰️ Duration", key="duration_input")
    description = st.text_area("📝 Description (Bullet points work best)", key="exp_desc_input")
    achievements = st.text_area("🏆 Achievements (Bullet points work best)", key="exp_achievements_input")

    # Projects details
    st.subheader("Step 4: Enter Your Projects Details")
    project_name = st.text_input("📈 Project Name", key="project_name_input")
    project_description = st.text_area("📝 Project Description (Bullet points work best)", key="project_desc_input")
    project_link = st.text_input("🔗 Project Link", key="project_link_input")

    # Skills details
    st.subheader("Step 5: Enter Your Skills Details")
    skills = st.text_area("🤖 Skills (Comma separated)*", key="skills_input")

    # Achievements
    st.subheader("Step 6: Enter Your Achievements Details")
    achievements = st.text_area("🏆 Achievements (Bullet points work best)", key="achievements_input")

    # Activities
    st.subheader("Step 7: Enter Your Activities Details")
    activities = st.text_area("🏋️‍♀️ Activities (Bullet points work best)", key="activities_input")

    # Job profile list
    job_profiles = [
        "Software Developer", "Software Engineer", "Web Developer", "Mobile App Developer",
        "Full-Stack Developer", "Game Developer", "Application Developer", "Embedded Systems Engineer",
        "DevOps Engineer", "Software Architect", "Data Scientist", "Data Analyst",
        "Machine Learning Engineer", "Data Engineer", "Business Intelligence Analyst", "Data Architect",
        "Information Security Analyst", "Cybersecurity Analyst", "Security Engineer", "Penetration Tester",
        "Digital Forensics Examiner", "IT Auditor", "Network Administrator", "Systems Administrator",
        "Cloud Solutions Architect", "Network Engineer", "Database Administrator (DBA)", "Database Architect",
        "Computer and Information Research Scientist", "Computer Hardware Engineer", "Technical Project Manager",
        "UI/UX Designer", "Technical Writer", "IT Consultant", "Technical Support Specialist",
        "Artificial Intelligence (AI) Engineer", "Robotics Engineer", "Bioinformatics Research Scientist",
        "Quantum Computing Scientist/Engineer", "Computer Systems Analyst", "Product Manager (Technical)",
        "Site Reliability Engineer (SRE)"
    ]

    job_profile = st.selectbox("💼 Select the Job Profile You're Applying For*", job_profiles, key="job_profile_select")

    # Validate phone number
    if phone and (not phone.isdigit() or len(phone) != 10):
        st.error("Please enter a valid 10-digit phone number (numbers only)")

    if st.button("Generate Resume", key="generate_resume_btn"):
        if name and email and phone and job_profile and degree_program and university and year and skills and phone.isdigit() and len(phone) == 10:
            with st.spinner("Generating your professional resume..."):
                # Prepare all user data
                user_data = {
                    "name": name,
                    "contact": {
                        "address": address,
                        "email": email,
                        "phone": phone,
                        "linkedin": linkedin,
                        "github": github,
                        "leetcode": leetcode
                    },
                    "education": {
                        "degree": degree_program,
                        "university": university,
                        "location": location,
                        "grade": grade,
                        "year": year
                    },
                    "experience": {
                        "company": company,
                        "position": position,
                        "duration": duration,
                        "description": description,
                        "achievements": achievements
                    },
                    "projects": {
                        "name": project_name,
                        "description": project_description,
                        "link": project_link
                    },
                    "skills": skills,
                    "achievements": achievements,
                    "activities": activities,
                    "job_profile": job_profile
                }
                
                # Generate resume PDF
                output_pdf_path = Path(tempfile.gettempdir()) / "new_resume.pdf"
                generate_new_resume_from_scratch(user_data, str(output_pdf_path))
                
                # Show download button
                with open(output_pdf_path, "rb") as f:
                    st.success("✅ Resume generated successfully!")
                    st.download_button(
                        "📥 Download Your Resume", 
                        f, 
                        file_name=f"{name.replace(' ', '_')}_Resume.pdf",
                        help="Click to download your professionally generated resume",
                        key="download_resume_btn"
                    )
                
                # Calculate ATS Score for the generated resume
                st.info("📊 Calculating ATS Score for your new resume...")
                ats_score, ats_feedback = calculate_ats_score(str(user_data), job_profile)
                
                # Display ATS Score
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
                    for category, feedback in ats_feedback.items():
                        st.markdown(f"**{category}**")
                        st.write(feedback)
                        st.markdown("---")
        else:
            st.warning("Please fill all required fields (marked with *) with valid information")

else:  # Enhance existing resume
    st.subheader("Step 1: Enter Basic Information")
    
    name = st.text_input("👤 Full Name", key="enhance_name_input")
    email = st.text_input("📧 Email ID", key="enhance_email_input")
    phone = st.text_input("📱 Phone Number (10 digits only)", max_chars=10, key="enhance_phone_input")
    
    # Job profile list
    job_profiles = [
        "Software Developer", "Software Engineer", "Web Developer", "Mobile App Developer",
        "Full-Stack Developer", "Game Developer", "Application Developer", "Embedded Systems Engineer",
        "DevOps Engineer", "Software Architect", "Data Scientist", "Data Analyst",
        "Machine Learning Engineer", "Data Engineer", "Business Intelligence Analyst", "Data Architect",
        "Information Security Analyst", "Cybersecurity Analyst", "Security Engineer", "Penetration Tester",
        "Digital Forensics Examiner", "IT Auditor", "Network Administrator", "Systems Administrator",
        "Cloud Solutions Architect", "Network Engineer", "Database Administrator (DBA)", "Database Architect",
        "Computer and Information Research Scientist", "Computer Hardware Engineer", "Technical Project Manager",
        "UI/UX Designer", "Technical Writer", "IT Consultant", "Technical Support Specialist",
        "Artificial Intelligence (AI) Engineer", "Robotics Engineer", "Bioinformatics Research Scientist",
        "Quantum Computing Scientist/Engineer", "Computer Systems Analyst", "Product Manager (Technical)",
        "Site Reliability Engineer (SRE)"
    ]

    job_profile = st.selectbox("💼 Select the Job Profile You're Applying For", job_profiles, key="enhance_job_profile_select")
    
    st.subheader("Step 2: Upload Your Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"], key="resume_uploader")
    
    # Paths to data files
    courses_csv_path = r"C:\careerseed\all_courses.csv"
    jobs_csv_path = r"C:\careerseed\job1.csv"

    if uploaded_file and name and email and phone and job_profile:
        if phone and (not phone.isdigit() or len(phone) != 10):
            st.error("Please enter a valid 10-digit phone number (numbers only)")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                input_pdf_path = tmp.name

            st.success("✅ Resume uploaded! Extracting text...")

            original_text = extract_text_from_pdf(input_pdf_path)
            
            # Calculate ATS Score
            st.info("📊 Calculating ATS Score...")
            ats_score, ats_feedback = calculate_ats_score(original_text, job_profile)
            
            # Display ATS Score
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
                for category, feedback in ats_feedback.items():
                    st.markdown(f"**{category}**")
                    st.write(feedback)
                    st.markdown("---")

            # Construct prompt
            user_intro = f"My name is {name}, my email is {email}, and my phone number is {phone}. I am applying for the position of {job_profile}."
            full_prompt = user_intro + "\n\n" + original_text

            st.info("🔍 Enhancing your resume with LLaMA...")

            try:
                enhanced_text = run_llama_enhancer(full_prompt)
            except Exception as e:
                st.error(f"❌ Failed to enhance resume: {e}")
                st.stop()

            st.info("📄 Parsing enhanced resume...")
            updated_sections = split_into_sections(enhanced_text)

            output_pdf_path = Path(tempfile.gettempdir()) / "enhanced_resume.pdf"
            generate_updated_resume_with_template(input_pdf_path, updated_sections, str(output_pdf_path), name, phone, email)

            with open(output_pdf_path, "rb") as f:
                st.success("✅ Resume enhanced! Download below.")
                st.download_button(
                    "📥 Download Enhanced Resume", 
                    f, 
                    file_name="enhanced_resume.pdf",
                    key="enhanced_download_btn"
                )

            # Show preview
            st.subheader("Preview of Enhanced Resume")
            with st.expander("View Enhanced Content"):
                for section, content in updated_sections.items():
                    st.markdown(f"**{section}**")
                    st.write(content)
                    st.markdown("---")
                    
            # Show recommendations after resume generation
            st.subheader("📚 Recommended Courses for Your Selected Job Profile")
            try:
                recommended_courses = get_relevant_courses(job_profile, courses_csv_path)
                if not recommended_courses.empty:
                    for _, row in recommended_courses.iterrows():
                        with st.container():
                            st.markdown(f"**📘 {row['Course Name']}**")
                            st.caption(f"🔗 [Course Link]({row['Course Link']})")
                            st.caption(f"🏷️ Degree Type: {row.get('degree type', 'N/A')}")
                            st.caption(f"📄 Description: {row.get('Description', 'No description provided.')}")
                            st.caption(f"🎚️ Level: {row.get('Level', 'N/A')}")
                            st.caption(f"🕒 Duration: {row.get('Duration', 'N/A')}")
                            st.caption(f"⭐ Rating: {row.get('Rating', 'N/A')}")
                            st.caption(f"🔧 Skills Covered: {row.get('Skills Covered', 'N/A')}")
                            st.caption(f"📝 Prerequisites: {row.get('Prerequisites', 'N/A')}")
                            st.caption(f"🏢 Job Profile: {row.get('job_profile', 'N/A')}")
                            st.markdown("---")
                else:
                    st.info("No matching courses found for this job profile.")
            except Exception as e:
                st.error(f"⚠️ Failed to load courses: {e}")

            st.subheader("💼 Recommended Job Listings")
            try:
                recommended_jobs = get_relevant_jobs(job_profile, jobs_csv_path)
                if not recommended_jobs.empty:
                    for _, row in recommended_jobs.iterrows():
                        with st.container():
                            st.markdown(f"**📌 {row['Job Title']} at {row['Company']}**")
                            st.caption(f"📍 Location: {row['Location']}")
                            st.caption(f"💰 Salary: {row['Salary Range']}")
                            st.caption(f"🏷️ Experience Level: {row['Experience Level']}")
                            st.caption(f"🏢 Industry: {row['Industry']}")
                            st.caption(f"📅 Posted: {row['Date Posted']}")
                            st.caption(f"🔧 Required Skills: {row['Required Skills']}")
                            st.caption(f"📄 Description: {row['Job Description']}")
                            st.markdown("---")
                else:
                    st.info("No matching job listings found for this job profile.")
            except Exception as e:
                st.error(f"⚠️ Failed to load job listings: {e}")