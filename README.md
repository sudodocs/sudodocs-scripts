# 🚀 Script Architect Pro

**Script Architect Pro** is an AI-powered content synthesis engine designed for high-authority YouTube creators. It leverages **Google's Gemini 2.5 Flash** model for real-time grounded research and **Edge-TTS** for professional neural voiceovers.

This tool transforms a simple topic into a fully researched, structured, and narrated script package suitable for Film Analysis, Tech Journalism, or Educational content.

## ✨ Key Features

* **🌐 Grounded Research:** Uses Gemini's web search capabilities to fetch real-time data from IMDb, Rotten Tomatoes, GitHub, and news sources (no hallucinations).
* **🧠 Multi-Mode Analysis:**
    * **Film & Series:** Deep character arcs, adaptation fidelity, and film theory.
    * **Tech Investigative:** Root cause analysis, market impact, and timeline tracking.
    * **EdTech:** Feynman technique simplification and industry trends.
* **🎛️ Tunable Matrix:** Customize the tone, complexity, visual signature, and adaptation fidelity before generation.
* **📝 Full Script Generation:** Generates complete narration (Intro, Acts 1-3, Outro, Hook) optimized for retention.
* **🎙️ Neural Voiceover:** Integrated **Edge-TTS** (Microsoft Azure Neural Voices) to generate high-quality audio narration directly within the app—free of charge.
* **📂 Export Ready:** Download full scripts as `.txt` and voiceovers as `.mp3`.

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **AI Engine:** [Google Gemini 2.5 Flash](https://ai.google.dev/) (via `google-generativeai` SDK & REST API)
* **Audio Engine:** [Edge-TTS](https://github.com/rany2/edge-tts) (Python wrapper for Microsoft Edge Read Aloud)
* **Async Processing:** Python `asyncio`

## ⚙️ Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/yourusername/script-architect-pro.git](https://github.com/yourusername/script-architect-pro.git)
    cd script-architect-pro
    ```

2.  **Create a Virtual Environment (Optional but Recommended)**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Usage

1.  **Get an API Key:**
    * Go to [Google AI Studio](https://aistudio.google.com/).
    * Create a free API key.

2.  **Run the Application:**
    ```bash
    streamlit run app.py
    ```

3.  **Workflow:**
    * **Sidebar:** Enter your API Key and select your Content Mode (e.g., Film Analysis).
    * **Tab 1 (Research):** Enter a topic (e.g., "The Matrix"). The AI will search the web for factual data.
    * **Tab 2 (Matrix):** Adjust sliders for Tone, Fidelity, and Complexity. Add your unique notes.
    * **Tab 3 (Studio):** View the generated script. Click **"Generate Audio"** to hear the neural voiceover.

## 📦 Requirements

Create a `requirements.txt` file with the following contents:

```text
streamlit
google-generativeai
edge-tts
requests
```

## 🎙️ Available Voices

The application currently supports the following Neural voices:

- Christopher (US Male - Deep/Professional)

- Eric (US Male - Casual)

- Aria (US Female - Clear)

- Jenny (US Female - Soft)

- Ryan (UK Male - British Accent)

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements.

## 📄 License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

What this means:

- You may copy, distribute, and modify the software as long as you track changes and release any modifications under the same license.

- Network Use: If you run this software over a network (e.g., as a web service), you must disclose the source code to the users of that service.
