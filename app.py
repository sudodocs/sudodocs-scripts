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
    
    /* Input Visibility */
    p, span, label, .stMarkdown { color: var(--text-main) !important; }

    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: white !important;
        border: 1px solid var(--border) !important;
        color: var(--text-main) !important;
    }

    /* Buttons */
    .stButton>button {
        background-color: var(--primary); color: white; border-radius: 8px; 
        height: 3.5em; font-weight: 600; width: 100%; border: none;
        transition: all 0.2s;
    }
    .stButton>button:hover { background-color: #1d4ed8; }

    /* Tabs Customization */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: transparent;
        color: var(--text-main); font-weight: 600;
    }
    .stTabs [aria-selected="true"] { color: var(--primary); border-bottom-color: var(--primary); }

    /* Analytics UI */
    .metric-badge {
        background-color: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe;
        padding: 4px 12px; border-radius: 6px; font-weight: bold; font-size: 0.9em;
    }
    .report-card {
        background-color: white; padding: 20px; border-radius: 12px;
        border: 1px solid var(--border); margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND FUNCTIONS ---

def perform_grounded_research(topic, mode, source_type, api_key):
    """Fetches real-time context using Google Search grounding."""
    genai.configure(api_key=api_key)
    
    # Fix: The Python SDK uses "google_search_retrieval"
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        tools=[{"google_search_retrieval": {}}]
    )
    
    if mode == "Film & Series Analysis":
        prompt = (
            f"Deep research '{topic}' (Source Material: {source_type}). "
            "1. ADAPTATION: Identify fidelity vs creative liberties from the source. "
            "2. CHARACTER: Identify 'Ghost' (trauma), 'Lie' (belief), and 'Truth' (need) for main characters. "
            "3. REAL-WORLD: Find actual news or historical events mirroring the themes. "
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
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Research Error: {str(e)}"

def generate_script_package(mode, topic, research, notes, matrix, source_type, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    personas = {
        "Film & Series Analysis": "Master Film Scholar. Use Character Arc Index (CACI) and Adaptation Worthiness (AFW) logic.",
        "Tech News & Investigative": "Investigative Journalist. Use Root Cause Analysis (RCA).",
        "Educational Technology": "Technical Educator. Use Feynman Technique."
    }
    
    prompt = f"""
    {personas.get(mode)}
    TOPIC: {topic}
    SOURCE: {source_type}
    RESEARCH: {research}
    USER NOTES: {notes}
    MATRIX: {matrix}
    
    TASK: Generate a viral, high-authority YouTube package in JSON.
    FIELDS:
    - viral_title, hook_script, script_outline, 
    - character_matrix (list of name, role, arc_score, ghost_vs_truth),
    - thematic_resonance (real_world_event, explanation),
    - adaptation_report (fidelity_score, worthiness_score, justification),
    - technical_report (script, direction, editing, acting scores 0-10),
    - seo_metadata (description, tags).
    """
    
    for delay in [1, 2, 4]:
        try:
            response = model.generate_content(prompt)
            clean = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except:
            time.sleep(delay)
    return {"error": "Synthesis failed. Please try again."}

# --- APPLICATION FLOW ---

st.title("🚀 Script Architect Pro")
st.caption("Professional Content Synthesis Engine")

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

# Linear Flow via Tabs
tab1, tab2, tab3 = st.tabs(["1. Research & Context", "2. Analysis Matrix", "3. Final Script Studio"])

# --- TAB 1: RESEARCH ---
with tab1:
    st.subheader("Gather Intelligence")
    topic = st.text_input("Topic or Title", placeholder="e.g., Dune Part Two, Crowdstrike Outage, Rust Basics")
    
    if st.button("🔍 Run Grounded Research"):
        if not api_key: st.warning("Please enter an API key.")
        elif not topic: st.warning("Please enter a topic.")
        else:
            with st.spinner("Accessing global databases..."):
                st.session_state['research'] = perform_grounded_research(topic, active_mode, source_type, api_key)

    if 'research' in st.session_state:
        st.info("### Research Briefing")
        st.markdown(st.session_state['research'])
        st.success("Research complete! Proceed to Step 2.")

# --- TAB 2: MATRIX ---
with tab2:
    st.subheader("Fine-Tune Analysis")
    
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    matrix_data = {}
    if active_mode == "Film & Series Analysis":
        c1, c2 = st.columns(2)
        with c1:
            matrix_data['Theory'] = st.select_slider("Film Theory Lens", ["Formalist", "Psychological", "Auteur", "Montage"])
            matrix_data['Style'] = st.select_slider("Visual Depth", ["Standard", "Stylized", "Iconic"])
        with c2:
            matrix_data['Fidelity'] = st.select_slider("Adaptation Fidelity", ["Loose", "Balanced", "Literal"])
            matrix_data['Tone'] = st.selectbox("Narrative Tone", ["Melancholic", "Frantic", "Academic", "Urgent"])
    elif active_mode == "Tech News & Investigative":
        matrix_data['Criticality'] = st.select_slider("Severity", ["Bug", "Outage", "Crisis"])
        matrix_data['Scope'] = st.select_slider("User Impact", ["Niche", "Widespread", "Global"])
    else:
        matrix_data['Level'] = st.select_slider("Complexity", ["Junior", "Senior", "Architect"])
        matrix_data['Style'] = st.select_slider("Pedagogy", ["Theory", "Balanced", "Practice"])
    st.markdown('</div>', unsafe_allow_html=True)

    user_notes = st.text_area("Your Perspective", placeholder="Add your unique take here...", height=150)
    
    if st.button("🎨 Synthesize Full Package"):
        if 'research' not in st.session_state: st.error("Please run Step 1 first.")
        else:
            with st.spinner("Synthesizing analysis..."):
                st.session_state['package'] = generate_script_package(active_mode, topic, st.session_state['research'], user_notes, str(matrix_data), source_type, api_key)

# --- TAB 3: OUTPUT ---
with tab3:
    if 'package' not in st.session_state:
        st.info("Complete Step 2 to generate your script.")
    else:
        p = st.session_state['package']
        if "error" in p: st.error(p['error'])
        else:
            st.success(f"### {p.get('viral_title')}")
            
            st.markdown("#### 🌍 Thematic Resonance")
            tr = p.get('thematic_resonance', {})
            st.warning(f"**Parallel Event:** {tr.get('real_world_event')}")
            st.write(tr.get('explanation'))
            
            if active_mode == "Film & Series Analysis":
                st.markdown("#### 👥 Character Matrix (CACI)")
                for char in p.get('character_matrix', []):
                    st.markdown(f"**{char['name']}** <span class='metric-badge'>{char['arc_score']}/10</span>", unsafe_allow_html=True)
                    st.caption(char['ghost_vs_truth'])

                st.markdown("#### 📚 Adaptation Fidelity Report")
                ar = p.get('adaptation_report', {})
                col_a1, col_a2 = st.columns(2)
                col_a1.metric("Fidelity", f"{ar.get('fidelity_score')}/10")
                col_a2.metric("Worthiness", f"{ar.get('worthiness_score')}/10")
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
            
            st.markdown("#### 🔍 Metadata")
            st.caption(p.get('seo_metadata', {}).get('description'))
            st.write(f"**Tags:** {', '.join(p.get('seo_metadata', {}).get('tags', []))}")

st.divider()
st.caption("Script Architect Pro v1.1 | Fixed Search Logic")
