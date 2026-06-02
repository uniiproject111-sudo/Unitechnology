import re
from pathlib import Path
import sqlite3

ROOT = Path(r"f:\year4\finale\code")
DB = ROOT / "test_fr.db"
HTML = ROOT / "templates" / "MicrosoftExcel.html"

# 1. Update HTML
with open(HTML, 'r', encoding='utf-8') as f:
    content = f.read()

ids = ["FVireqWyAwY", "V-dwtRTdCSw", "jC1agjqWNmo"]

for yt_id in ids:
    content = content.replace("dQw4w9WgXcQ", yt_id, 1)

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated HTML.")

# 2. Update DB
conn = sqlite3.connect(DB)
vid_ids = [111, 112, 113]
for idx, yt_id in enumerate(ids):
    conn.execute(
        "UPDATE videos SET video_url = ? WHERE id = ? AND course_id = 'excel'",
        (f"https://www.youtube.com/embed/{yt_id}", vid_ids[idx])
    )

conn.commit()
conn.close()
print("Updated DB.")
