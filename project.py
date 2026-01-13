# import demucs.separate
import streamlit as st
import streamlit.components.v1 as components
import yt_dlp
from yt_dlp.utils import download_range_func

st.set_page_config(
    layout="wide"
)

st.markdown("""
<style>

/* RESET TOTAL */
html, body {
    margin: 0 !important;
    padding: 0 !important;
}

/* App root */
[data-testid="stApp"] {
    margin: 0 !important;
    padding: 0 !important;
}

/* Header Streamlit (même invisible) */
header {
    height: 0rem !important;
    min-height: 0rem !important;
    margin: 0 !important;
    padding: 0 !important;
    display: none !important;
}

/* Main wrapper */
section.main {
    padding: 0 !important;
    margin: 0 !important;
}

/* Vertical blocks internes */
div[data-testid="stVerticalBlock"] {
    padding: 0 !important;
    margin: 0 !important;
    gap: 0 !important;
}

/* Container principal */
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

/* CRUCIAL: Supprimer la marge du composant HTML */
div[data-testid="stVerticalBlock"] > div:has(iframe) {
    margin: 0 !important;
    padding: 0 !important;
}

/* Iframe - Forcer la hauteur totale */
iframe {
    width: 100vw !important;
    height: 100vh !important;
    border: none !important;
    display: block !important;
    margin: 0 !important;
    padding: 0 !important;
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
}
</style>
""", unsafe_allow_html=True)

start_time = 0
end_time = -1

yt_opts = {
    'verbose': True,
    'cookies': 'cookies.txt',  # ← ICI
    'download_ranges': download_range_func(None, [(start_time, end_time)]),
    'force_keyframes_at_cuts': True,
}

with yt_dlp.YoutubeDL(yt_opts) as ydl:
    ydl.download(["https://www.youtube.com/watch?v=Q0oIoR9mLwc"])


# def separer_audio(enter_path_file):
#     demucs.separate.main(["--mp3", "--two-stems", "vocals", "n", "mdx-extra", enter_path_file])
#     print(f"Terminé! Les fichiers sont dans: separated")

def main():
    with open ("index.html", "r") as f:
        html_data = f.read()

    # Ajouter un script pour forcer le redimensionnement
    html_with_script = html_data.replace('</body>', '''
    <script>
        // Envoyer la hauteur réelle de la fenêtre à Streamlit
        function resizeIframe() {
            const height = Math.max(
                document.documentElement.scrollHeight,
                document.body.scrollHeight,
                window.innerHeight,
                screen.height
            );
            window.parent.postMessage({
                type: 'streamlit:setFrameHeight',
                height: height
            }, '*');
        }

        window.addEventListener('load', resizeIframe);
        window.addEventListener('resize', resizeIframe);

        // Force initial resize
        resizeIframe();
    </script>
    </body>''')

    # Utiliser une grande hauteur par défaut
    st.components.v1.html(html_with_script, height=1000, scrolling=False)

if __name__ == "__main__":
    main()