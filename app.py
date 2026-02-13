import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIG & THEME ---
st.set_page_config(
    page_title="SudoDocs | Script Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a modern look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #e50914;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ff0a16;
        border: none;
    }
    .stTextArea textarea {
        border-radius: 10px;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    div[data-testid="stExpander"] {
        border: none;
        background-color: #1a1c24;
        border-radius: 10px;
    }
    </style>
    """, unsafe_content_label=True)

# --- BACKEND LOGIC ---

def fetch_movie_context(title, api_key):
    if not title: return None
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Act as a professional cinema historian. Research the movie/series: "{title}".
    Provide a structured summary:
    - Director's name and 2 significant past works.
    - Top 3 Cast members and their recent career trajectory.
    - Music Director and their signature style.
    - Release Year, Genre, and specific cinematic 'vibe' (e.g., Neo-noir, maximalist).
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Research Error: {e}"

def generate_script(title, duration, context, ratings, notes, api_key):
    genai.configure(api_key=api_key)
    # Using Pro for the high-quality narrative writing
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = f"""
    You are the writer for 'Beyond Cinemas'. 
    Persona: Male, early 40s, highly analytical, film-literate, critical but fair.
    Context: {context}
    Ratings: {ratings}
    User Notes: {notes}
    
    Format: {duration} Review for {title}.
    Structure the script with:
    1. A provocative Hook.
    2. Deep analysis of the technicals (Direction, Cinematography) based on the ratings.
    3. Integration of the User Notes.
    4. A final 'Beyond Cinemas' verdict.
    
    Spoken narration ONLY. No stage directions.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Scripting Error: {e}"

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/clapperboard.png", width=80)
    st.title("Studio Settings")
    api_key = st.text_input("Gemini API Key", type="password", help="Get your key from Google AI Studio")
    
    st.divider()
    st.markdown("### 📽️ Channel Voice")
    st.caption("Current Persona: Analytical / 40s Male")
    
    st.divider()
    st.info("💡 **Tip:** Use the 'Research' button first to give the AI context about the director's history.")

# --- MAIN UI ---
st.title("🎬 SudoDocs: Script Studio")
st.caption("Refining raw movie thoughts into professional cinema analysis.")

# Layout: Grid System
tab_input, tab_output = st.tabs(["🏗️ Build Review", "📜 Final Script"])

with tab_input:
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("1. Setup & Research")
        title = st.text_input("Movie/Series Title", placeholder="Enter title...")
        v_format = st.select_slider("Review Depth", options=["Shorts", "Standard Review", "Deep Dive Analysis"], value="Standard Review")
        
        if st.button("🔍 Run AI Research"):
            if not api_key: st.error("Please provide an API Key.")
            else:
                with st.spinner("Analyzing filmography..."):
                    st.session_state['research'] = fetch_movie_context(title, api_key)
        
        if 'research' in st.session_state:
            with st.expander("View Research Data", expanded=True):
                st.write(st.session_state['research'])

    with col2:
        st.subheader("2. Technical Scorecard")
        st.write("Rate the filmmaking aspects:")
        
        score_opts = ["Poor", "Bad", "Average", "Good", "Outstanding", "Unique"]
        
        c1, c2 = st.columns(2)
        with c1:
            r_dir = st.select_slider("Direction", options=score_opts, value="Good")
            r_vis = st.select_slider("Visuals", options=score_opts, value="Good")
            r_act = st.select_slider("Acting", options=score_opts, value="Good")
        with c2:
            r_pace = st.select_slider("Pacing", options=score_opts, value="Average")
            r_sound = st.select_slider("Soundtrack", options=score_opts, value="Good")
            r_scr = st.select_slider("Screenplay", options=score_opts, value="Average")
            
        ratings_summary = f"Dir: {r_dir}, Act: {r_act}, Vis: {r_vis}, Pace: {r_pace}, Sound: {r_sound}, Script: {r_scr}"

    st.divider()
    st.subheader("3. Personal Brain Dump")
    notes = st.text_area("Your raw thoughts, scene specifics, and 'Beyond Cinemas' flavor:", height=150, placeholder="Example: The cinematography in the desert scenes reminded me of Lawrence of Arabia. RDJ's performance felt a bit forced in the second act...")

    if st.button("🚀 Generate Professional Script"):
        if not api_key or not title or not notes:
            st.error("Missing required fields (Key, Title, or Notes).")
        else:
            with st.spinner("Synthesizing analysis..."):
                final_text = generate_script(title, v_format, st.session_state.get('research',''), ratings_summary, notes, api_key)
                st.session_state['final_script'] = final_text
                st.toast("Script Generated!", icon="✅")

with tab_output:
    if 'final_script' in st.session_state:
        st.subheader(f"Final Script for: {title}")
        st.markdown("---")
        st.write(st.session_state['final_script'])
        st.markdown("---")
        st.download_button("📂 Download Script (.txt)", st.session_state['final_script'], file_name=f"{title}_script.txt")
    else:
        st.warning("Please generate a script in the 'Build Review' tab first.")
