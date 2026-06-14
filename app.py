import streamlit as st
import time

# --- MOCK API DATA ---
# In production, this data comes from scraping APIs (e.g., TheirStack) filtered for >₹40LPA, Remote, Last 24h
MOCK_JOBS = [
    {
        "title": "Director of Engineering", 
        "company": "Global Tech AI", 
        "salary": "₹45,000,000 ($540k)", 
        "remote": True, 
        "posted": "2 hours ago", 
        "yoe_required": "12+",
        "match_score": 96
    },
    {
        "title": "Senior VP of Product", 
        "company": "Fintech Innovations", 
        "salary": "₹50,000,000 ($600k)", 
        "remote": True, 
        "posted": "8 hours ago", 
        "yoe_required": "10+",
        "match_score": 92
    },
]

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Executive Remote Matcher", layout="wide")

st.title("🌍 Executive Remote Job Matcher (10+ YOE)")
st.write("Upload your resume to instantly find global, 100% remote positions paying ₹40LPA+ posted in the last 24 hours.")

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload your Resume (PDF/DOCX)", type=["pdf", "docx"])

if uploaded_file is not None:
    # Simulate API latency and AI vector matching
    with st.spinner("Parsing resume via NLP and extracting key skills..."):
        time.sleep(1.5) 
        
    with st.spinner("Scanning global job APIs for manager+ roles posted today..."):
        time.sleep(1.5)
        
    st.success("Analysis complete! Found high-compatibility global roles.")
    st.divider()
    
    st.subheader("🔥 Top Matches (>90% Similarity)")
    
    # --- RENDER JOB MATCHES ---
    for job in MOCK_JOBS:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {job['title']} at {job['company']}")
                st.markdown(f"**Salary:** {job['salary']} | **Experience:** {job['yoe_required']} Years | **Posted:** {job['posted']}")
                
                # Render match score visually
                st.progress(job['match_score'] / 100)
                st.caption(f"Semantic Match Score: {job['match_score']}%")
            
            with col2:
                # Note: True 1-click apply requires enterprise ATS integrations
                st.button("⚡ 1-Click Apply", key=job['company'], help="Simulates application dispatch to company ATS.")
            st.divider()

# --- REAL-TIME ALERTS SIDEBAR ---
st.sidebar.header("Instant Alerts")
st.sidebar.write("Get pinged the second a matching ₹40LPA+ role drops.")
st.sidebar.text_input("Webhook URL or Email")
if st.sidebar.button("Enable Real-Time Alerts"):
    st.sidebar.success("Alerts enabled! Listening for new global postings.")
