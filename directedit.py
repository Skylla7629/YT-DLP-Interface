import os
from mutagen.easyid3 import EasyID3
from database import Database
from time import sleep


class DirectEdit:
    def __init__(self, directory, database=None):
        self.directory = directory
        if database:
            self.database:Database = database
        else:
            self.database:Database = Database()


    def edit_tags(self, file, title, artist, album, album_artist, genre, year):
        audio = EasyID3(file)
        audio['title'] = title
        audio['artist'] = artist
        audio['album'] = album
        audio['albumartist'] = album_artist
        audio['genre'] = genre
        audio['date'] = year
        audio.save()


    def check_file(self, file):
        audio = EasyID3(file)
        title = audio.get('title', '')
        artist = audio.get('artist', '')
        album = audio.get('album', '')
        album_artist = audio.get('albumartist', '')

        if title or artist or album or album_artist:
            return True
        else:
            return False

    def edit_files(self):
        files = []
        ed_fileCount = 0
        for file in os.listdir(self.directory):
            if file.endswith(".mp3"):
                files.append(file)
                if self.check_file(f"{self.directory}/{file}"):
                    ed_fileCount += 1
        
        if ed_fileCount > 0:
            response = input(f"Found {ed_fileCount} files with existing tags. Do you still want to edit? (y/N): ").lower()
            if response != 'y':
                self.status_file_msg(0, 0, f"[Editing] \x1b[31mCancelled\x1b[0m - No changes have been made")
                return

        failcount = 0
        for i, file in enumerate(files):
            self.status_file_msg(i+1, len(files), f"[Editing] {file}")
            sleep(0.05)
            name = file[:-4].replace("｜", "|").replace("⧸", "/").replace("＊", "*")
            data = self.database.get_title_exact(name)
            if data:
                mp3ID = data[0]
                title = data[1]
                artist = data[3]
                album = data[4]
                album_artist = data[5]
                genre = data[6]
                year = data[7]
                flag = data[11]
                if flag == 0:
                    self.database.itunes_toggle(mp3ID, 1)
                    self.database.commit()
                self.status_file_msg(i+1, len(files), f"[Editing] \x1b[32mFound Data\x1b[0m {title} - {artist} - {year}")
                self.edit_tags(f"{self.directory}/{file}", title, artist, album, album_artist, genre, year)    
            else:
                self.status_file_msg(i+1, len(files), f"[Editing] \x1b[31mNo Data Found\x1b[0m")
                failcount += 1
            sleep(0.05)

        self.status_file_msg(0, 0, f"[Editing] \x1b[32mFinished\x1b[0m - \x1b[35m{len(files) - failcount}\x1b[0m files edited - \x1b[31m{failcount}\x1b[0m files failed")

    def status_file_msg(self, i, n, msg):
        print(f"\x1b[35m({i}/{n}) \x1b[0m {msg}\x1b[0m")

# EOF