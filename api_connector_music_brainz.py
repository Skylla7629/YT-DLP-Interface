import json

import requests


class MusicBrainzAPI:
    BASE_URL = "https://musicbrainz.org/ws/2/"

    def __init__(self, user_agent: str):
        self.headers = {"User-Agent": user_agent}

    ## Search
    def search(self, entity: str, query: str, limit=5, offset=0) -> list:
        url = f"{self.BASE_URL}{entity}/"
        params = {"query": query, "fmt": "json", "limit": limit, "offset": offset}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            data = response.json()
            for key, value in data.items():
                if isinstance(value, list):
                    return value
            return []
        else:
            print("Error:", response.status_code)
            return []

    def get_title(
        self, title: str, artist: str = "", artist_id: str = "", limit=5
    ) -> list:
        if artist_id:
            query = f"recording:{title} AND arid:{artist_id}"
        else:
            query = f"recording:{title}"
            if artist:
                query += f" AND artist:{artist}"  # Lucene syntax
        return self.search("recording", query, limit)

    def get_artist(self, name: str, limit=5) -> list:
        query = f"artist:{name}"
        return self.search("artist", query, limit)

    def get_album(
        self, title: str, artist: str = "", artist_id: str = "", limit=5
    ) -> list:
        if artist_id:
            query = f"release-group:{title} AND arid:{artist_id}"
        else:
            query = f"release-group:{title}"
            if artist:
                query += f" AND artist:{artist}"
        return self.search("release-group", query, limit)

    ## Lookup
    def id_lookup(self, entity, mbid: str) -> dict:
        url = f"{self.BASE_URL}{entity}/{mbid}"
        params = {"fmt": "json"}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error:", response.status_code)
            return {}

    def get_title_by_id(self, mbid: str) -> dict:
        return self.id_lookup("recording", mbid)

    def get_artist_by_id(self, mbid: str) -> dict:
        return self.id_lookup("artist", mbid)

    def get_album_by_id(self, mbid: str) -> dict:
        return self.id_lookup("release-group", mbid)


def main():
    api = MusicBrainzAPI(
        user_agent="YT-DLP-Interface/1.0 (https://github.com/Skylla7629/YT-DLP-Interface)"
    )
    res = api.get_title(
        input("Enter song title: "),
        input("Enter artist name (optional): "),
        "",  # artist_id is not used in this example
        int(input("Limit: ") or 5),
    )
    with open("response-MB.json", "w") as f:
        json.dump(res, f, indent=4)


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
