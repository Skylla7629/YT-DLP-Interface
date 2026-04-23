import json

import requests


def main():
    res = get_title(
        input("Enter song title: "),
        input("Enter artist name (optional): "),
        int(input("Limit: ") or 5),
    )
    with open("response-TADB.json", "w") as f:
        json.dump(res, f, indent=4)


def get_title(title: str, artist: str = "", limit=5) -> dict:
    url = "https://theaudiodb.com/api/v1/json/2/searchtrack.php"
    params = {"s": artist, "t": title}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["track"]:
            album_id = ""
            for item in data["track"]:
                album_id = item.get("idAlbum", "")
                break
            album_data = get_album(album_id)
            return {
                "track": data["track"],
                "album": album_data,
            }
        else:
            print("No results found.")
            return {}
    else:
        print("Error:", response.status_code)
        return {}


def get_album(id: str):
    url = "https://theaudiodb.com/api/v1/json/2/album.php"
    params = {"m": id}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["album"]:
            return data["album"]
        else:
            print("No results found.")
            return []
    else:
        print("Error:", response.status_code)
        return []


def format(response):
    title = ""
    artist_name = ""
    for item in response["track"]:
        title = item.get("strTrack", "Unknown Title")
        artist_name = item.get("strArtist", "Unknown Artist")

    album_name = ""
    album_artist = ""
    genre = ""
    year = ""
    for item in response["album"]:
        album_name = item.get("strAlbum", "Unknown Album")
        album_artist = item.get("strArtist", "Unknown Artist")
        genre = item.get("strGenre", "Unknown Genre")
        year = item.get("intYearReleased", "Unknown Year")

    return f"{title} by {artist_name} from the album '{album_name}' by {album_artist} - Genre: {genre}, Year: {year}"


if __name__ == "__main__":
    main()

# EOF
