import os
import whisper
from moviepy import VideoFileClip
from pathlib import Path
import speech_recognition as sr
from pprint import pprint
from PIL import Image
import tempfile
from yt_dlp import YoutubeDL


# Set FFMPEG path
os.environ["FFMPEG_BINARY"] = r"D:\New movies\ffmpeg\ffmpeg-2025-04-23-git-25b0a8e295-essentials_build\bin\ffmpeg.exe"

video_url = "https://youtu.be/aVqgUT2-NBw?si=Ws7PR6rmfJ_-whKS"

output_video_path = "video_data"
output_folder = "mixed_data"
output_audio_path = "mixed_data/output_audio.wav"
filepath=output_video_path + "/input_vid.mp4"
def download_video(video_url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'ffmpeg_location': r"D:\New movies\ffmpeg\ffmpeg-2025-04-23-git-25b0a8e295-essentials_build\bin",
        'outtmpl': os.path.join(output_video_path, 'input_vid.%(ext)s'),
        'quiet': False,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        video_ext = info_dict.get('ext', 'mp4')
        filepath = os.path.join(output_video_path, f"input_vid.{video_ext}")
    
    return {
        "video_path": filepath,
        "metadata": {
            "Title": info_dict.get('title', ''),
            "Author": info_dict.get('uploader', ''),
            "Views": info_dict.get('view_count', 0)
        }
    }
    
download_video(video_url=video_url)
