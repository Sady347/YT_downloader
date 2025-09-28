import streamlit as st 
import yt_dlp
import os 
from io import BytesIO

st.set_page_config(page_title="Omar's Video Downloader", layout="wide", initial_sidebar_state="collapsed")

url = st.text_input("Enter video url:")



def safe_filename(title, ext="mp4"):
    return "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip() + f".{ext}"

if url:
    try:
        # Get video info first to extract title
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "video")
        
        file_name = safe_filename(title, "mp4")

        ydl_opts = {
            'format': 'best',
            'outtmpl': file_name,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open(file_name, "rb") as f:
            st.download_button(
                label="Save video",
                data=f,
                file_name=file_name,
                mime="video/mp4"
            )

        os.remove(file_name)

    except Exception as e:
        st.error(f" Error: {e}")