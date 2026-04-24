import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main():
    with open("fetched_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    titles = set()
    for item in data:
        title = item.get("input", {}).get("title")
        mbid = item.get("fetched", {}).get("id")
        if title and mbid:
            titles.add((title, mbid))
    with open("titles.json", "w", encoding="utf-8") as f:
        json.dump(sorted(list(titles)), f, ensure_ascii=False, indent=4)

    artists = set()
    for item in data:
        artist_list = item.get("fetched", {}).get("artist-credit", [])
        for artist in artist_list:
            name = artist.get("artist", {}).get("sort-name")
            mbid = artist.get("artist", {}).get("id")
            if name and mbid:
                artists.add((name, mbid))
        album_artist_list = item.get("fetched", {}).get("releases", [])
        for release in album_artist_list:
            artist_list = release.get("artist-credit", [])
            for artist in artist_list:
                name = artist.get("artist", {}).get("sort-name")
                mbid = artist.get("artist", {}).get("id")
                if name and mbid:
                    artists.add((name, mbid))
    with open("artists.json", "w", encoding="utf-8") as f:
        json.dump(sorted(list(artists)), f, ensure_ascii=False, indent=4)

    albums = set()
    album_mbids = set()
    for item in data:
        release_groups = item.get("fetched", {}).get("releases", [])
        for release in release_groups:
            album = release.get("release-group", {}).get("title")
            mbid = release.get("release-group", {}).get("id")
            year = (
                release.get("date", "")[:4]
                if release.get("date")
                else item.get("fetched", {}).get("first-release-date", "")[:4]
            )
            if not year:
                year = "0"
            artist_mbid = (
                release.get("artist-credit", [{}])[0].get("artist", {}).get("id")
            )
            type = release.get("release-group", {}).get("primary-type")
            type_bkup = release.get("release-group", {}).get("secondary-types", [])
            for t in type_bkup:
                if t in ["Compilation", "DJ-mix", "Live"]:
                    type = t
                    break
            if album and mbid and artist_mbid and (type in ["Album", "EP", "Single"]):
                albums.add((album, mbid, year, artist_mbid))
                album_mbids.add(mbid)
    with open("albums.json", "w", encoding="utf-8") as f:
        json.dump(sorted(list(albums)), f, ensure_ascii=False, indent=4)

    tracks_out = set()
    for item in data:
        title_mbid = item.get("fetched", {}).get("id")
        tracks = item.get("fetched", {}).get("releases", [])
        for release in tracks:
            album_mbid = release.get("release-group", {}).get("id")
            track_num = release.get("media", [{}])[0].get("track-offset", 0) + 1

            if title_mbid and album_mbid and track_num and (album_mbid in album_mbids):
                tracks_out.add((title_mbid, album_mbid, track_num))
    with open("tracks.json", "w", encoding="utf-8") as f:
        json.dump(sorted(list(tracks_out)), f, ensure_ascii=False, indent=4)

    title_genres = set()
    for item in data:
        title_mbid = item.get("fetched", {}).get("id")
        genres = item.get("fetched", {}).get("tags", [])
        for genre in genres:
            genre_name = genre.get("name")
            if title_mbid and genre_name:
                title_genres.add((title_mbid, genre_name))
    with open("title_genres.json", "w", encoding="utf-8") as f:
        json.dump(sorted(list(title_genres)), f, ensure_ascii=False, indent=4)

    title_artist = set()
    for item in data:
        title_mbid = item.get("fetched", {}).get("id")
        artist_list = item.get("fetched", {}).get("artist-credit", [])
        for artist in artist_list:
            artist_mbid = artist.get("artist", {}).get("id")
            if title_mbid and artist_mbid:
                title_artist.add((title_mbid, artist_mbid))
    with open("title_artist.json", "w", encoding="utf-8") as f:
        json.dump(sorted(list(title_artist)), f, ensure_ascii=False, indent=4)

    videos = set()
    for item in data:
        source = item.get("input", {})
        title = source.get("video_title")
        url = source.get("URL").strip() if source.get("URL") else None
        desc = source.get("description", "")
        release_date = source.get("releaseDate", "")
        if title and url:
            videos.add((title, url, desc, release_date))
    with open("videos.json", "w", encoding="utf-8") as f:
        json.dump(sorted(list(videos)), f, ensure_ascii=False, indent=4)

    video_title = set()
    for item in data:
        url = (
            item.get("input", {}).get("URL").strip()
            if item.get("input", {}).get("URL")
            else None
        )
        title_mbid = item.get("fetched", {}).get("id")
        if url and title_mbid:
            video_title.add((url, title_mbid))
    with open("video_title.json", "w", encoding="utf-8") as f:
        json.dump(sorted(list(video_title)), f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()


# EOF
