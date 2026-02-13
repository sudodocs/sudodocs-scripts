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
    
    prompts = {
        "Cinema Logic (Beyond Cinemas)": f"""
        ACT AS: Film Historian & Scraper.
        TOPIC: {topic}
        EXTRACT: Director Signature, Production History, Audience vs Critic Gap, Interior Meaning.
        OUTPUT: Structured summary for a scriptwriter.
        """,
        
        "Tech News Logic (Viral Tech Blog)": f"""
        ACT AS: Senior Tech Journalist.
        TOPIC: {topic}
        EXECUTE ROOT CAUSE ANALYSIS: Immediate Symptom vs Systemic Issue, Technical Debt timeline, Industry Response.
        OUTPUT: Bullet points focused on 'Insider Insights'.
        """,
        
        "Documentation Logic (SudoDocs-tv)": f"""
        ACT AS: Developer Advocate / YouTube Educator.
        TOPIC: {topic} (e.g., Sphinx, DITA, AI Agents).
        
        RESEARCH FOR VIDEO ENGAGEMENT:
        1. THE STRUGGLE: What specifically confuses users about this? (e.g., "Why does Sphinx build fail silently?")
        2. THE "AHA!" MOMENT: What is the visual concept that unlocks understanding?
        3. VISUAL ASSETS: Identify needed diagrams (e.g., "DITA Map Hierarchy") vs. Live Code demos.
        4. REAL-WORLD USE CASE: Where is this actually used? (e.g., "Linux Kernel docs uses Sphinx").
        
        OUTPUT: A list of engagement hooks and visual analogies.
        """
    }
    
    try:
        response = model.generate_content(prompts[mode])
        return response.text
    except Exception as e:
        return f"Research Engine Error: {e}"

def generate_viral_package(mode, title, research, notes, matrix_data, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')
    
    system_instructions = {
        "Cinema Logic (Beyond Cinemas)": """
        ROLE: Auteur Theory Critic.
        LOGIC: Analyze visual motifs and 'showing vs telling'. Use the Technical Matrix to decode the director's signature.
        """,
        "Tech News Logic (Viral Tech Blog)": """
        ROLE: Systemic Tech Reporter.
        LOGIC: Root Cause Analysis. Explain WHY it happened, don't just report WHAT happened.
        """,
        "Documentation Logic (SudoDocs-tv)": """
        ROLE: Senior DevRel & Video Creator (Tone: Friendly, authoritative, high-energy).
        GOAL: Teach complex docs-as-code concepts simply.
        LOGIC: 
        1. Start with the "Pain Point" (e.g., "DITA tags are confusing...").
        2. Bridge to the "Solution" using the selected Analogy (from Matrix).
        3. Focus on "Show, Don't Tell" – describe the code snippets or diagrams needed on screen.
        """
    }
    
    # Metadata Formulas
    title_formulas = {
        "Cinema Logic (Beyond Cinemas)": "[Adjective] + [Topic] + [Provocative Question]",
        "Tech News Logic (Viral Tech Blog)": "[Topic] + [Causal Factor] + [Outcome]",
        "Documentation Logic (SudoDocs-tv)": "Stop Doing [Mistake] | How to Master [Topic] in [Time]"
    }

    prompt = f"""
    {system_instructions[mode]}
    
    INPUT DATA:
    - Topic: {title}
    - Deep Research: {research}
    - Video Style Matrix: {matrix_data}
    - Creator Notes: "{notes}"
    
    TASK: Generate a 2026 Viral Content Package.
    
    ### 1. CLICK-DRIVEN TITLES (3 Options)
    - Formula: {title_formulas[mode]}
    
    ### 2. DESCRIPTION
    - Hook + Keyword (first 125 chars).
    - Summary with "Key Takeaways".
    - Timestamp Outline (e.g., 0:00 Intro, 1:30 The Setup...).
    
    ### 3. VIDEO SCRIPT (Spoken Narration)
    - [VISUAL CUE] placeholders are mandatory (e.g., [SHOW TERMINAL], [ANIMATE DIAGRAM]).
    - Narrative must flow like a tutorial: Hook -> Concept -> Code/Demo -> Summary.
    
    ### 4. METADATA
    - 15 Tags (mix of broad/niche).
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Generation Error: {e}"

# --- UI COMPONENTS ---

def render_technical_matrix(mode):
    st.subheader("🎛️ Video Style Matrix")
    data = {}
    
    if mode == "Cinema Logic (Beyond Cinemas)":
        c1, c2 = st.columns(2)
        with c1:
            data['Visual_Motifs'] = st.select_slider("Visual Motifs", ["None", "Subtle", "Dominant"], "Subtle")
            data['Color_Symbolism'] = st.select_slider("Color Palette", ["Natural", "Stylized", "Discordant"], "Stylized")
        with c2:
            data['Screenplay_Structure'] = st.selectbox("Structure", ["Linear", "Episodic", "Fragmented"])
            
    elif mode == "Tech News Logic (Viral Tech Blog)":
        c1, c2 = st.columns(2)
        with c1:
            data['Criticality'] = st.select_slider("Impact", ["Minor", "Major", "Critical"], "Major")
        with c2:
            data['Systemic_Stress'] = st.selectbox("Failure Type", ["Single Point", "Cascading", "Security"])

    elif mode == "Documentation Logic (SudoDocs-tv)":
        c1, c2 = st.columns(2)
        with c1:
            data['Visual_Density'] = st.select_slider(
                "Visual Style", 
                ["Talking Head", "Balanced", "Heavy Screen-Share", "Animation Heavy"], 
                "Heavy Screen-Share"
            )
            data['Prerequisite_Level'] = st.select_slider(
                "Target Audience", 
                ["Total Beginner", "Junior Dev", "Senior Architect"], 
                "Junior Dev"
            )
        with c2:
            data['Teaching_Analogy'] = st.selectbox(
                "Core Analogy Style", 
                ["None/Direct", "Construction/Building", "Cooking/Recipes", "Lego Blocks", "Traffic/Flow"]
            )
            data['Demo_Type'] = st.selectbox(
                "Demonstration Format", 
                ["Live Coding", "Diagram Walkthrough", "Before/After Comparison", "Mistake Fix"]
            )
            
    return str(data)

# --- MAIN APP LAYOUT ---

with st.sidebar:
    st.title("🛡️ SudoDocs Script Studio")
    api_key = st.text_input("Gemini API Key", type="password")
    st.markdown("---")
    active_mode = st.radio(
        "Select Channel Logic:",
        ["Cinema Logic (Beyond Cinemas)", "Tech News Logic (Viral Tech Blog)", "Documentation Logic (SudoDocs-tv)"]
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
