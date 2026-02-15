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
        --text-secondary: #64748b;
    }
    
    .stApp { background-color: var(--bg-main); color: var(--text-main); }
    
    /* Global Text visibility */
    p, span, label, .stMarkdown, h1, h2, h3, .stMetric label { 
        color: var(--text-main) !important; 
    }
    
    .stCaption { color: var(--text-secondary) !important; }

    /* Input & Select Box Styling */
    .stTextInput input, .stTextArea textarea, [data-baseweb="select"], .stSelectbox div {
        background-color: white !important;
        border: 1px solid var(--border) !important;
        color: var(--text-main) !important;
    }

    /* Buttons */
    .stButton>button {
        background-color: var(--primary); color: white; border-radius: 8px; 
        height: 3.5em; font-weight: 600; width: 100%; border: none;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .stButton>button:hover { background-color: #1d4ed8; transform: translateY(-1px); }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid var(--border); }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: transparent;
        color: var(--text-secondary); font-weight: 600;
        border-bottom: 2px solid transparent;
    }
    .stTabs [aria-selected="true"] { 
        color: var(--primary) !important; 
        border-bottom-color: var(--primary) !important; 
    }

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
    
    /* Metrics Visibility */
    [data-testid="stMetricValue"] { color: var(--primary) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND LOGIC ---

import requests

def call_gemini(api_key, prompt, system_instruction="", use_search=False):
    """
    ✅ FIXED: Now properly enables Google Search grounding when use_search=True
    Uses REST API for better grounding support
    """
    if not use_search:
        # Use SDK for non-search queries
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_instruction,
        )
        for delay in [1, 2, 4, 8, 16]:
            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                if delay == 16:
                    return f"Error: {str(e)}"
                time.sleep(delay)
    else:
        # Use REST API with grounding for search queries
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        headers = {'Content-Type': 'application/json'}
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            },
            "tools": [{
                "googleSearch": {}
            }]
        }
        
        for delay in [1, 2, 4, 8, 16]:
            try:
                response = requests.post(url, headers=headers, json=data, timeout=60)
                response.raise_for_status()
                result = response.json()
                
                # Extract text from response
                if 'candidates' in result and len(result['candidates']) > 0:
                    parts = result['candidates'][0]['content']['parts']
                    text_parts = [part.get('text', '') for part in parts if 'text' in part]
                    return '\n'.join(text_parts)
                else:
                    return f"Error: Unexpected response format"
                    
            except requests.exceptions.RequestException as e:
                if delay == 16:
                    return f"Error: {str(e)}"
                time.sleep(delay)
            except Exception as e:
                if delay == 16:
                    return f"Error: {str(e)}"
                time.sleep(delay)
            
def perform_grounded_research(topic, mode, source_type, api_key):
    """Fetches factual context and real-world parallels using grounding."""
    if mode == "Film & Series Analysis":
        prompt = (
            f"Search the web for the most current and accurate information about '{topic}' (Original Material: {source_type}). "
            "IMPORTANT: Use real-time search results from IMDb, Rotten Tomatoes, and recent news articles. "
            "1. RELEASE INFO: When did this air/release? What is the actual release date and status? "
            "2. ADAPTATION: Identify fidelity vs creative liberties from the source material. "
            "3. CHARACTER: List the ACTUAL cast and characters from the show/film. For main characters, identify their 'Ghost' (trauma), 'Lie' (belief), and 'Truth' (need). "
            "4. REAL-WORLD: Find current news or historical events mirroring the core themes. "
            "5. DATA: Get IMDb rating, number of episodes/runtime, and critic consensus from review aggregators. "
            "Cite your sources with URLs."
        )
    elif mode == "Tech News & Investigative":
        prompt = (
            f"Search the web for the latest information on '{topic}'. "
            "1. IMPACT: Current affected user stats and severity level. "
            "2. THE GAP: Company official statements vs community findings on Reddit, GitHub, or X. "
            "3. MARKET: Recent stock fluctuations or industry-wide shifts. "
            "4. TIMELINE: When did this occur and what's the current status? "
            "Cite sources with URLs."
        )
    else: # Educational Technology
        prompt = (
            f"Search for current 2026 information about '{topic}'. "
            "1. PITFALLS: Common beginner mistakes documented in recent tutorials or Stack Overflow. "
            "2. ARCHITECTURE: Best practices and design patterns being used today. "
            "3. TRENDS: Latest industry standards, framework versions, and adoption rates. "
            "Cite sources with URLs."
        )
    
    return call_gemini(api_key, prompt, "You are a factual Research Assistant. Always search the web for current, accurate information and cite your sources.", use_search=True)

def generate_script_package(mode, topic, research, notes, matrix, source_type, api_key):
    """Synthesizes all inputs into the final multi-pillar script JSON."""
    personas = {
        "Film & Series Analysis": "Master Film Scholar. Provide deep character arc metrics (CACI), Adaptation worthiness (AFW), and technical scores.",
        "Tech News & Investigative": "Investigative Tech Journalist. Provide Root Cause Analysis (RCA) and industry impact metrics.",
        "Educational Technology": "Senior Technical Educator. Use the Feynman Technique to simplify complex logic."
    }
    
    prompt = f"""
    TOPIC: {topic}
    SOURCE TYPE: {source_type}
    RESEARCH DATA (Based on web search): {research}
    CREATOR NOTES: {notes}
    SELECTED MATRIX: {matrix}
    
    TASK: Generate a viral, high-authority YouTube package in JSON format.
    
    JSON SCHEMA REQUIREMENTS:
    - thematic_resonance: {{ "real_world_event": "String", "explanation": "Detailed parallel" }}
    - character_matrix: [ {{ "name": "Name", "role": "Main/Side", "arc_score": 0-10, "ghost_vs_truth": "String" }} ]
    - adaptation_report: {{ "fidelity_score": 0-10, "worthiness_score": 0-10, "justification": "Why liberties were/weren't worthy" }}
    - technical_report: {{ "script": 0-10, "direction": 0-10, "editing": 0-10, "acting": 0-10 }}
    - viral_title: "String", "hook_script": "String", "script_outline": ["Act 1", "Act 2", "Act 3"], "seo_metadata": {{ "description": "String", "tags": ["tag1", "tag2"] }}
    
    Use ONLY the information from the RESEARCH DATA which came from live web searches.
    """
    
    result = call_gemini(api_key, prompt, personas.get(mode))
    try:
        clean = result.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return {"error": "Synthesis failed to return valid JSON.", "raw": result}

# --- APPLICATION UI ---

st.title("🚀 Script Architect Pro")
st.caption("Content Synthesis Engine for High-Authority Media")

with st.sidebar:
    st.header("🔑 Authentication")
    api_key = st.text_input("Gemini API Key", type="password")
    
    if api_key:
        st.success("✓ API Key provided")
    else:
        st.warning("⚠️ API Key required")
    
    st.divider()
    active_mode = st.selectbox("Content Mode", ["Film & Series Analysis", "Tech News & Investigative", "Educational Technology"])
    
    source_type = "Original"
    if active_mode == "Film & Series Analysis":
        source_type = st.radio("Source Material", ["Original", "Book", "Comic", "True Event", "Remake"])
    
    st.divider()
    if st.button("Reset All Steps"):
        st.session_state.clear()
        st.rerun()

# Linear Workflow Tabs
tab1, tab2, tab3 = st.tabs(["1. Research & Grounding", "2. Analysis Matrix", "3. Final Studio"])

# --- TAB 1: RESEARCH ---
with tab1:
    st.subheader("Step 1: Intelligence Gathering")
    st.info("🌐 This step will search the web for real-time information from IMDb, news sites, and other authoritative sources.")
    
    topic = st.text_input("Topic or Title", placeholder="e.g., The Night Manager Season 2, Crowdstrike Outage, Rust vs C++")
    
    if st.button("🔍 Execute Research"):
        if not api_key: 
            st.warning("Please provide an API Key in the sidebar.")
        elif not topic: 
            st.warning("Please provide a topic.")
        else:
            with st.spinner("🌐 Searching the web for latest information..."):
                st.session_state['research'] = perform_grounded_research(topic, active_mode, source_type, api_key)
                st.session_state['topic'] = topic

    if 'research' in st.session_state:
        st.success("✅ Research Complete")
        st.info("### Research Briefing")
        st.markdown(st.session_state['research'])
        st.success("Context established. Proceed to the 'Analysis Matrix' tab.")

# --- TAB 2: MATRIX ---
with tab2:
    st.subheader("Step 2: Analysis Tuning")
    
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    matrix_data = {}
    if active_mode == "Film & Series Analysis":
        c1, c2 = st.columns(2)
        with c1:
            matrix_data['Theory'] = st.select_slider("Film Theory Focus", ["Formalist", "Psychological", "Auteur", "Montage"])
            matrix_data['Visuals'] = st.select_slider("Visual Signature", ["Standard", "Stylized", "Iconic"])
        with c2:
            matrix_data['Fidelity'] = st.select_slider("Adaptation Fidelity", ["Loose", "Balanced", "Literal"])
            matrix_data['Tone'] = st.selectbox("Narrative Tone", ["Melancholic", "Frantic", "Academic", "Urgent"])
    elif active_mode == "Tech News & Investigative":
        matrix_data['Severity'] = st.select_slider("Criticality", ["Bug", "Outage", "Crisis"])
        matrix_data['Scope'] = st.select_slider("User Impact", ["Niche", "Widespread", "Global"])
    else:
        matrix_data['Complexity'] = st.select_slider("Knowledge Level", ["Junior", "Senior", "Architect"])
        matrix_data['Method'] = st.select_slider("Pedagogical Style", ["Theory", "Mixed", "Practical"])
    st.markdown('</div>', unsafe_allow_html=True)

    user_notes = st.text_area("Your Unique Angle", placeholder="Add your unique observations or 'secret sauce' here...", height=150)
    
    if st.button("🚀 Architect Final Package"):
        if 'research' not in st.session_state: 
            st.error("Please run Step 1 (Research) first.")
        else:
            topic = st.session_state.get('topic', 'Unknown Topic')
            with st.spinner("Synthesizing script components..."):
                st.session_state['package'] = generate_script_package(active_mode, topic, st.session_state['research'], user_notes, str(matrix_data), source_type, api_key)

# --- TAB 3: OUTPUT ---
with tab3:
    if 'package' not in st.session_state:
        st.info("Complete Step 2 to generate the final script suite.")
    else:
        p = st.session_state['package']
        if "error" in p: 
            st.error(p['error'])
            with st.expander("View Details"): st.text(p.get('raw'))
        else:
            st.success(f"### {p.get('viral_title')}")
            
            # Thematic Resonance
            st.markdown("#### 🌍 Thematic Resonance")
            tr = p.get('thematic_resonance', {})
            st.warning(f"**Analogous Event:** {tr.get('real_world_event')}")
            st.write(tr.get('explanation'))
            
            if active_mode == "Film & Series Analysis":
                # Character Matrix
                st.markdown("#### 👥 Character Arc Index (CACI)")
                for char in p.get('character_matrix', []):
                    st.markdown(f"**{char['name']}** <span class='metric-badge'>{char['arc_score']}/10</span>", unsafe_allow_html=True)
                    st.caption(f"Role: {char['role']} | {char['ghost_vs_truth']}")

                # Adaptation Worthiness
                st.markdown("#### 📚 Adaptation Worthiness (AFW)")
                ar = p.get('adaptation_report', {})
                col_a1, col_a2 = st.columns(2)
                col_a1.metric("Fidelity Score", f"{ar.get('fidelity_score')}/10")
                col_a2.metric("Worthiness Score", f"{ar.get('worthiness_score')}/10")
                st.caption(ar.get('justification'))

                # Report Card
                st.markdown("#### 🏆 Technical Report Card")
                trc = p.get('technical_report', {})
                tc1, tc2, tc3, tc4 = st.columns(4)
                tc1.metric("Script", trc.get('script'))
                tc2.metric("Direction", trc.get('direction'))
                tc3.metric("Editing", trc.get('editing'))
                tc4.metric("Acting", trc.get('acting'))

            # Common Fields
            st.markdown("#### 🪝 The Hook")
            st.info(p.get('hook_script'))
            
            with st.expander("📜 Master Script Outline", expanded=True):
                for item in p.get('script_outline', []):
                    st.write(f"• {item}")
            
            st.markdown("#### 🏷️ Metadata")
            st.caption(p.get('seo_metadata', {}).get('description'))
            st.write(f"**Tags:** {', '.join(p.get('seo_metadata', {}).get('tags', []))}")

st.divider()
st.caption("Script Architect Pro v1.4 | ✅ Google Search Grounding FIXED")
