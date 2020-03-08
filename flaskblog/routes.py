from flask import render_template, url_for, flash, abort, redirect, request
from flaskblog.models import User, Post, Stock
import pygal
from datetime import date, datetime
from datetime import timedelta
import secrets
from PIL import Image
from pyzbar import pyzbar
import os
from sqlalchemy import desc
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, \
    PostForm, SortDays, Search, UploadScan, AddStock
from flaskblog import app, db, bcrypt
import flask_sqlalchemy
from werkzeug.utils import secure_filename
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    is_empty = False
    page = request.args.get('page', 1, type=int)
    num_posts = min(request.args.get('limit', 10), 50)
    query = request.args.get('q', '')

    per_page = 20
    form = SortDays()
    search_form = Search()

    posts = Post.query.order_by(desc(Post.date_posted))

    if form.sort_days.data == '1':
        posts = Post.query.order_by(desc(Post.date_posted)).filter(
            Post.date_posted > (datetime.now() - timedelta(days=1)))
    elif form.sort_days.data == '7':
        posts = Post.query.order_by(desc(Post.date_posted)).filter(
            Post.date_posted > (datetime.now() - timedelta(days=7)))
    elif form.sort_days.data == '30':
        posts = Post.query.order_by(desc(Post.date_posted)).filter(
            Post.date_posted > (datetime.now() - timedelta(days=30)))
    elif form.sort_days.data == '90':
        posts = Post.query.order_by(desc(Post.date_posted)).filter(
            Post.date_posted > (datetime.now() - timedelta(days=90)))
    elif form.sort_days.data == '360':
        posts = Post.query.order_by(desc(Post.date_posted)).filter(
            Post.date_posted > (datetime.now() - timedelta(days=360)))
    elif form.sort_days.data == 'All':
        posts = Post.query.order_by(desc(Post.date_posted))

    # This is to check if the there are no posts, then we can put a message
    # on the screen saying that there are no posts for the available dates
    if len(posts.all()) == 0:
        is_empty = True

    barcode_data = None
    form_barcode = UploadScan()
    if form_barcode.validate_on_submit():
        if form_barcode.picture.data:
            barcode_path = save_barcode(form_picture=form_barcode.picture.data)
            barcode_data = extract_barcode(barcode_path)
            print(barcode_data)
            if len(barcode_data) == 0:
                barcode_data = None

    return render_template('home.html', form=form, search_form=search_form,
                           posts=posts.paginate(page=page, per_page=per_page),
                           is_empty=is_empty, form_barcode=form_barcode,
                           barcode_data=barcode_data)


@app.route("/about")
def about():
    text_about = """“Capital Urjatech Ltd, ISO 9001:2008 certified company is the leading electric cable manufacture of XLPE / PVC Insulated Aluminum Cables including Low Tension Power and Aerial Bunched Cable in India and subcontinent. "
To accelerate the mission of electricity for all, we are determined to provide transmission cable required to power and empower next generation of India. As fast growing power equipment manufacturer, our mission is to help connect everyone with cheap electricity supply through an efficient and well maintained smart transmission grid network while maintaining low AT&C losses. With our moto of 'Delivering Best’, we work closely with all State Electricity Boards as well as Private electrification turnkey projects contractors to supply various sizes of transmission and service cable under various state and central government initiatives schemes"""
    return render_template('about.html', title='About', text_about=text_about)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(name=form.name.data, username=form.username.data,
                    email=form.email.data, password=hashed_password)
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
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):
            login_user(user=user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(
                url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password',
                  'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics',
                                picture_filename)
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
    image_file = url_for('static',
                         filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(material_id=form.material_id.data,
                    numbers_issued=form.numbers_issued.data,
                    unit=form.unit.data,
                    person=form.person.data,
                    location=form.location.data,
                    type_issued=form.type_issued.data,
                    author=current_user)
        unique_id = form.material_id.data
        db.session.add(post)
        item = Stock.query.filter_by(unique_id=unique_id).first()
        print("Quantity issued:", form.numbers_issued.data)
        print(f"Quantity for the selected item {unique_id} BEFORE update:",
              item.quantity)
        if item.quantity - form.numbers_issued.data < 0:
            flash("You have issued more than in Current Stock!", "danger")
        item.quantity = item.quantity - form.numbers_issued.data
        item.date_posted = datetime.now()
        print(f"Quantity for the selected item {unique_id} AFTER update:",
              item.quantity)
        db.session.commit()

        flash('Item has been issued!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='Issue', form=form,
                           legend='New Issue')


@app.route("/post/<int:post_id>")
def post(post_id):
    # get_or_404 is a method that gives a 404 if the post does not exist
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.material_id, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    # get_or_404 is a method that gives a 404 if the post does not exist
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.material_id = form.material_id.data
        post.type_issued = form.type_issued.data
        post.numbers_issued = form.numbers_issued.data
        post.unit = form.unit.data
        post.person = form.person.data
        post.location = form.location.data

        db.session.commit()
        flash("Your post has been updated", 'success')
        return redirect(url_for('post', post_id=post_id))
    elif request.method == 'GET':
        form.material_id.data = post.material_id
        form.type_issued.data = post.type_issued
        form.numbers_issued.data = post.numbers_issued
        form.unit.data = post.unit
        form.person.data = post.person
        form.location.data = post.location

    return render_template('create_post.html', title='Update Entry', form=form,
                           legend='Update Entry')


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


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    pie_chart = pygal.Pie()
    pie_chart.title = 'Browser usage in February 2012 (in %)'
    pie_chart.add('IE', 19.5)
    pie_chart.add('Firefox', 36.6)
    pie_chart.add('Chrome', 36.3)
    pie_chart.add('Safari', 4.5)
    pie_chart.add('Opera', 2.3)
    graph_data = pie_chart.render_data_uri()
    return render_template('graphing.html', graph_data=graph_data)


@app.route("/stock", methods=['GET', 'POST'])
@login_required
def stock():
    # page = request.args.get('page', 1, type=int)
    # per_page=100
    # return render_template('stock.html',stock_data=Stock.query.paginate(page=page, per_page=per_page))

    return render_template('stock_datatable.html', stock_data=Stock.query.all())


@app.route("/stock_add", methods=['GET', 'POST'])
@login_required
def stock_add():
    form = AddStock()
    if form.validate_on_submit():
        entry = Stock(material_type=form.material.data,
                      teeth=form.teeth.data,
                      quantity=form.quantity.data,
                      units=form.unit.data,
                      diameter_size=form.diameter_size.data,
                      dp=form.dp.data,
                      pitch=form.pitch.data,
                      module_value=form.module_value.data,
                      storage_location=form.location.data,
                      unique_id=form.unique_id.data)

        db.session.add(entry)
        db.session.commit()
        flash('Your stock has been added!', 'success')
        return redirect(url_for('stock'))
    return render_template('stock_add.html', title='Issue', form=form,
                           legend='New Issue')


def save_barcode(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_ext
    picture_path = os.path.join(app.root_path, 'static/barcodes',
                                picture_filename)
    # output_size = (1000, 1000)
    i = Image.open(form_picture)
    # i.thumbnail(output_size)
    i.save(picture_path)

    return picture_path

# def extract_barcode(barcode_path):
#
#     # image = cv2.imread(args["image"])
#
#     print ('the path to the barcode: ', barcode_path)
#     image = cv2.imread(barcode_path)
#     barcodes = pyzbar.decode(image)
#     list_barcode_data = []
#
#     # loop over the detected barcodes
#
#     for (itr, barcode) in enumerate(barcodes):
#
#         # extract the bounding box location of the barcode and draw the
#         # bounding box surrounding the barcode on the image
#
#         (x, y, w, h) = barcode.rect
#         cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
#
#         # the barcode data is a bytes object so if we want to draw it on
#         # our output image we need to convert it to a string first
#
#         barcodeData = barcode.data.decode('utf-8')
#         barcodeType = barcode.type
#
#         # draw the barcode data and barcode type on the image
#
#         text = '{} ({})'.format(barcodeData, barcodeType)
#         # cv2.putText(
#         #     image,
#         #     text,
#         #     (x, y - 10),
#         #     cv2.FONT_HERSHEY_SIMPLEX,
#         #     0.5,
#         #     (0, 0, 255),
#         #     2,
#         #     )
#
#         # print the barcode type and data to the terminal
#
#         # print(f"[INFO] Found {barcodeType} barcode: {barcodeData}")
#
#         barcode_data = {'id': itr+1, 'type': barcodeType,
#                         'data': barcodeData, "timestamp": str(datetime.now())}
#
#         list_barcode_data.append(barcode_data)
#     try:
#         os.remove(barcode_path)
#     except:
#         print("Trying to delete Barcode image that does not exist. ")
#
#     return list_barcode_data


# @app.route("stock", methods=['GET', 'POST'])
# @login_required
# def stock():
