import streamlit as st 
import yt_dlp
import os 
import io
import tempfile
from pathlib import Path

st.set_page_config(page_title="Omar's Video Downloader", layout="wide", initial_sidebar_state="collapsed")


url = st.text_input("Enter YouTube URL")
cookies_up = st.file_uploader(
    "Upload cookies.txt (Netscape format; exported while signed in to youtube.com)",
    type=["txt"]
)

def try_download_with_cookies(url: str, cookie_bytes: bytes) -> tuple[str, bytes]:
    """
    Requires valid cookies. Tries progressive MP4 first (22/18), then DASH.
    Rotates player clients to avoid 403/SABR. Returns (filename, data).
    """
    clients = ["android", "ios", "web_safari"]                     # rotate clients
    formats = ["22/18", "137+140/136+140/135+140/134+140", "bv*+ba/b"]  # prog → DASH → best

    with tempfile.TemporaryDirectory() as tmp:
        outtmpl = str(Path(tmp) / "%(title).200s.%(ext)s")

        cookiefile = os.path.join(tmp, "cookies.txt")
        with open(cookiefile, "wb") as f:
            f.write(cookie_bytes)

        last_err = None
        for client in clients:
            for fmt in formats:
                opts = {
                    "noplaylist": True,
                    "quiet": True,
                    "no_warnings": True,
                    "retries": 10,
                    "fragment_retries": 10,
                    "concurrent_fragment_downloads": 3,

                    "extractor_args": {"youtube": {"player_client": [client]}},
                    "format": fmt,
                    "merge_output_format": "mp4",      # try to keep MP4 container
                    "source_address": "0.0.0.0",       # force IPv4
                    "http_headers": {
                        "User-Agent": "Mozilla/5.0",
                        "Referer": "https://www.youtube.com/",
                    },
                    "cookiefile": cookiefile,
                    "outtmpl": outtmpl,
                }
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(url, download=True)

                        # Resolve output path robustly
                        paths = [
                            d.get("filepath") or d.get("filename")
                            for d in (info.get("requested_downloads") or [])
                            if d.get("filepath") or d.get("filename")
                        ]
                        if not paths:
                            guess = Path(ydl.prepare_filename(info))
                            for ext in (".mp4", ".mkv", guess.suffix):
                                p = guess.with_suffix(ext)
                                if p.exists():
                                    paths = [str(p)]
                                    break

                        final = Path(paths[0])
                        data = final.read_bytes()
                        return final.name, data
                except yt_dlp.utils.DownloadError as e:
                    last_err = e
                    continue

        raise last_err or yt_dlp.utils.DownloadError("All client/format attempts failed with provided cookies.")

if st.button("Download"):
    if not url:
        st.error("Paste a YouTube URL.")
    elif not cookies_up:
        st.error("This deployment requires login. Please upload cookies.txt (Netscape format).")
        with st.expander("How to get cookies.txt"):
            st.markdown(
                """
1. Sign in to YouTube in your browser.
2. Open the video page (stay on **youtube.com**, not m.youtube.com).
3. Use a “cookies.txt” exporter extension to export as **Netscape format**.
4. Make sure the file includes entries for **.youtube.com** (CONSENT, SID, HSID, SAPISID/`__Secure-3PAPISID`, etc.).
5. Upload that file here.
                """
            )
    else:
        with st.spinner("Downloading with your cookies…"):
            try:
                name, data = try_download_with_cookies(url, cookies_up.getbuffer())
                mime = "video/mp4" if name.lower().endswith(".mp4") else "video/x-matroska"
                st.success(f"Ready: {name}")
                st.download_button("Save video", data=data, file_name=name, mime=mime)
            except yt_dlp.utils.DownloadError as e:
                st.error(f"Download error: {e}")
                st.info("Refresh your cookies (they may be expired), or try again later.")
            except Exception as e:
                st.error(f"Error: {e}")