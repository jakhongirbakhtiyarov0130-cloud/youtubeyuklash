import os
import yt_dlp
import asyncio

# YouTube blokirovkalarini aylanib o'tish uchun "brauzer" ma'lumotlari
YDL_OPTIONS = {
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    # Eng muhim qism: YouTube-ni aldash uchun brauzer sarlavhalari
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }
}

async def download_video(url: str, output_path: str = "downloads"):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    opts = {
        **YDL_OPTIONS,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'noplaylist': True,
    }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = await asyncio.to_thread(ydl.extract_info, url, download=True)
        return ydl.prepare_filename(info)

async def download_audio(url: str, output_path: str = "downloads"):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    opts = {
        **YDL_OPTIONS,
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
    }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = await asyncio.to_thread(ydl.extract_info, url, download=True)
        base = ydl.prepare_filename(info)
        return os.path.splitext(base)[0] + ".mp3"
