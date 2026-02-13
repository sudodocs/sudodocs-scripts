import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SudoDocs: Script Studio",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clean, Dark Mode Aesthetic
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e6e6e6; }
    .stButton>button {
        background-color: #d93025; color: white; border-radius: 6px; height: 3em; font-weight: 600; border: none;
    }
    .stButton>button:hover { background-color: #b31412; }
    .stTextInput>div>div>input { background-color: #161b22; color: white; border: 1px solid #30363d; }
    .stTextArea>div>div>textarea { background-color: #161b22; color: white; border: 1px solid #30363d; font-family: sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND LOGIC ---

def run_deep_research(topic, mode, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # KEYS MUST MATCH SIDEBAR EXACTLY
    prompts = {
        "Movie/Series Review": f"""
        ACT AS: Senior Film Critic.
        TOPIC: {topic}
        RESEARCH TASKS:
        1. CONTEXT: Director's track record and the genre's current state.
        2. THEMES: The deeper philosophical or social questions the story asks.
        3. PRODUCTION: Any notable behind-the-scenes conflict or budget constraints?
        4. RECEPTION: General audience sentiment vs. critical consensus.
        OUTPUT: Concise research notes for an essay.
        """,
        
        "Tech & Docs (SudoDocs)": f"""
        ACT AS: Tech Educator & Journalist.
        TOPIC: {topic}
        RESEARCH TASKS:
        1. PAIN POINTS: Why do users struggle with this? (Root Cause).
        2. SOLUTION: The "Aha!" moment or fix.
        3. CONTEXT: Industry impact or "Docs-as-Code" relevance.
        OUTPUT: Technical context for an article.
        """
    }
    
    # Fallback to prevent KeyErrors
    prompt_text = prompts.get(mode, prompts["Movie/Series Review"])
    
    try:
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        return f"Research Error: {e}"

def generate_script_package(mode, title, research, notes, matrix_data, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')
    
    # KEYS MUST MATCH SIDEBAR EXACTLY
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
    
    # Fallback to prevent KeyErrors
    instruction_text = system_instructions.get(mode, system_instructions["Movie/Series Review"])
    
    prompt = f"""
    {instruction_text}
    
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

def render_matrix(mode):
    data = {}
    st.subheader("🎛️ Analysis Matrix")
    
    if mode == "Movie/Series Review":
        c1, c2 = st.columns(2)
        with c1:
            data['Thematic_Depth'] = st.select_slider("Thematic Depth", ["Superficial", "Standard", "Profound"], "Standard")
            data['Visual_Craft'] = st.select_slider("Visuals", ["Ugly/Generic", "Competent", "Masterpiece"], "Competent")
        with c2:
            data['Acting_Quality'] = st.select_slider("Performances", ["Wooden", "Serviceable", "Transformative"], "Serviceable")
            data['Verdict'] = st.selectbox("Final Verdict", ["Skip It", "Wait for Streaming", "Must Watch"])
            
    else: # Tech & Docs
        c1, c2 = st.columns(2)
        with c1:
            data['Complexity'] = st.select_slider("Topic Complexity", ["Beginner", "Intermediate", "Advanced"], "Intermediate")
            data['Urgency'] = st.select_slider("News Urgency", ["Evergreen Guide", "Trending Now", "Breaking News"], "Evergreen Guide")
        with c2:
            data['Tone'] = st.selectbox("Article Tone", ["Tutorial (Step-by-Step)", "Opinion/Rant", "Deep Dive Explanation"])
            
    return str(data)

# --- MAIN LAYOUT ---

with st.sidebar:
    st.title("🎬 SudoDocs Studio")
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    
    # THIS LIST MUST MATCH THE KEYS IN 'prompts' AND 'system_instructions'
    active_mode = st.radio(
        "Select Mode:", 
        ["Movie/Series Review", "Tech & Docs (SudoDocs)"]
    )

st.title(f"📝 {active_mode} Generator")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 1. Topic & Research")
    topic = st.text_input("Topic / Title")
    
    if st.button("🔍 Fetch Context"):
        if not api_key: st.error("Need API Key")
        else:
            with st.spinner("Researching..."):
                st.session_state['res'] = run_deep_research(topic, active_mode, api_key)
    
    if 'res' in st.session_state:
        st.info(st.session_state['res'])

    matrix_data = render_matrix(active_mode)

with col2:
    st.markdown("### 2. Your Take")
    notes = st.text_area("Brain Dump (Your raw thoughts/opinions):", height=200)
    
    if st.button("🚀 Write Article"):
        if not api_key or not topic: st.error("Missing Info")
        else:
            with st.spinner("Writing..."):
                script = generate_script_package(
                    active_mode, 
                    topic, 
                    st.session_state.get('res', ''), 
                    notes, 
                    matrix_data, 
                    api_key
                )
                st.session_state['final'] = script

if 'final' in st.session_state:
    st.divider()
    st.subheader("📦 Final Content Package")
    st.text_area("Copy-Paste Ready", value=st.session_state['final'], height=800)
    st.download_button("💾 Download", st.session_state['final'], file_name=f"{topic}_Article.txt")
