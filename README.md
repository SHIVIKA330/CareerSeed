# 🌱 CareerSeeds: AI-Powered Career Assistant

CareerSeeds is a premium AI career counseling and resume enhancement platform. It helps users bloom in their professional journey by providing expert advice, ATS-optimized resume feedback, and personalized course/job recommendations.

## ✨ Features
- **🤖 AI Career Chatbot**: Real-time advice on career paths and industry trends.
- **📄 Resume Enhancer**: AI-driven content improvement and ATS score calculation.
- **💡 Smart Recommendations**: Matches your skills with relevant courses and jobs.
- **🎨 Premium UI**: Modern glassmorphic design for a superior user experience.

## 🚀 Deployment on Render

To deploy this project successfully, follow these steps:

### 1. Upload Project Files
Ensure you have uploaded all the Python files to your GitHub repository. The application no longer requires manual CSV files for recommendations; it uses AI to generate them dynamically.

### 2. Configure Render
1.  Sign in to **Render** and click **New > Blueprint** or **New > Web Service**.
2.  Connect your GitHub repository.
3.  **Build Command**: `pip install -r requirements.txt`
4.  **Start Command**: `streamlit run app.py`

### 3. Set Environment Variables
Go to the **Environment** tab in your Render dashboard and add:
- `AIML_API_KEY`: Your API key (e.g., `1a6...`)

## 🛠️ Local Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the app: `streamlit run app.py`.

---
*Developed with ❤️ for the next generation of professionals.*
