# databaes connection for YT-dlp project
import os
from typing import Any, List

import dotenv
import mysql.connector


class Database:
    def __init__(self):

        dotenv.load_dotenv("./.env")

        self.conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database="yt_dlp_cli",  # os.getenv("DB_DATABASE", "youtube_itunes_upload"),
        )
        self.cursor = self.conn.cursor(buffered=True)
        self.main_table_init()

    def __del__(self):
        self.conn.close()

    def main_table_init(self):
        self.cursor.execute(
            """
                            CREATE TABLE IF NOT EXISTS title
                            (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            MBID VARCHAR(255) NULL,
                            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            ) ENGINE = InnoDB
                              DEFAULT CHARSET = utf8mb4;
                            """
        )
        self.cursor.execute(
            """
                            CREATE TABLE IF NOT EXISTS artist
                            (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            MBID VARCHAR(255) NULL,
                            CONSTRAINT unique_artist_name_mbid UNIQUE (name, MBID),
                            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            ) ENGINE = InnoDB
                                DEFAULT CHARSET = utf8mb4;
                            """
        )
        self.cursor.execute(
            """
                            CREATE TABLE IF NOT EXISTS album
                            (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            year INT NOT NULL,
                            MBID VARCHAR(255) NULL,
                            artist_id INT NOT NULL,
                            CONSTRAINT fk_album_artist_id FOREIGN KEY (artist_id) REFERENCES artist(id) ON DELETE CASCADE,
                            CONSTRAINT unique_album_name_artist_id UNIQUE (name, artist_id),
                            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            ) ENGINE = InnoDB
                                DEFAULT CHARSET = utf8mb4;
                            """
        )
        self.cursor.execute(
            """
                            CREATE TABLE IF NOT EXISTS genre
                            (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            CONSTRAINT unique_genre_name UNIQUE (name),
                            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            ) ENGINE = InnoDB
                                DEFAULT CHARSET = utf8mb4;
            """
        )
        self.cursor.execute(
            """
                            CREATE TABLE IF NOT EXISTS video
                            (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            title VARCHAR(255) NOT NULL,
                            url VARCHAR(255) NOT NULL,
                            platform VARCHAR(255) NOT NULL,
                            releaseDate VARCHAR(255) NOT NULL,
                            description TEXT,
                            CONSTRAINT unique_video_url UNIQUE (url),
                            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
            """
        )
        self.cursor.execute(
            """
                                    CREATE TABLE IF NOT EXISTS track
                                    (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    title_id INT NOT NULL,
                                    album_id INT NOT NULL,
                                    CONSTRAINT fk_title_track_id FOREIGN KEY (title_id) REFERENCES title(id) ON DELETE CASCADE,
                                    CONSTRAINT fk_album_track_id FOREIGN KEY (album_id) REFERENCES album(id) ON DELETE CASCADE,
                                    CONSTRAINT unique_album_track UNIQUE (album_id, title_id),
                                    track_number INT NOT NULL,
                                    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                    ) ENGINE = InnoDB
                                      DEFAULT CHARSET = utf8mb4;
                                     """
        )
        self.cursor.execute(
            """
                            CREATE TABLE IF NOT EXISTS title_artist
                            (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            title_id INT NOT NULL,
                            artist_id INT NOT NULL,
                            CONSTRAINT fk_title_artist_title_id FOREIGN KEY (title_id) REFERENCES title(id) ON DELETE CASCADE,
                            CONSTRAINT fk_title_artist_artist_id FOREIGN KEY (artist_id) REFERENCES artist(id) ON DELETE CASCADE,
                            CONSTRAINT unique_title_artist UNIQUE (title_id, artist_id),
                            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            ) ENGINE = InnoDB
                                DEFAULT CHARSET = utf8mb4;
            """
        )
        self.cursor.execute(
            """
                            CREATE TABLE IF NOT EXISTS title_genre
                            (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            title_id INT NOT NULL,
                            genre_id INT NOT NULL,
                            CONSTRAINT fk_title_genre_title_id FOREIGN KEY (title_id) REFERENCES title(id) ON DELETE CASCADE,
                            CONSTRAINT fk_title_genre_genre_id FOREIGN KEY (genre_id) REFERENCES genre(id) ON DELETE CASCADE,
                            CONSTRAINT unique_title_genre UNIQUE (title_id, genre_id),
                            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            ) ENGINE = InnoDB
                                DEFAULT CHARSET = utf8mb4;
            """
        )
        self.cursor.execute(
            """
                            CREATE TABLE IF NOT EXISTS album_genre
                            (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            album_id INT NOT NULL,
                            genre_id INT NOT NULL,
                            CONSTRAINT fk_album_genre_album_id FOREIGN KEY (album_id) REFERENCES album(id) ON DELETE CASCADE,
                            CONSTRAINT fk_album_genre_genre_id FOREIGN KEY (genre_id) REFERENCES genre(id) ON DELETE CASCADE,
                            CONSTRAINT unique_album_genre UNIQUE (album_id, genre_id),
                            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            ) ENGINE = InnoDB
                                DEFAULT CHARSET = utf8mb4;
            """
        )
        self.cursor.execute(
            """
                            CREATE TABLE IF NOT EXISTS video_title
                            (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            video_id INT NOT NULL,
                            title_id INT NOT NULL,
                            CONSTRAINT fk_video_title_video_id FOREIGN KEY (video_id) REFERENCES video(id) ON DELETE CASCADE,
                            CONSTRAINT fk_video_title_title_id FOREIGN KEY (title_id) REFERENCES title(id) ON DELETE CASCADE,
                            CONSTRAINT unique_video_title UNIQUE (video_id, title_id),
                            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            ) ENGINE = InnoDB
                                DEFAULT CHARSET = utf8mb4;
            """
        )
        self.commit()

    def commit(self):
        self.conn.commit()

    ## Insert functions
    def insert(
        self, query: str, params: tuple, failover_query: str, failover_params: tuple
    ) -> (
        int | Any | None
    ):  # returns the id of the unique constraint over the parameters, or None if an error occurs
        try:
            self.cursor.execute(
                query, params
            )  # expects an insert query with unique constraints on the parameters
            self.commit()
            return self.cursor.lastrowid
        except mysql.connector.IntegrityError:
            self.cursor.execute(
                failover_query, failover_params
            )  # expects a search query over the failover parameters, returning the id of the unique constraint
            result: Any = self.cursor.fetchone()
            return (
                (int(result[0]) or None) if result else None
            )  # works only with 1-based ids
        except mysql.connector.Error as err:
            print("Error:", err)
            return None

    def insert_artist(self, name: str, mbid: str = "") -> int | Any | None:
        return self.insert(
            "INSERT INTO artist (name, MBID) VALUES (%s, %s)",
            (name, mbid),
            "SELECT id FROM artist WHERE name = %s AND MBID = %s",
            (name, mbid),
        )

    def insert_genre(self, name: str) -> int | Any | None:
        return self.insert(
            "INSERT INTO genre (name) VALUES (%s)",
            (name,),
            "SELECT id FROM genre WHERE name = %s",
            (name,),
        )

    def insert_title(self, name: str, mbid: str = "") -> int | Any | None:
        return self.insert(
            "INSERT INTO title (name, MBID) VALUES (%s, %s)",
            (name, mbid),
            "SELECT id FROM title WHERE name = %s AND MBID = %s",
            (name, mbid),
        )

    def insert_album(
        self, name: str, year: int, artist_id: int, mbid: str = ""
    ) -> int | Any | None:
        return self.insert(
            "INSERT INTO album (name, year, artist_id, MBID) VALUES (%s, %s, %s, %s)",
            (name, year, artist_id, mbid),
            "SELECT id FROM album WHERE name = %s AND artist_id = %s",
            (name, artist_id),
        )

    def insert_video(
        self,
        title: str,
        url: str,
        platform: str,
        releaseDate: str,
        description: str = "",
    ) -> int | Any | None:
        return self.insert(
            "INSERT INTO video (title, url, platform, releaseDate, description) VALUES (%s, %s, %s, %s, %s)",
            (title, url, platform, releaseDate, description),
            "SELECT id FROM video WHERE url = %s",
            (url,),
        )

    def insert_track(
        self, title_id: int, album_id: int, track_number: int
    ) -> int | Any | None:
        return self.insert(
            "INSERT INTO track (title_id, album_id, track_number) VALUES (%s, %s, %s)",
            (title_id, album_id, track_number),
            "SELECT id FROM track WHERE title_id = %s AND album_id = %s",
            (title_id, album_id),
        )

    def insert_title_artist(self, title_id: int, artist_id: int) -> int | Any | None:
        return self.insert(
            "INSERT INTO title_artist (title_id, artist_id) VALUES (%s, %s)",
            (title_id, artist_id),
            "SELECT id FROM title_artist WHERE title_id = %s AND artist_id = %s",
            (title_id, artist_id),
        )

    def insert_relation_genre(
        self, tgt_id: int, genre_id: int, table: str
    ) -> int | Any | None:
        if table not in ["title", "album"]:
            raise ValueError("Table must be either 'title' or 'album'")

        base_query = f"INSERT INTO {table}_genre ({table}_id, genre_id) VALUES (%s, %s)"
        failover_query = (
            f"SELECT id FROM {table}_genre WHERE {table}_id = %s AND genre_id = %s"
        )
        return self.insert(
            base_query,
            (tgt_id, genre_id),
            failover_query,
            (tgt_id, genre_id),
        )

    def insert_video_title(self, video_id: int, title_id: int) -> int | Any | None:
        return self.insert(
            "INSERT INTO video_title (video_id, title_id) VALUES (%s, %s)",
            (video_id, title_id),
            "SELECT id FROM video_title WHERE video_id = %s AND title_id = %s",
            (video_id, title_id),
        )

    ## Lookup / Get Functions
    def get_entry_by_mbid(self, table: str, mbid: str) -> tuple | None:
        if table not in ["title", "artist", "album"]:
            raise ValueError("Table must one of 'title', 'artist', 'album'")

        self.cursor.execute(f"SELECT * FROM {table} WHERE MBID = %s", (mbid,))
        ret = self.cursor.fetchone()
        return tuple(ret) if ret else None

    def get_id_by_mbid(self, table: str, mbid: str) -> int | None:
        entry = self.get_entry_by_mbid(table, mbid)
        return entry[0] if entry else None

    def get_artist(self, name: str) -> List[tuple]:
        self.cursor.execute("SELECT * FROM artist WHERE name = %s", (name,))
        return [tuple(row) for row in self.cursor.fetchall()]

    def get_album(self, name: str, artist_id: int) -> List[tuple]:
        self.cursor.execute(
            "SELECT * FROM album WHERE name = %s AND artist_id = %s",
            (name, artist_id),
        )
        return [tuple(row) for row in self.cursor.fetchall()]

    def get_title(self, name: str) -> List[tuple]:
        self.cursor.execute("SELECT * FROM title WHERE name = %s", (name,))
        return [tuple(row) for row in self.cursor.fetchall()]

    def get_title_by_artist(self, title_name: str, artist_id: int) -> List[tuple]:
        self.cursor.execute(
            """
            SELECT t.* FROM title t
            JOIN title_artist ta ON t.id = ta.title_id
            WHERE t.name = %s AND ta.artist_id = %s
            """,
            (title_name, artist_id),
        )
        return [tuple(row) for row in self.cursor.fetchall()]


# EOF
