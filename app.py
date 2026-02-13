import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SudoDocs: Script Studio",
    page_icon="✍️",
    layout="wide"
)

# Professional CSS for 2026 Modern Aesthetic
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; }
    .stButton>button {
        width: 100%; border-radius: 6px; height: 3.5em;
        background-color: #238636; color: white; border: none; font-weight: bold;
    }
    .stButton>button:hover { background-color: #2ea043; }
    .stTextArea textarea { font-family: 'Fira Code', monospace; font-size: 14px; }
    .seo-card {
        background-color: #161b22; padding: 20px; border-radius: 10px;
        border: 1px solid #30363d; margin-bottom: 20px;
    }
    </style>
    """, unsafe_content_label=True)

# --- BACKEND LOGIC ---

def fetch_research(topic, mode, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompts = {
        "Movie/Series Review": f"Research movie/series '{topic}'. Provide technical facts: Director, Cast, Composer, and its place in film history.",
        "Technology Blog": f"Analyze latest news/topics regarding '{topic}' (e.g. Windows failures, AI updates). Provide technical root cause, user impact, and industry response.",
        "Educational/Docs Content": f"Technical deep-dive on '{topic}'. Contextualize for Technical Writers: Sphinx, DITA XML, Docs-as-Code, and AI-documentation standards."
    }
    
    try:
        response = model.generate_content(prompts[mode])
        return response.text
    except Exception as e:
        return f"Research Error: {e}"

def generate_viral_package(mode, title, research, notes, matrix, api_key):
    """Generates the full Viral Metadata Suite and Script."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # Define Persona voices
    personas = {
        "Movie/Series Review": "Beyond Cinemas: Analytical, technical cinephile (40s male), cinematic critique focus.",
        "Technology Blog": "Tech Insider: Sharp, professional, focused on technical impact and user frustration/wins.",
        "Educational/Docs Content": "SudoDocs Lead: Precise, educational, Senior Technical Writer tone."
    }
    
    prompt = f"""
    {personas[mode]}
    Topic: {title}
    Data: {research} | Matrix: {matrix} | Notes: {notes}
    
    Generate a complete YouTube Viral Package with this exact structure:

    ### 1. VIRAL TITLES (SEO-OPTIMIZED)
    - Provide 3 options (1 Click-Driven, 1 Question-Based, 1 Technical/Analytical).
    - Front-load keywords. 

    ### 2. SEO DESCRIPTION
    - Include primary keywords in the first 125 characters.
    - Write a 3-paragraph summary.
    - Add timestamp placeholders and links placeholders.

    ### 3. THE SCRIPT (SUBTITLES FORMAT)
    - Full narrative script.
    - Strong Hook in the first 10 seconds.
    - Balanced technical analysis and personal flavor.

    ### 4. VIRAL TAGS & HASHTAGS
    - 15 high-volume tags (comma-separated).
    - 5 trending hashtags (#Topic, #TechNews, etc.).
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Generation Error: {e}"

# --- MAIN UI ---
st.title("🛡️ SudoDocs: Script Studio")
st.caption("2026 Content Suite: Analytics-Driven Scripting for Movies, Tech, and Docs.")

with st.sidebar:
    st.title("⚙️ Studio Config")
    api_key = st.text_input("Gemini API Key", type="password")
    active_module = st.selectbox("Active Module", ["Movie/Series Review", "Technology Blog", "Educational/Docs Content"])
    st.divider()
    st.info(f"Targeting Viral Reach for: **{active_module}**")

col_input, col_meta = st.columns([1, 1], gap="large")

with col_input:
    st.markdown("### 🏗️ Content Inputs")
    topic_title = st.text_input("Enter Video Topic")
    
    if st.button("🔍 Run Strategic Research"):
        if not api_key: st.error("API Key required.")
        else:
            with st.spinner("Analyzing current trends..."):
                st.session_state['res_out'] = fetch_research(topic_title, active_module, api_key)
    
    if 'res_out' in st.session_state:
        st.info(st.session_state['res_out'])

    st.subheader("🛠️ Technical Matrix")
    if active_module == "Movie/Series Review":
        m1 = st.select_slider("Direction", ["Bad", "Avg", "Good", "Masterpiece"], "Good")
        matrix_sum = f"Direction: {m1}"
    elif active_module == "Technology Blog":
        m1 = st.select_slider("Criticality", ["Minor", "Major", "Catastrophic"], "Major")
        matrix_sum = f"Impact: {m1}"
    else:
        m1 = st.select_slider("Complexity", ["Basic", "Int", "Adv"], "Int")
        matrix_sum = f"Level: {m1}"

    brain_dump = st.text_area("Personal Brain Dump (Your unique take):", height=200)

with col_meta:
    st.markdown("### ✨ Generate Viral Package")
    if st.button("🚀 Build Full YouTube Suite"):
        if api_key and topic_title:
            with st.spinner("Generating SEO Package..."):
                pkg = generate_viral_package(active_module, topic_title, st.session_state.get('res_out', ''), brain_dump, matrix_sum, api_key)
                st.session_state['full_pkg'] = pkg

if 'full_pkg' in st.session_state:
    st.divider()
    st.subheader("📦 Final Production Package")
    st.text_area("Metadata & Script (Copy-Paste Ready)", value=st.session_state['full_pkg'], height=700)
    st.download_button("📂 Download Studio Package", st.session_state['full_pkg'], file_name=f"{topic_title}_Package.txt")
