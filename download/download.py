import json
import os
import time

import dotenv
from yt_dlp import YoutubeDL
from yt_dlp.networking.impersonate import ImpersonateTarget

from database import Database


class Downloader:
    def __init__(
        self,
        url,
        database: Database,
        cookies_from_browser: bool = False,
        keep_video: bool = False,
        get_thumbnail: bool = False,
        postprocess: bool = False,
    ):
        self.videoInfos = None
        self.database: Database = database

        dotenv.load_dotenv("./.env")

        self.ffmpeg_path = os.getenv("FFMPEG_PATH", "")
        self.cookies_path = os.getenv("COOKIES_PATH", "")
        path = os.getenv("OUTPUT_TEMPLATE", "")
        if path.endswith("/"):
            path = path[:-1]
        date = time.strftime("%Y-%d-%m")
        self.outfile = f"{path}/yt-dlp-{date}/%(title)s.%(ext)s"

        self.format = os.getenv("FORMAT", "bestaudio/best")

        self.cookies_from_browser = cookies_from_browser
        self.browser = os.getenv("BROWSER", "")

        self.postprocess = postprocess
        self.keep_video = keep_video
        self.get_thumbnail = get_thumbnail

        self.url = url

    def download_playlist(self):
        if self.url:
            self.videoInfos = self.extract_info(self.url)
            self.save()

    def save(self):
        if not self.videoInfos:
            return
        try:
            with open("videoInfos.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        data.update(self.videoInfos)

        with open("videoInfos.json", "w") as f:
            json.dump(data, f, indent=4)

        print("Download complete!")

    def extract_info(self, url):
        if not self.ffmpeg_path:
            print("FFmpeg path not set in environment variables.")
            return
        if not self.outfile:  # downloadPath + "/%(title)s.%(ext)s"
            print("Output file template not set.")
            return

        impersonateTgt = ImpersonateTarget.from_str("chrome-136")

        optionsDownload = {
            "format": self.format,
            "remote_components": ["ejs:github"],
            "outtmpl": self.outfile,
            "impersonate": impersonateTgt,
            "use_curl_cffi": True,
            "extractor_args": {
                "youtubetab": {
                    "skip": ["authcheck"],  # Bypasses the failing tab verification
                },
                "youtube": {
                    "player_client": [
                        "web",
                        "android",
                    ],  # ISO is broken, so we stick to these
                    "skip": ["dash", "hls"],  # Speed up by avoiding manifests
                },
            },
            "js_runtimes": {
                "deno": {},  # Pass an empty dict to use default system path
                "node": {},  # Fallback
            },
            "fragment_retries": 10,  # retry each fragment up to 10 times
            "retries": 3,  # retry full download on error
            "skip_unavailable_fragments": False,
            "ffmpeg_location": self.ffmpeg_path,
            "ignoreerrors": True,
            "keepvideo": self.keep_video,
            "writethumbnail": self.get_thumbnail,
        }

        if self.cookies_from_browser:
            optionsDownload["cookiesfrombrowser"] = (self.browser, None, None, None)
        else:
            optionsDownload["cookiefile"] = self.cookies_path

        if self.postprocess:
            optionsDownload["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
                {
                    "key": "EmbedThumbnail",  # Optional: adds album art
                },
                {
                    "key": "FFmpegMetadata",  # Optional: adds title/artist tags
                },
            ]

        data = {}

        with YoutubeDL(optionsDownload) as ydl:
            playlist = None
            try:
                playlist = ydl.extract_info(url, download=True)
            except Exception as e:
                print(e)

            if not playlist:
                return

            if "entries" in playlist:
                for video in playlist["entries"]:
                    self.video_data(video, data)
            else:
                self.video_data(playlist, data)

        return data

    def video_data(self, video, data):
        title = video.get("title", "No title")
        url = video.get("webpage_url", "No url")
        description = video.get("description", "No description")
        releaseDate = video.get("upload_date", "No release date")

        if releaseDate != "No release date":
            releaseDate = f"{releaseDate[:4]}-{releaseDate[4:6]}-{releaseDate[6:]}"

        data[title] = {
            "title": title,
            "url": url,
            "description": description,
            "releaseDate": releaseDate,
        }


# EOF
