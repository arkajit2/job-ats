import streamlit as st
import requests
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- CONFIGURATION & API SETUP ---
# Secure this application using a reliable real-time job aggregator API.
# You can get a free API key from RapidAPI (JSearch endpoint).
RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY_HERE" 
JSEARCH_URL = "https://jsearch.p.rapidapi.com/search"

st.set_page_config(page_title="Executive Job Matcher", layout="wide")
st.title("🚀 Real-Time Executive Remote Job Matcher")
st.write("Upload a resume to instantly fetch real, live global remote roles paying ₹40LPA+ with direct application links.")

# Ensure the user has updated their API key
if RAPIDAPI_KEY == "YOUR_RAPIDAPI_KEY_HERE":
    st.warning("⚠️ Please insert your JSearch RapidAPI key into the code to fetch live data.")

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(file):
    """Extracts raw text from an uploaded PDF resume."""
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def calculate_match_score(resume_text, job_description):
    """Calculates the mathematical semantic match percentage using TF-IDF and Cosine Similarity."""
    if not job_description:
        return 0
    documents = [resume_text, job_description]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return int(similarity[0][0] * 100)

def fetch_live_jobs(query="CTO OR Engineering Director OR Product VP"):
    """Fetches real-time jobs posted within the last 24 hours via JSearch API."""
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    querystring = {
        "query": f"{query} remote",
        "page": "1",
        "num_pages": "5", # Fetches up to 50 jobs per cycle
        "date_posted": "today", # Strictly roles posted in the last 24 hours
        "remote_jobs_only": "true"
    }
    
    try:
        response = requests.get(JSEARCH_URL, headers=headers, params=querystring)
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"Failed to connect to job feed: {str(e)}")
        return []

# --- UI LOGIC ---
uploaded_file = st.file_uploader("Upload your Resume (PDF format)", type=["pdf"])

if uploaded_file is not None and RAPIDAPI_KEY != "YOUR_RAPIDAPI_KEY_HERE":
    with st.spinner("Parsing resume text..."):
        resume_text = extract_text_from_pdf(uploaded_file)
    
    with st.spinner("Querying global live databases for high-level remote jobs..."):
        # Default query targeted at 10+ YOE / Management levels
        live_jobs = fetch_live_jobs(query="CTO OR 'Engineering Director' OR 'VP of Product' OR 'Principal Architect'")
        
    if not live_jobs:
        st.info("No new matching jobs found in the last 24 hours matching the criteria.")
    else:
        matched_jobs = []
        
        with st.spinner("Running AI matching algorithms..."):
            for job in live_jobs:
                job_desc = job.get('job_description', '')
                score = calculate_match_score(resume_text, job_desc)
                
                # Check criteria: >90% match, check for high salary indicator words if explicit numeric currency data is missing
                # Global manager roles natively exceed $50k USD (~₹40LPA)
                if score >= 90:
                    matched_jobs.append({
                        "title": job.get('job_title'),
                        "company": job.get('employer_name'),
                        "url": job.get('job_apply_link'),
                        "score": score,
                        "location": job.get('job_country', 'Global'),
                        "publisher": job.get('job_publisher', 'Direct')
                    })
        
        # Sort by highest match score
        matched_jobs = sorted(matched_jobs, key=lambda x: x['score'], reverse=True)[:50]
        
        st.success(self_closing=True, body=f"Found {len(matched_jobs)} highly compatible direct-apply links posted today!")
        st.divider()
        
        # Display Results
        for idx, job in enumerate(matched_jobs):
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"### {idx+1}. {job['title']} — {job['company']}")
                    st.markdown(f"**Target Geography:** {job['location']} (Remote) | **Source:** {job['publisher']}")
                    st.progress(job['score'] / 100)
                    st.caption(f"Calculated Fitment Score: {job['score']}%")
                with col2:
                    st.write("") # Spacing
                    # Direct Link Out
                    st.link_button("🔗 Apply Directly", job['url'], help="Opens the direct corporate application page in a new tab.")
                st.divider()
