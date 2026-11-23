"""Daily Dose Studio: Ultra-minimalist, child-friendly web dashboard."""

import os
import time
import uuid
from pathlib import Path
import streamlit as st
from config import DOWNLOADS_DIR, EXPORTS_DIR, settings
from daemon.scheduler import run_full_pipeline
from models import (
    CandidateStatus,
    ClipCandidate,
    JobStatus,
    NicheTopic,
    PlatformSource,
    ProcessedClip,
    VideoJob,
)
from ui.style import PURE_WHITE_CSS

# Page Configuration
st.set_page_config(
    page_title="Daily Dose Studio",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Apply Ultra-Minimalist Pure White Theme
st.markdown(PURE_WHITE_CSS, unsafe_allow_html=True)


def main():
    # 1. Header
    st.markdown(
        """
        <div class="studio-header">
            <h1 class="studio-title">Daily Dose Studio</h1>
            <p class="studio-subtitle">Create amazing funny compilation videos in 1 click</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Main Creator Card
    with st.container():
        st.markdown('<div class="studio-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">1. Choose How to Start</div>', unsafe_allow_html=True)

        mode_choice = st.radio(
            label="Creation Mode",
            options=["🌐 Find Videos For Me (Magic Live Search)", "📁 Upload My Own Clips"],
            index=0,
            label_visibility="collapsed",
        )

        st.markdown('<div class="card-title" style="margin-top: 1.5rem;">2. Video Settings</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            topic_labels = {
                "Funny & Fails (Daily Dose Style)": NicheTopic.FUNNY_FAILS,
                "Cute & Funny Animals": NicheTopic.ANIMALS,
                "Oddly Satisfying & ASMR": NicheTopic.SATISFYING,
                "Cool Inventions & Gadgets": NicheTopic.GADGETS,
            }
            selected_topic_label = st.selectbox(
                "What kind of video?",
                options=list(topic_labels.keys()),
                index=0,
            )
            selected_topic = topic_labels[selected_topic_label]

        with col2:
            clip_count_choice = st.selectbox(
                "How many clips?",
                options=["5 Clips (Short)", "10 Clips (Standard)", "15 Clips (Full)"],
                index=1,
            )
            clip_count_map = {"5 Clips (Short)": 5, "10 Clips (Standard)": 10, "15 Clips (Full)": 15}
            target_clips = clip_count_map[clip_count_choice]

        aspect_choice = st.radio(
            "Video Shape",
            options=["16:9 (YouTube Horizontal)", "9:16 (Shorts / TikTok Vertical)"],
            index=0,
            horizontal=True,
        )
        aspect_ratio = "16:9" if "16:9" in aspect_choice else "9:16"

        uploaded_files = []
        if "Upload My Own Clips" in mode_choice:
            st.markdown('<div class="card-title" style="margin-top: 1.5rem;">3. Drop Your Video Clips</div>', unsafe_allow_html=True)
            uploaded_files = st.file_uploader(
                "Upload video files (.mp4, .mov)",
                type=["mp4", "mov"],
                accept_multiple_files=True,
                label_visibility="collapsed",
            )
            if uploaded_files:
                st.caption(f"📁 {len(uploaded_files)} clip(s) ready to edit.")

        st.markdown("</div>", unsafe_allow_html=True)

    # 3. Big Action Button
    create_clicked = st.button("✨ MAKE MY VIDEO NOW", use_container_width=True)

    # 4. Pipeline Execution
    if create_clicked:
        job_id = f"job_{int(time.time())}"
        job_mode = "manual_upload" if "Upload My Own Clips" in mode_choice else "magic_search"

        # Validate uploads if in manual mode
        if job_mode == "manual_upload" and not uploaded_files:
            st.error("Please drop at least 1 video clip to continue.")
            return

        # Prepare uploaded clips if applicable
        manual_clips = []
        if job_mode == "manual_upload" and uploaded_files:
            for idx, uf in enumerate(uploaded_files):
                saved_path = DOWNLOADS_DIR / f"{job_id}_up_{idx}_{uf.name}"
                with open(saved_path, "wb") as f:
                    f.write(uf.getbuffer())

                c = ClipCandidate(
                    id=f"up_{idx}",
                    title=Path(uf.name).stem,
                    source_platform=PlatformSource.MANUAL_UPLOAD,
                    creator_handle="@creator",
                    video_path=str(saved_path),
                    status=CandidateStatus.DOWNLOADED,
                )
                manual_clips.append(ProcessedClip(candidate=c))

        job = VideoJob(
            job_id=job_id,
            mode=job_mode,
            topic=selected_topic,
            target_clip_count=len(manual_clips) if manual_clips else target_clips,
            aspect_ratio=aspect_ratio,
            clips=manual_clips,
        )

        # Progress display container
        progress_bar = st.progress(5)
        status_text = st.empty()

        def update_ui(pct: int, msg: str):
            progress_bar.progress(pct)
            status_text.markdown(f"**Status:** {msg}")

        try:
            with st.spinner("Creating your video..."):
                completed_job = run_full_pipeline(job, progress_callback=update_ui)

            progress_bar.progress(100)
            status_text.success("🎉 Your video is finished!")

            # Display video player
            if completed_job.final_video_path and Path(completed_job.final_video_path).exists():
                st.markdown("### 🎬 Watch Your Finished Video")
                st.video(completed_job.final_video_path)

                # Download button
                with open(completed_job.final_video_path, "rb") as vf:
                    st.download_button(
                        label="⬇️ Download Finished MP4 Video",
                        data=vf,
                        file_name=Path(completed_job.final_video_path).name,
                        mime="video/mp4",
                        use_container_width=True,
                    )

                # Display high-CTR YouTube thumbnail if available
                thumb_path = EXPORTS_DIR / "DailyDose_Thumbnail.jpg"
                if thumb_path.exists():
                    st.markdown("### 🖼️ High-CTR YouTube Thumbnail (1280x720)")
                    st.image(str(thumb_path), use_container_width=True)
                    with open(thumb_path, "rb") as tf:
                        st.download_button(
                            label="⬇️ Download High-CTR Thumbnail (.JPG)",
                            data=tf,
                            file_name="DailyDose_Thumbnail.jpg",
                            mime="image/jpeg",
                            use_container_width=True,
                        )

        except Exception as e:
            st.error(f"Something went wrong while making the video: {e}")


if __name__ == "__main__":
    main()

