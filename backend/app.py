from flask_sqlalchemy import SQLAlchemy

from flask import Flask, render_template, send_from_directory, request, redirect, jsonify, url_for, session
from werkzeug.utils import secure_filename
import os, json

# ============================================
# ABSOLUTE PATHS FOR ALL ENVIRONMENTS
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")
POSTS_PATH = os.path.join(DATA_DIR, "posts.json")
HODS_PATH = os.path.join(DATA_DIR, "hods.json")

# Upload folders
UPLOAD_POSTS = os.path.join(STATIC_DIR, "uploads")
UPLOAD_HODS = os.path.join(STATIC_DIR, "uploads", "hods")

# Ensure upload folders exist
os.makedirs(UPLOAD_POSTS, exist_ok=True)
os.makedirs(UPLOAD_HODS, exist_ok=True)
UPLOAD_VIDEOS = os.path.join(STATIC_DIR, "uploads", "videos")
os.makedirs(UPLOAD_VIDEOS, exist_ok=True)
# ============================================


app = Flask(__name__)
app.secret_key = "super-secret-key-456"

# Load raw DB URL from environment
raw_url = os.environ.get("DATABASE_URL", "")

# Convert to SQLAlchemy-compatible psycopg3 URL
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql+psycopg://")

if raw_url.startswith("postgresql://"):
    raw_url = raw_url.replace("postgresql://", "postgresql+psycopg://")

app.config["SQLALCHEMY_DATABASE_URI"] = raw_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.String, primary_key=True)
    type = db.Column(db.String(20))
    title = db.Column(db.Text)
    excerpt = db.Column(db.Text)
    category = db.Column(db.String(100))
    date = db.Column(db.String(20))
    image = db.Column(db.String(255))
    video_file = db.Column(db.String(255))
    video_url = db.Column(db.Text)
    content = db.Column(db.Text)

# ===========================================================
# PAGE ROUTES
# ===========================================================
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/services")
def services():
    with open(HODS_PATH) as f:
        hods = json.load(f)
    return render_template("services.html", hods=hods)


@app.route("/md-general")
def md_general():
    return render_template("md_general.html")


# ===========================================================
# BLOG PAGES
# ===========================================================
@app.route("/blog")
def blog_list():
    posts = Post.query.order_by(Post.id.desc()).all()  # newest first
    return render_template("blog_list.html", posts=posts)


@app.route("/blog/<post_id>")
def blog_details(post_id):
    post = Post.query.get(post_id)
    if not post:
        return "Post Not Found", 404

    # get 3 other posts except current one
    related_posts = (
        Post.query.filter(Post.id != post_id)
        .order_by(Post.id.desc())
        .limit(3)
        .all()
    )

    return render_template(
        "blog_details.html",
        post=post,
        related_posts=related_posts
    )

# ===========================================================
# STATIC PAGES
# ===========================================================
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# ===========================================================
# AUTH HELPERS
# ===========================================================
def admin_required(f):
    def wrap(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap


# ===========================================================
# ADMIN LOGIN
# ===========================================================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    from config import ADMIN_USERNAME, ADMIN_PASSWORD

    if request.method == "POST":
        if request.form["username"] == ADMIN_USERNAME and request.form["password"] == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect("/admin/dashboard")
        return render_template("admin_login.html", error="Invalid login details")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect("/admin/login")


# ===========================================================
# ADMIN DASHBOARD
# ===========================================================
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    posts = Post.query.order_by(Post.id.desc()).all()  # newest first

    # HODS still JSON for now
    with open(HODS_PATH) as f:
        hods = json.load(f)

    return render_template("admin_dashboard.html", posts=posts, hods=hods)


# Make sure these constants exist near the top of your app.py
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# POSTS_PATH = os.path.join(BASE_DIR, "data", "posts.json")
# UPLOAD_POSTS = os.path.join(BASE_DIR, "static", "uploads")
# os.makedirs(UPLOAD_POSTS, exist_ok=True)

@app.route("/admin/new-post", methods=["GET", "POST"])
@admin_required
def admin_new_post():

    if request.method == "POST":
        # Form fields
        post_type = request.form.get("type", "article")
        title = request.form.get("title", "").strip()
        excerpt = request.form.get("excerpt", "").strip()
        category = request.form.get("category", "General")
        date = request.form.get("date", "")
        content = request.form.get("content", "")
        video_url = request.form.get("video_url", "").strip()

        # ---------------- IMAGE UPLOAD ----------------
        image_file = request.files.get("image")
        if image_file and image_file.filename:
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(UPLOAD_POSTS, image_filename))
        else:
            image_filename = "default.jpg"

        # ---------------- VIDEO UPLOAD ----------------
        video_file = request.files.get("video_file")
        if video_file and video_file.filename:
            video_filename = secure_filename(video_file.filename)
            video_file.save(os.path.join(UPLOAD_POSTS, video_filename))
            post_type = "video"
        else:
            video_filename = ""

        # Create DB object
        new_post = Post(
            id=os.urandom(8).hex(),  # 🔥 unique ID
            type=post_type,
            title=title,
            excerpt=excerpt,
            category=category,
            date=date,
            image=image_filename,
            video_file=video_filename,
            video_url=video_url,
            content=content
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect("/admin/dashboard")

    return render_template("admin_new_post.html")



# ===========================================================
# EDIT POST  (FIXED)
# ===========================================================
@app.route("/admin/edit/<post_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_post(post_id):

    post = Post.query.get(post_id)
    if not post:
        return "Post not found", 404

    if request.method == "POST":

        post.title = request.form.get("title", "")
        post.excerpt = request.form.get("excerpt", "")
        post.category = request.form.get("category", "General")
        post.date = request.form.get("date", "")
        post.content = request.form.get("content", "")
        post.video_url = request.form.get("video_url", "").strip()

        # IMAGE
        image_file = request.files.get("image")
        if image_file and image_file.filename:
            img_name = secure_filename(image_file.filename)
            image_file.save(os.path.join(UPLOAD_POSTS, img_name))
            post.image = img_name

        # VIDEO
        video_file = request.files.get("video_file")
        if video_file and video_file.filename:
            video_name = secure_filename(video_file.filename)
            video_file.save(os.path.join(UPLOAD_POSTS, video_name))
            post.video_file = video_name

        # TYPE auto-detect
        if post.video_file or post.video_url:
            post.type = "video"
        else:
            post.type = "article"

        db.session.commit()
        return redirect("/admin/dashboard")

    return render_template("admin_edit_post.html", post=post)



# ===========================================================
# DELETE POST
# ===========================================================
@app.route("/admin/delete/<post_id>", methods=["POST"])
@admin_required
def admin_delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return "Not found", 404

    db.session.delete(post)
    db.session.commit()

    return redirect("/admin/dashboard")

# ===========================================================
# TINYMCE IMAGE UPLOADER
# ===========================================================
@app.route("/admin/upload_tinymce_image", methods=["POST"])
def upload_tinymce_image():

    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file"}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_POSTS, filename)
    file.save(save_path)

    return jsonify({"location": url_for("static", filename=f"uploads/{filename}")})


# ===========================================================
# LOAD & SAVE HODS
# ===========================================================
def load_hods():
    with open(HODS_PATH) as f:
        return json.load(f)

def save_hods(hods):
    with open(HODS_PATH, "w") as f:
        json.dump(hods, f, indent=4)


# ===========================================================
# HODS ADMIN
# ===========================================================
@app.route("/admin/hods")
@admin_required
def admin_hods():
    return render_template("admin_hods.html", hods=load_hods())


@app.route("/admin/hod/new", methods=["GET", "POST"])
@admin_required
def admin_hod_new():

    if request.method == "POST":

        hods = load_hods()
        new_id = max([h["id"] for h in hods]) + 1 if hods else 1

        # upload photo
        photo = request.files["photo"]
        filename = secure_filename(photo.filename)
        save_path = os.path.join(UPLOAD_HODS, filename)
        photo.save(save_path)

        new_hod = {
            "id": new_id,
            "name": request.form["name"],
            "role": request.form["role"],
            "department": request.form["department"],
            "bio": request.form["bio"],
            "photo": f"uploads/hods/{filename}",
            "active": True
        }

        hods.append(new_hod)
        save_hods(hods)

        return redirect("/admin/hods")

    return render_template("admin_hod_form.html", mode="new")


@app.route("/admin/hod/edit/<int:hod_id>", methods=["GET", "POST"])
@admin_required
def admin_hod_edit(hod_id):

    hods = load_hods()
    hod = next((h for h in hods if h["id"] == hod_id), None)

    if not hod:
        return "HOD not found", 404

    if request.method == "POST":

        hod["name"] = request.form["name"]
        hod["role"] = request.form["role"]
        hod["department"] = request.form["department"]
        hod["bio"] = request.form["bio"]
        hod["active"] = ("active" in request.form)

        if request.files["photo"].filename != "":
            photo = request.files["photo"]
            filename = secure_filename(photo.filename)
            save_path = os.path.join(UPLOAD_HODS, filename)
            photo.save(save_path)
            hod["photo"] = f"uploads/hods/{filename}"

        save_hods(hods)

        return redirect("/admin/hods")

    return render_template("admin_hod_form.html", mode="edit", hod=hod)


@app.route("/admin/hod/delete/<int:hod_id>", methods=["POST"])
@admin_required
def admin_hod_delete(hod_id):

    hods = load_hods()
    hods = [h for h in hods if h["id"] != hod_id]
    save_hods(hods)

    return jsonify({"success": True})


@app.route("/hod/<int:hod_id>")
def hod_details(hod_id):

    hods = load_hods()
    hod = next((h for h in hods if h["id"] == hod_id), None)

    if not hod:
        return "HOD not found", 404

    return render_template("hod_details.html", hod=hod)


# ===========================================================
# RUN SERVER
# ===========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)










