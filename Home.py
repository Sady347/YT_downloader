import streamlit as st

st.set_page_config(page_title="Omar's Video Downloader", page_icon="🎵", layout="wide")


# Home page content
st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="color: #1d5689; font-size: 3rem; margin-bottom: 0.5rem;">🐸 Omar's Video Downloader</h1>
        <h2 style="color: #4f7a1a; font-size: 2rem; margin-top: 0rem; margin-bottom: 1.5rem;">For those no wifi days :)</h2>
        <p style="font-size: 1.2rem; color: #666; max-width: 600px; margin: 0 auto;">
            With this app, you can download YouTube videos and playlists to watch outside. 
            Use the left menu to navigate through pages.
        </p>
    </div>
""", unsafe_allow_html=True)

# Usage instructions
with st.expander("How to Use?"):
    st.markdown("""           
    ### Step by Step Guide:
    
    1. **Select a page from the left menu:**
       - ** Youtube Downloader:** To download a single video
       - ** Playlist Downloader:** To download multiple videos
    
    2. **Choose format and quality:**
       - Select MP4 for video or MP3 for audio
       - Choose your desired video quality
    
    3. **Enter URLs:**
       - Paste YouTube video links
       - For batch downloading, enter one URL per line
    
    4. **Start the download process:**
       - Click the "Download" button
       - Wait for the process to complete
    
    ### Tips:
    - FFmpeg is required for MP3 downloading
    - Large files may take longer
    - Ensure your internet connection is stable
    """)

# Footer
st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: #666; border-top: 1px solid #eee; margin-top: 2rem;">
        <p>🚀 Powered by <strong>yt-dlp</strong> | 
        📁 Files are saved in the <code>Downloads</code> folder</p>
    </div>
""", unsafe_allow_html=True)