# Python API Reference - Course Progress System

## Module: `app.py`

### Progress Tracking Functions

#### `get_course_progress(user_id: int, course_id: str) -> dict`

Calculate progress for a user in a specific course.

**Parameters:**
- `user_id` (int): User's database ID
- `course_id` (str): Course package ID (e.g., 'pkg-office')

**Returns:**
```python
{
    "total_videos": int,           # Total videos in course
    "completed_videos": int,       # How many user completed
    "progress_percent": int,       # Percentage 0-100
    "is_completed": bool,          # Course fully completed?
    "last_video_id": int | None    # Last watched video ID
}
```

**Example:**
```python
from app import get_course_progress

progress = get_course_progress(user_id=1, course_id='pkg-office')

print(f"Progress: {progress['progress_percent']}%")
print(f"Completed: {progress['completed_videos']}/{progress['total_videos']}")

if progress['is_completed']:
    print("Course finished!")
else:
    print(f"Last video watched: {progress['last_video_id']}")
```

---

#### `get_all_course_progress(user_id: int, enrolled_packages: list) -> dict`

Get progress for ALL enrolled courses at once.

**Parameters:**
- `user_id` (int): User's database ID
- `enrolled_packages` (list): List of course IDs user is enrolled in

**Returns:**
```python
{
    'pkg-office': {...progress_data...},
    'pkg-design': {...progress_data...},
    ...
}
```

**Example:**
```python
from app import get_all_course_progress

progress_map = get_all_course_progress(
    user_id=1,
    enrolled_packages=['pkg-office', 'pkg-design', 'pkg-ai']
)

# Print all progress
for course_id, progress in progress_map.items():
    print(f"{course_id}: {progress['progress_percent']}%")
    
# Access specific course
office_progress = progress_map['pkg-office']
print(f"Office course: {office_progress['completed_videos']}/{office_progress['total_videos']}")
```

---

#### `get_course_videos(course_id: str) -> list`

Retrieve all videos for a course ordered by lesson number.

**Parameters:**
- `course_id` (str): Course package ID

**Returns:**
List of sqlite3.Row objects (behave like dicts):
```python
[
    {
        'id': 1,
        'course_id': 'pkg-office',
        'title': 'Word Basics',
        'video_url': 'https://youtube.com/embed/...',
        'duration': 15,
        'lesson_order': 1
    },
    ...
]
```

**Example:**
```python
from app import get_course_videos

videos = get_course_videos('pkg-office')

print(f"Total videos: {len(videos)}")

for video in videos:
    print(f"{video['lesson_order']}. {video['title']} ({video['duration']} min)")
    
# Access specific video
first_video = videos[0]
print(f"First video: {first_video['title']}")
print(f"URL: {first_video['video_url']}")
```

---

#### `mark_video_completed(user_id: int, video_id: int) -> bool`

Mark a video as completed for a user.

**Parameters:**
- `user_id` (int): User's database ID
- `video_id` (int): Video's database ID

**Returns:**
- `True` if successful
- `False` if error occurred

**Behavior:**
1. Inserts/updates user_progress record with `completed=1`
2. Sets `watched_at` timestamp
3. Checks if entire course is now completed
4. If course complete, records in course_completion table

**Example:**
```python
from app import mark_video_completed

# Mark video 1 as complete for user 1
success = mark_video_completed(user_id=1, video_id=1)

if success:
    print("Video marked complete!")
    
    # Get updated progress
    from app import get_course_progress
    progress = get_course_progress(1, 'pkg-office')
    print(f"Progress: {progress['completed_videos']}/{progress['total_videos']}")
else:
    print("Error marking video complete")

# Mark multiple videos
for video_id in [1, 2, 3]:
    mark_video_completed(1, video_id)
```

---

### Database Functions

#### `get_db_connection() -> sqlite3.Connection`

Get a new database connection with Row factory enabled.

**Returns:** sqlite3.Connection object

**Example:**
```python
from app import get_db_connection

conn = get_db_connection()

# Query users
users = conn.execute("SELECT * FROM users").fetchall()

# Each row is a dict-like object
for user in users:
    print(f"User: {user['username']}")

conn.close()
```

---

### Context Processor

#### `inject_user_context() -> dict`

Automatically called by Flask before rendering every template.

**Returns:**
```python
{
    'user_name': str | None,              # Logged-in user name
    'enrolled_packages': list,            # Course IDs user enrolled in
    'course_progress': dict               # Progress for all courses
}
```

**Usage in Templates:**
```jinja2
<!-- Automatically available in all templates -->
<p>User: {{ user_name }}</p>

{% set progress = course_progress.get('pkg-office', {}) %}
<p>Progress: {{ progress.progress_percent }}%</p>
```

---

### Routes (HTTP)

#### `GET /course/<course_id>`
**Handler:** `course_detail(course_id: str)`

Display course detail page with all videos.

**Authentication:** Required (checks login & enrollment)

**Parameters:**
- `course_id` (str): Course package ID

**Returns:** Rendered `course_player.html` template

**Template Variables Passed:**
- `course`: Dict with course metadata
- `videos`: List of video dicts
- `progress`: Progress dict from `get_course_progress()`
- `video_progress_map`: Dict of `{video_id: {completed, watch_position}}`

**Errors:**
- 401: Not logged in
- 403: Not enrolled in course
- 404: Course not found

**Example:**
```html
<a href="{{ url_for('course_detail', course_id='pkg-office') }}">
    Open Office Course
</a>
```

---

#### `POST /api/track-video/<int:video_id>`
**Handler:** `track_video(video_id: int)`

API endpoint to mark a video as completed.

**Authentication:** Required

**Parameters:**
- `video_id` (int): Video database ID

**Returns:** JSON
```json
{"status": "success", "message": "Video marked as completed"}
```

**Errors:**
```json
{"error": "Unauthorized"} [401]
{"error": "User not found"} [404]
{"error": "Failed to track video"} [500]
```

**Example:**
```javascript
// Mark video 1 as complete
const response = await fetch('/api/track-video/1', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'}
});

const data = await response.json();
if (data.status === 'success') {
    console.log('Video marked complete!');
}
```

---

#### `GET /api/course-progress/<course_id>`
**Handler:** `get_progress(course_id: str)`

Get course progress data for current user.

**Authentication:** Required

**Parameters:**
- `course_id` (str): Course package ID

**Returns:** JSON progress dict
```json
{
    "total_videos": 10,
    "completed_videos": 5,
    "progress_percent": 50,
    "is_completed": false,
    "last_video_id": 5
}
```

**Example:**
```javascript
// Get progress for Office course
const response = await fetch('/api/course-progress/pkg-office');
const progress = await response.json();

console.log(`${progress.completed_videos}/${progress.total_videos}`);
console.log(`${progress.progress_percent}%`);
```

---

#### `GET /api/last-video/<course_id>`
**Handler:** `get_last_video(course_id: str)`

Get the last video user watched in a course.

**Authentication:** Required

**Parameters:**
- `course_id` (str): Course package ID

**Returns:** JSON
```json
{
    "last_video_id": 5,
    "progress_percent": 50
}
```

**Example:**
```javascript
// Get where user left off
const response = await fetch('/api/last-video/pkg-office');
const data = await response.json();

console.log(`Resume from video: ${data.last_video_id}`);
console.log(`Course progress: ${data.progress_percent}%`);
```

---

## Database Schema

### courses
```python
{
    'id': str,              # PRIMARY KEY (e.g., 'pkg-office')
    'title': str,           # Course title
    'description': str,     # Course description
    'image_url': str,       # Course image/thumbnail
    'created_at': datetime  # Creation timestamp
}
```

**Query Examples:**
```python
conn = get_db_connection()

# Get all courses
courses = conn.execute("SELECT * FROM courses").fetchall()

# Get specific course
course = conn.execute(
    "SELECT * FROM courses WHERE id = ?",
    ('pkg-office',)
).fetchone()

# Count courses
count = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
```

---

### videos
```python
{
    'id': int,              # PRIMARY KEY
    'course_id': str,       # FOREIGN KEY → courses(id)
    'title': str,           # Video/Lesson title
    'video_url': str,       # YouTube embed URL
    'duration': int,        # Video length in minutes
    'lesson_order': int,    # Sequence number (1, 2, 3...)
    'created_at': datetime  # Creation timestamp
}
```

**Query Examples:**
```python
conn = get_db_connection()

# Get all videos in a course
videos = conn.execute(
    "SELECT * FROM videos WHERE course_id = ? ORDER BY lesson_order",
    ('pkg-office',)
).fetchall()

# Get video count per course
counts = conn.execute("""
    SELECT course_id, COUNT(*) as video_count
    FROM videos
    GROUP BY course_id
""").fetchall()

# Get specific video
video = conn.execute(
    "SELECT * FROM videos WHERE id = ?",
    (1,)
).fetchone()
```

---

### user_progress
```python
{
    'id': int,              # PRIMARY KEY
    'user_id': int,         # FOREIGN KEY → users(id)
    'video_id': int,        # FOREIGN KEY → videos(id)
    'completed': bool,      # 1 if fully watched, 0 if partial
    'watch_position': int,  # Seconds watched (for resume)
    'watched_at': datetime  # Last watch timestamp
}
```

**Query Examples:**
```python
conn = get_db_connection()

# Get user's completed videos
completed = conn.execute(
    "SELECT * FROM user_progress WHERE user_id = ? AND completed = 1",
    (1,)
).fetchall()

# Get incomplete videos
incomplete = conn.execute(
    "SELECT * FROM user_progress WHERE user_id = ? AND completed = 0",
    (1,)
).fetchall()

# Get videos watched in a course
course_videos = conn.execute("""
    SELECT up.* FROM user_progress up
    INNER JOIN videos v ON up.video_id = v.id
    WHERE up.user_id = ? AND v.course_id = ?
    ORDER BY up.watched_at DESC
""", (1, 'pkg-office')).fetchall()

# Get last watched video in course
last_video = conn.execute("""
    SELECT video_id FROM user_progress
    WHERE user_id = ? 
    AND video_id IN (SELECT id FROM videos WHERE course_id = ?)
    ORDER BY watched_at DESC
    LIMIT 1
""", (1, 'pkg-office')).fetchone()
```

---

### course_completion
```python
{
    'id': int,              # PRIMARY KEY
    'user_id': int,         # FOREIGN KEY → users(id)
    'course_id': str,       # FOREIGN KEY → courses(id)
    'completed_at': datetime # Completion timestamp
}
```

**Query Examples:**
```python
conn = get_db_connection()

# Get user's completed courses
completed = conn.execute(
    "SELECT * FROM course_completion WHERE user_id = ?",
    (1,)
).fetchall()

# Check if user completed a course
completed = conn.execute(
    "SELECT * FROM course_completion WHERE user_id = ? AND course_id = ?",
    (1, 'pkg-office')
).fetchone()

if completed:
    print(f"Completed on: {completed['completed_at']}")

# Count completed courses
count = conn.execute(
    "SELECT COUNT(*) FROM course_completion WHERE user_id = ?",
    (1,)
).fetchone()[0]

# Leaderboard - users by courses completed
leaderboard = conn.execute("""
    SELECT u.username, COUNT(cc.id) as courses_completed
    FROM users u
    LEFT JOIN course_completion cc ON u.id = cc.user_id
    GROUP BY u.id
    ORDER BY courses_completed DESC
""").fetchall()
```

---

## Complete Example: Track User Progress

```python
from app import (
    get_course_progress,
    get_all_course_progress,
    get_course_videos,
    mark_video_completed,
    get_db_connection
)

# Setup
user_id = 1
course_id = 'pkg-office'

# Get initial progress
progress = get_course_progress(user_id, course_id)
print(f"Initial: {progress['completed_videos']}/{progress['total_videos']} ({progress['progress_percent']}%)")

# Get all videos in course
videos = get_course_videos(course_id)
print(f"\nCourse has {len(videos)} videos:")
for video in videos:
    print(f"  {video['lesson_order']}. {video['title']}")

# Simulate user completing videos
print("\nCompleting videos...")
for video in videos[:3]:  # Complete first 3 videos
    success = mark_video_completed(user_id, video['id'])
    if success:
        progress = get_course_progress(user_id, course_id)
        print(f"  ✓ {video['title']} - Progress: {progress['progress_percent']}%")

# Check all courses
print("\nAll course progress:")
progress_map = get_all_course_progress(user_id, ['pkg-office', 'pkg-design'])
for course, prog in progress_map.items():
    if prog['total_videos'] > 0:
        status = "✅" if prog['is_completed'] else f"{prog['progress_percent']}%"
        print(f"  {course}: {prog['completed_videos']}/{prog['total_videos']} {status}")

# Query database directly
print("\nDirect database queries:")
conn = get_db_connection()

# Count progress
result = conn.execute("""
    SELECT 
        COUNT(*) as total_videos,
        SUM(CASE WHEN completed=1 THEN 1 ELSE 0 END) as watched_videos
    FROM user_progress
    WHERE user_id = ? AND video_id IN 
        (SELECT id FROM videos WHERE course_id = ?)
""", (user_id, course_id)).fetchone()

print(f"  Database: {result['watched_videos']}/{result['total_videos']} videos")

conn.close()
```

**Output Example:**
```
Initial: 0/5 (0%)

Course has 5 videos:
  1. Word Basics
  2. Advanced Formatting
  3. Tables and Lists
  4. Excel Intro
  5. Excel Advanced

Completing videos...
  ✓ Word Basics - Progress: 20%
  ✓ Advanced Formatting - Progress: 40%
  ✓ Tables and Lists - Progress: 60%

All course progress:
  pkg-office: 3/5 60%
  pkg-design: 0/4 0%

Direct database queries:
  Database: 3/5 videos
```

---

## Error Handling

```python
from app import mark_video_completed, get_course_progress, get_db_connection

try:
    # Try to mark video complete
    success = mark_video_completed(user_id=1, video_id=999)
    
    if not success:
        print("Failed to mark video as complete")
    else:
        # Get updated progress
        progress = get_course_progress(1, 'pkg-office')
        print(f"Success! Progress: {progress['progress_percent']}%")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

---

## Performance Tips

```python
# ✅ GOOD: Use context processor (caches for duration of request)
# Variables automatically available in template:
# {{ course_progress.get('pkg-office') }}

# ❌ AVOID: Multiple function calls
# for course_id in enrolled_packages:
#     progress = get_course_progress(user_id, course_id)  # Multiple queries!

# ✅ GOOD: Use bulk function
progress_map = get_all_course_progress(user_id, enrolled_packages)

# ✅ GOOD: Close connections
conn = get_db_connection()
# ... do work ...
conn.close()

# ❌ AVOID: Leaving connections open
conn = get_db_connection()
# ... forgot to close!
```

---

## Testing

```python
# test_progress.py
import unittest
from app import (
    app,
    get_course_progress,
    mark_video_completed,
    get_db_connection
)

class TestProgress(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        
    def test_mark_video_complete(self):
        """Test marking video as complete"""
        success = mark_video_completed(user_id=1, video_id=1)
        self.assertTrue(success)
        
    def test_get_progress(self):
        """Test getting course progress"""
        progress = get_course_progress(user_id=1, course_id='pkg-office')
        self.assertIn('progress_percent', progress)
        self.assertGreaterEqual(progress['progress_percent'], 0)
        self.assertLessEqual(progress['progress_percent'], 100)

if __name__ == '__main__':
    unittest.main()
```

Run with: `python -m unittest test_progress.py`

---

## Full Implementation Reference

See `COURSE_PROGRESS_SYSTEM.md` for:
- Database schema details
- Complete route documentation
- Template integration examples
- Extending the system
- Troubleshooting
