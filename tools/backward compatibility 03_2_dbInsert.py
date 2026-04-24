import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database_v2 import Database

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
RESET = "\033[0m"


def main():
    db = Database()
    db.main_table_init()

    r = input("Clear existing data in database? (y/N): ").lower()
    if r == "y":
        db.clear_all_data()
        r2 = input(
            "Commit delete operations? !WARNING this will delete all data and is irreversible (y/N): "
        ).lower()
        if r2 == "y":
            db.commit()
            print("All existing data cleared from database | COMMIT")
        else:
            db.rollback()
            print("Delete operations cancelled - existing data has been preserved")

    # insert artists
    print("Inserting artists...")
    with open("artists.json", "r") as f:
        artists = json.load(f)
    x = 1
    for name, mbid in artists:
        db.insert_artist(name, mbid)
        print(f"({x}/{len(artists)}) Inserted artist: {name} with mbid: {mbid}")
        x += 1
    print(f"Inserted {len(artists)} artists | COMMIT")
    db.commit()

    # insert videos
    print("Inserting videos...")
    with open("videos.json", "r") as f:
        videos = json.load(f)
    x = 1
    for title, url, description, releaseDate in videos:
        db.insert_video(title, url, "Youtube", releaseDate, description)
        print(f"({x}/{len(videos)}) Inserted video: {title} with url: {url}")
        x += 1
    print(f"Inserted {len(videos)} videos | COMMIT")
    db.commit()

    # insert titles
    print("Inserting titles...")
    with open("titles.json", "r") as f:
        titles = json.load(f)
    x = 1
    for name, mbid in titles:
        db.insert_title(name, mbid)
        print(f"({x}/{len(titles)}) Inserted title: {name} with mbid: {mbid}")
        x += 1
    print(f"Inserted {len(titles)} titles | COMMIT")
    db.commit()

    # insert albums
    print("Inserting albums...")
    with open("albums.json", "r") as f:
        albums = json.load(f)
    x = 1
    for name, mbid, releaseDate, artist_mbid in albums:
        artist_id = db.get_id_by_mbid("artist", artist_mbid)
        if artist_id:
            db.insert_album(name, releaseDate, artist_id, mbid)
            print(f"({x}/{len(albums)}) Inserted album: {name} with mbid: {mbid}")
            x += 1
        else:
            raise RuntimeError(f"Artist with mbid {artist_mbid} not found in database")
    print(f"Inserted {len(albums)} albums | COMMIT")
    db.commit()

    # insert tracks
    print("Inserting tracks...")
    with open("tracks.json", "r") as f:
        tracks = json.load(f)
    x = 1
    for title_mbid, album_mbid, track_num in tracks:
        title_id = db.get_id_by_mbid("title", title_mbid)
        album_id = db.get_id_by_mbid("album", album_mbid)
        if title_id and album_id:
            db.insert_track(title_id, album_id, track_num)
            print(
                f"({x}/{len(tracks)}) Inserted track: t:{title_mbid} | a:{album_mbid} | num:{track_num}"
            )
            x += 1
        else:
            if title_id:
                print(
                    f"Title with mbid {title_mbid} found in database\nbut {RED}Album with mbid {album_mbid} not found{RESET} - attempting to find album by name and artist and link track to it"
                )
                with open("albums.json", "r") as f:
                    albums = json.load(f)
                for name, mbid, releaseDate, artist_mbid in albums:
                    if mbid == album_mbid:
                        artist_id = db.get_id_by_mbid("artist", artist_mbid)
                        if artist_id:
                            album_id = db.get_album(name, artist_id)
                            if album_id:
                                print(
                                    f"{GREEN}Found album:{RESET} {name} by artist with mbid {artist_mbid} - linking track to album with id {album_id[0][0]}"
                                )
                                db.insert_track(title_id, album_id[0][0], track_num)
                                print(
                                    f"({x}/{len(tracks)}) Inserted track: t:{title_mbid} | a:{album_mbid} | num:{track_num}"
                                )
                                x += 1
                                break
                if not album_id:
                    raise RuntimeError(
                        f"Album with mbid {album_mbid} not found in database even after attempting to find by name and artist"
                    )
            else:
                raise RuntimeError(
                    f"Title with mbid {title_mbid} not found in database"
                )
    print(f"Inserted {len(tracks)} tracks | COMMIT")
    db.commit()

    # insert title_artist
    print("Inserting title_artist relationships...")
    with open("title_artist.json", "r") as f:
        title_artist = json.load(f)
    x = 1
    for title_mbid, artist_mbid in title_artist:
        title_id = db.get_id_by_mbid("title", title_mbid)
        artist_id = db.get_id_by_mbid("artist", artist_mbid)
        if title_id and artist_id:
            db.insert_title_artist(title_id, artist_id)
            print(
                f"({x}/{len(title_artist)}) Inserted title_artist relationship: t:{title_mbid} | a:{artist_mbid}"
            )
            x += 1
        else:
            raise RuntimeError(
                f"Title with mbid {title_mbid} or Artist with mbid {artist_mbid} not found in database"
            )
    print(f"Inserted {len(title_artist)} title_artist relationships | COMMIT")
    db.commit()

    # insert video_title
    print("Inserting video_title relationships...")
    with open("video_title.json", "r") as f:
        video_title = json.load(f)
    x = 1
    for url, title_mbid in video_title:
        video_id = db.get_video_id_by_url(url)
        title_id = db.get_id_by_mbid("title", title_mbid)
        if title_id and video_id:
            db.insert_video_title(video_id, title_id)
            print(
                f"({x}/{len(video_title)}) Inserted video_title relationship: v:{url} | t:{title_mbid}"
            )
            x += 1
        else:
            raise RuntimeError(
                f"Video with url {url} or Title with mbid {title_mbid} not found in database"
            )
    print(f"Inserted {len(video_title)} video_title relationships | COMMIT")
    db.commit()

    # make genres (fuzzymatching against set list of genres)


if __name__ == "__main__":
    main()

# EOF
