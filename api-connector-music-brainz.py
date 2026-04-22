import requests


def main():
    print(
        # format(
        get_title(
            input("Enter song title: "),
            input("Enter artist name (optional): "),
            int(input("Limit: ") or 5),
        )
        # )
    )


def search(entity, query, limit=5, offset=0) -> list:
    headers = {"User-Agent": "MyMusicDiscoveryApp/1.0.0 ( contact@example.com )"}

    url = f"https://musicbrainz.org/ws/2/{entity}/"
    params = {"query": query, "fmt": "json", "limit": limit, "offset": offset}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        for key, value in data.items():
            if isinstance(value, list):
                return value
        return []
    else:
        print("Error:", response.status_code)
        return []


def get_title(title: str, artist: str = "", limit=5) -> list:
    query = f"recording:{title}"
    if artist:
        query += f" AND artist:{artist}"  # Lucene syntax
    results = search("recording", query, limit)
    if not results:
        print("No results found.")
        return []

    return results


def format(response):
    formatted = []
    for item in response:
        title = item.get("title", "Unknown Title")
        artist_credit = item.get("artist-credit", [])
        artist_name = (
            artist_credit[0].get("name", "Unknown Artist")
            if artist_credit
            else "Unknown Artist"
        )
        genres = item.get("tags", [])
        formatted.append(
            f"{title} by {artist_name} - Genres: {', '.join([genre['name'] for genre in genres])}"
        )
    return formatted


if __name__ == "__main__":
    main()


# EOF
