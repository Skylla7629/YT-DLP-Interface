# tool to download a json with a url list

from yt_dlp import YoutubeDL
import json



def download_playlist(urls):
    config = get_config()
    ffmpeg_path = config.get('FFMPEG_PATH')

    if not ffmpeg_path:
        print("FFmpeg location not set in config.json")
        return
    
    optionsDownload = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': 'audio/%(title)s.%(ext)s',
        'verbose': False,
        'silent': True,

        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': ffmpeg_path,
    }

    data = {}

    with YoutubeDL(optionsDownload) as ydl:        
        for url in urls:
            data.update(download_single(ydl, url, optionsDownload))
            print(f"Downloaded {url}")
            print(f"Progress: \033[35m{len(data)}/{len(urls)}\033[0m")

    return data        


def download_single(ydl, url, options):
    video = ydl.extract_info(url, download=True)

    data = {}

    title = video.get('title', 'No title')
    url = video.get('webpage_url', 'No url')
    description = video.get('description', 'No description')
    releaseDate = video.get('upload_date', 'No release date')

    if releaseDate != 'No release date':
        releaseDate = f"{releaseDate[:4]}-{releaseDate[4:6]}-{releaseDate[6:]}"

    data[title] = {
        'title': title,
        'url': url,
        'description': description,
        'releaseDate': releaseDate
    }
    return data


def get_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config


def load_json():
    with open('urls.json', 'r') as f:
        urls = json.load(f)
    return urls


def save_data(data):
    with open('videoInfos.json', 'w') as f:
        json.dump(data, f, indent=4)


def main():
    urls = load_json()
    data = download_playlist(urls)
    save_data(data)


if __name__ == "__main__":
    main()


# E