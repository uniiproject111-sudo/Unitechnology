from pathlib import Path
import sqlite3
from urllib.parse import urljoin, urlparse
from flask import Flask, abort, render_template, send_from_directory, request, redirect, url_for, session
from jinja2 import TemplateNotFound
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)
app.secret_key = "x9K$2mP!7Qv#L8s@N4wZ"

ROOT = Path(__file__).resolve().parent
DATABASE = ROOT / "test_fr.db"
ALIAS_PAGES = {
    "mainpage": "index",
}

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            package_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, package_id)
        )
        """
    )
    
    # ===== COURSE PROGRESS TRACKING TABLES =====
    # Table for course metadata
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            exam_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    
    # Table for videos/lessons within a course
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT NOT NULL,
            title TEXT NOT NULL,
            video_url TEXT NOT NULL,
            duration INTEGER,
            lesson_order INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
        """
    )
    
    # Table to track user progress on videos
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_progress (
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
        """
    )
    
    # Table to track course completion status
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS course_completion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id TEXT NOT NULL,
            completed_at TIMESTAMP,
            UNIQUE(user_id, course_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
        """
    )
    
    conn.commit()
    conn.close()


init_db()


def is_safe_url(target: str) -> bool:
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc)


# ===== PROGRESS TRACKING HELPERS =====
def get_course_progress(user_id: int, course_id: str) -> dict:
    """
    Calculate progress for a user in a specific course.
    Returns dict with: total_videos, completed_videos, progress_percent, is_completed, last_video
    """
    conn = get_db_connection()
    
    # Get all videos in the course
    videos = conn.execute(
        """
        SELECT id FROM videos WHERE course_id = ? ORDER BY lesson_order
        """,
        (course_id,)
    ).fetchall()
    
    total_videos = len(videos)
    
    if total_videos == 0:
        conn.close()
        return {
            "total_videos": 0,
            "completed_videos": 0,
            "progress_percent": 0,
            "is_completed": False,
            "last_video_id": None
        }
    
    # Get completed videos for this user in this course
    completed = conn.execute(
        """
        SELECT COUNT(*) as count FROM user_progress
        WHERE user_id = ? AND completed = 1
        AND video_id IN (SELECT id FROM videos WHERE course_id = ?)
        """,
        (user_id, course_id)
    ).fetchone()
    
    completed_videos = completed["count"]
    progress_percent = int((completed_videos / total_videos) * 100) if total_videos > 0 else 0
    
    # Check if course is fully completed
    is_completed = completed_videos == total_videos and total_videos > 0
    
    # Get last watched video
    last_video = conn.execute(
        """
        SELECT video_id FROM user_progress
        WHERE user_id = ? AND video_id IN (SELECT id FROM videos WHERE course_id = ?)
        ORDER BY watched_at DESC LIMIT 1
        """,
        (user_id, course_id)
    ).fetchone()
    
    conn.close()
    
    return {
        "total_videos": total_videos,
        "completed_videos": completed_videos,
        "progress_percent": progress_percent,
        "is_completed": is_completed,
        "last_video_id": last_video["video_id"] if last_video else None
    }


def get_all_course_progress(user_id: int, enrolled_packages: list) -> dict:
    """
    Get progress for all enrolled courses.
    Maps package_id to progress data.
    """
    progress_data = {}
    for package_id in enrolled_packages:
        progress_data[package_id] = get_course_progress(user_id, package_id)
    return progress_data


def get_course_videos(course_id: str) -> list:
    """
    Retrieve all videos for a course ordered by lesson order.
    """
    conn = get_db_connection()
    videos = conn.execute(
        """
        SELECT id, title, video_url, duration, lesson_order
        FROM videos WHERE course_id = ?
        ORDER BY lesson_order
        """,
        (course_id,)
    ).fetchall()
    conn.close()
    return videos


def get_course_by_id(course_id: str):
    """
    Retrieve a course by its package ID.
    """
    conn = get_db_connection()
    course = conn.execute(
        "SELECT * FROM courses WHERE id = ?",
        (course_id,)
    ).fetchone()
    conn.close()
    return course


def get_enrolled_courses(user_id: int) -> list:
    """
    Retrieve enrolled courses for a user, including total video count.
    """
    conn = get_db_connection()
    courses = conn.execute(
        """
        SELECT c.id, c.title, c.description, c.image_url,
               COUNT(v.id) AS total_videos
        FROM courses c
        LEFT JOIN videos v ON c.id = v.course_id
        WHERE c.id IN (
            SELECT package_id FROM enrollments WHERE user_id = ?
        )
        GROUP BY c.id
        """,
        (user_id,)
    ).fetchall()
    conn.close()
    return courses


def mark_video_completed(user_id: int, video_id: int) -> bool:
    """
    Mark a video as completed for a user.
    """
    try:
        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO user_progress (user_id, video_id, completed, watched_at)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, video_id) DO UPDATE SET
            completed = 1, watched_at = CURRENT_TIMESTAMP
            """,
            (user_id, video_id)
        )
        
        # Check if course is now fully completed
        video = conn.execute("SELECT course_id FROM videos WHERE id = ?", (video_id,)).fetchone()
        if video:
            course_id = video["course_id"]
            progress = get_course_progress(user_id, course_id)
            
            # If fully completed, record it
            if progress["is_completed"]:
                conn.execute(
                    """
                    INSERT INTO course_completion (user_id, course_id, completed_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id, course_id) DO UPDATE SET
                    completed_at = CURRENT_TIMESTAMP
                    """,
                    (user_id, course_id)
                )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error marking video completed: {e}")
        return False


def get_enrolled_packages():
    enrolled_packages = []
    user_name = session.get("user_name")
    if not user_name:
        return enrolled_packages

    conn = get_db_connection()
    user = conn.execute("SELECT id FROM users WHERE username = ?", (user_name,)).fetchone()
    if user:
        enrollments = conn.execute("SELECT package_id FROM enrollments WHERE user_id = ?", (user["id"],)).fetchall()
        enrolled_packages = [row["package_id"] for row in enrollments]
    conn.close()
    return enrolled_packages


@app.context_processor
def inject_user_context():
    user_name = session.get("user_name")
    enrolled_packages = get_enrolled_packages()
    course_progress = {}
    
    # Get progress for all enrolled courses
    if user_name:
        conn = get_db_connection()
        user = conn.execute("SELECT id FROM users WHERE username = ?", (user_name,)).fetchone()
        conn.close()
        
        if user:
            course_progress = get_all_course_progress(user["id"], enrolled_packages)
    
    return {
        "user_name": user_name,
        "enrolled_packages": enrolled_packages,
        "course_progress": course_progress,  # Dict of {course_id: progress_data}
    }


def render_safe_template(page_name: str):
    safe_page = Path(page_name).stem
    template_name = f"{ALIAS_PAGES.get(safe_page, safe_page)}.html"
    return render_template(template_name)


# =========================
# HOME PAGE
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/courses")
def courses_page_alias():
    return redirect(url_for("page", page_name="courses"))


@app.route("/korsati")
def korsati_page_alias():
    return redirect(url_for("page", page_name="korsati"))


@app.route("/coursespage_mobile")
def coursespage_mobile_alias():
    return redirect(url_for("page", page_name="coursespage_mobile"))


# =========================
# DYNAMIC PAGES
# =========================

# Maps each package_id to the actual course HTML page
COURSE_PAGE_MAP = {
    "word": "/page/MicrosoftWord",
    "excel": "/page/MicrosoftExcel",
    "powerpoint": "/page/powerpoint",
    "teams": "/page/MicrosoftTeams",
    "outlook": "/page/MicrosoftOutlook",
    "onenote": "/page/MicrosoftOneNote",
    "access": "/page/MicrosoftAccess",
    "photoshop": "/page/Photoshop",
    "ilustrator": "/page/Ilustrator",
    "canva": "/page/Canva",
    "indesign": "/page/InDesign",
    "premiere": "/page/premiere",
    "capcut": "/page/CapCut",
    "filmora": "/page/Filmora",
    "lightroom": "/page/Lightroom",
    "panoramamaker": "/page/PanoramaMaker",
    "audacity": "/page/Audacity",
    "audition": "/page/Audition",
    "wordpress": "/page/WordPress",
    "googleclassroom": "/page/googleclassroom",
    "googledrive": "/page/Googledrive",
    "googleforms": "/page/GoogleForms",
    "googlesites": "/page/GoogleSites",
    "claudeai": "/page/claudeai",
    "klingai": "/page/KlingAI",
    "openread": "/page/Openread",
    "notebooklm": "/page/NotebookLM",
    "flowai": "/page/FlowAI",
    "لهجاتي": "/page/لهجاتي",
    "figma": "/page/figma"
}

# Maps package_id to its video IDs for custom progress tracking
COURSE_VIDEO_IDS = {
    "word": [101, 102, 103, 104, 105],
    "excel": [111, 112, 113],
    "powerpoint": [121, 122],
    "teams": [131],
    "outlook": [141],
    "onenote": [151, 152],
    "access": [161, 162],
    "photoshop": [171, 172, 173],
    "ilustrator": [181],
    "canva": [191, 192],
    "indesign": [201],
    "premiere": [211],
    "capcut": [221, 222, 223, 224],
    "filmora": [231, 232],
    "lightroom": [241],
    "panoramamaker": [251],
    "audacity": [261, 262],
    "audition": [271],
    "wordpress": [281, 282, 283, 284, 285],
    "googleclassroom": [291, 292],
    "googledrive": [301, 302],
    "googleforms": [311, 312],
    "googlesites": [321],
    "claudeai": [331, 332],
    "klingai": [341, 342],
    "openread": [351],
    "notebooklm": [361],
    "flowai": [371],
    "لهجاتي": [381],
    "figma": [391, 392, 393, 394, 395]
}

def get_course_page_data(course_id):
    """
    Helper to get progress data and auto-enroll user for custom course pages.
    """
    video_completions = {}
    enrolled = False
    progress = {"completed_videos": 0, "total_videos": 0, "progress_percent": 0, "is_completed": False}
    exam_url = None
    
    if session.get("user_name"):
        conn = get_db_connection()
        user = conn.execute("SELECT id FROM users WHERE username = ?", (session.get("user_name"),)).fetchone()
        if user:
            user_id = user["id"]
            # Auto-enroll
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO enrollments (user_id, package_id) VALUES (?, ?)",
                    (user_id, course_id)
                )
                conn.commit()
            except Exception: pass
            enrolled = True
            
            # Get detailed progress
            progress = get_course_progress(user_id, course_id)
            
            # Get individual video completions for UI buttons
            v_ids = COURSE_VIDEO_IDS.get(course_id, [])
            if v_ids:
                placeholders = ",".join(["?"] * len(v_ids))
                completions = conn.execute(
                    f"SELECT video_id FROM user_progress WHERE user_id = ? AND video_id IN ({placeholders}) AND completed = 1",
                    [user_id] + v_ids
                ).fetchall()
                video_completions = {row["video_id"]: True for row in completions}
        
        # Get exam URL
        course = conn.execute("SELECT exam_url FROM courses WHERE id = ?", (course_id,)).fetchone()
        if course and course["exam_url"]:
            exam_url = course["exam_url"]
        
        conn.close()
    return {"video_completions": video_completions, "enrolled": enrolled, "progress": progress, "exam_url": exam_url}

@app.route("/page/<path:page_name>")
def page(page_name):
    # Strip extension if present
    safe_page = Path(page_name).stem
    
    try:
        if safe_page == "korsati":
            enrolled_courses = []
            if session.get("user_name"):
                conn = get_db_connection()
                user = conn.execute("SELECT id FROM users WHERE username = ?", (session.get("user_name"),)).fetchone()
                conn.close()
                if user:
                    courses = get_enrolled_courses(user["id"])
                    for course in courses:
                        progress = get_course_progress(user["id"], course["id"])
                        enrolled_courses.append({
                            "id": course["id"],
                            "title": course["title"],
                            "description": course["description"],
                            "image_url": course["image_url"],
                            "total_videos": course["total_videos"],
                            "progress": progress,
                            "page_url": COURSE_PAGE_MAP.get(course["id"], f"/page/{course['id']}"),
                        })
            return render_template("korsati.html", enrolled_courses=enrolled_courses)

        # Specialized course data for custom HTML templates
        course_id = None
        PAGE_TO_COURSE = {
            "word": "word", "MicrosoftWord": "word",
            "excel": "excel", "MicrosoftExcel": "excel",
            "powerpoint": "powerpoint",
            "teams": "teams", "MicrosoftTeams": "teams",
            "outlook": "outlook", "MicrosoftOutlook": "outlook",
            "onenote": "onenote", "MicrosoftOneNote": "onenote",
            "acsses": "access", "MicrosoftAccess": "access",
            "Photoshop": "photoshop",
            "Ilustrator": "ilustrator",
            "Canva": "canva",
            "InDesign": "indesign",
            "premiere": "premiere",
            "CapCut": "capcut",
            "Filmora": "filmora",
            "Lightroom": "lightroom",
            "PanoramaMaker": "panoramamaker",
            "Audacity": "audacity",
            "Audition": "audition",
            "WordPress": "wordpress",
            "googleclassroom": "googleclassroom",
            "Googledrive": "googledrive",
            "GoogleForms": "googleforms",
            "GoogleSites": "googlesites",
            "claudeai": "claudeai",
            "KlingAI": "klingai",
            "Openread": "openread",
            "NotebookLM": "notebooklm",
            "FlowAI": "flowai",
            "لهجاتي": "لهجاتي",
            "figma": "figma"
        }
        
        course_id = PAGE_TO_COURSE.get(safe_page)
        
        if course_id:
            data = get_course_page_data(course_id)
            template_name = f"{ALIAS_PAGES.get(safe_page, safe_page)}.html"
            return render_template(template_name, **data)

        return render_safe_template(page_name)

    except TemplateNotFound:
        abort(404)


@app.route("/<path:page_name>.html")
def html_page(page_name):
    # Redirect to the cleaner /page/ route
    return redirect(url_for("page", page_name=page_name))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    message = None
    next_page = request.args.get("next") or request.form.get("next")

    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not fullname or not email or not password or not confirm_password:
            message = "يرجى تعبئة جميع الحقول."
        elif not email.endswith("@gmail.com"):
            message = "يرجى استخدام بريد Gmail فقط (ينتهي بـ @gmail.com)."
        elif password != confirm_password:
            message = "كلمتا المرور غير متطابقتين."
        else:
            password_hash = generate_password_hash(password)
            try:
                conn = get_db_connection()
                conn.execute(
                    "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                    (fullname, email, password_hash),
                )
                conn.commit()
                conn.close()
                session["user_name"] = fullname
                if next_page and is_safe_url(next_page):
                    return redirect(next_page)
                return redirect(url_for("home"))
            except sqlite3.IntegrityError:
                message = "هذا البريد الإلكتروني مستخدم بالفعل."

    return render_template("signup.html", message=message, next=next_page)


def verify_user_password(stored_password, provided_password):
    try:
        if check_password_hash(stored_password, provided_password):
            return True
    except ValueError:
        pass
    return stored_password == provided_password


@app.route("/login", methods=["GET", "POST"])
def login():
    message = None
    next_page = request.args.get("next") or request.form.get("next")

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            message = "يرجى إدخال البريد الإلكتروني وكلمة المرور."
        else:
            conn = get_db_connection()
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            conn.close()

            if user and verify_user_password(user["password"], password):
                session["user_name"] = user["username"]
                if next_page and is_safe_url(next_page):
                    return redirect(next_page)
                return redirect(url_for("home"))

            message = "البريد الإلكتروني أو كلمة المرور غير صحيحة."

    return render_template("login.html", message=message, next=next_page)


@app.route("/logout")
def logout():
    session.pop("user_name", None)
    session.pop("user_email", None)
    return redirect(url_for("home"))


@app.route("/debug/users")
def debug_users():
    conn = get_db_connection()
    users = conn.execute("SELECT id, username, email, created_at FROM users ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("debug_users.html", users=users)


@app.route("/enroll/<package_id>", methods=["GET", "POST"])
def enroll(package_id):
    next_page = request.form.get("next") or request.args.get("next") or request.referrer

    if not session.get("user_name"):
        if next_page and is_safe_url(next_page):
            return redirect(url_for("login", next=next_page))
        return redirect(url_for("login"))
        
    conn = get_db_connection()
    user = conn.execute("SELECT id FROM users WHERE username = ?", (session.get("user_name"),)).fetchone()
    
    if user:
        user_id = user["id"]
        try:
            conn.execute("INSERT INTO enrollments (user_id, package_id) VALUES (?, ?)", (user_id, package_id))
            conn.commit()
        except sqlite3.IntegrityError:
            pass # Already enrolled
            
    conn.close()
    if next_page and is_safe_url(next_page):
        return redirect(next_page)
    return redirect(url_for("page", page_name="korsati"))


# ===== COURSE PROGRESS TRACKING ROUTES =====

@app.route("/course/<course_id>")
def course_detail(course_id):
    """
    Display course detail page with all videos.
    Requires user to be enrolled in the course.
    """
    if not session.get("user_name"):
        return redirect(url_for("login", next=request.url))
    
    conn = get_db_connection()
    user = conn.execute("SELECT id FROM users WHERE username = ?", (session.get("user_name"),)).fetchone()
    
    if not user:
        abort(401)
    
    user_id = user["id"]
    
    # Check if user is enrolled in this course
    enrollment = conn.execute(
        "SELECT id FROM enrollments WHERE user_id = ? AND package_id = ?",
        (user_id, course_id)
    ).fetchone()

    if not enrollment:
        # Redirect logged-in users to enroll before viewing the course.
        return redirect(url_for('enroll', package_id=course_id, next=url_for('course_detail', course_id=course_id)))

    # Get course info
    course = conn.execute(
        "SELECT * FROM courses WHERE id = ?",
        (course_id,)
    ).fetchone()
    
    # Get all videos
    videos = conn.execute(
        """
        SELECT id, title, video_url, duration, lesson_order
        FROM videos WHERE course_id = ?
        ORDER BY lesson_order
        """,
        (course_id,)
    ).fetchall()
    
    # Get progress
    progress = get_course_progress(user_id, course_id)
    
    # Get user progress for each video
    video_progress = conn.execute(
        """
        SELECT video_id, completed, watch_position
        FROM user_progress WHERE user_id = ?
        AND video_id IN (SELECT id FROM videos WHERE course_id = ?)
        """,
        (user_id, course_id)
    ).fetchall()
    
    video_progress_map = {row["video_id"]: row for row in video_progress}
    
    conn.close()
    
    return render_template(
        "course_player.html",
        course=course,
        videos=videos,
        progress=progress,
        video_progress_map=video_progress_map,
        user_name=session.get("user_name")
    )


@app.route("/api/track-video/<int:video_id>", methods=["POST"])
def track_video(video_id):
    """
    API endpoint to mark a video as completed.
    """
    if not session.get("user_name"):
        return {"error": "Unauthorized"}, 401
    
    conn = get_db_connection()
    user = conn.execute("SELECT id FROM users WHERE username = ?", (session.get("user_name"),)).fetchone()
    conn.close()
    
    if not user:
        return {"error": "User not found"}, 404
    
    success = mark_video_completed(user["id"], video_id)
    
    if success:
        return {"status": "success", "message": "Video marked as completed"}
    else:
        return {"error": "Failed to track video"}, 500


@app.route("/api/course-progress/<course_id>")
def get_progress(course_id):
    """
    API endpoint to get course progress for the current user.
    """
    if not session.get("user_name"):
        return {"error": "Unauthorized"}, 401
    
    conn = get_db_connection()
    user = conn.execute("SELECT id FROM users WHERE username = ?", (session.get("user_name"),)).fetchone()
    conn.close()
    
    if not user:
        return {"error": "User not found"}, 404
    
    progress = get_course_progress(user["id"], course_id)
    return progress


@app.route("/api/last-video/<course_id>")
def get_last_video(course_id):
    """
    API endpoint to get the last watched video in a course.
    """
    if not session.get("user_name"):
        return {"error": "Unauthorized"}, 401
    
    conn = get_db_connection()
    user = conn.execute("SELECT id FROM users WHERE username = ?", (session.get("user_name"),)).fetchone()
    
    progress = get_course_progress(user["id"], course_id)
    conn.close()
    
    return {
        "last_video_id": progress.get("last_video_id"),
        "progress_percent": progress.get("progress_percent")
    }


@app.route("/photos/<path:filename>")
def photos_static(filename):
    return send_from_directory(ROOT / "photos", filename)


@app.route("/page/photos/<path:filename>")
def page_photos_static(filename):
    return send_from_directory(ROOT / "photos", filename)


# =========================
# STATIC ASSETS
# =========================
@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(ROOT / "static", filename)

 
# =========================
# 404 PAGE
# =========================
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )