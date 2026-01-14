import streamlit as st
import yt_dlp
import os
from jinja2 import Template
from yt_dlp.utils import download_range_func
import demucs
import demucs.separate
import subprocess
import base64


# Configuration de la page
st.set_page_config(layout="wide", page_title="YouTube Downloader")

# --- DESIGN PERSONNALISÉ (CSS INJECTÉ) ---
st.markdown("""
<style>
    /* Masquer le header et le footer de Streamlit */
    header, footer {visibility: hidden;}
    
    /* Fond dégradé radial sur toute la page */
    .stApp {
        background: radial-gradient(
            ellipse 150% 100% at center,
            #006BE4 0%,
            #004A9E 25%,
            #003275 40%,
            #001F4D 55%,
            #010934 75%
        ) !important;
    }

    /* Centrage du contenu */
    .main .block-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }

    /* Style du conteneur de saisie */
    .custom-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(8px);
        padding: 2rem;
        border-radius: 12px;
        border: 2px solid white;
        display: flex;
        gap: 0;
    }

    /* Style de l'input Streamlit pour qu'il ressemble au vôtre */
    .stTextInput input {
        border-radius: 8px 0 0 8px !important;
        border: 2px solid white !important;
        height: 48px;
        width: 400px !important;
    }

    /* Style du bouton Streamlit */
    .stButton button {
        border-radius: 0 8px 8px 0 !important;
        background-color: #2563eb !important; /* blue-600 */
        color: white !important;
        height: 48px;
        border: 2px solid white !important;
        border-left: none !important;
        padding: 0 25px !important;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        background-color: #1d4ed8 !important; /* blue-700 */
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# --- LOGIQUE DE RÉCUPÉRATION DE PISTE ---

def get_audio_html(file_path):
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    return f"data:audio/mp3;base64,{audio_base64}"

# --- LOGIQUE DE SEPRATION ---
def separate_audio(input_path, output_path):
    demucs.separate.main([
        "--mp3", 
        "--two-stems", "vocals", 
        "-n", "mdx_extra", 
        "-d", "cpu", 
        input_path, 
        "-o", output_path
    ])

# --- LOGIQUE DE TÉLÉCHARGEMENT ---
def download_youtube_audio(url, start_time=2, end_time=7):
    os.makedirs('downloads', exist_ok=True)
    try:
        yt_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,
            # --- AJOUT POUR CONVERTIR EN MP3 ---
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        # On a supprimé la partie 'download_ranges' pour avoir toute la musique
            
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # yt-dlp change l'extension en .mp3 après la conversion
            return {'status': 'success', 'title': info.get('title', 'Audio')}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# --- INTERFACE ---
def main():
    # Créer un conteneur pour centrer les éléments
    with st.container():
        # Utiliser des colonnes pour simuler le design côte à côte
        col1, col2 = st.columns([3, 1], gap="small")
        
        with col1:
            url_input = st.text_input("", placeholder="Lien YouTube", label_visibility="collapsed")
        
        with col2:
            if st.button("Télécharger"):
                if url_input:
                    with st.status("Téléchargement...", expanded=False) as status:
                        result = download_youtube_audio(url_input)
                        if result['status'] == 'success':
                            status.update(label=f"✅ {result['title']} téléchargé !", state="complete")
                            st.toast(f"Fichier prêt : {result['title']}")

                            separate_audio(f"downloads/{result['title']}.mp3", "separated")
                            # 1. Charger le fichier HTML
                            with open("index.html", "r") as f:
                                html_content = f.read()

                            # 2. Créer le template et injecter les variables
                            template = Template(html_content)
                            html_final = template.render(
                                titre_musique=result['title'],
                                vocal_url=get_audio_html(f"separated/mdx_extra/{result['title']}/no_vocals.mp3"), # La fonction base64 d'avant
                                # 3. Afficher dans Streamlit
                            )
                            st.markdown(html_final, unsafe_allow_html=True)
                            audio_path = f"separated/mdx_extra/{result['title']}/no_vocals.mp3"
                            if not os.path.exists(audio_path):
                                st.error(f"Le fichier audio n'a pas été trouvé : {audio_path}")
                                return
                            st.audio(audio_path, format="audio/mp3")
                            print(f"separated/mdx_extra/{result['title']}/vocals.mp3")
                        else:
                            status.update(label="❌ Erreur de téléchargement", state="error")
                            st.error(result['message'])
                else:
                    st.warning("Veuillez entrer une URL")

if __name__ == "__main__":
    main()