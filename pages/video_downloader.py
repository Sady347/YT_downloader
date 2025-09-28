import streamlit as st 
import yt_dlp
import os 
import io
import tempfile
from pathlib import Path

st.set_page_config(page_title="Omar's Video Downloader", layout="wide", initial_sidebar_state="collapsed")

url = st.text_input("Enter video URL:")
cookies_up = st.file_uploader("Optional: upload cookies.txt (Netscape format)", type=["txt"])

def download_cloud(url, cookies_file=None):
    clients = ["android", "ios", "web_safari"]   # rotate to evade SABR/403
    formats = ["22/18", "137+140/136+140/135+140/134+140", "bv*+ba/b"]  # prog → DASH → best
    last_err = None
    with tempfile.TemporaryDirectory() as tmp:
        outtmpl = str(Path(tmp) / "%(title).200s.%(ext)s")
        for c in clients:
            for fsel in formats:
                opts = {
                    "noplaylist": True,
                    "quiet": True,
                    "no_warnings": True,
                    "retries": 10,
                    "fragment_retries": 10,
                    "concurrent_fragment_downloads": 3,
                    "extractor_args": {"youtube": {"player_client": [c]}},
                    "format": fsel,
                    "merge_output_format": "mp4",       # keep mp4 if possible
                    "source_address": "0.0.0.0",        # force IPv4
                    "http_headers": { "User-Agent": "Mozilla/5.0", "Referer": "https://www.youtube.com/" },
                    "outtmpl": outtmpl,
                }
                if cookies_file:
                    opts["cookiefile"] = cookies_file
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        # Resolve final path
                        paths = [d.get("filepath") or d.get("filename")
                                 for d in (info.get("requested_downloads") or []) if d.get("filepath") or d.get("filename")]
                        if not paths:
                            guess = Path(ydl.prepare_filename(info))
                            for ext in (".mp4", ".mkv", guess.suffix):
                                p = guess.with_suffix(ext)
                                if p.exists():
                                    paths = [str(p)]; break
                        return paths[0], info
                except yt_dlp.utils.DownloadError as e:
                    last_err = e
                    continue
        raise last_err or yt_dlp.utils.DownloadError("All client/format attempts failed.")

if st.button("Download") and url:
    try:
        cookies_path = None
        if cookies_up:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as cf:
                cf.write(cookies_up.getbuffer())
                cookies_path = cf.name

        final_path, info = download_cloud(url, cookies_file=cookies_path)
        data = Path(final_path).read_bytes()
        name = Path(final_path).name
        mime = "video/mp4" if name.endswith(".mp4") else "video/x-matroska"
        st.success(f"Ready: {name}")
        st.download_button("Save video", data=data, file_name=name, mime=mime)
        try:
            Path(final_path).unlink(missing_ok=True)
            if cookies_path: Path(cookies_path).unlink(missing_ok=True)
        except Exception:
            pass
    except yt_dlp.utils.DownloadError as e:
        st.error(f"Download error: {e}")
        st.info("If this repeats, upload cookies.txt (age/region lock) or try a different client/format.")
    except Exception as e:
        st.error(f"Error: {e}")