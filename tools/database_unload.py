import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import database


def main():
    db = database.Database()
    data = db.get_titles()
    out = []
    for entry in data:
        out.append(
            {
                "id": entry[0],
                "title": entry[1],
                "video_title": entry[2],
                "artist": entry[3],
                "album": entry[4],
                "album_artist": entry[5],
                "genre": entry[6],
                "releaseDate": entry[8],
                "URL": entry[9],
                "description": entry[10],
            }
        )
    with open("titles.json", "w") as f:
        json.dump(out, f, indent=4)


if __name__ == "__main__":
    main()


# EOF
