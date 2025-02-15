from langchain.tools import YouTubeSearchTool
import os

class VideoSummarizer:
    """YouTube Video Summarizer using OpenAI."""
    
    def __init__(self):
        self.search = YouTubeSearchTool(api_key=os.getenv("YOUTUBE_API_KEY"))

    def __call__(self, query: str):
        """Find and summarize a YouTube video."""
        video_info = self.search.run(query)
        return f"📺 **Recommended Video**: {video_info['url']}\n\n🎥 **Summary**: {video_info['summary']}"
