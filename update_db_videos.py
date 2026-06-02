import sqlite3
from pathlib import Path

ROOT = Path(r"f:\year4\finale\code")
DB = ROOT / "test_fr.db"

REQUESTED_COUNTS = {
    "word": 5, "excel": 3, "powerpoint": 2, "teams": 1, "outlook": 1, 
    "onenote": 2, "access": 2, "photoshop": 3, "ilustrator": 1, "canva": 2, 
    "indesign": 1, "premiere": 1, "capcut": 4, "filmora": 2, "lightroom": 1, 
    "panoramamaker": 1, "audacity": 2, "audition": 1, "wordpress": 5, 
    "googleclassroom": 2, "googledrive": 2, "googleforms": 2, "googlesites": 1, 
    "claudeai": 5, "klingai": 2, "openread": 1, "notebooklm": 1, "flowai": 1, 
    "لهجاتي": 1, "figma": 5
}

BASE_MULTIPLIER = {
    "word": 10, "excel": 11, "powerpoint": 12, "teams": 13, "outlook": 14,
    "onenote": 15, "access": 16, "photoshop": 17, "ilustrator": 18, "canva": 19,
    "indesign": 20, "premiere": 21, "capcut": 22, "filmora": 23, "lightroom": 24,
    "panoramamaker": 25, "audacity": 26, "audition": 27, "wordpress": 28,
    "googleclassroom": 29, "googledrive": 30, "googleforms": 31, "googlesites": 32,
    "claudeai": 33, "klingai": 34, "openread": 35, "notebooklm": 36, "flowai": 37,
    "لهجاتي": 38, "figma": 39
}

def get_ids(pkg):
    base = BASE_MULTIPLIER[pkg]
    count = REQUESTED_COUNTS[pkg]
    return [base * 10 + i + 1 for i in range(count)]

conn = sqlite3.connect(DB)

for course_id, count in REQUESTED_COUNTS.items():
    # Delete old videos for this course
    conn.execute("DELETE FROM user_progress WHERE video_id IN (SELECT id FROM videos WHERE course_id = ?)", (course_id,))
    conn.execute("DELETE FROM videos WHERE course_id = ?", (course_id,))
    
    ids = get_ids(course_id)
    for i, vid in enumerate(ids):
        title = f"فيديو {i+1}"
        conn.execute(
            "INSERT INTO videos (id, course_id, title, video_url, duration, lesson_order) VALUES (?, ?, ?, ?, ?, ?)",
            (vid, course_id, title, "https://www.youtube.com/embed/dQw4w9WgXcQ", 10, i + 1)
        )

conn.commit()
conn.close()
print("Database videos updated.")
