"""Streamlit webapp for YouTube video management and transcript viewing."""

import pandas as pd
import streamlit as st
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled

from constants import YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID
from youtube_helper import YouTubeHelper


def initialize_session_state() -> None:
    """Initialize session state variables."""
    if "youtube_helper" not in st.session_state:
        st.session_state.youtube_helper = None
    if "video_ids" not in st.session_state:
        st.session_state.video_ids = []
    if "video_stats" not in st.session_state:
        st.session_state.video_stats = {}
    if "selected_video_id" not in st.session_state:
        st.session_state.selected_video_id = None
    if "transcript" not in st.session_state:
        st.session_state.transcript = None
    if "transcript_text" not in st.session_state:
        st.session_state.transcript_text = None


def format_number(num: int) -> str:
    """Format large numbers with commas."""
    return f"{num:,}"


def format_duration(duration: str) -> str:
    """Format ISO 8601 duration to readable format."""
    if not duration:
        return "N/A"
    # Parse PT1H2M3S format
    duration = duration.replace("PT", "")
    hours = 0
    minutes = 0
    seconds = 0

    if "H" in duration:
        hours_str, duration = duration.split("H")
        hours = int(hours_str)
    if "M" in duration:
        minutes_str, duration = duration.split("M")
        minutes = int(minutes_str)
    if "S" in duration:
        seconds = int(duration.replace("S", ""))

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0:
        parts.append(f"{seconds}s")

    return " ".join(parts) if parts else "0s"


def duration_to_seconds(duration: str) -> int:
    """Convert ISO 8601 duration to total seconds.

    Args:
        duration: ISO 8601 duration string (e.g., "PT1H2M3S")

    Returns:
        Total duration in seconds
    """
    if not duration:
        return 0
    # Parse PT1H2M3S format
    duration = duration.replace("PT", "")
    hours = 0
    minutes = 0
    seconds = 0

    if "H" in duration:
        hours_str, duration = duration.split("H")
        hours = int(hours_str)
    if "M" in duration:
        minutes_str, duration = duration.split("M")
        minutes = int(minutes_str)
    if "S" in duration:
        seconds = int(duration.replace("S", ""))

    return hours * 3600 + minutes * 60 + seconds


# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
def main() -> None:
    """Main Streamlit app."""
    st.set_page_config(page_title="YouTube Transcript Manager", layout="wide")

    initialize_session_state()

    st.title("YouTube Transcript Manager")
    st.markdown("---")

    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input(
            "YouTube API Key",
            value=YOUTUBE_API_KEY or "",
            type="password",
            help="Enter your YouTube Data API v3 key (or set YOUTUBE_API_KEY in .env)",
        )
        channel_id = st.text_input(
            "Channel ID",
            value=YOUTUBE_CHANNEL_ID or "",
            help=(
                "Enter the YouTube channel ID to fetch videos from "
                "(or set YOUTUBE_CHANNEL_ID in .env)"
            ),
        )

        if st.button("Load Videos", type="primary"):
            if not api_key:
                st.error("Please enter a YouTube API key")
            elif not channel_id:
                st.error("Please enter a channel ID")
            else:
                try:
                    with st.spinner("Loading videos..."):
                        helper = YouTubeHelper(api_key)
                        video_ids = helper.get_video_ids_from_channel(channel_id, max_results=200)

                        if video_ids:
                            st.session_state.youtube_helper = helper
                            st.session_state.video_ids = video_ids
                            st.session_state.video_stats = helper.get_video_stats_batch(video_ids)
                            st.success(f"Loaded {len(video_ids)} videos!")
                        else:
                            st.warning("No videos found for this channel")
                except Exception as e:
                    st.error(f"Error loading videos: {str(e)}")

        st.markdown("---")
        st.markdown("### Instructions")
        st.markdown(
            """
            1. Enter your YouTube API key
            2. Enter the channel ID
            3. Click "Load Videos"
            4. Select a video from the dropdown
            5. View stats and transcript
            6. Download transcript if needed
            """
        )

    # Main content area
    if not st.session_state.youtube_helper:
        st.info("👈 Please configure your API key and channel ID in the sidebar to get started")
        return

    if not st.session_state.video_ids:
        st.warning("No videos available. Please load videos first.")
        return

    # Video selection dropdown
    st.header("Select Video")

    # Filter checkbox
    filter_shorts = st.checkbox(
        "Filter out Shorts (videos ≤ 60 seconds or with hashtags in title)", value=False
    )

    # Create dropdown options with video titles
    video_options = {}
    filtered_video_ids = []

    for video_id in st.session_state.video_ids:
        stats = st.session_state.video_stats.get(video_id, {})
        duration_str = stats.get("duration", "")
        duration_seconds = duration_to_seconds(duration_str)
        title = stats.get("title", f"Video {video_id}")

        # Filter out Shorts if checkbox is checked
        # Shorts are defined as: <= 60 seconds OR has hashtags in title
        if filter_shorts:
            is_short_duration = 0 < duration_seconds <= 60
            has_hashtags = "#" in title
            if is_short_duration or has_hashtags:
                continue

        filtered_video_ids.append(video_id)
        video_options[f"{title} ({video_id})"] = video_id

    if filter_shorts and not filtered_video_ids:
        st.info("No full-length videos found after filtering out Shorts.")
        return

    selected_option = st.selectbox(
        "Choose a video:",
        options=list(video_options.keys()),
        index=0 if video_options else None,
    )

    if selected_option:
        selected_video_id = video_options[selected_option]
        st.session_state.selected_video_id = selected_video_id

        # Display video stats
        stats = st.session_state.video_stats.get(selected_video_id, {})

        if stats:
            st.markdown("---")
            st.header("Video Player")

            # YouTube video embed
            embed_url = f"https://www.youtube.com/embed/{selected_video_id}"
            st.components.v1.iframe(embed_url, width=None, height=500, scrolling=False)

            # YouTube video link
            video_url = f"https://www.youtube.com/watch?v={selected_video_id}"
            st.markdown(f"🔗 [Watch on YouTube]({video_url})")

            st.markdown("---")
            st.header("Video Statistics")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Views", format_number(stats.get("view_count", 0)))
            with col2:
                st.metric("Likes", format_number(stats.get("like_count", 0)))
            with col3:
                st.metric("Comments", format_number(stats.get("comment_count", 0)))
            with col4:
                st.metric("Duration", format_duration(stats.get("duration", "")))

            st.markdown("### Video Details")
            detail_col1, detail_col2 = st.columns(2)

            with detail_col1:
                st.write("**Title:**", stats.get("title", "N/A"))
                st.write("**Channel:**", stats.get("channel_title", "N/A"))
                st.write("**Published:**", stats.get("published_at", "N/A"))

            with detail_col2:
                st.write("**Video ID:**", stats.get("video_id", "N/A"))
                st.write("**Channel ID:**", stats.get("channel_id", "N/A"))

            if stats.get("tags"):
                st.write("**Tags:**", ", ".join(stats.get("tags", [])))

            if stats.get("description"):
                with st.expander("Description"):
                    st.write(stats.get("description", ""))

        # Transcript section
        st.markdown("---")
        st.header("Transcript")

        transcript_col1, transcript_col2 = st.columns([3, 1])

        with transcript_col1:
            if st.button("Load Transcript", type="primary"):
                try:
                    with st.spinner("Loading transcript..."):
                        transcript = st.session_state.youtube_helper.get_transcript(
                            selected_video_id
                        )
                        transcript_text = st.session_state.youtube_helper.get_transcript_text(
                            selected_video_id
                        )
                        st.session_state.transcript = transcript
                        st.session_state.transcript_text = transcript_text
                        st.success("Transcript loaded successfully!")
                except TranscriptsDisabled:
                    st.error("Transcripts are disabled for this video")
                except NoTranscriptFound:
                    st.error("No transcript found for this video")
                except Exception as e:
                    st.error(f"Error loading transcript: {str(e)}")

        with transcript_col2:
            if st.session_state.transcript_text:
                transcript_download = st.session_state.transcript_text.encode("utf-8")
                st.download_button(
                    label="Download Transcript",
                    data=transcript_download,
                    file_name=f"transcript_{selected_video_id}.txt",
                    mime="text/plain",
                )

        # Display transcript
        if st.session_state.transcript:
            st.markdown("### Transcript Content")
            st.text_area(
                "Transcript",
                value=st.session_state.transcript_text,
                height=400,
                disabled=True,
            )

            # Show transcript with timestamps
            with st.expander("View Transcript with Timestamps"):
                transcript_df_data = []
                for entry in st.session_state.transcript:
                    transcript_df_data.append(
                        {
                            "Time": f"{entry['start']:.2f}s",
                            "Text": entry["text"],
                        }
                    )
                if transcript_df_data:

                    df = pd.DataFrame(transcript_df_data)
                    st.dataframe(df, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
