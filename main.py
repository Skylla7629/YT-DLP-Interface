import argparse
import json
import sys

from database import Database
from directedit import DirectEdit
from download import Downloader


class Yt_dlp_cli:
    def __init__(self):
        self.downloader = None
        self.database = Database()
        self.dirEditor = None

    def run(self):

        parser = argparse.ArgumentParser(description="YT-dlp CLI Tool")
        parser.add_argument(
            "--url", "-u", type=str, help="URL of the playlist to download"
        )
        parser.add_argument("--edit", "-e", action="store_true", help="Edit mode")
        parser.add_argument(
            "--db-init", action="store_true", help="Initialize database"
        )
        parser.add_argument(
            "--edit-directory",
            "-d",
            type=str,
            help="Automatically edit mp3s in this directory with data from database",
        )
        parser.add_argument(
            "--edit-existing",
            "-x",
            action="store_true",
            help="Edit existing entries in database",
        )
        parser.add_argument(
            "--keep-video",
            "-k",
            action="store_true",
            help="Keep video files after download (when postprocessing to mp3 is enabled)",
        )
        parser.add_argument(
            "--cookies-from-browser",
            "-b",
            action="store_true",
            help="Use cookies from browser configured in environment variables",
        )
        parser.add_argument(
            "--get-thumbnail",
            "-t",
            action="store_true",
            help="Get thumbnail for downloaded videos",
        )
        parser.add_argument(
            "--no-postprocessing",
            "-p",
            action="store_true",
            help="Disable postprocessing to mp3",
        )
        parser.add_argument(
            "--duplicate-check",
            "-c",
            action="store_true",
            help="Check for duplicate mp3 files in a directory and remove them",
        )

        try:
            args = parser.parse_args()
        except:
            sys.exit(1)

        print("YT-dlp CLI is running...")

        if args.db_init:
            print("Initializing database...")
            self.database.main_table_init()
            print("Database initialized.")

        if not args.url:
            args.url = input("If you wish to download a playlist enter URL now: ")

        if args.url:
            print("Downloading URL:", args.url)
            if args.keep_video:
                print("Keeping video files after download.")
            self.downloader = Downloader(
                args.url,
                database=self.database,
                keep_video=args.keep_video,
                cookies_from_browser=args.cookies_from_browser,
                get_thumbnail=args.get_thumbnail,
                postprocess=not args.no_postprocessing,
            )
            self.downloader.download_playlist()

        if args.edit:
            print("Editing mode")
            self.edit_mode()

        if args.edit_existing:
            self.edit_existing()

        if args.edit_directory:
            print("Editing mp3s in directory:", args.edit_directory)

            self.dirEditor = DirectEdit(args.edit_directory, database=self.database)
            self.dirEditor.edit_files()

        if args.duplicate_check:
            from tools.duplicateAudio import main as duplicate_main

            print("Checking for duplicate mp3 files in directory...")
            duplicate_main()

    def edit_existing(self):
        while True:
            search_option = input(
                "Search by \n\t(1) Title\n\t(2) Title + Artist\n\t(q) Quit\n\n: "
            )
            results = None
            match search_option:
                case "1":
                    search_title = input("Enter title to search: ")
                    results = self.entry_search(search_title)
                case "2":
                    search_title = input("Enter title to search: ")
                    search_artist = input("Enter artist to search: ")
                    results = self.entry_search(search_title, search_artist)
                case "q":
                    break
                case _:
                    print("Invalid option. Please try again.")
                    continue
            if not results:
                print("No results found. Please try again.")
                continue
            print("\nSearch Results:")
            for idx, row in enumerate(results, start=1):
                print(
                    f"{idx}. Title: {row[1]}, Artist: {row[3]}, Album: {row[4]}, Year: {row[7]}"
                )
            selection = input("Select an entry to edit by number (or 'q' to quit): ")
            if selection.lower() == "q":
                break
            try:
                selection_idx = int(selection) - 1
                if selection_idx < 0 or selection_idx >= len(results):
                    print("Invalid selection. Please try again.")
                    continue
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue
            selected_entry = results[selection_idx]
            info = {
                "title": selected_entry[2],
                "url": selected_entry[9],
                "description": selected_entry[10],
                "releaseDate": selected_entry[8],
            }
            self.edit_title(info, selected_entry[2])

    def entry_search(self, search_title, search_artist=None):
        if search_artist:
            return self.database.get_titles(
                title=search_title, artist=search_artist, limit=3
            )
        else:
            return self.database.get_titles(title=search_title, limit=5)

    def edit_mode(self):
        # loop over vidoeInfos

        # accept return of insert (db)
        # fork
        # 0 -> inserted
        # non-0 -> overwrite?
        # fork
        # if overwrite:
        #     overwrite existing entry
        # else:
        #     skip to next?
        #     change data?
        # next

        with open("videoInfos.json", "r") as f:
            data = json.load(f)
        if not data:
            print("No video information found.")
            return
        for video_org_title, info in data.items():
            if self.database.get_title_by_url(info.get("url", "")):
                print(
                    f"Title '{video_org_title}' already exists in database. Skipping."
                )
                continue
            self.edit_title(info, video_org_title)

    def edit_title(self, info, video_org_title):
        data = info
        data["original_title"] = video_org_title
        # data["title"], data["original_title"], data["artist"], data["album"], data["album_artist"], data["genre"], data["year"], data["releaseDate"], data["url"], data["description"]
        print("\nVideo Title:", video_org_title)
        print("Current Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        new_title = input("Enter new title (or press Enter to keep current): ")
        if new_title:
            data["title"] = new_title
        else:
            data["title"] = video_org_title
        data["artist"] = input("Enter artist name: ")
        data["album"] = input("Enter album name (return for single): ")
        if not data["album"]:
            data["album"] = data["title"] + " - Single"
        data["album_artist"] = input(
            "Enter album artist name (return for same as song): "
        )
        if not data["album_artist"]:
            data["album_artist"] = data["artist"]
        data["genre"] = input("Enter genre: ")
        data["year"] = input("Enter year (return to use releaseDate): ")
        if not data["year"]:
            data["year"] = info.get("releaseDate", "")[:4]

        overwrite: int = self.database.insert_title(data)
        if overwrite != 0:
            print("Title already exists in database:")
            print(self.database.get_title(overwrite))
            overwrite_input = input("Do you want to overwrite it? (y/n): ").lower()
            if overwrite_input == "y":
                self.database.update_title(data, overwrite)
                print("Title overwritten.")
            else:
                print("Skipping title.")


if __name__ == "__main__":
    cli = Yt_dlp_cli()
    cli.run()
