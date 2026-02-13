import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SudoDocs: Script Studio",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- FIXED CSS BLOCK ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stButton>button {
        width: 100%; border-radius: 6px; height: 3em;
        background-color: #238636; color: white; border: none; font-weight: 600;
    }
    .stButton>button:hover { background-color: #2ea043; }
    .metric-card {
        background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)  # <--- FIXED PARAMETER HERE

# --- BACKEND LOGIC ---

def run_deep_research(topic, mode, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # SIMPLIFIED & HUMANIZED PROMPTS
    prompts = {
        "Cinema Logic (Realist-Industrial Critic)": f"""
        ACT AS: Senior Film Critic.
        TOPIC: {topic}
        RESEARCH TASKS:
        1. CONTEXT: Director's track record and the genre's current state.
        2. THEMES: The deeper philosophical or social questions the story asks.
        3. PRODUCTION: Any notable behind-the-scenes conflict or budget constraints?
        4. RECEPTION: General audience sentiment vs. critical consensus.
        OUTPUT: Concise research notes for a script.
        """,
        
        "Tech News Logic (Viral Tech Blog)": f"""
        ACT AS: Senior Tech Journalist.
        TOPIC: {topic}
        RESEARCH TASKS:
        1. PAIN POINTS: Why do users struggle with this? (Root Cause).
        2. SOLUTION: The "Aha!" moment or fix.
        3. CONTEXT: Industry impact or "Docs-as-Code" relevance.
        OUTPUT: Engagement hooks and technical context.
        """,
        
        "Documentation Logic (SudoDocs-tv)": f"""
        ACT AS: Developer Advocate.
        TOPIC: {topic}
        RESEARCH TASKS:
        1. THE STRUGGLE: Common user errors.
        2. THE FIX: Best practices and "Aha!" moments.
        3. VISUALS: needed diagrams or code snippets.
        OUTPUT: Educational context.
        """
    }
    
    # Fallback to handle different mode names if sidebar changes
    prompt_text = prompts.get(mode, prompts["Cinema Logic (Realist-Industrial Critic)"])
    
    try:
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        return f"Research Error: {e}"
        
def generate_script_package(mode, title, research, notes, matrix_data, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')
    
    system_instructions = {
        "Movie/Series Review": """
        ROLE: Sophisticated Film Critic (Tone: Critical, Insightful, Human).
        
        NARRATIVE STRUCTURE (THE 5 ACTS):
        1. THE ANCHOR: Start with a broad observation about life, society, or the genre.
        2. THE SETUP: Introduce the film/series as a case study of that Anchor.
        3. THE 'WHY': Analyze the characters' motivations. Are they 'Second Nature' (believable) or 'Plastic' (fake)?
        4. THE CRAFT: Critique the Direction and Writing. Use words like "Finesse," "Resilience," "Dull," "Junk."
        5. THE VERDICT: A definitive "Watch" or "Skip" conclusion.
        
        RULE: Write a cohesive ESSAY/ARTICLE. Focus on flow and argument. Do NOT use [Visual Cues], camera directions, or scene numbers.
        """,
        
        "Tech & Docs (SudoDocs)": """
        ROLE: Senior DevRel & Tech Reporter (Tone: Helpful, Authoritative, 'No-Fluff').
        
        STRUCTURE:
        1. THE HOOK: The immediate problem/news.
        2. THE DIAGNOSIS: Why is this happening? (Root Cause).
        3. THE FIX/LESSON: How to solve it or what it means for the industry.
        4. THE TAKEAWAY: Final thought for the reader.
        
        RULE: Use Analogies (Lego, Traffic) to explain complex concepts. Write as a BLOG POST/ARTICLE. No visual placeholders.
        """
    }
    
    prompt = f"""
    {system_instructions[mode]}
    
    INPUTS:
    - Topic: {title}
    - Research: {research}
    - User Vibes/Notes: "{notes}"
    - Technical Ratings: {matrix_data}
    
    TASK: Write a High-Quality Article/Essay + Metadata.
    
    FORMAT:
    ### TITLES (3 Options - Clickable but Honest)
    ### DESCRIPTION (SEO Optimized)
    ### ARTICLE BODY (Pure text, engaging prose, no visual cues)
    ### TAGS (15 comma-separated)
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Generation Error: {e}"
        
# --- UI COMPONENTS ---

def render_technical_matrix(mode):
    st.subheader("🎛️ Analysis Matrix")
    data = {}
    
    # LOGIC 1: MOVIE / SERIES
    if "Cinema" in mode or "Movie" in mode:
        c1, c2 = st.columns(2)
        with c1:
            data['Thematic_Depth'] = st.select_slider("Thematic Depth", ["Superficial", "Standard", "Profound"], "Standard")
            data['Visual_Craft'] = st.select_slider("Visuals", ["Ugly/Generic", "Competent", "Masterpiece"], "Competent")
        with c2:
            data['Acting_Quality'] = st.select_slider("Performances", ["Wooden", "Serviceable", "Transformative"], "Serviceable")
            data['Verdict'] = st.selectbox("Final Verdict", ["Skip It", "Wait for Streaming", "Must Watch"])
            
    # LOGIC 2: TECH & DOCS
    else:
        c1, c2 = st.columns(2)
        with c1:
            data['Complexity'] = st.select_slider("Topic Complexity", ["Beginner", "Intermediate", "Advanced"], "Intermediate")
            data['Urgency'] = st.select_slider("News Urgency", ["Evergreen Guide", "Trending Now", "Breaking News"], "Evergreen Guide")
        with c2:
            data['Tone'] = st.selectbox("Video Tone", ["Tutorial (Step-by-Step)", "Opinion/Rant", "Deep Dive Explanation"])
            
    return str(data)

# --- MAIN APP LAYOUT ---

with st.sidebar:
    st.title("🛡️ SudoDocs: Script Studio")
    api_key = st.text_input("Gemini API Key", type="password")
    st.markdown("---")
    
    # UPDATE: Ensure these names match the new function keys EXACTLY
    active_mode = st.radio(
        "Select Logic Module:",
        [
            "Cinema Logic (Realist-Industrial Critic)", 
            "Tech News Logic (Viral Tech Blog)", 
            "Documentation Logic (SudoDocs-tv)"
        ]
    )
    
    st.info(f"Persona: **{active_mode.split('(')[0]}**")

st.title("📺 SudoDocs: Script Studio")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("### 1. Topic & Research")
    topic_title = st.text_input("Video Topic", placeholder="e.g. Sphinx Auto-Doc Setup")
    
    if st.button("🔍 Run Engagement Research"):
        if not api_key: st.error("Authentication Missing")
        else:
            with st.spinner("Analyzing Pain Points & Visuals..."):
                st.session_state['research_data'] = run_deep_research(topic_title, active_mode, api_key)
    
    if 'research_data' in st.session_state:
        with st.expander("View Research Notes", expanded=True):
            st.markdown(st.session_state['research_data'])

    matrix_summary = render_technical_matrix(active_mode)

with col_right:
    st.markdown("### 2. Script & Metadata")
    brain_dump = st.text_area("Brain Dump / Specific Code to Mention", height=150)
    
    if st.button("🚀 Generate Video Package"):
        if not api_key or not topic_title: st.error("Missing Inputs")
        else:
            with st.spinner("Writing Script & Visual Cues..."):
                package = generate_viral_package(
                    active_mode, 
                    topic_title, 
                    st.session_state.get('research_data', ""), 
                    brain_dump, 
                    matrix_summary, 
                    api_key
                )
                st.session_state['final_package'] = package

if 'final_package' in st.session_state:
    st.markdown("---")
    st.subheader("📦 Final Upload Package")
    st.text_area("Full Script & SEO Data", value=st.session_state['final_package'], height=800)
    st.download_button("💾 Download Script", st.session_state['final_package'], file_name=f"{topic_title}_Script.txt")
