## make old json compatible

import json
import sqlite3
from tkinter import filedialog


def main():
    db_path = filedialog.askopenfilename(title="Select old database")
    new_db_path = filedialog.askopenfilename(title="Select new database")
    base_json_path = filedialog.askopenfilename(title="Select old base json")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    with open(base_json_path, 'r') as f:
        data = json.load(f)

    new_data = {}
    for key, value in data.items():
        query = f"SELECT * FROM titles WHERE url LIKE '%{value['url'].strip()}%'"
        c.execute(query)
        result = c.fetchone()
        new_data[key] = {
            "title": result[1],
            "original_title": value["title"],
            "artist": result[2],
            "album": result[3],
            "album_artist": result[4],
            "genre": result[5],
            "releaseDate": result[7],
            "year": result[6],
            "url": result[8],
            "description": result[9],
        }
    
    conn.close()
    conn = sqlite3.connect(new_db_path)
    c = conn.cursor()

    for key, value in new_data.items():
        c.execute("INSERT INTO titles (title, original_title, artist, album, album_artist, genre, release_date, year, url, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (value["title"], value["original_title"], value["artist"], value["album"], value["album_artist"], value["genre"], value["releaseDate"], value["year"], value["url"], value["description"]))
    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()