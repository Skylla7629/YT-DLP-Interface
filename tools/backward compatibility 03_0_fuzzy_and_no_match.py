import json
import os
import re
import sys
from time import sleep

from rapidfuzz import fuzz

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_connector_music_brainz import MusicBrainzAPI
from database_v2 import Database

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
RESET = "\033[0m"


class CompatibilityTool:
    def __init__(self) -> None:
        with open("fetched_data.json", "r", encoding="utf-8") as f:
            self.fetch_full = json.load(f)

        with open("fuzzy_matches.json", "r", encoding="utf-8") as f:
            self.fuzzy_matches = json.load(f)

        with open("no_matches.json", "r", encoding="utf-8") as f:
            self.no_matches = json.load(f)

        self.api = MusicBrainzAPI(
            user_agent="YT-DLP-Interface/1.0 (https://github.com/Skylla7629/YT-DLP-Interface)"
        )

        self.db = Database()

    def check_fuzzy_matches(self):
        for item in self.fuzzy_matches:
            print(
                f"\033[33mFuzzy match with high score ({item['highscore']}):\033[0m {item['input']['title']} by {item['input']['artist']}"
            )
            for i, rec in enumerate(item["fetched"], 1):
                print(
                    f"  - ({i}) - {rec.get('title', 'N/A')} by {rec.get('artist-credit', [{'name': 'N/A'}])[0].get('name', 'N/A')}"
                )
            print()
            res = input("Select option (0) for manual entry: ")
            match res:
                case "0":
                    print("Manual entry selected - skipping to next item")
                    self.no_matches.append(item["input"])
                case _ if res.isdigit() and 1 <= int(res) <= len(item["fetched"]):
                    selected = item["fetched"][int(res) - 1]
                    print(
                        f"Selected: {selected.get('title', 'N/A')} by {selected.get('artist-credit', [{'name': 'N/A'}])[0].get('name', 'N/A')}"
                    )
                    self.fetch_full.append(
                        {
                            "input": item["input"],
                            "fetched": selected,
                        }
                    )
                case _:
                    print("Invalid input - skipping to next item")
            print("-" * 50)

    def process_artist(self, item: dict):
        ## Artist field
        print("Processing artist field...")
        # possible delimiters: [ ' x ', ' X ', ' feat. ', ' ft. ', '&', ', ', '; ' ]
        artists = re.split(r"\s*(?: x | X | feat\. | ft\. |&|,|;)\s*", item["artist"])
        print("List of artists parsed from artist field:")
        sleep(0.2)
        for i, artist in enumerate(artists, 1):
            print(f"  - ({i}) - {artist}")
            sleep(0.05)
        print()
        res = input(f"Use generated list of artists? ({GREEN}y{RESET}/{RED}n{RESET}): ")
        if res.lower() == "y":
            print(f"{GREEN}Using generated list of artists{RESET}")
            sleep(0.2)
        else:
            while True:
                res = input("Enter custom list of artists separated by comma: ")
                custom_artists = [a.strip() for a in res.split(",") if a.strip()]
                if custom_artists:
                    print("Custom list of artists:")
                    for i, artist in enumerate(custom_artists, 1):
                        print(f"  - ({i}) - {artist}")
                    ack = input(f"Is this correct? ({GREEN}y{RESET}/{RED}n{RESET}): ")
                    if ack.lower() == "y":
                        artists = custom_artists
                        print(f"{YELLOW}Using custom list of artists{RESET}")
                        break
                else:
                    print(
                        f"{RED}Invalid input{RESET} - please enter at least one artist"
                    )
        print("|" + "-" * 49)
        sleep(0.5)
        self.storage_object["artists"] = self.check_artists(artists)
        print("-" * 50)
        sleep(0.5)

    def generate_new_artist(self, name):
        print("Generating new entry for artist...")
        new_artist = {
            "name": name,
            "id": self.db.generate_uid("artist"),
        }
        print(
            f"{MAGENTA}Generated new artist{RESET} entry: {new_artist['name']} (ID: {new_artist['id']})"
        )
        sleep(0.1)
        return new_artist

    def check_artists(self, artists: list[str]) -> list[dict]:
        print("Checking artists against MusicBrainz database...")
        final = []
        for artist in artists:
            sleep(1)
            results = self.api.get_artist(artist, limit=5)
            if results:
                score_best = fuzz.ratio(results[0].get("name", ""), artist)
                if score_best == 100:
                    print(
                        f"{GREEN}Exact match found{RESET} for artist: {artist} -> {results[0].get('name', 'N/A')} (MBID: {results[0].get('id', 'N/A')})"
                    )
                    sleep(0.1)
                    final.append(results[0])
                    continue
                print(f"{YELLOW}Results for artist:{RESET} {artist}")
                for i, res in enumerate(results, 1):
                    score = fuzz.ratio(res.get("name", ""), artist)
                    print(
                        f"  - ({i}) - ({round(score, 0)}) - {res.get('name', 'N/A')} (MBID: {res.get('id', 'N/A')})"
                    )
                    sleep(0.05)
                print()
                res = input(f"Select correct artist ({RED}0 for new{RESET}): ")
                if res.isdigit() and 1 <= int(res) <= len(results):
                    selected = results[int(res) - 1]
                    final.append(selected)
                    print(
                        f"{GREEN}Selected artist:{RESET} {selected.get('name', 'N/A')} (MBID: {selected.get('id', 'N/A')})"
                    )
                else:
                    final.append(self.generate_new_artist(artist))
            else:
                print(f"{RED}No results found for artist:{RESET} {artist}")
                final.append(self.generate_new_artist(artist))
            print("|" + "-" * 49)
            sleep(0.5)
        return final

    def generate_new_album(self, name, artist_mbid):
        while True:
            res = input("Enter Album Year (Optional): ")
            if res.strip() == "":
                year = "0"
                break
            elif res.isdigit() and 1900 <= int(res) <= 9999:
                year = res.strip()
                print(f"Album Year: {year}")
                break
            else:
                print(
                    f"{RED}Invalid input{RESET} - please enter a valid year or leave blank"
                )
        print("Generating new entry for album...")
        new_album = {
            "title": name,
            "id": self.db.generate_uid("album"),
            "year": year,
            "artist_mbid": artist_mbid,
        }
        print(
            f"{MAGENTA}Generated new album{RESET} entry: {new_album['title']} (ID: {new_album['id']})"
        )
        sleep(0.1)
        return new_album

    def check_album(self, album: str, album_artist: str, album_artist_mbid: str):
        print("Checking album against MusicBrainz database...")
        sleep(1)
        results = self.api.get_album(album, artist=album_artist, limit=5)
        if results:
            score_best = fuzz.ratio(results[0].get("title", ""), album)
            if score_best == 100:
                print(
                    f"{GREEN}Exact match found{RESET} for album: {album} -> {results[0].get('title', 'N/A')} (MBID: {results[0].get('id', 'N/A')})"
                )
                sleep(0.1)
                return results[0]
            print(f"{YELLOW}Results for album:{RESET} {album}")
            for i, res in enumerate(results, 1):
                score = fuzz.ratio(res.get("title", ""), album)
                print(
                    f"  - ({i}) - ({round(score, 0)}) - {res.get('title', 'N/A')} (MBID: {res.get('id', 'N/A')})"
                )
                sleep(0.05)
            print()
            res = input(f"Select correct album ({RED}0 for manual entry{RESET}): ")
            if res.isdigit() and 1 <= int(res) <= len(results):
                selected = results[int(res) - 1]
                print(
                    f"{GREEN}Selected album:{RESET} {selected.get('title', 'N/A')} (MBID: {selected.get('id', 'N/A')})"
                )
                year = selected.get("first-release-date", "")[:4]
                if not year:
                    year = "0"
                object = {
                    "title": selected.get("title", ""),
                    "id": selected.get("id", ""),
                    "year": year,
                    "artist_mbid": album_artist_mbid,
                }
                return object
            else:
                return self.generate_new_album(album, album_artist_mbid)
        else:
            print(f"{RED}No results found for album:{RESET} {album}")
            return self.generate_new_album(album, album_artist_mbid)

    def process_album(self, item: dict):
        print("Processing album field...")
        album = item.get("album", "")
        album_artist = item.get("album_artist", "")
        print(f"Album: {album}")
        print(f"Album Artist: {album_artist}")
        res = input(f"Keep album info? ({GREEN}y{RESET}/{RED}n{RESET}): ")
        if res.lower() == "y":
            print(f"{GREEN}Keeping album info{RESET}")
            sleep(0.2)
        else:
            while True:
                res = input("Enter custom album name: ")
                if res.strip():
                    album = res.strip()
                    print(f"Custom album name: {album}")
                    break
                else:
                    print(
                        f"{RED}Invalid input{RESET} - please enter a valid album name"
                    )
            while True:
                res = input("Enter custom album artist: ")
                if res.strip():
                    album_artist = res.strip()
                    print(f"Custom album artist: {album_artist}")
                    break
                else:
                    print(
                        f"{RED}Invalid input{RESET} - please enter a valid album artist"
                    )
            print(f"{YELLOW}Using custom album info{RESET}")
            sleep(0.2)
        album_artist = self.check_artists([album_artist])[0]
        self.storage_object["album"] = self.check_album(
            album, str(album_artist.get("name")), str(album_artist.get("id"))
        )
        print("-" * 50)
        sleep(0.5)

    def process_genre(self, item: dict):
        pass

    def generate_new_title(self, name):
        print("Generating new entry for title...")
        new_title = {
            "title": name,
            "id": self.db.generate_uid("title"),
        }
        print(
            f"{MAGENTA}Generated new title{RESET} entry: {new_title['title']} (ID: {new_title['id']})"
        )
        sleep(0.1)
        return new_title

    def check_no_matches(self):
        for item in self.no_matches:
            print(f"\033[31mNo match for:\033[0m {item['title']} by {item['artist']}")
            print("Manual entry required.")
            print("Data:")
            print(f"""
    Title:          {item["title"]}
    Artist:         {item["artist"]}
    Album:          {item.get("album", "N/A")}
    Album Artist:   {item.get("album_artist", "N/A")}
    Genre:          {item.get("genre", "N/A")}
""")

            self.storage_object = {
                "input": item,
                "title": self.generate_new_title(item["title"]),
            }

            self.process_artist(item)
            self.process_album(item)
            self.process_genre(item)

            try:
                with open("test.json", "r", encoding="utf-8") as f:
                    test_data = json.load(f)
            except FileNotFoundError:
                test_data = []
            test_data.append(self.storage_object)
            with open("test.json", "w", encoding="utf-8") as f:
                json.dump(test_data, f, ensure_ascii=False, indent=4)

    def save(self):
        with open("fetched_data.json", "w", encoding="utf-8") as f:
            json.dump(self.fetch_full, f, ensure_ascii=False, indent=4)
        with open("no_matches.json", "w", encoding="utf-8") as f:
            json.dump(self.no_matches, f, ensure_ascii=False, indent=4)

    def run(self):
        # self.check_fuzzy_matches()
        self.check_no_matches()
        # self.save()


if __name__ == "__main__":
    tool = CompatibilityTool()
    tool.run()


# EOF
