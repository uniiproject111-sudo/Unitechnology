import re
from pathlib import Path
import sqlite3
import ast

ROOT = Path(r"f:\year4\finale\code")
APP_PY = ROOT / "app.py"
TEMPLATES = ROOT / "templates"
DB = ROOT / "test_fr.db"

with open(APP_PY, 'r', encoding='utf-8') as f:
    content = f.read()
    match = re.search(r'COURSE_VIDEO_IDS\s*=\s*(\{.*?\})', content, re.DOTALL)
    COURSE_VIDEO_IDS = ast.literal_eval(match.group(1))

PAGE_MAP = {
    "word": "MicrosoftWord", "excel": "MicrosoftExcel", "powerpoint": "powerpoint",
    "teams": "MicrosoftTeams", "outlook": "MicrosoftOutlook", "onenote": "MicrosoftOneNote",
    "access": "MicrosoftAccess", "photoshop": "Photoshop", "ilustrator": "Ilustrator",
    "canva": "Canva", "indesign": "InDesign", "premiere": "premiere", "capcut": "CapCut",
    "filmora": "Filmora", "lightroom": "Lightroom", "panoramamaker": "PanoramaMaker",
    "audacity": "Audacity", "audition": "Audition", "wordpress": "WordPress",
    "googleclassroom": "googleclassroom", "googledrive": "Googledrive", "googleforms": "GoogleForms",
    "googlesites": "GoogleSites", "claudeai": "claudeai", "klingai": "KlingAI",
    "openread": "Openread", "notebooklm": "NotebookLM", "flowai": "FlowAI",
    "لهجاتي": "لهجاتي", "figma": "figma"
}

YOUTUBE_IDS = {
    "photoshop": ["ElQuygyNJoI", "VImiyh14-Oc", "eINxsyOJqqA"],
    "canva": ["YcooyPrNP_w", "QMq9H1P8lqE"],
    "ilustrator": ["FqYEb1ehLvs"],
    "indesign": ["QV4ZK0eL0xQ"],
    "لهجاتي": ["BM5zYb3EKmg"],
    "klingai": ["OY1DHnggLxM", "MHR1rXPV_8M"],
    "notebooklm": ["sI2Sk9S1xow"],
    "openread": ["jm4DWbCENy0"],
    "claudeai": ["fFYj7ji1XHk", "Xz_ZsKu4bIU"],
    "flowai": ["TfXHnR4lyns"],
    "panoramamaker": ["p7gltQMYVDk"],
    "lightroom": ["i2BPw9WzeK4"],
    "googledrive": ["rKi3CHKRXdA", "yI2K6FAU-78"],
    "googleclassroom": ["P3Y74Aslq58", "KTDKbpbJFZ0"],
    "googleforms": ["DnLLVcPMu8Q", "2GN88GBMGEg"],
    "googlesites": ["1BJCgzS7Q58"],
    "access": ["qam55Vw_ZZY", "8LPq8W6KkPI"],
    "word": ["-YcM5ZDZC5U", "Ia_7r-oFPjg", "Ptt1KAjMnMw", "PAfoQPXucWg", "zo0mk-5SKSc"],
    "powerpoint": ["FqY6SFpYUJg", "0g6b2Ny9kes"],
    "onenote": ["W1sWHcY9Hm0", "vzUh8t6I5aI"],
    "outlook": ["IfLm5y0cg2w"],
    "teams": ["PkZm9K_HuuQ"],
    "audacity": ["m6IU28HZGiQ", "TJnY3ni-KLc"],
    "audition": ["Hnw0QbnLW_8"],
    "capcut": ["UKiJEYTtTH4", "3RG4LBy4oug", "4wDd7IgE1ho", "6Akh4kAqVVY"],
    "filmora": ["-AFblL4wSQI", "XVS6LOXpYS8"],
    "premiere": ["CPAkJG77jNM"]
}

conn = sqlite3.connect(DB)

for pkg, vids in COURSE_VIDEO_IDS.items():
    if pkg not in PAGE_MAP:
        continue
        
    yt_ids = YOUTUBE_IDS.get(pkg, [])
    
    # Update HTML
    page_name = PAGE_MAP[pkg]
    html_file = TEMPLATES / f"{page_name}.html"
    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        videos_jinja = "{% set videos = [\n"
        for i, vid in enumerate(vids):
            yt_id = yt_ids[i] if i < len(yt_ids) else "dQw4w9WgXcQ"
            videos_jinja += f"        {{'id': {vid}, 'yt_id': '{yt_id}'}}"
            if i < len(vids) - 1:
                videos_jinja += ",\n"
            else:
                videos_jinja += "\n"
        videos_jinja += "    ] %}"
        
        pattern = re.compile(r'{%\s*set\s+videos\s*=\s*\[.*?\]\s*%}', re.DOTALL)
        new_content = pattern.sub(videos_jinja, content)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {html_file.name}")

    # Update DB
    conn.execute("DELETE FROM user_progress WHERE video_id IN (SELECT id FROM videos WHERE course_id = ?)", (pkg,))
    conn.execute("DELETE FROM videos WHERE course_id = ?", (pkg,))
    
    for i, vid in enumerate(vids):
        yt_id = yt_ids[i] if i < len(yt_ids) else "dQw4w9WgXcQ"
        title = f"فيديو {i+1}"
        embed_url = f"https://www.youtube.com/embed/{yt_id}"
        conn.execute(
            "INSERT INTO videos (id, course_id, title, video_url, duration, lesson_order) VALUES (?, ?, ?, ?, ?, ?)",
            (vid, pkg, title, embed_url, 10, i + 1)
        )

conn.commit()
conn.close()
print("Database videos updated.")
