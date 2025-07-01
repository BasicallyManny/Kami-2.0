from langchain.tools import Tool
from youtubesearchpython import VideosSearch

def youtube_search(query: str) -> str:
    print(f"[YouTube Tool Invoked] Query: {query}")  # <-- debug confirmation
    try:
        search = VideosSearch(query, limit=3)
        results = search.result().get("result", [])
        if not results:
            return "No YouTube videos found."

        lines = []
        for video in results:
            title = video["title"]
            url = video["link"]
            duration = video.get("duration", "unknown")
            channel = video["channel"]["name"]
            published = video.get("publishedTime", "")
            lines.append(f"{title} ({duration}) by {channel} — {published}\n{url}")
        return "\n\n".join(lines)

    except Exception as e:
        return f"Error in YouTube tool: {str(e)}"

youtube_tool = Tool(
    name="YouTubeSearch",
    func=youtube_search,
    description=(
        "Search YouTube for Minecraft-related videos. "
        "Returns recent tutorials, builds, or gameplay guides. "
        "Input should be a search query like 'netherite farm tutorial'."
    )
)
