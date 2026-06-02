"""
Database seeding script for course progress tracking system.
This script adds sample courses and videos to get started.
"""

import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "test_fr.db"

def seed_courses():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Clean old data to ensure exact match with this script
    cursor.execute("DELETE FROM user_progress") # Clear progress if we are resetting videos
    cursor.execute("DELETE FROM videos")
    cursor.execute("DELETE FROM enrollments")
    cursor.execute("DELETE FROM courses")
    
    # Sample courses
    courses_data = [
        ("pkg-office", "حزمة برامج الأوفيس", "تعلم استخدام جميع برامج Microsoft Office", "/static/images/ايقونات حزمة الاوفيس/word.png"),
        ("pkg-design", "حزمة برامج التصميم", "أدوات احترافية للتصميم الجرافيكي", "/static/images/ايقونات حزمة التصميم/photoshop.png"),
        ("pkg-montage", "حزمة برامج المونتاج", "تعديل الفيديوهات واحترافية المونتاج", "/static/images/ايقونات حزمة المونتاج/filmora.png"),
        ("pkg-ai", "أدوات الذكاء الاصطناعي", "استخدام أحدث أدوات الذكاء الاصطناعي", "/static/images/ايقونات حزمة ادوات الذكاء/claudeai.png"),
        ("pkg-photo", "حزمة برامج التصوير", "احتراف فن التصوير وتعديل الصور", "/static/images/ايقونات حزمة التصوير/Adobe Lightroom.png"),
        ("pkg-audio", "حزمة برامج تحرير الصوت", "هندسة وتحرير الصوت بشكل احترافي", "/static/images/ايقونات حزمة تحرير الصوت/audacity.png"),
        ("pkg-nocode", "حزمة البرمجة بدون كود", "بناء المواقع والتطبيقات بدون برمجة", "/static/images/ايقونات حزمة البرمجة/wordpress.png"),
        ("pkg-google", "حزمة أدوات جوجل", "احتراف استخدام خدمات جوجل السحابية", "/static/images/ايقونات حزمة ادوات جوجل/google drive.png"),
    ]
    
    for course_id, title, desc, image in courses_data:
        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO courses (id, title, description, image_url)
                VALUES (?, ?, ?, ?)
                """,
                (course_id, title, desc, image)
            )
        except Exception as e:
            print(f"Error inserting course {course_id}: {e}")
    
    conn.commit()
    
    # Sample videos for each course
    videos_data = [
        # Office package (1-5)
        (1, "pkg-office", "مقدمة إلى Microsoft Word", "https://www.youtube.com/embed/9FgG3kHzzlE", 15, 1),
        (2, "pkg-office", "التنسيق والأنماط المتقدمة", "https://www.youtube.com/embed/dQw4w9WgXcQ", 20, 2),
        (3, "pkg-office", "إنشاء جداول وقوائم", "https://www.youtube.com/embed/dQw4w9WgXcQ", 18, 3),
        (4, "pkg-office", "Microsoft Excel الأساسيات", "https://www.youtube.com/embed/dQw4w9WgXcQ", 25, 4),
        (5, "pkg-office", "الدوال والصيغ المتقدمة", "https://www.youtube.com/embed/dQw4w9WgXcQ", 30, 5),
        
        # Design package (6-9)
        (6, "pkg-design", "مقدمة إلى Photoshop", "https://www.youtube.com/embed/dQw4w9WgXcQ", 20, 1),
        (7, "pkg-design", "الطبقات والقناع", "https://www.youtube.com/embed/dQw4w9WgXcQ", 25, 2),
        (8, "pkg-design", "الفرش والرسم", "https://www.youtube.com/embed/dQw4w9WgXcQ", 22, 3),
        (9, "pkg-design", "تأثيرات وتصفية", "https://www.youtube.com/embed/dQw4w9WgXcQ", 28, 4),
        
        # Montage package (10-15)
        (10, "pkg-montage", "مقدمة إلى Filmora", "https://www.youtube.com/embed/dQw4w9WgXcQ", 15, 1),
        (11, "pkg-montage", "استيراد وتنظيم المشاريع", "https://www.youtube.com/embed/dQw4w9WgXcQ", 18, 2),
        (12, "pkg-montage", "قص وترتيب الفيديوهات", "https://www.youtube.com/embed/dQw4w9WgXcQ", 20, 3),
        (13, "pkg-montage", "الانتقالات والمؤثرات", "https://www.youtube.com/embed/dQw4w9WgXcQ", 25, 4),
        (14, "pkg-montage", "إضافة الصوت والموسيقى", "https://www.youtube.com/embed/dQw4w9WgXcQ", 22, 5),
        (15, "pkg-montage", "تصدير وحفظ الفيديو", "https://www.youtube.com/embed/dQw4w9WgXcQ", 12, 6),
        
        # AI package (16-20)
        (16, "pkg-ai", "مقدمة إلى ChatGPT", "https://www.youtube.com/embed/dQw4w9WgXcQ", 18, 1),
        (17, "pkg-ai", "مفاهيم الذكاء الاصطناعي", "https://www.youtube.com/embed/dQw4w9WgXcQ", 22, 2),
        (18, "pkg-ai", "استخدام الإكمال التلقائي", "https://www.youtube.com/embed/dQw4w9WgXcQ", 20, 3),
        (19, "pkg-ai", "الخوارزميات والتعلم الآلي", "https://www.youtube.com/embed/dQw4w9WgXcQ", 28, 4),
        (20, "pkg-ai", "التطبيقات العملية", "https://www.youtube.com/embed/dQw4w9WgXcQ", 25, 5),

        # Photo package (21-25)
        (21, "pkg-photo", "Lightroom Basics", "https://www.youtube.com/embed/dQw4w9WgXcQ", 15, 1),
        (22, "pkg-photo", "Color Grading", "https://www.youtube.com/embed/dQw4w9WgXcQ", 20, 2),
        (23, "pkg-photo", "Editing Landscape", "https://www.youtube.com/embed/dQw4w9WgXcQ", 18, 3),
        (24, "pkg-photo", "Portrait Retouching", "https://www.youtube.com/embed/dQw4w9WgXcQ", 25, 4),
        (25, "pkg-photo", "Export Settings", "https://www.youtube.com/embed/dQw4w9WgXcQ", 10, 5),

        # Audio package (26-30)
        (26, "pkg-audio", "Audacity Introduction", "https://www.youtube.com/embed/dQw4w9WgXcQ", 12, 1),
        (27, "pkg-audio", "Noise Reduction", "https://www.youtube.com/embed/dQw4w9WgXcQ", 15, 2),
        (28, "pkg-audio", "Multi-track Editing", "https://www.youtube.com/embed/dQw4w9WgXcQ", 20, 3),
        (29, "pkg-audio", "Compression and Limiting", "https://www.youtube.com/embed/dQw4w9WgXcQ", 18, 4),
        (30, "pkg-audio", "Mastering Audio", "https://www.youtube.com/embed/dQw4w9WgXcQ", 22, 5),

        # No-code package (31-35)
        (31, "pkg-nocode", "WordPress Basics", "https://www.youtube.com/embed/dQw4w9WgXcQ", 20, 1),
        (32, "pkg-nocode", "Themes and Plugins", "https://www.youtube.com/embed/dQw4w9WgXcQ", 25, 2),
        (33, "pkg-nocode", "Creating Pages", "https://www.youtube.com/embed/dQw4w9WgXcQ", 15, 3),
        (34, "pkg-nocode", "SEO Basics", "https://www.youtube.com/embed/dQw4w9WgXcQ", 20, 4),
        (35, "pkg-nocode", "E-commerce setup", "https://www.youtube.com/embed/dQw4w9WgXcQ", 30, 5),

        # Google package (36-40)
        (36, "pkg-google", "Google Drive Intro", "https://www.youtube.com/embed/dQw4w9WgXcQ", 10, 1),
        (37, "pkg-google", "Sharing and Collaboration", "https://www.youtube.com/embed/dQw4w9WgXcQ", 12, 2),
        (38, "pkg-google", "Google Forms setup", "https://www.youtube.com/embed/dQw4w9WgXcQ", 15, 3),
        (39, "pkg-google", "Google Sites builder", "https://www.youtube.com/embed/dQw4w9WgXcQ", 20, 4),
        (40, "pkg-google", "Managing Files", "https://www.youtube.com/embed/dQw4w9WgXcQ", 12, 5),
    ]
    
    for video_id, course_id, title, url, duration, order in videos_data:
        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO videos (id, course_id, title, video_url, duration, lesson_order)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (video_id, course_id, title, url, duration, order)
            )
        except Exception as e:
            print(f"Error inserting video {title}: {e}")
    
    conn.commit()
    conn.close()
    
    print("✅ Database seeding completed successfully!")
    print("📚 Added 4 courses with 20 sample videos")


if __name__ == "__main__":
    seed_courses()
