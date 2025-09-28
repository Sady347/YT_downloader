import streamlit as st 
import yt_dlp
import os 
import io
import tempfile
from pathlib import Path

st.set_page_config(page_title="Omar's Video Downloader", layout="wide", initial_sidebar_state="collapsed")

url = st.text_input("Enter video url:")

if st.button("Fetch & prepare") and url:
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            outtmpl = str(Path(tmpdir) / "%(title).200s.%(ext)s")

            ydl_opts = {
                "noplaylist": True,
                "ignoreerrors": False,
                "quiet": True,
                "no_warnings": True,

          
                "extractor_args": {"youtube": {"player_client": ["android"]}},

                # ---- Format selection ----

                "format": "bv*+ba/b",

                "merge_output_format": "mp4",

                "outtmpl": outtmpl,

            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                final_paths = []
                for d in (info.get("requested_downloads") or []):
                    p = d.get("filepath") or d.get("filename")
                    if p:
                        final_paths.append(p)

                if not final_paths:
                    guessed = Path(ydl.prepare_filename(info))
                    candidates = [
                        guessed.with_suffix(".mp4"),
                        guessed.with_suffix(".mkv"),
                        guessed  # as-is
                    ]
                    final_path = next((str(p) for p in candidates if Path(p).exists()), str(guessed))
                else:
                    final_path = final_paths[0]

            final_path = str(final_path)
            file_bytes = Path(final_path).read_bytes()
            ext = Path(final_path).suffix.lower().lstrip(".")
            mime = "video/mp4" if ext == "mp4" else ("video/x-matroska" if ext == "mkv" else "application/octet-stream")

            nice_name = Path(final_path).name

            st.success(f"Ready: {nice_name}")
            st.download_button(
                label="Save video",
                data=file_bytes,
                file_name=nice_name,
                mime=mime
            )

    except yt_dlp.utils.DownloadError as e:
        st.error("Download failed. Listing available formats below…")
        st.code(str(e))
        try:
            with yt_dlp.YoutubeDL({
                "listformats": True,
                "noplaylist": True,
                "quiet": False,
                "extractor_args": {"youtube": {"player_client": ["android"]}},
            }) as ydl:
                ydl.extract_info(url, download=False)
            st.info("Pick a format code from the list (e.g., 22 or 140) and re-run with ydl_opts['format'] = '22' (or similar).")
        except Exception as e2:
            st.error(f"Also failed to list formats: {e2}")

    except Exception as e:
        st.error(f"Error: {e}")