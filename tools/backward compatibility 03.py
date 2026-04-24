import json
import os
import sys
from time import sleep

from rapidfuzz import fuzz

from api import MusicBrainzAPI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main():
    with open(input("Old DB Unload File Path: "), "r") as f:
        data = json.load(f)

    api = MusicBrainzAPI(
        user_agent="YT-DLP-Interface/1.0 (https://github.com/Skylla7629/YT-DLP-Interface)"
    )

    fetched_data = []
    fuzzy_matches = []
    no_matches = []

    for i, item in enumerate(data, 1):
        title = item.get("title", "")
        artist = item.get("artist", "")

        if title.startswith("Nightcore - "):
            search_title = title[len("Nightcore - ") :]
        else:
            search_title = title
        sleep(1)

        print(f"({i}/{len(data)})", end=" ")
        recordings = api.get_title(search_title, artist, limit=1)
        if recordings:
            recording = recordings[0]
            score = fuzz.ratio(recording.get("title", ""), search_title)
            if score == 100:
                print(
                    f"Fetched data for: {title} by {artist}\n\033[35m-- Score: {round(score, 1)} -- \033[0m{recording['title']} by {recording['artist-credit'][0]['name']}"
                )
                fetched_data.append(
                    {
                        "input": item,
                        "fetched": recording,
                    }
                )
            else:
                print(f"\033[33mNo exact match for:\033[0m {title} by {artist}")
                fuzzy_matches.append(
                    {
                        "input": item,
                        "fetched": recordings,
                        "highscore": round(score, 1),
                    }
                )

        else:
            print(f"\033[31mNo results for:\033[0m {title} by {artist}")
            no_matches.append(item)

    with open("fetched_data.json", "w") as f:
        json.dump(fetched_data, f, indent=4)
    with open("fuzzy_matches.json", "w") as f:
        json.dump(fuzzy_matches, f, indent=4)
    with open("no_matches.json", "w") as f:
        json.dump(no_matches, f, indent=4)


if __name__ == "__main__":
    main()


# EOF
