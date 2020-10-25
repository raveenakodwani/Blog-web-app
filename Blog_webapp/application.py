from flask import Flask, session, render_template, request, redirect, flash
from flask_session import Session
from cs50 import SQL
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


from helpers import login_required

#import sqlite3
import datetime


app = Flask(__name__)


#app.config["IMAGE_UPLOADS"] = "/home/ubuntu/FINAL_PROJECT/Blog_webapp/static/images/uploads"

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///blog.db")

@app.route("/")
@login_required
def index():
    bloglist = db.execute("SELECT * from blogs order by blog_id desc")
    print(bloglist)
    if not bloglist:
        return render_template("index.html", message="No blogs published yet!")

    for blogs in bloglist:
        timestamp = blogs['timestamp']
        month = timestamp[5:7]
        if month == '01':
            month = 'Jan'
        elif month =='02':
            month = 'Feb'
        elif month =='03':
            month = 'Mar'
        elif month =='04':
            month = 'Apr'
        elif month =='05':
            month = 'May'
        elif month =='06':
            month = 'Jun'
        elif month =='07':
            month = 'Jul'
        elif month =='08':
            month = 'Aug'
        elif month =='09':
            month = 'Sep'
        elif month =='10':
            month = 'Oct'
        elif month =='11':
            month = 'Nov'
        else:
            month = 'Dec'

        timestamp = month+' '+timestamp[8:10]+', '+timestamp[0:4]+' at '+timestamp[11:16]
        print(timestamp)
        blogs['timestamp'] = timestamp

    return render_template("index.html" , bloglist = bloglist)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        username_list = db.execute("SELECT username from users where username = :username", username = username)

        if (len(username_list)!=0) or (not username) or (not password) or (not confirm) or (password!=confirm):

            err_msg = []

            if len(username_list) != 0:
                err_msg.append("Username already taken")

            if not username:
                err_msg.append("You must provide a username")

            if not password:
                err_msg.append("You must provide password")

            if not confirm:
                err_msg.append("You must confirm password")

            if password != confirm:
                err_msg.append("Passwords do not match")

            print(err_msg)

            return render_template("register.html", err_msg = err_msg)

        db.execute ("INSERT INTO users (username, hash) VALUES ( :username, :hashed)", username = username, hashed = generate_password_hash(password))
        flash("Registered!")
        return render_template("login.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    else:
        # Forget any user_id
        session.clear()

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            err_msg = []

            if not username:
                err_msg.append("You must provide a username")
            if not password:
                err_msg.append("You must provide a password")

            return render_template("login.html", err_msg = err_msg)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username = username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            err_msg=[]
            err_msg.append("Invalid username or password")
            return render_template("login.html", err_msg = err_msg)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        print(session)

        # Redirect user to home page
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/addblog", methods=["GET", "POST"])
@login_required
def addblog():
    if request.method == "GET":
        return render_template("addblog.html")
    else:
        title = request.form.get("title")
        author = request.form.get("author")
        category = request.form.get("category")
        content = request.form.get("content")

        print(title,author,category,content)
        db.execute("INSERT INTO blogs (person_id, title, author, category, content) VALUES (:id, :title, :author, :category, :content)",id = session["user_id"], title = title, author = author, category = category, content = content)
        flash("Published!")
        return redirect("/")


@app.route("/myblogs")
@login_required
def myblogs():
    mybloglist = db.execute("SELECT * FROM blogs WHERE person_id = :id", id = session["user_id"])
    print(mybloglist)
    if not mybloglist:
        print("sorry")
        return render_template("apology.html", message="You have not published any blogs!")
    return render_template("myblogs.html", mybloglist = mybloglist)


@app.route("/blog/<blog_id>")
@login_required
def blog(blog_id):
    print(blog_id)
    blog_details = db.execute("SELECT * from blogs where blog_id = :blog_id", blog_id = blog_id)
    print(blog_details)
    return render_template("blog.html", blog_details = blog_details)


@app.route("/editblog/<blog_id>", methods = ["GET","POST"])
@login_required
def editblog(blog_id):
    if request.method == "GET":
        myblog = db.execute("SELECT * from blogs where blog_id = :blog_id", blog_id = blog_id)
        print(myblog)
        return render_template("editblog.html", myblog = myblog)
    else:
        title = request.form.get('title')
        author = request.form.get('author')
        category = request.form.get('category')
        content = request.form.get('content')

        db.execute("delete from blogs where blog_id=:blog_id", blog_id = blog_id)
        db.execute("insert into blogs (person_id, title, author, category, content) values (:id, :title, :author, :category, :content)", id=session["user_id"], title=title, author=author, category= category, content= content)
        flash("Edited!")
        return redirect("/")


@app.route("/deleteblog/<blog_id>")
@login_required
def deleteblog(blog_id):
    db.execute("delete from blogs where blog_id=:blog_id", blog_id = blog_id)
    flash("Deleted!")
    return redirect("/myblogs")



if __name__ == '__main__':
    app.run(debug = True)



