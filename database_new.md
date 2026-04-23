Step A: Artist (The Anchor)
- Search artist by MBID.
- If not found, search by name.
- If still not found: INSERT INTO artist --> Get artist_id.
Step B: Album
- Search album by MBID.
- If not found, search by name AND check the album_artist junction to see if it's linked to your artist_id.
- If not found: INSERT INTO album (using the artist_id from Step A) --> Get album_id.
Step C: Title (The Recording)
- Search title by MBID.
- If no MBID, search title by name AND check the title_artist junction to see if it's linked to your artist_id.
- If not found: INSERT INTO title --> Get title_id.
Step D: Create the Links (Junctions)
- Link Artist to Title: INSERT IGNORE INTO title_artist (title_id, artist_id).
- Link Title to Album (The Track): INSERT IGNORE INTO track (title_id, album_id, track_number).
- - Handle Genres: Loop through your genre list:Find/Insert genre --> Get genre_id.
- - INSERT IGNORE INTO title_genre (title_id, genre_id).
Step E: Since the goal is knowing if it exists in the server, your final step should be:
- Insert into video: Store the URL and file path.
- Link Video to Title: INSERT INTO video_title (video_id, title_id).
