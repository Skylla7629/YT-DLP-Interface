'''mermaid

erDiagram

  ARTIST ||--o{ TITLE_ARTIST : "owner of"
  TITLE ||--o{ TITLE_ARTIST : "is used in"
  
  ARTIST ||--o{ ALBUM : "owner of"
  ALBUM ||--o{ TRACK : "consists of"
  TITLE ||--o{ TRACK : "is used in"
  
  TITLE ||--o{ TITLE_GENRE : "classified as"
  GENRE ||--o{ TITLE_GENRE : "is used in"
  ALBUM ||--o{ ALBUM_GENRE : "classified as"
  GENRE ||--o{ ALBUM_GENRE : "is used in"
  
  VIDEO ||--o{ VIDEO_TITLE : "associated with" # compilations / multiple vids contain same title
  TITLE ||--o{ VIDEO_TITLE : "associated with"
  
  TITLE_ARTIST {
    int id PK
    int title_id FK
    int artist_id FK
  }
  
  TITLE_GENRE {
    int id PK
    int title_id FK
    int genre_id FK
  }
  
  ALBUM_GENRE {
    int id PK
    int album_id FK
    int genre_id FK
  }
  
  VIDEO_TITLE {
    int id PK
    int video_id FK
    int title_id FK
  }
  
  TITLE {
    int id PK
    string MusicBrainzID UK (recording.id)
    string Name
    string date-added
  }
  
  TRACK {
    int id PK
    int album_id FK
    int title_id FK
    int track_number
  }
  
  ARTIST { # in this case simplyfied artist and groups
    int id PK
    int artist_id FK
    string MusicBrainzID UK (artist.id)
    string Name
  }
  
  ALBUM {
    int id PK
    string MusicBrainzID UK (release-group.id)
    string year
    string Name
  }
  
  GENRE { # list of predefined genres to map added titles against
    int id PK
    string Name
  }
  
  VIDEO {
    int id PK
    string url UK
    string platform
    string releaseDate
    string title
    string description
    string date-added
  }

'''
