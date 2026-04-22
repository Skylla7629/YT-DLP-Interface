from sqlite3.dbapi2 import paramstyle

import requests


def main():
    print(
        format(
            get_title(
                input("Enter song title: "),
                input("Enter artist name (optional): "),
                int(input("Limit: ") or 5),
            )
        )
    )


def get_title(title: str, artist: str = "", limit=5) -> list:
    url = "https://theaudiodb.com/api/v1/json/2/searchtrack.php"
    params = {"s": artist, "t": title}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["track"]:
            return data["track"][:limit]
        else:
            print("No results found.")
            return []
    else:
        print("Error:", response.status_code)
        return []


def format(response):
    formatted = []
    for item in response:
        title = item.get("strTrack", "Unknown Title")
        artist_name = item.get("strArtist", "Unknown Artist")
        album_name = item.get("strAlbum", "Unknown Album")

        genre = item.get("strGenre", "Unknown Genre") or "Unknown Genre"
        formatted.append(f"{title} by {artist_name} - Genre: {genre}")
    return formatted


if __name__ == "__main__":
    main()

# EOF
