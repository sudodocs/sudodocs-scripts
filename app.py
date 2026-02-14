import streamlit as st
import google.generativeai as genai
import json
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Script Architect Pro",
    page_icon="✍️",
    layout="centered", 
)

# --- PROFESSIONAL LIGHT THEME CSS ---
st.markdown("""
    <style>
    :root {
        --primary: #2563eb;
        --bg-main: #f8fafc;
        --bg-card: #ffffff;
        --border: #e2e8f0;
        --text-main: #1e293b;
    }
    .stApp { background-color: var(--bg-main); color: var(--text-main); }
    
    /* Global Text visibility */
    p, span, label, .stMarkdown, h1, h2, h3 { color: var(--text-main) !important; }

    /* Input & Select Box Styling */
    .stTextInput input, .stTextArea textarea, [data-baseweb="select"] {
        background-color: white !important;
        border: 1px solid var(--border) !important;
        color: var(--text-main) !important;
    }

    /* Buttons */
    .stButton>button {
        background-color: var(--primary); color: white; border-radius: 8px; 
        height: 3.5em; font-weight: 600; width: 100%; border: none;
        transition: all 0.2s;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .stButton>button:hover { background-color: #1d4ed8; transform: translateY(-1px); }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: transparent;
        color: var(--text-main); font-weight: 600;
        border-bottom: 2px solid transparent;
    }
    .stTabs [aria-selected="true"] { color: var(--primary); border-bottom-color: var(--primary); }

    /* Analysis Result Cards */
    .metric-badge {
        background-color: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe;
        padding: 4px 12px; border-radius: 6px; font-weight: bold; font-size: 0.9em;
    }
    .report-card {
        background-color: white; padding: 24px; border-radius: 12px;
        border: 1px solid var(--border); margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND LOGIC ---

def call_gemini(api_key, prompt, system_instruction="", use_search=False):
    """Universal API caller with exponential backoff and grounding."""
    genai.configure(api_key=api_key)
    
    # Tool definition fix: using 'google_search' as requested by the 400 error
    tools = [{"google_search": {}}] if use_search else None
    
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=system_instruction,
        tools=tools
    )
    
    # Exponential backoff: 1s, 2s, 4s, 8s, 16s
    for delay in [1, 2, 4, 8, 16]:
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if delay == 16:
                return f"Error: {str(e)}"
            time.sleep(delay)

def perform_grounded_research(topic, mode, source_type, api_key):
    """Fetches factual context and real-world parallels."""
    if mode == "Film & Series Analysis":
        prompt = (
            f"Perform deep research on '{topic}' (Source Material: {source_type}). "
            "1. ADAPTATION: Identify fidelity vs creative liberties from the source. "
            "2. CHARACTER: Identify 'Ghost' (trauma), 'Lie' (belief), and 'Truth' (need) for main characters. "
            "3. REAL-WORLD: Search for current news or historical events mirroring the core themes of this movie. "
            "4. DATA: Fetch IMDb trivia and critic consensus."
        )
    elif mode == "Tech News & Investigative":
        prompt = (
            f"Root Cause Analysis on '{topic}'. "
            "1. IMPACT: Affected user stats and severity. "
            "2. THE GAP: Company PR vs community findings (Reddit/GitHub). "
            "3. MARKET: Stock or industry shifts."
        )
    else: # Educational Technology
        prompt = (
            f"Educational analysis for '{topic}'. "
            "1. PITFALLS: Common beginner mistakes. "
            "2. ARCHITECTURE: The 'Why' vs the 'How'. "
            "3. TRENDS: 2026 industry standards."
        )
    
    return call_gemini(api_key, prompt, "You are a factual Research Assistant with access to Google Search.", use_search=True)

def generate_script_package(mode, topic, research, notes, matrix, source_type, api_key):
    """Synthesizes all inputs into the final multi-pillar script JSON."""
    personas = {
        "Film & Series Analysis": "Master Film Scholar. Analyze character arcs (CACI) and Adaptation Worthiness (AFW). Connect themes to real-world news.",
        "Tech News & Investigative": "Investigative Tech Journalist. Use Root Cause Analysis (RCA) to bridge PR gaps.",
        "Educational Technology": "Technical Educator. Use the Feynman Technique to bridge knowledge gaps."
    }
    
    prompt = f"""
    TOPIC: {topic}
    SOURCE TYPE: {source_type}
    RESEARCH DATA: {research}
    CREATOR NOTES: {notes}
    SELECTED MATRIX: {matrix}
    
    TASK: Generate a viral, high-authority YouTube package in JSON.
    REQUIREMENTS:
    - Provide 'real_world_resonance' (connecting the story to actual news/history).
    - If Film: Provide 'character_matrix' (Ghost, Truth, Arc Score) and 'adaptation_report'.
    - Provide 'technical_report' (Script, Direction, Editing, Acting scores 0-10).
    - Provide 'script_outline' (Act 1, 2, 3) and 'hook_script'.
    
    FORMAT AS JSON:
    {{
        "viral_title": "String",
        "hook_script": "String",
        "thematic_resonance": {{ "real_world_event": "String", "explanation": "String" }},
        "character_matrix": [ {{ "name": "String", "role": "String", "arc_score": 0, "ghost_vs_truth": "String" }} ],
        "adaptation_report": {{ "fidelity_score": 0, "worthiness_score": 0, "justification": "String" }},
        "technical_report": {{ "script": 0, "direction": 0, "editing": 0, "acting": 0 }},
        "script_outline": ["Act 1", "Act 2", "Act 3"],
        "seo_metadata": {{ "description": "String", "tags": ["tag1", "tag2"] }}
    }}
    """
    
    result = call_gemini(api_key, prompt, personas.get(mode))
    try:
        clean = result.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return {"error": "Synthesis failed to return valid JSON.", "raw": result}

# --- APPLICATION UI ---

st.title("🚀 Script Architect Pro")
st.caption("Factual Research & Creative Synthesis Engine")

with st.sidebar:
    st.header("🔑 Setup")
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    active_mode = st.selectbox("Content Mode", ["Film & Series Analysis", "Tech News & Investigative", "Educational Technology"])
    
    source_type = "Original"
    if active_mode == "Film & Series Analysis":
        source_type = st.radio("Source Material", ["Original", "Book", "Comic", "True Event", "Remake"])
    
    st.divider()
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()

# Linear Workflow Tabs
tab1, tab2, tab3 = st.tabs(["1. Grounded Research", "2. Analysis Matrix", "3. Final Studio"])

# --- TAB 1: RESEARCH ---
with tab1:
    st.subheader("Step 1: Gather Context")
    topic = st.text_input("Topic or Title", placeholder="e.g., The Bear, Crowdstrike Outage, Rust Basics")
    
    if st.button("🔍 Execute Research Engine"):
        if not api_key: st.warning("Please provide an API Key.")
        elif not topic: st.warning("Please provide a topic.")
        else:
            with st.spinner("Accessing global databases & news archives..."):
                st.session_state['research'] = perform_grounded_research(topic, active_mode, source_type, api_key)

    if 'research' in st.session_state:
        st.info("### Research Intelligence Briefing")
        st.markdown(st.session_state['research'])
        st.success("Research loaded. Proceed to 'Analysis Matrix'.")

# --- TAB 2: MATRIX ---
with tab2:
    st.subheader("Step 2: Fine-Tune & Contextualize")
    
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    matrix_data = {}
    if active_mode == "Film & Series Analysis":
        c1, c2 = st.columns(2)
        with c1:
            matrix_data['Theory'] = st.select_slider("Film Theory Lens", ["Formalist", "Psychological", "Auteur", "Montage"])
            matrix_data['Visuals'] = st.select_slider("Visual Signature", ["Standard", "Stylized", "Iconic"])
        with c2:
            matrix_data['Fidelity'] = st.select_slider("Adaptation Fidelity", ["Loose", "Balanced", "Literal"])
            matrix_data['Tone'] = st.selectbox("Narrative Tone", ["Melancholic", "Frantic", "Academic", "Urgent"])
    elif active_mode == "Tech News & Investigative":
        matrix_data['Severity'] = st.select_slider("Criticality", ["Bug", "Outage", "Crisis"])
        matrix_data['Impact'] = st.select_slider("Scope", ["Niche", "Widespread", "Global"])
    else:
        matrix_data['Level'] = st.select_slider("Difficulty", ["Junior", "Senior", "Architect"])
        matrix_data['Method'] = st.select_slider("Pedagogy", ["Theory", "Mixed", "Practical"])
    st.markdown('</div>', unsafe_allow_html=True)

    user_notes = st.text_area("Your Perspective", placeholder="Add your unique angle or observations...", height=150)
    
    if st.button("🚀 Architect Final Package"):
        if 'research' not in st.session_state: st.error("Please run Step 1 (Research) first.")
        else:
            with st.spinner("Synthesizing script components..."):
                st.session_state['package'] = generate_script_package(active_mode, topic, st.session_state['research'], user_notes, str(matrix_data), source_type, api_key)

# --- TAB 3: OUTPUT ---
with tab3:
    if 'package' not in st.session_state:
        st.info("Complete Step 2 to view your final script suite.")
    else:
        p = st.session_state['package']
        if "error" in p: 
            st.error(p['error'])
            with st.expander("View Raw Output"):
                st.text(p.get('raw'))
        else:
            st.success(f"### {p.get('viral_title')}")
            
            st.markdown("#### 🌍 Thematic Resonance (Real-World Parallel)")
            tr = p.get('thematic_resonance', {})
            st.warning(f"**Analogous Event:** {tr.get('real_world_event')}")
            st.write(tr.get('explanation'))
            
            if active_mode == "Film & Series Analysis":
                st.markdown("#### 👥 Character Arc Index (CACI)")
                for char in p.get('character_matrix', []):
                    st.markdown(f"**{char['name']}** <span class='metric-badge'>{char['arc_score']}/10</span>", unsafe_allow_html=True)
                    st.caption(f"Role: {char['role']} | {char['ghost_vs_truth']}")

                st.markdown("#### 📚 Adaptation Worthiness (AFW)")
                ar = p.get('adaptation_report', {})
                col_a1, col_a2 = st.columns(2)
                col_a1.metric("Fidelity Score", f"{ar.get('fidelity_score')}/10")
                col_a2.metric("Liberty Justification", f"{ar.get('worthiness_score')}/10")
                st.caption(ar.get('justification'))

                st.markdown("#### 🏆 Technical Report Card")
                trc = p.get('technical_report', {})
                tc1, tc2, tc3, tc4 = st.columns(4)
                tc1.metric("Script", trc.get('script'))
                tc2.metric("Direction", trc.get('direction'))
                tc3.metric("Editing", trc.get('editing'))
                tc4.metric("Acting", trc.get('acting'))

            st.markdown("#### 🪝 The Hook")
            st.info(p.get('hook_script'))
            
            with st.expander("📜 Master Script Outline", expanded=True):
                for item in p.get('script_outline', []):
                    st.write(f"• {item}")
            
            st.markdown("#### 🔍 SEO Metadata")
            st.caption(p.get('seo_metadata', {}).get('description'))
            st.write(f"**Tags:** {', '.join(p.get('seo_metadata', {}).get('tags', []))}")

st.divider()
st.caption("Script Architect Pro v1.2 | Grounded Search Logic Fixed")
