CREATE TABLE IF NOT EXISTS audio_files (
    id TEXT PRIMARY KEY,
    file_name TEXT NOT NULL,
    bytes BLOB NOT NULL,
    processing_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS generated_ads (
    id TEXT PRIMARY KEY,
    segue TEXT NOT NULL,
    content TEXT NOT NULL,
    exit TEXT NOT NULL,
    audio_bytes BLOB NOT NULL,
    audio_file_id TEXT NOT NULL,
    processing_status TEXT NOT NULL,
    FOREIGN KEY (audio_file_id) REFERENCES audio_files(id)
);

CREATE TABLE IF NOT EXISTS stitched_audio (
    id TEXT PRIMARY KEY,
    audio_file_id TEXT NOT NULL,
    generated_ad_id TEXT NOT NULL,
    bytes BLOB NOT NULL,
    processing_status TEXT NOT NULL,
    FOREIGN KEY (audio_file_id) REFERENCES audio_files(id),
    FOREIGN KEY (generated_ad_id) REFERENCES generated_ads(id)
);
