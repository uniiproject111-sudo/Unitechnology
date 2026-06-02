# 📚 Course Progress Tracking System - Complete Documentation

## Overview

A complete course progress tracking system for Flask + SQLite course platform. Automatically tracks video completion, calculates progress percentage, shows completion status, and enables users to resume from their last watched video.

---

## Architecture

### Database Tables

#### 1. `courses` - Course Metadata
```sql
CREATE TABLE courses (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```
- **id**: Package ID (e.g., 'pkg-office', 'pkg-design')
- **title**: Course title
- **description**: Course description
- **image_url**: Course thumbnail/banner image

#### 2. `videos` - Course Lessons/Videos
```sql
CREATE TABLE videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT NOT NULL,
    title TEXT NOT NULL,
    video_url TEXT NOT NULL,
    duration INTEGER,
    lesson_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(course_id) REFERENCES courses(id)
)
```
- **id**: Unique video ID
- **course_id**: Link to course
- **title**: Video title
- **video_url**: YouTube embed URL or video URL
- **duration**: Video length in minutes
- **lesson_order**: Video sequence in course (1, 2, 3...)

#### 3. `user_progress` - Track Watched Videos
```sql
CREATE TABLE user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    video_id INTEGER NOT NULL,
    completed BOOLEAN DEFAULT 0,
    watch_position INTEGER DEFAULT 0,
    watched_at TIMESTAMP,
    UNIQUE(user_id, video_id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(video_id) REFERENCES videos(id)
)
```
- **user_id**: User who watched the video
- **video_id**: Video watched
- **completed**: Whether video is fully watched (1) or partial (0)
- **watch_position**: Last video position in seconds (for resume)
- **watched_at**: Timestamp of last watch

#### 4. `course_completion` - Course Completion Status
```sql
CREATE TABLE course_completion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_id TEXT NOT NULL,
    completed_at TIMESTAMP,
    UNIQUE(user_id, course_id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(course_id) REFERENCES courses(id)
)
```
- Tracks when a user completes an entire course

---

## Backend Routes

### 1. Course Detail Page
```python
GET /course/<course_id>
```
- **Purpose**: Display course with all videos and progress
- **Authentication**: Requires login and enrollment in course
- **Returns**: course_player.html template
- **Data Passed**:
  - `course`: Course metadata
  - `videos`: List of all videos
  - `progress`: Progress data (completed, total, %)
  - `video_progress_map`: Individual video completion status

**Example Usage**:
```html
<a href="{{ url_for('course_detail', course_id='pkg-office') }}">
  Open Course
</a>
```

### 2. Track Video Completion
```python
POST /api/track-video/<video_id>
```
- **Purpose**: Mark a video as completed
- **Authentication**: Requires login
- **Request**: JSON POST
- **Response**: `{"status": "success", "message": "Video marked as completed"}`
- **Behavior**:
  - Inserts/updates user_progress record
  - Automatically checks if course is fully completed
  - Updates course_completion table if all videos watched

**Example Usage**:
```javascript
fetch('/api/track-video/1', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'}
})
.then(res => res.json())
.then(data => console.log(data));
```

### 3. Get Course Progress
```python
GET /api/course-progress/<course_id>
```
- **Purpose**: Get progress data for a course
- **Authentication**: Requires login
- **Response JSON**:
```json
{
  "total_videos": 10,
  "completed_videos": 5,
  "progress_percent": 50,
  "is_completed": false,
  "last_video_id": 5
}
```

**Example Usage**:
```javascript
fetch('/api/course-progress/pkg-office')
  .then(res => res.json())
  .then(data => {
    console.log(`Progress: ${data.progress_percent}%`);
    console.log(`Completed: ${data.completed_videos}/${data.total_videos}`);
  });
```

### 4. Get Last Watched Video
```python
GET /api/last-video/<course_id>
```
- **Purpose**: Get the last video user watched for resuming
- **Authentication**: Requires login
- **Response JSON**:
```json
{
  "last_video_id": 5,
  "progress_percent": 50
}
```

---

## Helper Functions

### `get_course_progress(user_id, course_id)`
Calculates complete progress data for a user in a course.

**Returns**:
```python
{
    "total_videos": 10,           # Total videos in course
    "completed_videos": 5,        # How many user completed
    "progress_percent": 50,       # Percentage (0-100)
    "is_completed": False,        # Is course fully completed?
    "last_video_id": 5            # Last watched video ID (or None)
}
```

**Usage**:
```python
progress = get_course_progress(user_id=1, course_id='pkg-office')
print(f"Progress: {progress['progress_percent']}%")
```

### `get_all_course_progress(user_id, enrolled_packages)`
Get progress for ALL enrolled courses at once.

**Returns**: Dictionary mapping course_id to progress data

**Usage**:
```python
progress_map = get_all_course_progress(
    user_id=1,
    enrolled_packages=['pkg-office', 'pkg-design']
)
# Result:
# {
#   'pkg-office': {...progress data...},
#   'pkg-design': {...progress data...}
# }
```

### `get_course_videos(course_id)`
Retrieve all videos for a course ordered by lesson.

**Returns**: List of video rows (dictionaries)

**Usage**:
```python
videos = get_course_videos('pkg-office')
for video in videos:
    print(f"{video['lesson_order']}. {video['title']}")
```

### `mark_video_completed(user_id, video_id)`
Mark a video as completed and auto-check for course completion.

**Returns**: True if successful, False if error

**Behavior**:
1. Updates/inserts user_progress record
2. Checks if entire course is now completed
3. If completed, records in course_completion table

**Usage**:
```python
success = mark_video_completed(user_id=1, video_id=5)
if success:
    print("Video marked as completed!")
```

---

## Template Integration

### Updated `korsati.html` - My Courses Page

Each enrolled course now displays:

1. **Progress Bar** - Visual progress indicator
2. **Stats** - "X/Y videos completed | Z%"
3. **Status Badge** - "✅ Completed" if course finished
4. **Continue Button** - Links to course player

**Example Display**:
```
┌─────────────────────────────────────────────────────────┐
│ 🖥️ Office Software Package      [Progress: 50% | 5/10] │
│ ████████░░░░░░░░░░░░░░░░░░░░░ 50%                      │
│ [Continue Course Button] ────────> Open course player   │
└─────────────────────────────────────────────────────────┘
```

### `course_player.html` - Video Player Page

Features:
- **Video Player**: Full-width iframe video player
- **Progress Bar**: Shows course-wide progress
- **Video Stats**: Completed/Total videos, percentage
- **Completion Status**: "✅ Course Completed!" or "🎯 In Progress"
- **Videos List**: 
  - All videos with lesson numbers
  - ✓ checkmark for completed videos
  - Click to select (extensible for multi-video)
- **Complete Button**: Mark current video as done

**Layout**:
```
[Navbar]
────────────────────────────────────────────────────────
│  [Video Player]          │  [Progress Card]        │
│  (Full 16:9)             │  ─────────────────      │
│  Title + Complete Btn    │  5/10 Videos Done       │
│  Video Info              │  Progress Bar (50%)     │
│                          │  Status Badge           │
│                          │  ─────────────────      │
│                          │  [Videos List]          │
│                          │  1. Intro      ✓        │
│                          │  2. Advanced           │
│                          │  3. Tables      ✓      │
│                          │  ...                    │
────────────────────────────────────────────────────────
```

---

## Context Processor

The `inject_user_context()` automatically injects into ALL templates:

```python
{
    "user_name": "Ahmed",
    "enrolled_packages": ["pkg-office", "pkg-design"],
    "course_progress": {
        "pkg-office": {
            "total_videos": 10,
            "completed_videos": 5,
            "progress_percent": 50,
            "is_completed": False,
            "last_video_id": 5
        },
        "pkg-design": {...}
    }
}
```

**Usage in Templates**:
```jinja2
<!-- Access progress in any template -->
{% set pkg_progress = course_progress.get('pkg-office', {}) %}

Progress: {{ pkg_progress.progress_percent }}%
Videos: {{ pkg_progress.completed_videos }}/{{ pkg_progress.total_videos }}

{% if pkg_progress.is_completed %}
  <p>✅ Course Completed!</p>
{% endif %}
```

---

## Database Seeding

The `seed_db.py` script creates sample data:

```python
python seed_db.py
```

**Adds**:
- 4 sample courses (Office, Design, Montage, AI)
- 20 sample videos with proper lesson ordering
- Ready-to-use for testing

**Manual Insertion Example**:
```python
import sqlite3

conn = sqlite3.connect('test_fr.db')
cursor = conn.cursor()

# Add course
cursor.execute("""
    INSERT INTO courses (id, title, description, image_url)
    VALUES ('pkg-custom', 'My Course', 'Description', '/img.png')
""")

# Add videos
for i in range(1, 6):
    cursor.execute("""
        INSERT INTO videos (course_id, title, video_url, duration, lesson_order)
        VALUES ('pkg-custom', f'Video {i}', 'https://youtube.com/embed/...', 15, {i})
    """)

conn.commit()
conn.close()
```

---

## Complete User Flow

### 1. User Signs Up & Enrolls
```
Signup Page → Login → Browse Courses → Enroll in 'pkg-office'
```

### 2. User Visits My Courses
```
/korsati → Displays all enrolled courses with progress bars
Click "Continue Course" → Redirects to course player
```

### 3. User Watches Video & Completes
```
/course/pkg-office (loads first video)
User clicks "Complete" button
→ POST /api/track-video/1 (video marked complete)
→ Progress updates: 1/10 videos (10%)
→ Page refreshes, shows ✓ on first video
```

### 4. User Completes Course
```
After completing all 10 videos
→ Progress reaches 100%
→ Course marked as completed
→ Status shows "✅ Course Completed!"
```

### 5. Resume Later
```
User revisits /course/pkg-office
→ System loads where they left off
→ Can click on any video to continue
→ Progress bar stays updated
```

---

## CSS Features

### Progress Bar
```css
/* Animated gradient fill */
.progress-bar-fill {
  background: linear-gradient(90deg, var(--blue), #2196F3);
  transition: width 0.3s ease;
}
```

### Video List
```css
/* Green highlight for completed videos */
.video-item.completed {
  background: #f0f7f0;
}

.video-item.completed .video-number {
  background: var(--success);  /* Green */
}
```

### Responsive Design
- **Desktop**: 2-column layout (player + sidebar)
- **Tablet**: Flex wrap layout
- **Mobile**: Single column stack

---

## API Examples

### JavaScript - Complete a Video
```javascript
async function completeCurrentVideo() {
  const videoId = 1;  // Get from page data
  
  try {
    const response = await fetch(`/api/track-video/${videoId}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'}
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
      alert('Video marked complete!');
      location.reload();  // Refresh to show updated progress
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### JavaScript - Get Course Progress
```javascript
async function showProgress() {
  const courseId = 'pkg-office';
  
  const response = await fetch(`/api/course-progress/${courseId}`);
  const progress = await response.json();
  
  console.log(`${progress.completed_videos}/${progress.total_videos}`);
  console.log(`Progress: ${progress.progress_percent}%`);
  
  if (progress.is_completed) {
    console.log('Course is completed!');
    console.log('Last video watched:', progress.last_video_id);
  }
}
```

### Python - Mark Videos Complete
```python
from app import mark_video_completed, get_course_progress

# Mark video as complete
mark_video_completed(user_id=1, video_id=5)

# Check progress
progress = get_course_progress(user_id=1, course_id='pkg-office')
print(f"Progress: {progress['progress_percent']}%")
print(f"Completed: {progress['is_completed']}")
```

---

## Extending the System

### Add New Course
```python
conn = get_db_connection()
conn.execute(
    "INSERT INTO courses (id, title, description, image_url) VALUES (?, ?, ?, ?)",
    ('pkg-photography', 'Photography Basics', '...', '/img.png')
)
conn.commit()

# Add videos
for i in range(1, 8):
    conn.execute(
        "INSERT INTO videos (course_id, title, video_url, duration, lesson_order) VALUES (?, ?, ?, ?, ?)",
        ('pkg-photography', f'Lesson {i}', 'youtube_url', 20, i)
    )
conn.commit()
```

### Add Video Tracking on Player Load
```javascript
// Track watch time (every 30 seconds)
setInterval(async () => {
  const watchPosition = player.currentTime;
  await fetch(`/api/update-position/${videoId}`, {
    method: 'POST',
    body: JSON.stringify({position: watchPosition})
  });
}, 30000);
```

### Add Quiz Before Completion
```python
# Modify mark_video_completed to require quiz first
def mark_video_completed(user_id, video_id, quiz_passed=False):
    if not quiz_passed:
        return False  # Quiz not passed yet
    
    # ... rest of completion logic
```

---

## Performance Optimization

### Database Indexing
```sql
-- Add indexes for faster queries
CREATE INDEX idx_user_progress_user ON user_progress(user_id);
CREATE INDEX idx_user_progress_video ON user_progress(video_id);
CREATE INDEX idx_course_completion ON course_completion(user_id);
CREATE INDEX idx_videos_course ON videos(course_id);
```

### Query Optimization
```python
# Instead of getting all data:
def get_course_progress_cached(user_id, course_id):
    # Use Redis or in-memory cache
    cache_key = f"progress_{user_id}_{course_id}"
    cached = cache.get(cache_key)
    
    if cached:
        return cached
    
    progress = get_course_progress(user_id, course_id)
    cache.set(cache_key, progress, timeout=300)  # 5 minute cache
    
    return progress
```

---

## Troubleshooting

### Videos not showing progress
- Check: Is user enrolled in course? (`enrollments` table)
- Check: Are videos in database? (`videos` table)
- Check: Does video have correct `course_id`?

### Progress bar not updating
- Check: Is video marked as `completed = 1` in database?
- Check: Is `watched_at` timestamp set?
- Clear browser cache and refresh

### "Course not found" error
- Verify course_id exists in `courses` table
- Check package_id in `enrollments` matches course_id in routes

### Database locked error
- Close all previous connections
- Restart Flask app: `python app.py`
- Check for concurrent writes

---

## Database Reset

To reset progress for testing:

```python
import sqlite3
conn = sqlite3.connect('test_fr.db')

# Clear all progress
conn.execute("DELETE FROM user_progress")
conn.execute("DELETE FROM course_completion")

conn.commit()
conn.close()
print("Progress reset!")
```

---

## File Structure

```
project/
├── app.py                    # Main Flask app with routes & helpers
├── seed_db.py               # Database seeding script
├── test_fr.db               # SQLite database
├── templates/
│   ├── korsati.html        # My Courses page (updated)
│   ├── course_player.html  # Course detail & video player
│   ├── navbar.html         # Navigation (included)
│   └── ...other templates
├── static/
│   ├── css/
│   ├── images/
│   └── ...assets
└── photos/                  # Course images

```

---

## Summary

✅ **Implemented**:
- Complete progress tracking system
- Automatic video completion detection
- Course completion status
- Progress bars & statistics
- Last watched video tracking
- Clean API endpoints
- Responsive video player
- Database seeding

🚀 **Ready for**:
- Production deployment
- User testing
- Further customization
- Integration with video players
- Email notifications on completion
- Certificate generation

---

## Support & Questions

For implementation details, refer to:
- `app.py` - All backend logic and comments
- `course_player.html` - Frontend video player
- `korsati.html` - Progress display integration
