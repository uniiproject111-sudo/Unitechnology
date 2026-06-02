"""
Script to add exam URLs to courses in the database.
"""

import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "test_fr.db"

# Mapping of course IDs to exam URLs
EXAM_URLS = {
    "photoshop": "https://app.quilgo.com/t/KwgaB4iHWehTLQzR",
    "لهجاتي": "https://app.quilgo.com/t/8fuHrBu67govrrvg",
    "googledrive": "https://app.quilgo.com/t/EJPh96uKlbHmdsnd",
    "notebooklm": "https://app.quilgo.com/t/QrTiJILxDDDMIsdK",
    "panoramamaker": "https://app.quilgo.com/t/7dS8j0Mioi8mtow5",
    "googleclassroom": "https://app.quilgo.com/t/ipTEIT90Q95OCJED",
    "lightroom": "https://app.quilgo.com/t/orDf8YUjMjLAkJwy",
    "powerpoint": "https://app.quilgo.com/t/gDZ4LL6i7VNgzPDw",
    "onenote": "https://app.quilgo.com/t/cTaZ0o2edmKp0HE6",
    "outlook": "https://app.quilgo.com/t/vyS7LnNoU25GUVTq",
    "teams": "https://app.quilgo.com/t/jJCb0EnTiTV9WrWq",
    "audacity": "https://app.quilgo.com/t/yMnoTC0CFcCuVF1D",
    "canva": "https://app.quilgo.com/t/g7OOTCf5IkAgYXYo",
    "googlesites": "https://app.quilgo.com/t/d5suDRDsaDNPurJa",
    "word": "https://app.quilgo.com/t/USHzBPjXwVSCBZdY",
    "openread": "https://app.quilgo.com/t/wBgVT3AKnNAZEAdq",
    "googleforms": "https://app.quilgo.com/t/NCkZFmDWSMixTQAw",
    "klingai": "https://app.quilgo.com/t/JI10B2Fs7qdBHZ0M",
    "access": "https://app.quilgo.com/t/jv4Yfac7qDDFMLWR",
    "claudeai": "https://app.quilgo.com/t/BDWwI2vl6FWzre7a",
    "wordpress": "https://app.quilgo.com/t/SvRZ6S1TSvSqyG1f",
    "excel": "https://app.quilgo.com/t/Cxrjtn1f08dTJXi1",
    "filmora": "https://app.quilgo.com/t/WiiHcbnGchRaxIfd",
    "capcut": "https://app.quilgo.com/t/N5drWdVIB1IUt0oZ",
    "indesign": "https://app.quilgo.com/t/C4HK48KaVobYyRpm",
    "audition": "https://app.quilgo.com/t/Ne7ihSiWo5kqr2oh",
    "flowai": "https://app.quilgo.com/t/t11MaaKvkv6XACuH",
    "ilustrator": "https://app.quilgo.com/t/zDvUmvvi1q9MTnVk",
    "premiere": "https://app.quilgo.com/t/OrLGU8G0OCk68HU7",
    "figma": "https://app.quilgo.com/t/8fuHrBu67govrrvg"  # Figma Exam (using Lahagati2 link as placeholder)
}

def add_exams():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Add exam_url column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE courses ADD COLUMN exam_url TEXT")
        print("✓ Added exam_url column to courses table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✓ exam_url column already exists")
        else:
            print(f"✗ Error: {e}")
    
    conn.commit()
    
    # Get all course IDs from database
    cursor.execute("SELECT id, title FROM courses")
    courses = cursor.fetchall()
    
    print("Adding exam URLs to courses...")
    print(f"Total courses in database: {len(courses)}")
    print()
    
    updated_count = 0
    
    for course_id, title in courses:
        if course_id in EXAM_URLS:
            exam_url = EXAM_URLS[course_id]
            try:
                cursor.execute(
                    "UPDATE courses SET exam_url = ? WHERE id = ?",
                    (exam_url, course_id)
                )
                print(f"✓ {course_id}: {title}")
                print(f"  Exam URL: {exam_url}")
                updated_count += 1
            except Exception as e:
                print(f"✗ Error updating {course_id}: {e}")
        else:
            print(f"- {course_id}: No exam URL found (skipped)")
    
    conn.commit()
    conn.close()
    
    print()
    print(f"Total courses updated: {updated_count}/{len(courses)}")

if __name__ == "__main__":
    add_exams()
