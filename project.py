import streamlit as st
import yt_dlp
import os
import demucs.separate
import whisper
import gc
import time

st.set_page_config(layout="wide", page_title="STEMSY", page_icon="")

if 'processed' not in st.session_state: st.session_state.processed = False
if 'title' not in st.session_state: st.session_state.title = ""
if 'transcript' not in st.session_state: st.session_state.transcript = None

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Space Grotesk', sans-serif; }
    header, footer {visibility: hidden;}
    
    .stApp { 
        background: linear-gradient(135deg, #0a192f 0%, #1a1a3e 30%, #0f2847 60%, #050b16 100%) !important;
        background-size: 200% 200% !important;
        animation: oceanFlow 20s ease-in-out infinite !important;
    }
    @keyframes oceanFlow { 
        0% { background-position: 0% 50%; } 
        50% { background-position: 100% 50%; } 
        100% { background-position: 0% 50%; } 
    }

    .glow-title {
        background: linear-gradient(135deg, #4facfe 0%, #00d2ff 50%, #667eea 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4.5rem; font-weight: 800; text-align: center;
        filter: drop-shadow(0 0 25px rgba(79, 172, 254, 0.5));
        margin-bottom: 40px;
        letter-spacing: -1px;
    }

    /* --- INPUT PREMIUM --- */
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.12) 0%, rgba(102, 126, 234, 0.15) 100%) !important;
        border: 2px solid transparent !important;
        border-radius: 0.375rem !important;
        color: #fff !important;
        padding: 20px 30px !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 8px 30px rgba(79, 172, 254, 0.2), inset 0 0 20px rgba(79, 172, 254, 0.05) !important;
    }
    .stTextInput > div > div {
        position: relative !important;
    }
    .stTextInput > div > div::before {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 0.375rem;
        padding: 2px;
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.6), rgba(102, 126, 234, 0.6));
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events: none;
        opacity: 0.5;
        transition: opacity 0.3s ease;
    }
    .stTextInput > div > div:focus-within::before {
        opacity: 1;
        animation: borderGlow 2s ease-in-out infinite;
    }
    @keyframes borderGlow {
        0%, 100% { filter: drop-shadow(0 0 8px rgba(79, 172, 254, 0.4)); }
        50% { filter: drop-shadow(0 0 15px rgba(79, 172, 254, 0.7)); }
    }
    .stTextInput > div > div > input:focus {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.18) 0%, rgba(102, 126, 234, 0.22) 100%) !important;
        box-shadow: 0 12px 40px rgba(79, 172, 254, 0.3), inset 0 0 30px rgba(79, 172, 254, 0.08) !important;
        outline: none !important;
        transform: translateY(-2px) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: rgba(79, 172, 254, 0.7) !important;
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    /* --- LOADERS STYLISÉS --- */
    .custom-loader {
        color: rgba(79, 172, 254, 0.9);
        text-align: center; padding: 22px;
        border: 2px solid rgba(79, 172, 254, 0.3);
        border-radius: 25px; 
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.08) 0%, rgba(102, 126, 234, 0.10) 100%);
        margin: 20px 0; letter-spacing: 2px; font-weight: 600;
        animation: pulse 3s infinite ease-in-out;
        box-shadow: 0 0 20px rgba(79, 172, 254, 0.15);
    }
    @keyframes pulse {
        0% { opacity: 0.4; box-shadow: 0 0 10px rgba(79, 172, 254, 0.1); }
        50% { opacity: 0.85; box-shadow: 0 0 25px rgba(79, 172, 254, 0.25); color: #4facfe; }
        100% { opacity: 0.4; box-shadow: 0 0 10px rgba(79, 172, 254, 0.1); }
    }
    .loader-static {
        color: #4facfe; text-align: center; padding: 18px;
        border: 2px solid rgba(79, 172, 254, 0.4);
        border-radius: 25px; 
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.12) 0%, rgba(0, 242, 254, 0.15) 100%);
        margin: 10px 0; letter-spacing: 2px; font-weight: 600;
        box-shadow: 0 0 15px rgba(79, 172, 254, 0.2);
    }

    /* --- BOUTON AVEC ANIMATION BALAYAGE --- */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.15) 0%, rgba(102, 126, 234, 0.25) 100%) !important;
        color: #fff !important; border: 2px solid rgba(79, 172, 254, 0.7) !important;
        padding: 1rem 2rem !important; border-radius: 50px !important;
        font-weight: 800 !important; text-transform: uppercase;
        letter-spacing: 2px; position: relative; overflow: hidden;
        transition: all 0.4s ease-in-out !important;
        box-shadow: 0 0 20px rgba(79, 172, 254, 0.25) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.3) 0%, rgba(102, 126, 234, 0.4) 100%) !important;
        box-shadow: 0 0 35px rgba(79, 172, 254, 0.5) !important;
        transform: translateY(-2px);
        border-color: rgba(79, 172, 254, 1) !important;
    }
    .stButton > button::after {
        content: ""; position: absolute; top: -50%; left: -60%; width: 20%; height: 200%;
        background: rgba(255, 255, 255, 0.3); transform: rotate(30deg);
        transition: 0s; filter: blur(5px);
    }
    .stButton > button:hover::after { left: 120%; transition: 0.6s ease-in-out; }

    /* --- MIXER & LYRICS --- */
    .mixer-card {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.08) 0%, rgba(102, 126, 234, 0.10) 100%);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(79, 172, 254, 0.25);
        border-radius: 30px; padding: 30px; margin-bottom: 25px;
        box-shadow: 0 0 30px rgba(79, 172, 254, 0.15);
    }

    .lyrics-card {
        background: linear-gradient(135deg, rgba(10, 25, 47, 0.6) 0%, rgba(79, 172, 254, 0.08) 100%);
        backdrop-filter: blur(20px);
        border: 2px solid rgba(79, 172, 254, 0.2);
        border-radius: 35px; padding: 40px; height: 450px;
        overflow-y: auto; scroll-behavior: smooth;
        box-shadow: inset 0 0 30px rgba(79, 172, 254, 0.08);
    }
    .lyrics-card::-webkit-scrollbar { display: none; }

    .lyric-line {
        font-size: 1.8rem; font-weight: 600; color: rgba(255, 255, 255, 0.2);
        margin: 30px 0; transition: all 0.5s ease; text-align: center;
    }
    .lyric-active {
        color: #fff !important;
        background: linear-gradient(135deg, #4facfe, #00d2ff, #667eea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 25px rgba(79, 172, 254, 0.8));
        transform: scale(1.1); font-weight: 800;
    }

    audio {
        width: 100%; height: 50px; border-radius: 50px;
        filter: sepia(100%) saturate(700%) hue-rotate(180deg) brightness(1) contrast(1.1);
        box-shadow: 0 0 20px rgba(79, 172, 254, 0.2);
    }
    
    h3 {
        color: #4facfe !important;
        text-align: center !important;
        margin-bottom: 25px !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        text-shadow: 0 0 20px rgba(79, 172, 254, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

def download_audio(url):
    os.makedirs('downloads', exist_ok=True)
    try:
        yt_opts = {'format': 'bestaudio/best','outtmpl': 'downloads/%(title)s.%(ext)s',
                   'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]}
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return {'status': 'success', 'title': info.get('title', 'Audio')}
    except Exception as e: return {'status': 'error', 'message': str(e)}

def separate_audio(input_path, output_path):
    demucs.separate.main(["--mp3", "--two-stems", "vocals", "-n", "mdx_extra", "-d", "cpu", input_path, "-o", output_path])
    gc.collect()

@st.cache_resource
def load_whisper(): return whisper.load_model("tiny")

def main():
    st.markdown('<h1 class="glow-title">STEMSY</h1>', unsafe_allow_html=True)
    url_input = st.text_input("", placeholder="Collez l'URL YouTube...", label_visibility="collapsed")
    
    if st.button("Lancer l'extraction"):
        if url_input:
            placeholder = st.empty()
            with placeholder.container():
                # Étape 1 : Download
                st.markdown('<div class="custom-loader">ÉTAPE 1 : RÉCUPÉRATION DU FLUX...</div>', unsafe_allow_html=True)
                res = download_audio(url_input)
                
                if res['status'] == 'success':
                    title = res['title']
                    st.session_state.title = title

                    placeholder.empty()
                    with placeholder.container():
                        st.markdown('<div class="loader-static">FLUX RÉCUPÉRÉ</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="custom-loader">ÉTAPE 2 : ISOLATION IA (DEMUCS)...</div>', unsafe_allow_html=True)
                        separate_audio(f"downloads/{title}.mp3", "separated")

                    placeholder.empty()
                    with placeholder.container():
                        st.markdown('<div class="loader-static">FLUX RÉCUPÉRÉ</div>', unsafe_allow_html=True)
                        st.markdown('<div class="loader-static">PISTES ISOLÉES</div>', unsafe_allow_html=True)
                        st.markdown('<div class="custom-loader">ÉTAPE 3 : ANALYSE DES PAROLES (WHISPER)...</div>', unsafe_allow_html=True)
                        model = load_whisper()
                        st.session_state.transcript = model.transcribe(f"separated/mdx_extra/{title}/vocals.mp3", fp16=False)
                    
                    st.session_state.processed = True
                    placeholder.empty()

    if st.session_state.processed:
        title = st.session_state.title
        path_instru = f"separated/mdx_extra/{title}/no_vocals.mp3"
        path_vocals = f"separated/mdx_extra/{title}/vocals.mp3"
        path_full = f"downloads/{title}.mp3"

        st.markdown(f"<h3 style='color:#4facfe; text-align:center; margin-bottom:20px;'>{title}</h3>", unsafe_allow_html=True)

        col_mix_1, col_mix_2 = st.columns([3, 1])
        with col_mix_2:
            mode = st.radio("Mode d'écoute", ["Mix Complet", "Instrumental", "Vocals Only"], label_visibility="collapsed")
        with col_mix_1:
            audio_source = path_full if mode == "Mix Complet" else (path_instru if mode == "Instrumental" else path_vocals)
            st.audio(audio_source)
        st.markdown('</div>', unsafe_allow_html=True)

        for i, segment in enumerate(st.session_state.transcript['segments']):
            st.markdown(f'<div class="lyric-line" id="line-{i}" data-start="{segment["start"]}" data-end="{segment["end"]}">{segment["text"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        js_sync = f"""
        <script>
            const audio = window.parent.document.querySelector('audio');
            const lines = window.parent.document.querySelectorAll('.lyric-line');
            if (audio) {{
                audio.ontimeupdate = () => {{
                    lines.forEach((line) => {{
                        const start = parseFloat(line.getAttribute('data-start'));
                        const end = parseFloat(line.getAttribute('data-end'));
                        if (audio.currentTime >= start && audio.currentTime <= end) {{
                            if (!line.classList.contains('lyric-active')) {{
                                line.classList.add('lyric-active');
                                line.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                            }}
                        }} else {{ line.classList.remove('lyric-active'); }}
                    }});
                }};
            }}
        </script>
        """
        st.components.v1.html(js_sync, height=0)

if __name__ == "__main__":
    main()