from flask import Flask, flash, render_template, redirect, request, url_for

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

from models import User, Profile, FriendRequest, Friend, Post, Like, Comment, db
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config.from_object('config')


login_manager = LoginManager(app)
login_manager.login_view = "login"

with app.app_context():
    db.init_app(app)
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



AVAILABLE_LANGUAGES = {
    'HTML': 'static/images/languages/html.png',
    'CSS': 'static/images/languages/css.png',
    'Python': 'static/images/languages/python.png',
    'JavaScript': 'static/images/languages/javascript.png',
    'Java': 'static/images/languages/java.png',
    'PHP': 'static/images/languages/php.png',
    'C++': 'static/images/languages/cpp.png',
    'C#': 'static/images/languages/csharp.png',
    'Ruby': 'static/images/languages/ruby.png',
    'SQL': 'static/images/languages/sql.png'
}





# Register Page
@app.route("/register")
def register():
    # Render Register page
    return render_template("register.html")

# Register user
@app.route("/register", methods=["POST"])
def register_user():
    # Get first name from form
    first_name = request.form["first_name"]
    # Get surname from form
    surname = request.form["surname"]
    # Get email from form
    email = request.form["email"]
    # Get username from form
    username = request.form["username"]
    # Get password from form
    password = request.form["password"]

    # If username already exists in user table
    if User.query.filter_by(username=username).first():
        # Flash messages
        flash(f"The username '{username}' is already taken")
        # Redirect to register page
        return redirect(url_for("register"))
    
    # Create new user
    user = User(username=username, password=password)
    # Create new profile
    profile=Profile(first_name=first_name, surname=surname, email=email)
    # Associate user and profile
    user.profile = profile
    # Add user to database
    db.session.add(user)
    # Add profile to database
    db.session.add(profile)
    db.session.commit()
    # Login newly created user
    login_user(user)
    # Flash message
    flash(f"Welcome {username}!")
    # Redirect to posts page
    return redirect(url_for("posts"))





# Login Page
@app.route("/login")
def login():
    # Render Login Page
    return render_template("login.html")

# Login action
@app.route("/login", methods=["POST"])
def login_action():
    # Get username from form
    username = request.form["username"]
    # Get password from form
    password = request.form["password"]
    # Get user by username
    user = User.query.filter_by(username=username).first()
    # If no user exists with the entered username
    if not user:
        # Flash message
        flash(f"No such user '{username}'")
        # Redirect to login page 
        return redirect(url_for("login"))
    # If incorrect password
    if password != user.password:
        # Flash message
        flash(f"Invalid password for the user '{username}'")
        # Redirect to login page 
        return redirect(url_for("login"))

    # Login user
    login_user(user)
    # Flash message
    flash(f"Welcome back, {username}!")
    # Redirect to posts page (index)
    return redirect(url_for("posts"))

# Logout action
@app.route("/logout", methods=["POST"])
@login_required
def logout_action():
    # Log out user
    logout_user()
    # Flash message
    flash("You have been logged out")
    # Redirect to login page
    return redirect(url_for("login"))





# Profile Page
@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    # Get user by user id
    user = User.query.get_or_404(user_id)

    # Get posts by user
    posts = Post.query.filter_by(user_id=user_id).all()

    # For each post check if the logged in user has liked it
    for post in posts:
        post.liked_by_current_user = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first() is not None


    # Render Profile page and pass user, profile and list of languages
    return render_template("profile.html", user=user, profile=user.profile, posts=posts, available_languages=AVAILABLE_LANGUAGES)

# Edit Profile Page
@app.route('/profile/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    # Get user by user id
    user = User.query.get_or_404(user_id)
    # Get users profile
    profile = user.profile

    if request.method == 'POST':
        # Set profile email as email from form
        profile.email = request.form.get('email') or profile.email
        # Set profile bio as bio from form
        profile.bio = request.form.get('bio') or profile.bio
        # Set profiles GitHub username as Github username from form
        profile.github = request.form.get('github') or profile.github
        # Set profiles Linkedin as Linkedin from form
        profile.linkedin = request.form.get('linkedin') or profile.linkedin
        # Get selected languages from form
        selected_languages = request.form.getlist('languages')
        # Create string of selected languagaes and set as profiles languages
        profile.programming_languages = ', '.join(selected_languages)

        # Commit to Database
        db.session.commit()

        # Flash message
        flash('Profile updated successfully!')

        # Redirect to Profile page for that user
        return redirect(url_for('profile', user_id=user_id))
    
    # Render edit profile page and pass user, profile and languages
    return render_template("edit_profile.html", user=user, profile=profile, languages=AVAILABLE_LANGUAGES)





# Users page
@app.route('/users')
@login_required
def users():
    # Get all users - filter where not current user
    users = User.query.filter(User.id != current_user.id).all()
    # Get friends where current user is one of the users in the friend record
    friends = Friend.query.filter((Friend.user1_id == current_user.id) | (Friend.user2_id == current_user.id)).all()
    friend_ids = set()
    friend_list = []
    # Create list of friends and set of friend ids for each friend
    for friend in friends:
        if friend.user1_id == current_user.id:
            friend_ids.add(friend.user2_id)
            friend_list.append(friend.user2)
        else:
            friend_ids.add(friend.user1_id)
            friend_list.append(friend.user1)
    # Get list of users you have sent requests to
    sent_requests = [req.receiver for req in FriendRequest.query.filter_by(sender_id=current_user.id).all()]
    # Get list of users who have sent you a request
    recieved_requests = {req.sender_id: req for req in FriendRequest.query.filter_by(receiver_id=current_user.id).all()}
    
    # Render user page. Pass users, sent requests, recieved requests friend ids and friends
    return render_template('users.html', users=users, sent_requests=sent_requests, recieved_requests=recieved_requests, friend_ids=friend_ids, friend_list=friend_list)

# Send Friend Request
@app.route('/send_request/<int:receiver_id>', methods=['POST'])
@login_required
def send_request(receiver_id):
    # Create new friend request and add to database
    friend_request = FriendRequest(sender_id=current_user.id, receiver_id=receiver_id)
    db.session.add(friend_request)
    db.session.commit()
    # Flash message
    flash("Friend request sent!")
    # Redirect to users page
    return redirect(url_for('users'))

# Accept Friend Request
@app.route('/accept_request/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    # Get friend request by request id
    friend_request = FriendRequest.query.get(request_id)
    # If friend request exists and current user is the reciever
    if friend_request and friend_request.receiver_id == current_user.id:
        # Create new friend and add to database
        friend = Friend(user1_id=friend_request.sender_id, user2_id=current_user.id)
        db.session.add(friend)
        # Delete friend request from database
        db.session.delete(friend_request)
        db.session.commit()
        # Flash message
        flash("Friend request accepted!")
    
    # Get next page to redirect to (either notifications on users page)
    next_page = request.form.get('next')
    if next_page == 'notifications':
        return redirect(url_for('notifications'))
    else:
        return redirect(url_for('users'))

# Decline Friend Request
@app.route('/decline_request/<int:request_id>', methods=['POST'])
def decline_request(request_id):
    # Get friend request by request id
    friend_request = FriendRequest.query.get(request_id)
    # If friend request exists and current user is the reciever
    if friend_request and friend_request.receiver_id == current_user.id:
        # Delete friend request
        db.session.delete(friend_request)
        db.session.commit()
        # Flash message
        flash("Friend request declined!")

    # Get next page to redirect to (either notifications on users page)
    next_page = request.form.get('next')
    if next_page == 'notifications':
        return redirect(url_for('notifications'))
    else:
        return redirect(url_for('users'))





# Notifications Page
@app.route('/notifications')
@login_required
def notifications():
    # Get likes
    likes = Like.query.join(Post).filter(Post.user_id == current_user.id).all()
    # Get Comments
    comments = Comment.query.join(Post).filter(Post.user_id == current_user.id).all()
    # Get Recieved Friend Requests
    received_requests = FriendRequest.query.filter_by(receiver_id=current_user.id).all()
    
    # Render Notifications page
    return render_template('notifications.html', likes=likes, comments=comments, received_requests=received_requests)





# Index Page / Posts
@app.route("/", methods=['GET', 'POST'])
@login_required
def posts():
    # Get the title search
    search_title = request.args.get('title')

    # Get all posts order by date/time descending
    query = Post.query.order_by(Post.timestamp.desc())

    # If there's a search term, filter posts by title
    if search_title:
        query = query.filter(Post.title.ilike(f"%{search_title}%"))

    # Execute the query to get the posts
    posts = query.all()

    # For each post check if the logged in user has liked it
    for post in posts:
        post.liked_by_current_user = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first() is not None

    # Render index(posts) page and pass all posts
    return render_template('index.html', posts=posts, search_title=search_title)

# Create new post
@app.route("/create_post", methods=['POST'])
@login_required
def create_post():
    # Get post title from form
    title = request.form.get('title')
    # Get post content from form
    content = request.form.get('content')

    # Create new post with title and content from form and set user as current user
    new_post = Post(title=title, content=content, user_id=current_user.id)

    # Add post to database
    db.session.add(new_post)
    db.session.commit()

    # Flash message
    flash('New Post Created!')

    # Redirect to posts page
    return redirect(url_for('posts')) 


# Edit Post Page
@app.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    # Get post by post id
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        # Get post title from form
        post.title = request.form.get('title') or post.title
        # Get post content from form
        post.content = request.form.get('content') or post.content

        # Commit to Database
        db.session.commit()

        # Flash message
        flash('Post updated successfully!')

        # Redirect to Profile page for that user
        return redirect(url_for('posts'))
    
    # Render edit post page and pass post id
    return render_template("edit_post.html", post=post)



# Delete post
@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    # Get post by post id
    post = Post.query.get_or_404(post_id)

    # Delete post from database
    db.session.delete(post)
    db.session.commit()

    # Flash message 
    flash('Your Post has been deleted.')
    
    next_page = request.form.get('next')

    if next_page == 'profile':
        next_user = request.form.get('nextuser')
        return redirect(url_for('profile', user_id=int(next_user)))
    else:
        return redirect(url_for('posts'))
    
# Like/unlike post
@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    # Check if user has already liked post
    existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    # If like exists, delete from database 
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        flash('You unliked the post')
    # Else add new like to database
    else:
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()
        flash('You liked the post')
    

    next_page = request.form.get('next')

    if next_page == 'profile':
        next_user = request.form.get('nextuser')
        return redirect(url_for('profile', user_id=int(next_user)))
    else:
        return redirect(url_for('posts'))

# Comment on post
@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment_post(post_id):
    # Get comment from form
    comment = request.form.get('comment')

    # Create new comment
    new_comment = Comment(comment=comment, user_id=current_user.id, post_id=post_id)
    # Add new comment to database
    db.session.add(new_comment)
    db.session.commit()

    # Flash message
    flash('Your comment was added')

    next_page = request.form.get('next')

    if next_page == 'profile':
        next_user = request.form.get('nextuser')
        return redirect(url_for('profile', user_id=int(next_user)))
    else:
        return redirect(url_for('posts'))    

# Delete Comment
@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    # Get comment by comment id
    comment = Comment.query.get_or_404(comment_id)

    # Delete comment from database
    db.session.delete(comment)
    db.session.commit()

    # Flash message
    flash('Your comment has been deleted.')
    
    next_page = request.form.get('next')

    if next_page == 'profile':
        next_user = request.form.get('nextuser')
        return redirect(url_for('profile', user_id=int(next_user)))
    else:
        return redirect(url_for('posts'))