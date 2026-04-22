'''mermaid

erDiagram

  artist||--o{ title : "owner of"
  artist||--o{ album : "owner of"
  album ||--o{ TRACK : "consists of"
  title ||--o{ TRACK : "is used in"
  
  title }o--o{ genre : "classified as"
  album }o--o{ genre : "classified as"
  
  video }o--o{ title : "associated with" # compilations / multiple vids contain same title
  

  title {
    int id PK
    string MusicBrainzID UK (recording.id)
    int artsist_id FK
    string Name UK "Name + artist_id = UK"
    string date-added
  }
  
  TRACK {
    int id PK
    string TheAudioDBID UK (idTrack)
    string MusicBrainzID UK (media.track.id)
    int album_id FK
    int title_id FK
    int track_number
  }
  
  artist { # in this case simplyfied artist and groups
    int id PK
    string MusicBrainzID UK (recording.artist-credit-id)
    string TheAudioDBID UK (idArtist)
    string Name
  }
  
  album {
    int id PK
    string MusicBrainzID UK (media.id)
    string TheAudioDBID UK (idAlbum)
    string year
    string Name
  }
  
  genre { # list of predefined genres to map added titles against
    int id PK
    string Name
  }
  
  video {
    int id PK
    int url UK
    string platform
    string releaseDate
    string title
    string description
    string date-added
  }

'''
