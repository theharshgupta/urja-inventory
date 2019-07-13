from flask import render_template, url_for, flash, abort, redirect, request
from flaskblog.models import User, Post
import secrets
from PIL import Image
import os
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    # text_about_loc = url_for('static', filename='text/about.txt')
    # print(text_about_loc)
    # with open(text_about_loc, 'r') as f:
    #     text_about = f.read()
    text_about = """
    If Led Zeppelin were the band most responsible for hard rock's vertical expansion in the '70s, hitting previously unforeseeable heights for the genre, Pink Floyd were the band that expanded it the most horizontally.
Obviously, they stretched out the length -- double albums, side-long jams, songs that had more movements and ideas than entire LPs by other bands. But they also broadened the music's width, with one of the most far-reaching musical palettes of any band approaching their magnitude. Starting with the Syd Barrett-stewarded kaleidoscopic psychedelia Piper at the Gates of Dawn in 1967 -- a half-century old this Saturday (Aug. 5) -- the band showed a truly staggering artistic flexibility and open-eared inventiveness, for which they remain oddly underrated in an era that increasingly views them as stodgy, cerebral rock puritans.

Yes, they set the standard for college-dorm stoner rock with the prismatic prog of The Dark Side of the Moon, but in between the LP's space-rock zone-outs are a pulse-racing proto-EDM instrumental, a heart-stopping soul vocal exorcism and a couple ripping sax solos. Yes, Wish You Were Here is overwhelmed by a combined 26 minutes and nine movements of jazzy art-funking (and no shortage of fretting about The Machine), but it's also centered around the profound humanity of one of the great tear-jerking ballads in rock history. Yes, the '77 punk movement largely followed in response to the overblown pomposity of their ilk, but play Never Mind the Bollocks, Here's the Sex Pistols and Animals back to back and see which one sounds more like a bilious screed from a bunch of pissed-off Britons who don't give a f--k what their fans want to hear. And yes, The Wall was a monstrous double-LP statement of egomania from which there was no returning, but the set's rock operatics couldn't obscure the most seamless integration of disco's thump that any major rock band had yet achieved -- resulting in a Hot 100 No. 1 rock fans didn't even bother to cry "sell out!" over.


    """
    return render_template('about.html', title='About', text_about=text_about)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created, you can now Login!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user=user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))

        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_filename


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form_picture=form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='Update Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    # get_or_404 is a method that gives a 404 if the post does not exist
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    # get_or_404 is a method that gives a 404 if the post does not exist
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated", 'success')
        return redirect(url_for('post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted", 'success')
    return redirect(url_for('home'))
