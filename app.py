import streamlit as st
import google.generativeai as genai
import json
import time
import asyncio
import edge_tts
import tempfile
import requests
import os
import urllib.parse

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

# --- AUDIO LOGIC (EDGE-TTS) ---

async def text_to_speech_edge(text, voice):
    """
    Generates high-quality neural voice audio using Edge-TTS.
    """
    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        await communicate.save(tmp_file.name)
        return tmp_file.name

def generate_audio_sync(text, voice):
    """
    Wrapper to run the async Edge-TTS function in Streamlit.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(text_to_speech_edge(text, voice))
    except Exception as e:
        st.error(f"Audio Generation Error: {e}")
        return None

# --- BACKEND LOGIC (GEMINI 2.5 FLASH) ---

def call_gemini(api_key, prompt, system_instruction="", use_search=False, is_json=False):
    if not use_search:
        genai.configure(api_key=api_key)
        gen_config = {"response_mime_type": "application/json"} if is_json else None
        
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_instruction,
            generation_config=gen_config
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
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "tools": [{"google_search": {}}] 
        }
        
        for delay in [1, 2, 4, 8, 16]:
            try:
                response = requests.post(url, headers=headers, json=data, timeout=60)
                response.raise_for_status()
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    parts = result['candidates'][0]['content']['parts']
                    text_parts = [part.get('text', '') for part in parts if 'text' in part]
                    return '\n'.join(text_parts)
                else:
                    return f"Error: Unexpected response format"
            except requests.exceptions.RequestException as e:
                if delay == 16:
                    return f"Error: {str(e)}\nResponse Content: {e.response.text if e.response else 'No response content'}"
                time.sleep(delay)
            except Exception as e:
                if delay == 16:
                    return f"Error: {str(e)}"
                time.sleep(delay)
            
def perform_grounded_research(topic, mode, source_type, api_key):
    if mode == "Film & Series Analysis":
        prompt = (
            f"Search the web for the most current and accurate information about '{topic}' (Original Material: {source_type}). "
            "1. RELEASE INFO: When did this air/release? What is the actual release date and status? "
            "2. CHARACTER & CAST: List the ACTUAL cast and characters. "
            "3. DATA: Get IMDb rating, number of episodes/runtime, and critic consensus. "
            "Gather factual context so I can verify gaps in my script later. Cite sources with URLs."
        )
    elif mode == "Tech News & Investigative":
        prompt = (
            f"Search the web for the latest information on '{topic}'. "
            "1. IMPACT: Current affected user stats and severity level. "
            "2. TIMELINE: When did this occur and what's the current status? "
            "Gather factual context to support an investigative script. Cite sources with URLs."
        )
    else: 
        prompt = (
            f"Search for current 2026 information about '{topic}'. "
            "1. ARCHITECTURE: Best practices and design patterns being used today. "
            "2. TRENDS: Latest industry standards, framework versions, and adoption rates. "
            "Gather factual context to verify educational content. Cite sources with URLs."
        )
    return call_gemini(api_key, prompt, "You are a factual Research Assistant. Always search the web for current, accurate information.", use_search=True)

def generate_script_package(mode, topic, research, notes, matrix, source_type, api_key):
    personas = {
        "Film & Series Analysis": "Master YouTube Film Critic. Focus on narrative, character arcs, and thematic depth.",
        "Tech News & Investigative": "Investigative Tech YouTuber. Focus on clarity, impact, and engaging storytelling.",
        "Educational Technology": "Senior Developer turned YouTuber. Explain things naturally, like a mentor talking to a junior."
    }
    
    prompt = f"""
    TOPIC: {topic}
    SOURCE TYPE: {source_type}
    CREATOR'S DRAFT / UNIQUE ANGLE: {notes}
    SELECTED MATRIX: {matrix}
    BACKGROUND RESEARCH: {research}
    
    TASK: You are a professional, conversational YouTube scriptwriter. Your goal is to refine the "CREATOR'S DRAFT" into a highly engaging, human-sounding script ready for voiceover.
    
    CRITICAL INSTRUCTIONS:
    1. HUMAN TONE: The script MUST sound like a real person talking to a camera. Use conversational phrasing, rhetorical questions, and natural transitions. AVOID robotic listicles, stiff academic phrasing, or generic AI structures.
    2. ANGLE-FIRST REFINEMENT: Your primary job is to expand and polish the text provided in the "CREATOR'S DRAFT". Preserve the creator's unique perspective and voice.
    3. STRATEGIC GAP-FILLING: Look at the "BACKGROUND RESEARCH". ONLY pull facts from this research to fill in missing details or to factually support the points the creator made in their draft. Do NOT dump all the research into the script. If a research point doesn't serve the creator's angle, completely ignore it.
    4. ALIGNMENT: Match the tone indicated in the "SELECTED MATRIX".
    5. ESCAPE CHARACTERS: Ensure ALL double quotes inside your script text are properly escaped (e.g., \\"Like this\\") so the JSON remains completely valid.
    
    JSON SCHEMA REQUIREMENTS:
    {{
      "thematic_resonance": {{ "real_world_event": "String", "explanation": "Detailed parallel based on angle" }},
      "character_matrix": [ {{ "name": "Name", "role": "Main/Side", "arc_score": 0, "ghost_vs_truth": "String" }} ],
      "technical_report": {{ "script": 0, "direction": 0, "editing": 0, "acting": 0 }},
      "viral_title": "String (Catchy YouTube Title)",
      "hook_script": "String (A punchy, conversational opening hook)",
      "full_script": {{ 
          "intro": "Conversational intro flowing from the hook.",
          "act1": "Conversational Act 1 (Refining the creator's angle).",
          "act2": "Conversational Act 2 (Adding factual support to the angle).",
          "act3": "Conversational Act 3 (Climax of the analysis).",
          "outro": "Natural conclusion and call-to-action."
      }},
      "script_outline": ["Brief point 1", "Brief point 2", "Brief point 3"],
      "seo_metadata": {{ "description": "String", "tags": ["tag1", "tag2"] }}
    }}
    """
    
    result = call_gemini(api_key, prompt, personas.get(mode), is_json=True)
    
    try:
        clean = result.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception as e:
        return {"error": f"Synthesis failed to return valid JSON. Error: {str(e)}", "raw": result}

def generate_youtube_bundle(api_key, script_text):
    """Generates the YouTube metadata and thumbnail prompt based on the final script."""
    prompt = f"""
    Analyze the following YouTube script and create a complete SEO and packaging bundle.
    
    SCRIPT:
    {script_text}
    
    JSON SCHEMA REQUIREMENTS:
    {{
        "viral_title": "String (A high-CTR, emotional, and catchy YouTube title)",
        "description": "String (A full YouTube description including a hook, summary, and placeholder for social links)",
        "tags": ["tag1", "tag2", "tag3", "etc (Generate 15 highly relevant SEO tags)"],
        "hashtags": ["#tag1", "#tag2", "#tag3 (Generate 3-5 highly relevant hashtags)"],
        "thumbnail_prompt": "String (A highly detailed, visual prompt for an AI image generator to create a catchy, high-contrast, professional YouTube thumbnail. Specify lighting, subjects, and mood.)"
    }}
    """
    result = call_gemini(api_key, prompt, "You are a master YouTube strategist and SEO expert.", is_json=True)
    try:
        clean = result.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception as e:
        return {"error": f"Failed to generate bundle. Error: {str(e)}", "raw": result}

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
    if st.button("Reset All Steps"):
        st.session_state.clear()
        st.rerun()

# --- 5 LINEAR WORKFLOW TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Research", 
    "2. Analysis", 
    "3. Script", 
    "4. Voiceover",
    "5. Content Bundle"
])

# --- TAB 1: RESEARCH ---
with tab1:
    st.subheader("Step 1: Intelligence Gathering")
    st.info("🌐 Gather background facts to act as a factual safety net for your script.")
    
    topic = st.text_input("Topic or Title", placeholder="e.g., The Night Manager Season 2, Crowdstrike Outage")
    
    current_mode = st.session_state.get("active_mode_key", "Film & Series Analysis")
    current_source = st.session_state.get("source_type_key", "Original")
    
    if st.button("🔍 Execute Background Research"):
        if not api_key: 
            st.warning("Please provide an API Key in the sidebar.")
        elif not topic: 
            st.warning("Please provide a topic.")
        else:
            with st.spinner("🌐 Gathering background facts from the web..."):
                st.session_state['research'] = perform_grounded_research(topic, current_mode, current_source, api_key)
                st.session_state['topic'] = topic

    if 'research' in st.session_state:
        st.success("✅ Background Research Complete")
        with st.expander("View Factual Briefing", expanded=False):
            st.markdown(st.session_state['research'])
        st.success("🎉 **Step 1 Complete!** Please click the **'2. Analysis Matrix'** tab above to add your unique angle.")

# --- TAB 2: MATRIX ---
with tab2:
    st.subheader("Step 2: Core Concept & Tuning")
    
    active_mode = st.selectbox("Content Mode", 
                               ["Film & Series Analysis", "Tech News & Investigative", "Educational Technology"],
                               key="active_mode_key")
    
    source_type = "Original"
    if active_mode == "Film & Series Analysis":
        source_type = st.radio("Source Material", 
                               ["Original", "Book", "Comic", "True Event", "Remake"],
                               key="source_type_key")
        
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    matrix_data = {}
    if active_mode == "Film & Series Analysis":
        c1, c2 = st.columns(2)
        with c1:
            matrix_data['Theory'] = st.select_slider("Film Theory Focus", ["Formalist", "Psychological", "Auteur", "Montage"])
            matrix_data['Visuals'] = st.select_slider("Visual Signature", ["Standard", "Stylized", "Iconic"])
        with c2:
            matrix_data['Fidelity'] = st.select_slider("Adaptation Fidelity", ["Loose", "Balanced", "Literal"])
            matrix_data['Tone'] = st.selectbox("Narrative Tone", ["Conversational", "Melancholic", "Frantic", "Academic"])
    elif active_mode == "Tech News & Investigative":
        matrix_data['Severity'] = st.select_slider("Criticality", ["Bug", "Outage", "Crisis"])
        matrix_data['Scope'] = st.select_slider("User Impact", ["Niche", "Widespread", "Global"])
    else:
        matrix_data['Complexity'] = st.select_slider("Knowledge Level", ["Junior", "Senior", "Architect"])
        matrix_data['Method'] = st.select_slider("Pedagogical Style", ["Theory", "Mixed", "Practical"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### ✍️ Your Unique Angle (Draft)")
    st.info("The AI will focus on refining YOUR draft into a conversational script. It will only use the research from Step 1 to fill in factual gaps.")
    
    angle_file = st.file_uploader("Upload your rough draft or notes (.txt)", type=["txt"])
    angle_text = st.text_area("Or type your angle/rough draft here:", height=150, placeholder="E.g., I think the main character's arc was ruined in episode 4 because...")
    
    if st.button("🚀 Architect Refined Script"):
        if 'research' not in st.session_state: 
            st.error("Please run Step 1 (Research) first to gather background facts.")
        else:
            final_angle = ""
            if angle_text.strip():
                final_angle = angle_text
            elif angle_file is not None:
                final_angle = angle_file.getvalue().decode("utf-8")
                
            if not final_angle:
                st.error("⚠️ Please provide your Unique Angle (either type it or upload a text file) so the AI has a foundation to refine.")
            else:
                topic = st.session_state.get('topic', 'Unknown Topic')
                with st.spinner("Synthesizing and refining your conversational script..."):
                    st.session_state['package'] = generate_script_package(
                        active_mode, topic, st.session_state['research'], final_angle, str(matrix_data), source_type, api_key
                    )
                    st.success("🎉 **Step 2 Complete!** Your script has been refined. Please click the **'3. Script'** tab.")

# --- TAB 3: GENERATED SCRIPT ---
with tab3:
    st.subheader("Step 3: Script Review & Editing")
    if 'package' not in st.session_state:
        st.info("Complete Step 2 to generate the final script suite.")
    else:
        p = st.session_state['package']
        if "error" in p: 
            st.error(p['error'])
            with st.expander("View Raw Output (For Debugging)"): st.text(p.get('raw'))
        else:
            st.success(f"### {p.get('viral_title')}")
            
            with st.expander("📊 View Script Architecture Details", expanded=False):
                st.markdown("#### 🌍 Thematic Resonance")
                st.warning(f"**Analogous Event:** {p.get('thematic_resonance', {}).get('real_world_event')}")
                st.write(p.get('thematic_resonance', {}).get('explanation'))
                
                if active_mode == "Film & Series Analysis":
                    for char in p.get('character_matrix', []):
                        st.markdown(f"**{char['name']}** <span class='metric-badge'>{char['arc_score']}/10</span>", unsafe_allow_html=True)

            st.markdown("### 📝 Conversational Script Editor")
            st.info("💡 Edit the text below exactly as you want it spoken. Add commas or dashes (---) to force natural pauses for the voiceover. Your edits are automatically saved.")
            
            full_script = p.get('full_script', {})
            
            default_script_text = f"{p.get('hook_script', '')}\n\n"
            default_script_text += f"{full_script.get('intro', '')}\n\n"
            default_script_text += f"{full_script.get('act1', '')}\n\n"
            default_script_text += f"{full_script.get('act2', '')}\n\n"
            default_script_text += f"{full_script.get('act3', '')}\n\n"
            default_script_text += f"{full_script.get('outro', '')}"
            
            st.session_state['final_script_text'] = st.text_area("Final Polish:", value=default_script_text.strip(), height=400)
            
            st.download_button(
                label="📥 Download Text Script",
                data=st.session_state['final_script_text'],
                file_name=f"{p.get('viral_title', 'script').replace(' ', '_').lower()}.txt",
                mime="text/plain"
            )
            
            st.success("🎉 **Step 3 Complete!** Once you are happy with the pacing, click the **'4. Voiceover'** tab.")

# --- TAB 4: GENERATE VOICEOVER ---
with tab4:
    st.subheader("Step 4: AI Voiceover Studio")
    st.info("Turn your finalized script or a custom uploaded file into professional audio.")

    st.markdown("### 🎙️ Voice Settings")
    voice_option = st.selectbox("Select Narrator (US English)", [
        ("en-US-ChristopherNeural", "Christopher (Male - Deep/Professional)"),
        ("en-US-GuyNeural", "Guy (Male - Natural/Conversational)"),
        ("en-US-EricNeural", "Eric (Male - Casual)"),
        ("en-US-RogerNeural", "Roger (Male - Confident)"),
        ("en-US-SteffanNeural", "Steffan (Male - Expressive)"),
        ("en-US-AndrewNeural", "Andrew (Male - Warm)"),
        ("en-US-BrianNeural", "Brian (Male - Crisp/News)"),
        ("en-US-AriaNeural", "Aria (Female - Clear)"),
        ("en-US-JennyNeural", "Jenny (Female - Conversational)"),
        ("en-US-MichelleNeural", "Michelle (Female - Bright)"),
        ("en-US-EmmaNeural", "Emma (Female - Friendly)"),
        ("en-US-AvaNeural", "Ava (Female - Engaging)")
    ], format_func=lambda x: x[1])

    st.markdown("---")

    source_mode = st.radio("Choose Text Source for Voiceover:", ["Use Generated Script (from Tab 3)", "Upload Custom Text File (.txt)"])
    
    text_to_synthesize = ""
    
    if source_mode == "Use Generated Script (from Tab 3)":
        text_to_synthesize = st.session_state.get('final_script_text', '')
        if not text_to_synthesize:
            st.warning("⚠️ No generated script found. Please complete Steps 1-3 first, or select 'Upload Custom Text File'.")
    else:
        uploaded_file = st.file_uploader("Upload a .txt file for Voiceover", type=["txt"], key="voice_upload")
        if uploaded_file is not None:
            text_to_synthesize = uploaded_file.getvalue().decode("utf-8")
            st.success("File uploaded successfully!")

    st.markdown("---")
    st.markdown("### Preview Text for Audio Generation")
    
    st.session_state['tab4_audio_text'] = st.text_area("This exact text will be sent to the AI Voice:", value=text_to_synthesize, height=250)

    if st.button("🔊 Generate Voiceover"):
        if not st.session_state['tab4_audio_text'].strip():
            st.error("Text box is empty. Please provide text to generate audio.")
        else:
            with st.spinner(f"Synthesizing audio with {voice_option[1]} (this may take 10-20 seconds)..."):
                selected_voice = voice_option[0] 
                audio_file_path = generate_audio_sync(st.session_state['tab4_audio_text'], selected_voice)
                
                if audio_file_path:
                    st.success("✅ Audio generated successfully!")
                    st.audio(audio_file_path, format='audio/mp3')
                    
                    with open(audio_file_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Audio File (.mp3)",
                            data=file,
                            file_name="professional_voiceover.mp3",
                            mime="audio/mp3"
                        )
                else:
                    st.error("Failed to generate audio. Please check your internet connection and try again.")
            
            st.success("🎉 **Step 4 Complete!** Ready to finalize? Click the **'5. Content Bundle'** tab to generate your SEO metadata and thumbnail.")

# --- TAB 5: CONTENT BUNDLE ---
with tab5:
    st.subheader("Step 5: YouTube Content Bundle")
    st.info("Package your final script with a viral title, SEO description, and an AI-generated thumbnail.")
    
    bundle_source_choice = st.radio("Select the script text to use as the foundation for your bundle:", 
                                    ["Use 'Generated Script' (from Tab 3)", "Use 'Final Audio Text' (from Tab 4)"])
    
    if st.button("📦 Generate Content Bundle"):
        target_text = ""
        if bundle_source_choice == "Use 'Generated Script' (from Tab 3)":
            target_text = st.session_state.get('final_script_text', '')
        else:
            target_text = st.session_state.get('tab4_audio_text', '')
            
        if not api_key:
            st.error("⚠️ API Key required. Please add it to the sidebar.")
        elif not target_text.strip():
            st.error("⚠️ Target text is empty. Please ensure you have generated or uploaded a script in the previous tabs.")
        else:
            with st.spinner("Analyzing script and generating YouTube metadata..."):
                st.session_state['yt_bundle'] = generate_youtube_bundle(api_key, target_text)
                
    if 'yt_bundle' in st.session_state:
        bundle = st.session_state['yt_bundle']
        if "error" in bundle:
            st.error(bundle['error'])
        else:
            st.success("✅ YouTube Bundle Generated!")
            
            # Text Metadata Section
            st.markdown("### 📝 YouTube Metadata")
            st.text_input("**Viral Title**", value=bundle.get('viral_title', ''))
            st.text_area("**Description**", value=bundle.get('description', ''), height=200)
            
            col_tags, col_hashes = st.columns(2)
            with col_tags:
                st.text_area("**Tags** (Comma separated)", value=", ".join(bundle.get('tags', [])), height=100)
            with col_hashes:
                st.text_area("**Hashtags**", value=" ".join(bundle.get('hashtags', [])), height=100)
            
            # Thumbnail Generation Section
            st.markdown("---")
            st.markdown("### 🎨 AI Thumbnail Studio")
            st.caption("Review the visual prompt below, tweak it if needed, and hit Generate to create your free thumbnail using Pollinations AI.")
            
            thumbnail_prompt = st.text_area("Image Prompt:", value=bundle.get('thumbnail_prompt', ''), height=100)
            
            if st.button("🖼️ Generate Thumbnail"):
                if not thumbnail_prompt:
                    st.warning("Please provide an image prompt.")
                else:
                    with st.spinner("Rendering your thumbnail..."):
                        # ✅ FIXED: Truncate prompt to prevent "URI Too Long" and added a User-Agent
                        safe_prompt = thumbnail_prompt[:800] 
                        encoded_prompt = urllib.parse.quote(safe_prompt)
                        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true"
                        
                        try:
                            # Setting a User-Agent so the API doesn't block the request
                            headers = {
                                "User-Agent": "ScriptArchitectPro/1.0 (Streamlit Application)"
                            }
                            
                            image_response = requests.get(image_url, headers=headers, timeout=30)
                            
                            if image_response.status_code == 200:
                                st.image(image_response.content, use_container_width=True, caption="Generated Thumbnail")
                                
                                st.download_button(
                                    label="📥 Download Thumbnail (.jpg)",
                                    data=image_response.content,
                                    file_name="youtube_thumbnail.jpg",
                                    mime="image/jpeg"
                                )
                            else:
                                # Provide specific error details for debugging
                                st.error(f"Failed to generate image. Server returned status code: {image_response.status_code}")
                                with st.expander("Show Server Response Details"):
                                    st.write(image_response.text)
                        except Exception as e:
                            st.error(f"Error fetching image: {e}")

st.divider()
st.caption("Script Architect Pro v4.1 | Fixes: Pollinations API Headers + Payload Sizes")
