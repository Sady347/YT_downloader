import streamlit as st 
import yt_dlp
import os 
import io
import tempfile
from pathlib import Path

st.set_page_config(page_title="Omar's Video Downloader", layout="wide", initial_sidebar_state="collapsed")

url = st.text_input("Enter video url:")


url = st.text_input("Enter video URL:")
cookies_up = st.file_uploader("Optional: upload cookies.txt (for age/region restricted videos)", type=["txt"])

if st.button("Download") and url:
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            outtmpl = str(Path(tmpdir) / "%(title).200s.%(ext)s")

            ydl_opts = {
                # --- Make Streamlit Cloud-friendly & resilient ---
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "retries": 10,
                "fragment_retries": 10,
                "concurrent_fragment_downloads": 3,

                # Use mobile/safari clients to avoid SABR/403 issues
                "extractor_args": {"youtube": {"player_client": ["android", "ios", "web_safari"]}},

                # Prefer a progressive mp4 first, else best video+audio
                "format": "22/18/bv*+ba/b",

                # Try to produce mp4 without re-encode (falls back to mkv if codecs mismatch)
                "merge_output_format": "mp4",

                # Force IPv4 (many 403s vanish with IPv4)
                "source_address": "0.0.0.0",

                # Helpful headers
                "http_headers": {
                    "User-Agent": "Mozilla/5.0",
                    "Referer": "https://www.youtube.com/",
                },

                "outtmpl": outtmpl,
            }

            # Optional cookies support (for age/region restricted)
            if cookies_up is not None:
                cookies_path = os.path.join(tmpdir, "cookies.txt")
                with open(cookies_path, "wb") as f:
                    f.write(cookies_up.getbuffer())
                ydl_opts["cookiefile"] = cookies_path

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                # Resolve final file path
                files = []
                for d in (info.get("requested_downloads") or []):
                    p = d.get("filepath") or d.get("filename")
                    if p:
                        files.append(p)
                if not files:
                    guess = Path(ydl.prepare_filename(info))
                    for ext in (".mp4", ".mkv", guess.suffix):
                        p = guess.with_suffix(ext)
                        if p.exists():
                            files = [str(p)]
                            break

            final_path = files[0]
            data = Path(final_path).read_bytes()
            name = Path(final_path).name
            mime = "video/mp4" if name.endswith(".mp4") else "video/x-matroska"

            st.success(f"Ready: {name}")
            st.download_button("Save video", data=data, file_name=name, mime=mime)

    except yt_dlp.utils.ExtractorError as e:
        st.error(f"Extractor error: {e}")
    except yt_dlp.utils.DownloadError as e:
        st.error(f"Download error: {e}")
        st.info("Tip: try another client (android/ios/web_safari), upload cookies.txt, or choose 22/18 explicitly.")
    except Exception as e:
        st.error(f"Error: {e}")