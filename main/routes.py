from flask import render_template, url_for, request, flash, redirect, abort, render_template_string
from main.form import *
from main.models import User, Post
from main import app, bcrypt, db
from flask_login import login_user, current_user, logout_user, login_required
import os
import secrets
from PIL import Image
from datetime import datetime


from flask import current_app
song_history_global = []
@app.context_processor
def inject_song_history():
    global song_history_global
    song_history = None
    if current_user.is_authenticated:
        song_history = song_history_global
    return dict(song_history=song_history)



@app.route('/')
@app.route('/home')
def home():
    with app.app_context():
        posts=Post.query.all()
        return render_template('home.html', posts = posts, ctx = app.app_context())


@app.route('/about')
def about():
    return render_template('about.html', title = 'About_Page')

@app.route('/register', methods = ['POST', 'GET'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == "POST":
        di = request.form
        username = di['username']
        email = di['email']
        password = di['pass']
        confirm_password = di['confirmpass']

        if validated(username, email,password,confirm_password):
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(username=username, email=email, password=hashed_pw)
            with app.app_context():
                db.session.add(user)
                db.session.commit()
            flash(f'Account Created For {username}! You are now able to login.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login',methods = ['POST', 'GET'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == "POST":
        di = request.form
        email = di['email']
        password = di['pass']

        user = None
        with app.app_context():
            # db.create_all()
            user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))

            return redirect(url_for('home'))
        else:
            flash(f"Incorrect Email or Password!", 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex+f_ext
    picture_path = os.path.join(app.root_path,'static','profile_pics',picture_fn)
    form_picture.save(picture_path)
    return picture_fn




@app.route('/account',methods = ['POST', 'GET'])
@login_required
def account():
    if request.method == 'POST':
        di = request.form
        username = di['username']
        email = di['email']
        file = request.files['file']
        print("********", file)
        _, f_ext = os.path.splitext(file.filename)
        print("*******", f_ext)
        if f_ext not in ['.png', '.jpg']:
            flash(f'Unsupported File ext.', 'danger')
        else:
            picture_file = save_picture(file)

            # to delete current image
            if current_user.image_file != 'default.jpg':
                old_picture_path = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
                if os.path.exists(old_picture_path):
                    os.remove(old_picture_path)

            with app.app_context():
                current_user.image_file = picture_file
                db.session.commit()
                flash(f'Profile Photo Updated Successfully', 'success')


        if email != current_user.email:
            if validate_email(email):
                with app.app_context():
                    current_user.email = email
                    db.session.commit()
                flash(f"Email Updated Successfully", 'success')

        if username != current_user.username:
            if validate_username(username):
                with app.app_context():
                    current_user.username=username
                    db.session.commit()
                flash(f"Username Updated Successfully", 'success')

        return redirect(url_for('account'))

    image_file = url_for('static', filename='profile_pics/'+current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file)


@app.route('/post/new', methods=['POST', 'GET'])
@login_required
def new_post():
    if request.method == "POST":
        di = request.form
        title = di['title']
        content = di['content']
            
        if validate_post(title, content):
            post = Post(title=title, content=content, author=current_user)
            with app.app_context():
                db.session.add(post)
                db.session.commit()
            flash(f'Your Post Has Been Created!', 'success')            
            return redirect(url_for('home'))
        
    return render_template('create_post.html',title="New Post")


@app.route('/post/<int:post_id>', methods=['POST', 'GET'])
@login_required
def post(post_id):
    with app.app_context():
        if request.method == 'POST':
            post = Post.query.get_or_404(post_id)
            if post.author != current_user:
                abort(403)
            else:
                di = request.form
                title = di['title']
                content = di['content']
                if validate_post(title, content):
                    post.title=title
                    post.content=content
                    db.session.commit()
                    flash(f'Post Updated Successfully', 'success')
                return redirect(url_for('post', post_id=post.id))
        
        post = Post.query.get_or_404(post_id)
        return render_template('post.html', title=post.title, post=post)
    

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    with app.app_context():
        post = Post.query.get_or_404(post_id)
        if post.author != current_user:
            abort(403)
        db.session.delete(post)
        db.session.commit()
        flash(f'Post Deleted Successfully', 'success')
        return redirect(url_for('home'))



### for humming bird

from . import jupyter_script

def save_audio(form_audio):
    # _, f_ext = os.path.splitext(form_audio.filename)
    audio_fn = form_audio.filename
    audio_path = os.path.join(app.root_path,'static','user_input_audio',audio_fn)

    form_audio.save(audio_path)
    return audio_path
    
@app.route('/backend', methods=['POST', 'GET'])
def humming_bird_main():

    if request.method == 'POST':
        # di = request.form
        file = request.files['file']
        # print("*************", file.filename, type(file.filename)) # str

        _, f_ext = os.path.splitext(file.filename)
        # print("*******", f_ext)
        if f_ext not in ['.mp3', '.wav']:
                return "unsupported file-type"
        else:
            # save_audio(file)
            song_name, four_songs = jupyter_script.perform_main(save_audio(file))
            # song_name = song_name[0:-4]
            print("you are humming for " + song_name)
    
            if current_user.is_authenticated:
                if song_name not in song_history_global:
                    song_history_global.append(song_name)
            return render_template('output.html', song_name=song_name, similar_songs = four_songs)

    return f"<h1> form not working as intended </h1>"