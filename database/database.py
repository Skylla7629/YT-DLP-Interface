# databaes connection for YT-dlp project
import os
from typing import List, Any

import mysql.connector
from tkinter import messagebox
import dotenv


class Database:
    def __init__(self):

        dotenv.load_dotenv("./.env")

        self.conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_DATABASE', 'youtube_itunes_upload')
        )
        self.cursor = self.conn.cursor(buffered=True)
        self.main_table_init()

    def __del__(self):
        self.conn.close()


    def main_table_init(self):
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS titles
                            (
                                id             INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
                                title          VARCHAR(255)                   NOT NULL,
                                original_title VARCHAR(255)                   NOT NULL,
                                artist         VARCHAR(255)                   NOT NULL,
                                album          VARCHAR(255)                   NOT NULL,
                                album_artist   VARCHAR(255)                   NOT NULL,
                                genre          VARCHAR(100)                   NOT NULL,
                                year           VARCHAR(10)                    NOT NULL,
                                release_date   VARCHAR(50)                    NOT NULL,
                                url            TEXT,
                                description    TEXT,
                                itunes         TINYINT(1) DEFAULT 0
                            ) ENGINE = InnoDB
                              DEFAULT CHARSET = utf8mb4;
                            """)
        self.commit()


    def insert_title_depricated(self, data: dict, overwrite=False, title_id=None):

        ovrdQuery = """ UPDATE titles
                        SET title = %s, artist = %s, album = %s, album_artist = %s, genre = %s, year = %s, release_date = %s, url = %s, description = %s
                        WHERE id = %s  """

        if title_id:
            self.cursor.execute("SELECT * FROM titles WHERE id = %s", (title_id,))
            title = self.cursor.fetchone()
            if title:
                if not overwrite:
                    overwrite = messagebox.askyesno("Title exists", "Title already exists. Do you want to overwrite it?")
                if overwrite:
                    self.cursor.execute(ovrdQuery, (data["title"], data["artist"], data["album"], data["album_artist"], data["genre"], data["year"], data["releaseDate"], data["url"], data["description"], title_id,))
                else:
                    return 1
            return

        self.cursor.execute("SELECT * FROM titles WHERE title = %s AND artist = %s", (data["title"], data["artist"],))
        title = self.cursor.fetchone()
        if title:
            if not overwrite:
                overwrite = messagebox.askyesno("Title exists", "Title already exists. Do you want to overwrite it?")
            if overwrite:
                self.cursor.execute(ovrdQuery, (data["title"], data["artist"], data["album"], data["album_artist"], data["genre"], data["year"], data["releaseDate"], data["url"], data["description"], title_id,))
            else:
                return 1
        else:
            self.cursor.execute("""
                INSERT INTO titles (title, original_title, artist, album, album_artist, genre, year, release_date, url, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  """,
                (data["title"], data["original_title"], data["artist"], data["album"], data["album_artist"], data["genre"], data["year"], data["releaseDate"], data["url"], data["description"],))


    def insert_title(self, data: dict):
        self.cursor.execute("SELECT * FROM titles WHERE title = %s AND artist = %s", (data["title"], data["artist"],))
        title = self.cursor.fetchone()
        if title:
            return title[0]  # return existing title id
        else:
            self.cursor.execute("""
                INSERT INTO titles (title, original_title, artist, album, album_artist, genre, year, release_date, url, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  """,
                (data["title"], data["original_title"], data["artist"], data["album"], data["album_artist"], data["genre"], data["year"], data["releaseDate"], data["url"], data["description"],))
            self.commit()
            return 0

    def update_title(self, data: dict, title_id:int):
        self.cursor.execute("""
            UPDATE titles
            SET title = %s, original_title = %s, artist = %s, album = %s, album_artist = %s, genre = %s, year = %s, release_date = %s, url = %s, description = %s
            WHERE id = %s  """,
            (data["title"], data["original_title"], data["artist"], data["album"], data["album_artist"], data["genre"], data["year"], data["releaseDate"], data["url"], data["description"], title_id,))
        self.commit()

    def get_title_by_url(self, url:str):
        self.cursor.execute("SELECT * FROM titles WHERE url LIKE %s", (f"%{url}%",))
        return self.cursor.fetchone()

    def get_titles(self, limit:int=None, title:str=None, artist:str=None, original_title:str=None, itunes:int=None):
        query = "SELECT * FROM titles"
        clauses: List[str] = []
        params: List[Any] = []

        if title:
            clauses.append("LOWER(title) LIKE LOWER(%s)")
            params.append(f"%{title}%")
        if artist:
            clauses.append("LOWER(artist) LIKE LOWER(%s)")
            params.append(f"%{artist}%")
        if original_title:
            clauses.append("original_title LIKE %s")
            params.append(f"%{original_title}%")
        if itunes is not None:
            clauses.append("itunes = %s")
            params.append(itunes)

        if clauses:
            query += " WHERE " + " AND ".join(clauses)

        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

        # debug
        # print(query)
        # print(params)

        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()


    def get_title_exact(self, org_title:str,):
        self.cursor.execute("SELECT * FROM titles WHERE original_title = %s", (org_title,))
        return self.cursor.fetchone()


    def itunes_toggle(self, title_id:int, state:int=None):
        if state is not None:
            self.cursor.execute("UPDATE titles SET itunes = %s WHERE id = %s", (state, title_id,))
            self.commit()
        else:
            self.cursor.execute("SELECT itunes FROM titles WHERE id = %s", (title_id,))
            row = self.cursor.fetchone()
            if not row:
                return
            itunes = 1 if row[0] == 0 else 0
            self.cursor.execute("UPDATE titles SET itunes = %s WHERE id = %s", (itunes, title_id,))
            self.commit()


    def get_title(self, title_id):
        self.cursor.execute("SELECT * FROM titles WHERE id = %s", (title_id,))
        return self.cursor.fetchone()


    def get_count(self, table="titles") -> int:
        self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
        return int(self.cursor.fetchone()[0])


    def delete_title(self, title_id):
        response = messagebox.askyesno("Delete", "Do you want to delete this title?")
        if response:
            self.cursor.execute("DELETE FROM titles WHERE id = %s", (title_id,))
            self.commit()


    def delete_all(self):
        response = messagebox.askyesno("Delete", "Do you want to delete all titles?")
        if response:
            self.cursor.execute("DELETE FROM titles")
            self.commit()


    def commit(self):
        self.conn.commit()


# EOF