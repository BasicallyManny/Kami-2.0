import yt_dlp
from langchain.tools import Tool
def youtube_search(query: str) -> str:
    """
    Search YouTube for videos based on the provided query.
    Returns a formatted string with video titles, channels, durations, and URLs.
    """
    search_term = query.split(',')[0].strip() if ',' in query else query.strip()
    try:
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        search_query = f"ytsearch5:{search_term}"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(search_query, download=False)
            
            if search_results and 'entries' in search_results:
                formatted_results = []
                for i, video in enumerate(search_results['entries'], 1):
                    if video:
                        title = video.get('title', 'Unknown Title')
                        video_id = video.get('id', '')
                        url = f"https://youtube.com/watch?v={video_id}" if video_id else "No URL"
                        uploader = video.get('uploader', 'Unknown Channel')
                        duration = video.get('duration_string', 'Unknown duration')
                        
                        formatted_results.append(
                            f"{i}. **{title}**\n"
                            f"   Channel: {uploader}\n"
                            f"   Duration: {duration}\n"
                            f"   URL: {url}\n"
                        )
                
                return "\n".join(formatted_results) if formatted_results else "No videos found."
    
    except ImportError:
        pass
    except Exception as e:
        print(f"yt-dlp failed: {e}")
    
    # Method 2: Try youtubesearchpython with error handling
    try:
        from youtubesearchpython import VideosSearch
        
        # Create search with minimal configuration to avoid proxies error
        search = VideosSearch(search_term, limit=5)
        results = search.result()["result"]
        
        if results:
            formatted_results = []
            for i, video in enumerate(results, 1):
                title = video.get("title", "Unknown Title")
                url = video.get("link", "No URL")
                duration = video.get("duration", "Unknown duration")
                channel = video.get("channel", {}).get("name", "Unknown Channel")
                published = video.get("publishedTime", "")
                
                formatted_results.append(
                    f"{i}. **{title}**\n"
                    f"   Channel: {channel}\n"
                    f"   Duration: {duration}\n"
                    f"   Published: {published}\n"
                    f"   URL: {url}\n"
                )
            
            return "\n".join(formatted_results)
    
    except Exception as e:
        if "proxies" in str(e).lower():
            print("Proxies error detected, using fallback...")
        else:
            print(f"YouTube search failed: {e}")
            
# Create YouTube tool
youtube_tool = Tool(
    name="YouTubeSearch",
    func=youtube_search,
    description=(
        "Search YouTube for videos on any topic. "
        "Input should be a search query like 'Minecraft netherite farm tutorial' or 'redstone contraptions'. "
        "Returns video titles, channels, duration, and URLs. Handles technical issues gracefully."
    )
)
    