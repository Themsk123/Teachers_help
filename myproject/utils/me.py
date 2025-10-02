import os
import whisper
from pathlib import Path
from yt_dlp import YoutubeDL

# Set FFMPEG path
os.environ["FFMPEG_BINARY"] = r"D:\New movies\ffmpeg\ffmpeg-2025-04-23-git-25b0a8e295-essentials_build\bin\ffmpeg.exe"

output_folder = "mixed_data"
audio_basename = "output_audio"
output_audio_path = os.path.join(output_folder, audio_basename + ".wav")

class MainText:
    def __init__(self, video_url):
        self.video_url = video_url
        self.output_audio_path = output_audio_path
        os.makedirs(output_folder, exist_ok=True)

    def download_video(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_folder, audio_basename),  # No extension!
            'ffmpeg_location': os.environ["FFMPEG_BINARY"],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'quiet': False
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.video_url, download=True)

        return {
            "video_path": self.output_audio_path,
            "metadata": {
                "Title": info_dict.get('title', ''),
                "Author": info_dict.get('uploader', ''),
                "Views": info_dict.get('view_count', 0)
            }
        }

    def video_to_audio(self):
        # Not needed anymore
        pass

    def audio_to_text(self):
        if not os.path.exists(self.output_audio_path):
            print(f"File not found: {self.output_audio_path}")
            return ""

        try:
            print("Transcribing with Whisper...")
            model = whisper.load_model("base")
            result = model.transcribe(self.output_audio_path)
            return result["text"]
        except Exception as e:
            print("Error during transcription:", e)
            return ""

    def last_fun(self):
        self.download_video()
        return self.audio_to_text()

if __name__ == "__main__":
    url = "https://youtu.be/RTHDyKovIBU?si=Ns66a6_7pOPFyHgZ"
    obj = MainText(url)
    transcript = obj.last_fun()
    print("\nTranscription:\n")
    print(transcript)
