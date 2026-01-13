import streamlit as st
import yt_dlp
import os
from yt_dlp.utils import download_range_func

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

# --- LOGIQUE DE TÉLÉCHARGEMENT ---
def download_youtube_audio(url, start_time=2, end_time=7):
    os.makedirs('downloads', exist_ok=True)
    try:
        yt_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,
        }
        if start_time is not None and end_time is not None:
            yt_opts['download_ranges'] = download_range_func(None, [(start_time, end_time)])
            yt_opts['force_keyframes_at_cuts'] = True
            
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            info = ydl.extract_info(url, download=True)
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
                        else:
                            status.update(label="❌ Erreur de téléchargement", state="error")
                            st.error(result['message'])
                else:
                    st.warning("Veuillez entrer une URL")

if __name__ == "__main__":
    main()