import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Google-Powered Job Matcher", layout="wide")
st.title("🔍 Direct Google-Indexed Job Matcher")
st.write("Extracts resume context and pulls real-time links directly from Google Search (last 24 hours only).")

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(file):
    """Extracts raw text from an uploaded PDF resume."""
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def calculate_match_score(resume_text, job_text):
    """Computes semantic matching using TF-IDF and Cosine Similarity."""
    if not job_text:
        return 0
    documents = [resume_text, job_text]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return int(similarity[0][0] * 100)

def search_google_jobs(executive_query):
    """Scrapes Google Search using time filters for the last 24 hours."""
    # Constructing a targeted query looking for direct tracking system paths
    full_query = f"{executive_query} remote (site:greenhouse.io OR site:lever.co OR site:boards.greenhouse.io)"
    encoded_query = urllib.parse.quote_plus(full_query)
    
    # num=50 requests up to 50 results; tbs=qdr:d restricts to the last 24 hours
    url = f"https://www.google.com/search?q={encoded_query}&num=50&tbs=qdr:d"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            st.error(f"Google structural block or rate limit encountered (Status Code: {response.status_code}).")
            return []
            
        soup = BeautifulSoup(response.text, "html.parser")
        search_results = []
        
        # Iterate over Google standard result containers
        for g in soup.find_all('div', class_='g'):
            anchors = g.find_all('a')
            if anchors:
                link = anchors[0]['href']
                title_box = g.find('h3')
                snippet_box = g.find('div', class_='VwiC3b') # Google snippet class wrapper
                
                if title_box and link.startswith('http'):
                    title = title_box.get_text()
                    snippet = snippet_box.get_text() if snippet_box else ""
                    
                    search_results.append({
                        "title": title,
                        "url": link,
                        "snippet": snippet
                    })
        return search_results
    except Exception as e:
        st.error(f"Network error while reaching search index: {str(e)}")
        return []

# --- MAIN APPLICATION FLOW ---
uploaded_file = st.file_uploader("Upload your Resume (PDF format)", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Processing resume file..."):
        resume_content = extract_text_from_pdf(uploaded_file)
        
    with st.spinner("Parsing live Google index listings for matching roles..."):
        # Naturally targeted at executive leadership roles matching top-tier compensation structures
        raw_jobs = search_google_jobs(executive_query="('CTO' OR 'VP of Engineering' OR 'Director of Technology' OR 'Principal Architect')")
        
    if not raw_jobs:
        st.info("No corporate tracking paths indexed by Google matching the criteria in the past 24 hours.")
    else:
        highly_matched_jobs = []
        
        for job in raw_jobs:
            # Evaluate relevance using both Title and the Snippet summary text
            combined_job_text = f"{job['title']} {job['snippet']}"
            score = calculate_match_score(resume_content, combined_job_text)
            
            # Since strict filtering is requested, we keep high-affinity returns
            # Adjust the threshold down slightly if snippets yield sparse keywords
            if score >= 30: 
                job['score'] = score
                highly_matched_jobs.append(job)
                
        # Sort results by highest calculated match score
        highly_matched_jobs = sorted(highly_matched_jobs, key=lambda x: x['score'], reverse=True)
        
        if not highly_matched_jobs:
            st.warning("No jobs met the baseline compatibility threshold against the search snippet text. Displaying top raw indexed matches instead:")
            highly_matched_jobs = raw_jobs[:50]
            for j in highly_matched_jobs:
                j['score'] = "N/A"

        st.success(f"Successfully compiled live application avenues direct from Google's past-24-hour index.")
        st.divider()
        
        # --- RENDER RESULTS ---
        for idx, job in enumerate(highly_matched_jobs[:50]):
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"### {idx+1}. {job['title']}")
                    if job['snippet']:
                        st.markdown(f"*{job['snippet']}*")
                    if isinstance(job['score'], int):
                        st.progress(job['score'] / 100)
                        st.caption(f"Relevance Compatibility: {job['score']}%")
                with col2:
                    st.write("") # Structural alignment spacing
                    st.link_button("🌐 Open Application", job['url'])
                st.divider()
