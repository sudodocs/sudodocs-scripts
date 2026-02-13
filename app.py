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
    
    # RE-ENGINEERED PROMPTS
    prompts = {
        "Cinema Logic (Realist-Industrial Critic)": f"""
        ACT AS: Cultural & Industrial Analyst (NOT just a film critic).
        TOPIC: {topic}
        
        EXECUTE "INDUSTRIAL BENCHMARKING":
        1. CORPORATE PARALLEL: Does the protagonist's struggle mirror a real-world business rise/fall (e.g., Nokia, Apple, Enron)?
        2. GEOPOLITICAL CONTEXT: If it's a spy/political thriller, how does it reflect current power dynamics?
        3. SYSTEMIC STRUGGLE: Identify the "System" the individual is fighting (e.g., The Exams, The Corporate Ladder, The Algorithm).
        4. VANTAGE POINTS: Whose perspective drives the narrative "Why"?
        
        OUTPUT: Strategic context for a "Realist-Industrial" review.
        """,
        
        "Tech News Logic (Viral Tech Blog)": f"""
        ACT AS: Senior Tech Journalist.
        TOPIC: {topic}
        EXECUTE ROOT CAUSE ANALYSIS: Immediate Symptom vs Systemic Issue, Technical Debt timeline, Industry Response.
        OUTPUT: Bullet points focused on 'Insider Insights'.
        """,
        
        "Documentation Logic (SudoDocs-tv)": f"""
        ACT AS: Developer Advocate / YouTube Educator.
        TOPIC: {topic}
        RESEARCH FOR ENGAGEMENT: Pain Points, "Aha!" Moments, Visual Assets, Real-World Use Cases.
        OUTPUT: Engagement hooks and analogies.
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
        # --- NEW "REALIST-INDUSTRIAL" PERSONA ---
        "Cinema Logic (Realist-Industrial Critic)": """
        ROLE: Realist-Industrial Critic.
        TONE: Skeptical of "content," reverent of "craft." Uses "Business Logic" to explain narrative failures.
        
        VOCABULARY RULES:
        - PRAISE: "Rare gem," "finesse," "second nature," "resilience," "vantage point."
        - CRITIQUE: "Marvel junk," "B-grade," "dull CGIs," "productized," "factory-made."
        
        NARRATIVE STRUCTURE (STRICT 5 ACTS):
        1. THE ANCHOR: Start with a personal anecdote or rhetorical question about the *theme* (not the movie).
        2. THE SETUP (BENCHMARKING): Compare the story to a corporate history (e.g., "Just like Nokia failed to adapt...").
        3. THE 'WHY': Explain the character's "Vantage Point." Focus on motivation, not plot points.
        4. THE CRITIQUE: Evaluate acting ("second nature") vs. technicals ("dull CGIs").
        5. THE VERDICT: A spoiler-free summary of the "Exhilarating" (or disappointing) experience.
        """,
        
        "Tech News Logic (Viral Tech Blog)": """
        ROLE: Systemic Tech Reporter.
        LOGIC: Root Cause Analysis. Explain WHY it happened, don't just report WHAT happened.
        """,
        
        "Documentation Logic (SudoDocs-tv)": """
        ROLE: Senior DevRel & Video Creator (Tone: Friendly, High-Energy).
        LOGIC: Teach using Analogies. Focus on [VISUAL CUES].
        """
    }
    
    # Metadata Formulas
    title_formulas = {
        "Cinema Logic (Realist-Industrial Critic)": "[Provocative Question] + [Topic] + [Industrial Verdict]",
        "Tech News Logic (Viral Tech Blog)": "[Topic] + [Causal Factor] + [Outcome]",
        "Documentation Logic (SudoDocs-tv)": "Stop Doing [Mistake] | How to Master [Topic] in [Time]"
    }

    prompt = f"""
    {system_instructions[mode]}
    
    INPUT DATA:
    - Topic: {title}
    - Research Context: {research}
    - Thematic Matrix: {matrix_data}
    - User Notes: "{notes}"
    
    TASK: Generate a 2026 Viral Content Package.
    
    ### 1. TITLES (3 Options)
    - Formula: {title_formulas[mode]}
    
    ### 2. DESCRIPTION
    - Hook + Keyword (first 125 chars).
    - Summary with "Key Takeaways".
    - Timestamp Outline.
    
    ### 3. VIDEO SCRIPT (Spoken Narration)
    - **STRICTLY FOLLOW THE 5-ACT STRUCTURE.**
    - Use the specific vocabulary (finesse, junk, resilience).
    - Compare the film's conflict to a Real-World Industry/Corporate struggle.
    - [VISUAL CUE] placeholders are mandatory.
    
    ### 4. METADATA
    - 15 Tags.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Generation Error: {e}"

# --- UI COMPONENTS ---

def render_technical_matrix(mode):
    st.subheader("🎛️ Strategic Matrix")
    data = {}
    
    if mode == "Cinema Logic (Realist-Industrial Critic)":
        # --- NEW "INDUSTRIAL" INPUTS ---
        c1, c2 = st.columns(2)
        with c1:
            data['Primary_Theme'] = st.selectbox(
                "Thematic Focus", 
                ["Resilience (Individual vs System)", "Corporate Strategy/Dynamics", "Geopolitical Fidelity", "Social Validation/Fame"]
            )
            data['Industry_Parallel'] = st.text_input(
                "Corporate/Historical Benchmark", 
                placeholder="e.g. Nokia's Fall, Apple's Rise, The 2008 Crash"
            )
        with c2:
            data['Tone_Bias'] = st.select_slider(
                "Critical Stance", 
                ["Cynical (Marvel Junk)", "Skeptical", "Balanced", "High-Praise (Rare Gem)"], 
                "Balanced"
            )
            data['Character_Depth'] = st.select_slider(
                "Performance Level", 
                ["Productized/Plastic", "Competent", "Second Nature (Transformative)"], 
                "Competent"
            )
            
    elif mode == "Tech News Logic (Viral Tech Blog)":
        c1, c2 = st.columns(2)
        with c1:
            data['Criticality'] = st.select_slider("Impact", ["Minor", "Major", "Critical"], "Major")
        with c2:
            data['Systemic_Stress'] = st.selectbox("Failure Type", ["Single Point", "Cascading", "Security"])

    elif mode == "Documentation Logic (SudoDocs-tv)":
        c1, c2 = st.columns(2)
        with c1:
            data['Visual_Density'] = st.select_slider("Visual Style", ["Talking Head", "Screen-Share Heavy"], "Screen-Share Heavy")
        with c2:
            data['Analogy'] = st.selectbox("Analogy", ["Lego", "Construction", "Traffic"])
            
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
