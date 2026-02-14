import streamlit as st
import google.generativeai as genai
import json
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SudoDocs: Master Script Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2026 PROFESSIONAL LIGHT UI ---
st.markdown("""
    <style>
    :root {
        --primary: #2563eb;
        --bg-main: #f8fafc;
        --bg-card: #ffffff;
        --border: #e2e8f0;
        --text-main: #1e293b;
        --text-sub: #64748b;
    }
    
    .stApp { background-color: var(--bg-main); color: var(--text-main); }
    
    /* Global Text Visibility */
    p, span, label, .stMarkdown, .stSelectbox label, .stSlider label {
        color: var(--text-main) !important;
    }

    /* Buttons */
    .stButton>button {
        background-color: var(--primary); color: white; border-radius: 8px; 
        height: 3.5em; font-weight: 600; border: none; width: 100%;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stButton>button:hover { background-color: #1d4ed8; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }

    /* Cards & Containers */
    .matrix-card {
        background-color: var(--bg-card); padding: 24px; border-radius: 12px;
        border: 1px solid var(--border); margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .metric-badge {
        background-color: #dbeafe; color: #1e40af; padding: 4px 12px; 
        border-radius: 20px; font-size: 0.85em; font-weight: bold;
    }

    /* Inputs */
    .stTextArea textarea, .stTextInput input {
        background-color: var(--bg-card) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border) !important;
    }
    
    /* Sidebar Fixes */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid var(--border);
    }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND LOGIC ---

def run_deep_research(topic, mode, source_type, api_key):
    """Deep Research using Gemini 2.5 Flash + Google Search Grounding."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        tools=[{"google_search": {}}]
    )
    
    if mode == "Cinema (Deep Analysis)":
        prompt = (
            f"Conduct a deep analytical research on '{topic}' (Source: {source_type}). "
            "1. ADAPTATION: Identify fidelity to the source material vs creative liberties taken. "
            "2. CHARACTER ARCS: Identify the 'Ghost' (trauma), 'Lie' (belief), and 'Truth' (need) for main and side characters. "
            "3. REAL-WORLD PARALLELS: Find current or historical news events that mirror the core theme of this story. "
            "4. TECHNICALS: Research director motifs (Auteur), cinematography styles, and editing rhythm. "
            "5. DATA: Fetch IMDb trivia, Rotten Tomatoes consensus, and Letterboxd keywords."
        )
    elif mode == "Tech News (Viral Blog)":
        prompt = (
            f"Perform Root Cause Analysis on '{topic}'. "
            "1. IMPACT: Find user percentage affected and technical criticality. "
            "2. THE GAP: Contrast official company PR statements with community findings on Reddit/GitHub. "
            "3. CONSEQUENCE: Research stock market reactions or industry-wide shifts."
        )
    else: # SudoDocs Educator
        prompt = (
            f"Educational gap analysis for '{topic}'. "
            "1. KNOWLEDGE GAP: What are the common beginner 'newbie traps' for this tool? "
            "2. MECHANISM: Explain the 'Why' (architecture) before the 'How' (syntax). "
            "3. TRENDS: Identify 2026 industry standards (Docs-as-Code)."
        )
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Research Engine Error: {e}"

def generate_script_package(mode, topic, research, notes, matrix_data, source_type, api_key):
    """Synthesizes all research into a structured script suite."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    system_instructions = {
        "Cinema (Deep Analysis)": f"""
        ROLE: Master Film Scholar. 
        TASK: Analyze character arcs (CACI), adaptation fidelity (AFW) from {source_type}, 
        and find real-world news parallels. Score Script, Direction, Editing, and Acting.
        """,
        "Tech News (Viral Blog)": "Investigative Tech Journalist. Focus on Root Cause Analysis and Impact.",
        "SudoDocs (Educational)": "Senior Technical Educator. Use Feynman Technique."
    }
    
    prompt = f"""
    {system_instructions.get(mode)}
    
    INPUT DATA:
    - Topic: {topic}
    - Research Background: {research}
    - User's Vision: "{notes}"
    - Matrix: {matrix_data}
    
    TASK: Generate a viral YouTube package in JSON.
    REQUIRED FIELDS:
    - viral_title, hook_script, script_outline, seo_metadata
    - character_analysis (list with name, role, arc_score, ghost_vs_truth)
    - thematic_resonance (real_world_event, explanation)
    - adaptation_report (fidelity_score, liberty_worthiness, justification)
    - technical_report_card (script, direction, editing, acting)
    """
    
    for delay in [1, 2, 4]:
        try:
            response = model.generate_content(prompt)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except:
            time.sleep(delay)
    return {"error": "Failed to synthesize package."}

# --- UI COMPONENTS ---

def render_matrix(mode):
    data = {}
    st.subheader("⚙️ Technical Matrix")
    st.markdown('<div class="matrix-card">', unsafe_allow_html=True)
    
    if mode == "Cinema (Deep Analysis)":
        c1, c2 = st.columns(2)
        with c1:
            data['Theory_Lens'] = st.select_slider("Film Theory Lens", ["Formalist", "Psychological", "Auteur", "Montage"])
            data['Visual_Style'] = st.select_slider("Visual Signature", ["Generic", "Stylish", "Iconic"])
        with c2:
            data['Fidelity'] = st.select_slider("Fidelity Target", ["Loose", "Moderate", "Literal"])
            data['Tone'] = st.selectbox("Narrative Tone", ["Melancholic", "Frantic", "Academic", "Satirical"])
            
    elif mode == "Tech News (Viral Blog)":
        c1, c2 = st.columns(2)
        with c1:
            data['Criticality'] = st.select_slider("Severity", ["Bug", "Outage", "Systemic Crisis"])
            data['Impact'] = st.select_slider("Scope", ["Niche", "Widespread", "Global"])
        with c2:
            data['Vibe'] = st.selectbox("Journalistic Tone", ["Whistleblower", "Analyst", "Helpful Insider"])

    else: # SudoDocs
        c1, c2 = st.columns(2)
        with c1:
            data['Level'] = st.select_slider("Concept Complexity", ["Junior", "Senior", "Architect"])
            data['Style'] = st.select_slider("Teaching Style", ["Theory-Heavy", "Balanced", "Hands-on"])
        with c2:
            data['Toolchain'] = st.selectbox("Domain Focus", ["Docs-as-Code", "API Architecture", "DevOps"])
            
    st.markdown('</div>', unsafe_allow_html=True)
    return str(data)

# --- MAIN LAYOUT ---

with st.sidebar:
    st.title("🎬 SudoDocs Studio")
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    
    active_mode = st.radio(
        "Persona Mode:", 
        ["Cinema (Deep Analysis)", "Tech News (Viral Blog)", "SudoDocs (Educational)"]
    )
    
    source_material = "N/A"
    if active_mode == "Cinema (Deep Analysis)":
        source_material = st.radio("Source Material:", ["Original", "Book", "Comic Book", "True Event", "Remake"])

    st.divider()
    st.caption("v5.1 | Master Engine Light")

st.title(f"🚀 {active_mode} Engine")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 1. Research & Inputs")
    topic = st.text_input("Title / Subject", placeholder="e.g., The Bear, Crowdstrike Outage, Sphinx Docs")
    
    if st.button("🔍 Step 1: Deep Research"):
        if not api_key: st.error("Need API Key")
        elif not topic: st.error("Enter a topic")
        else:
            with st.spinner("Analyzing Global Databases..."):
                st.session_state['res'] = run_deep_research(topic, active_mode, source_material, api_key)
    
    if 'res' in st.session_state:
        with st.expander("📝 Extracted Intelligence Brief", expanded=True):
            st.markdown(st.session_state['res'])

    matrix_data = render_matrix(active_mode)

with col2:
    st.markdown("### 2. Synthesis")
    notes = st.text_area("Your Unique Angle:", height=180, placeholder="The 'secret sauce' everyone misses...")
    
    if st.button("🚀 Step 2: Build Final Package"):
        if not api_key or not topic: st.error("Missing Info")
        else:
            with st.spinner("Architecting Viral Suite..."):
                pkg = generate_script_package(active_mode, topic, st.session_state.get('res', ''), notes, matrix_data, source_material, api_key)
                st.session_state['pkg'] = pkg

# --- OUTPUT DISPLAY ---

if 'pkg' in st.session_state:
    p = st.session_state['pkg']
    if "error" not in p:
        st.divider()
        st.subheader("📦 Generated Script Suite")
        
        st.success(f"**Viral Title:** {p.get('viral_title')}")
        
        o1, o2 = st.columns([1.2, 1])
        
        with o1:
            st.markdown("#### 🌍 Thematic Resonance")
            tr = p.get('thematic_resonance', {})
            st.warning(f"**Real-World Parallel:** {tr.get('real_world_event')}")
            st.write(tr.get('explanation'))
            
            with st.expander("📜 Script Flow & Hook", expanded=True):
                st.info(f"🪝 **Hook:** {p.get('hook_script')}")
                for step in p.get('script_outline', []):
                    st.write(f"🔹 {step}")

        with o2:
            if active_mode == "Cinema (Deep Analysis)":
                st.markdown("#### 🏆 Technical Report Card")
                trc = p.get('technical_report_card', {})
                tc1, tc2, tc3, tc4 = st.columns(4)
                tc1.metric("Script", f"{trc.get('script')}/10")
                tc2.metric("Directing", f"{trc.get('direction')}/10")
                tc3.metric("Editing", f"{trc.get('editing')}/10")
                tc4.metric("Acting", f"{trc.get('acting')}/10")

                st.markdown("#### 📚 Adaptation Report")
                ar = p.get('adaptation_report', {})
                ac1, ac2 = st.columns(2)
                ac1.metric("Fidelity", f"{ar.get('fidelity_score')}/10")
                ac2.metric("Liberty Worth", f"{ar.get('liberty_worthiness')}/10")
                st.caption(ar.get('justification'))

                st.markdown("#### 👥 Character Arc Matrix (CACI)")
                for c in p.get('character_analysis', []):
                    st.markdown(f"**{c['name']}** <span class='metric-badge'>{c['arc_score']}/10</span>", unsafe_allow_html=True)
                    st.caption(c['ghost_vs_truth'])
            
            st.markdown("#### 🔍 Metadata")
            st.caption(p.get('seo_metadata', {}).get('description'))
            st.write(f"**Tags:** {', '.join(p.get('seo_metadata', {}).get('tags', []))}")
    else:
        st.error("Failed to generate. Check your API Key or try again.")

st.divider()
st.caption("Master Engine v5.1 Light | SudoDocs & Beyond Cinemas")
