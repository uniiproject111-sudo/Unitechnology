# Quick Start Guide - Course Progress Tracking

## Setup (2 minutes)

### 1. Database is Ready
✅ Tables created automatically when app starts
- `courses`, `videos`, `user_progress`, `course_completion`

### 2. Seed Sample Data
```bash
python seed_db.py
```
Creates 2 sample courses with 5 sample videos each.

### 3. Start Flask App
```bash
python app.py
```
Server runs at `http://localhost:5000`

---

## Test the System (5 minutes)

### Step 1: Create Account
1. Go to http://localhost:5000
2. Click "إنشاء حساب" (Sign Up)
3. Fill in username, email, password

### Step 2: Enroll in Course
1. Click "كورسات" (Courses) in navbar
2. Click "سجل في هذه الحزمة" on Office course
3. Confirm enrollment

### Step 3: View My Courses
1. Click "كورساتي" (My Courses) in navbar
2. See enrolled course with **progress bar** (currently 0%)
3. Click "استكمل الآن" button

### Step 4: Watch & Complete Videos
1. Course player opens with video list
2. Click "اكتمل" (Complete) button to mark video done
3. Watch progress update: **1/3 videos (33%)**
4. Complete all videos to see **✅ Course Completed!**

### Step 5: Check Progress
- Go back to "كورساتي"
- See progress bar updated: **3/3 videos (100%)**
- Status badge shows "✅ مكتمل"

---

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | All backend routes & logic |
| `course_player.html` | Video player & progress display |
| `korsati.html` | My Courses page (updated) |
| `seed_db.py` | Sample data generator |
| `COURSE_PROGRESS_SYSTEM.md` | Complete documentation |

---

## New Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/course/<course_id>` | GET | Open course player |
| `/api/track-video/<video_id>` | POST | Mark video complete |
| `/api/course-progress/<course_id>` | GET | Get progress JSON |
| `/api/last-video/<course_id>` | GET | Get last watched |

---

## Database Overview

### courses
```sql
SELECT * FROM courses;
-- Shows: pkg-office, pkg-design (from seeding)
```

### videos
```sql
SELECT * FROM videos WHERE course_id='pkg-office';
-- Shows: 3 videos: Word Basics, Advanced Formatting, Tables
```

### user_progress
```sql
SELECT * FROM user_progress WHERE user_id=1;
-- Empty until user completes videos
-- Gets filled as user marks videos complete
```

### course_completion
```sql
SELECT * FROM course_completion WHERE user_id=1;
-- Empty until all videos in course complete
-- Gets filled when course reaches 100%
```

---

## Common Tasks

### Add Your Own Course

```python
import sqlite3

conn = sqlite3.connect('test_fr.db')
cursor = conn.cursor()

# Add course
cursor.execute("""
    INSERT INTO courses (id, title, description, image_url)
    VALUES ('pkg-photography', 'Photography 101', 'Learn photography basics', '/img.png')
""")

# Add 5 videos
for i in range(1, 6):
    cursor.execute("""
        INSERT INTO videos 
        (course_id, title, video_url, duration, lesson_order)
        VALUES (?, ?, ?, ?, ?)
    """, ('pkg-photography', f'Lesson {i}', 'https://youtube.com/embed/...', 15, i))

conn.commit()
conn.close()
```

Then enroll user in course:
```python
# In app with logged-in user
conn = get_db_connection()
conn.execute(
    "INSERT INTO enrollments (user_id, package_id) VALUES (?, ?)",
    (user_id, 'pkg-photography')
)
conn.commit()
```

### Check User Progress

```bash
# In Python shell or script
import sqlite3
conn = sqlite3.connect('test_fr.db')

# User 1's progress in pkg-office
result = conn.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN completed=1 THEN 1 ELSE 0 END) as completed
    FROM user_progress
    WHERE user_id=1 
    AND video_id IN (SELECT id FROM videos WHERE course_id='pkg-office')
""").fetchone()

print(f"Completed {result['completed']}/{result['total']} videos")
```

### Reset User Progress

```python
import sqlite3

conn = sqlite3.connect('test_fr.db')

# Clear all progress for user 1
conn.execute("DELETE FROM user_progress WHERE user_id=1")
conn.execute("DELETE FROM course_completion WHERE user_id=1")

conn.commit()
conn.close()

print("User progress cleared!")
```

---

## Template Usage

### Show Progress in Any Template

```jinja2
<!-- Access in any template -->
{% set progress = course_progress.get('pkg-office', {}) %}

<!-- Show progress bar -->
<div class="progress-bar">
    <div style="width: {{ progress.progress_percent }}%">
        {{ progress.progress_percent }}%
    </div>
</div>

<!-- Show stats -->
<p>{{ progress.completed_videos }}/{{ progress.total_videos }} videos</p>

<!-- Show status -->
{% if progress.is_completed %}
    <p>✅ Course Completed!</p>
{% else %}
    <p>{{ progress.progress_percent }}% complete</p>
{% endif %}
```

---

## Debugging

### Check if database tables exist
```python
import sqlite3
conn = sqlite3.connect('test_fr.db')
tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()
print([t[0] for t in tables])
# Should show: users, enrollments, courses, videos, user_progress, course_completion
```

### Check course data
```python
import sqlite3
conn = sqlite3.connect('test_fr.db')

courses = conn.execute("SELECT * FROM courses").fetchall()
print(f"Courses: {len(courses)}")

videos = conn.execute("SELECT * FROM videos").fetchall()
print(f"Videos: {len(videos)}")

for video in videos:
    print(f"  - {video[2]} (course: {video[1]})")
```

### Check user progress
```python
import sqlite3
conn = sqlite3.connect('test_fr.db')

progress = conn.execute(
    "SELECT * FROM user_progress WHERE user_id=1"
).fetchall()
print(f"User 1 progress entries: {len(progress)}")

for p in progress:
    print(f"  - Video {p[2]}: {'✓ Complete' if p[3] else '✗ Incomplete'}")
```

---

## Next Steps

1. **Customize Videos**: Replace YouTube URLs with your own videos
2. **Add More Courses**: Use the course add example above
3. **Style**: Customize colors in `course_player.html` CSS
4. **Features**: Add quizzes, certificates, leaderboards
5. **Deploy**: Use production WSGI server (Gunicorn, uWSGI)

---

## Tips

✅ **Best Practices**:
- Always mark user as authenticated before accessing `/course/<id>`
- Check enrollment before granting access
- Cache progress for performance
- Use HTTPS in production

⚠️ **Common Issues**:
- Make sure videos are in database before opening course
- Check user is enrolled in course
- Verify course_id matches in URL
- Clear browser cache if changes don't show

📊 **Monitoring**:
- Track completion rates
- Identify drop-off points
- Send reminders at milestones
- Award achievements/badges

---

## API Examples

### Mark Video Complete (JavaScript)
```javascript
fetch('/api/track-video/1', {method: 'POST'})
  .then(r => r.json())
  .then(d => console.log(d));
```

### Get Progress (JavaScript)
```javascript
fetch('/api/course-progress/pkg-office')
  .then(r => r.json())
  .then(p => console.log(p.progress_percent + '%'));
```

### Get Last Video (JavaScript)
```javascript
fetch('/api/last-video/pkg-office')
  .then(r => r.json())
  .then(d => {
    console.log('Resume from video', d.last_video_id);
    console.log('Progress:', d.progress_percent + '%');
  });
```

---

## Support

Full documentation: `COURSE_PROGRESS_SYSTEM.md`

Questions? Check:
1. Database schema in `app.py` `init_db()`
2. Routes in `app.py` (lines 450+)
3. Helper functions in `app.py` (lines 150+)
4. Template examples in `course_player.html`

Good luck! 🚀
