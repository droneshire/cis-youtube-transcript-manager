"""YouTubeHelper class for interacting with YouTube API and transcripts."""

from typing import Any, Dict, List, Optional

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled


class YouTubeHelper:
    """Helper class for YouTube API operations and transcript retrieval."""

    def __init__(self, api_key: str):
        """
        Initialize YouTubeHelper with API key.

        Args:
            api_key: YouTube Data API v3 key
        """
        self.api_key = api_key
        self.youtube = build("youtube", "v3", developerKey=api_key)
        self.transcript_api = YouTubeTranscriptApi()

    def get_video_ids_from_channel(self, channel_id: str, max_results: int = 50) -> List[str]:
        """
        Get video IDs from a YouTube channel.

        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to retrieve (default: 50, max: 50)

        Returns:
            List of video IDs
        """
        video_ids: List[str] = []
        next_page_token = None

        while len(video_ids) < max_results:
            request = self.youtube.search().list(  # pylint: disable=no-member
                part="id",
                channelId=channel_id,
                type="video",
                maxResults=min(50, max_results - len(video_ids)),
                pageToken=next_page_token,
                order="date",
            )
            response = request.execute()

            for item in response.get("items", []):
                video_ids.append(item["id"]["videoId"])

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return video_ids[:max_results]

    def get_video_ids_from_playlist(self, playlist_id: str, max_results: int = 50) -> List[str]:
        """
        Get video IDs from a YouTube playlist.

        Args:
            playlist_id: YouTube playlist ID
            max_results: Maximum number of videos to retrieve (default: 50, max: 50)

        Returns:
            List of video IDs
        """
        video_ids: List[str] = []
        next_page_token = None

        while len(video_ids) < max_results:
            request = self.youtube.playlistItems().list(  # pylint: disable=no-member
                part="contentDetails",
                playlistId=playlist_id,
                maxResults=min(50, max_results - len(video_ids)),
                pageToken=next_page_token,
            )
            response = request.execute()

            for item in response.get("items", []):
                video_ids.append(item["contentDetails"]["videoId"])

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return video_ids[:max_results]

    def get_video_ids_from_search(self, query: str, max_results: int = 50) -> List[str]:
        """
        Get video IDs from a search query.

        Args:
            query: Search query string
            max_results: Maximum number of videos to retrieve (default: 50, max: 50)

        Returns:
            List of video IDs
        """
        video_ids: List[str] = []
        next_page_token = None

        while len(video_ids) < max_results:
            request = self.youtube.search().list(  # pylint: disable=no-member
                part="id",
                q=query,
                type="video",
                maxResults=min(50, max_results - len(video_ids)),
                pageToken=next_page_token,
                order="relevance",
            )
            response = request.execute()

            for item in response.get("items", []):
                video_ids.append(item["id"]["videoId"])

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return video_ids[:max_results]

    def get_video_stats(self, video_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary containing video statistics and metadata
        """
        request = self.youtube.videos().list(  # pylint: disable=no-member
            part="statistics,snippet,contentDetails", id=video_id
        )
        response = request.execute()

        if not response.get("items"):
            return {}

        item = response["items"][0]
        stats = item.get("statistics", {})
        snippet = item.get("snippet", {})
        content_details = item.get("contentDetails", {})

        return {
            "video_id": video_id,
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "channel_id": snippet.get("channelId"),
            "channel_title": snippet.get("channelTitle"),
            "published_at": snippet.get("publishedAt"),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "duration": content_details.get("duration"),
            "tags": snippet.get("tags", []),
        }

    def get_video_stats_batch(self, video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for multiple videos.

        Args:
            video_ids: List of YouTube video IDs

        Returns:
            Dictionary mapping video IDs to their statistics
        """
        # YouTube API allows up to 50 IDs per request
        batch_size = 50
        all_stats = {}

        for i in range(0, len(video_ids), batch_size):
            batch = video_ids[i : i + batch_size]
            request = self.youtube.videos().list(  # pylint: disable=no-member
                part="statistics,snippet,contentDetails", id=",".join(batch)
            )
            response = request.execute()

            for item in response.get("items", []):
                video_id = item["id"]
                stats = item.get("statistics", {})
                snippet = item.get("snippet", {})
                content_details = item.get("contentDetails", {})

                all_stats[video_id] = {
                    "video_id": video_id,
                    "title": snippet.get("title"),
                    "description": snippet.get("description"),
                    "channel_id": snippet.get("channelId"),
                    "channel_title": snippet.get("channelTitle"),
                    "published_at": snippet.get("publishedAt"),
                    "view_count": int(stats.get("viewCount", 0)),
                    "like_count": int(stats.get("likeCount", 0)),
                    "comment_count": int(stats.get("commentCount", 0)),
                    "duration": content_details.get("duration"),
                    "tags": snippet.get("tags", []),
                }

        return all_stats

    def get_transcript(
        self,
        video_id: str,
        languages: Optional[List[str]] = None,
        preserve_formatting: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Get transcript for a given video ID.

        Args:
            video_id: YouTube video ID
            languages: List of language codes to try (e.g., ['en', 'es']).
                      If None, tries to fetch any available transcript.
            preserve_formatting: If True, preserves formatting like line breaks

        Returns:
            List of transcript entries, each containing:
            - text: The transcript text
            - start: Start time in seconds
            - duration: Duration in seconds

        Raises:
            TranscriptsDisabled: If transcripts are disabled for the video
            NoTranscriptFound: If no transcript is available
        """
        try:
            if languages:
                transcript = self.transcript_api.fetch(video_id, languages=languages)
            else:
                transcript = self.transcript_api.fetch(video_id)

            transcript_list = transcript.to_raw_data()

            if preserve_formatting:
                return transcript_list

            # Format transcript entries
            formatted_transcript = []
            for entry in transcript_list:
                formatted_transcript.append(
                    {
                        "text": entry["text"],
                        "start": entry["start"],
                        "duration": entry.get("duration", 0),
                    }
                )
            return formatted_transcript

        except (TranscriptsDisabled, NoTranscriptFound) as e:
            raise e

    def get_transcript_text(
        self,
        video_id: str,
        languages: Optional[List[str]] = None,
        separator: str = " ",
    ) -> str:
        """
        Get transcript as a single text string.

        Args:
            video_id: YouTube video ID
            languages: List of language codes to try (e.g., ['en', 'es']).
                      If None, tries to fetch any available transcript.
            separator: String to join transcript segments (default: space)

        Returns:
            Complete transcript text as a single string

        Raises:
            TranscriptsDisabled: If transcripts are disabled for the video
            NoTranscriptFound: If no transcript is available
        """
        transcript = self.get_transcript(video_id, languages=languages)
        return separator.join([entry["text"] for entry in transcript])
