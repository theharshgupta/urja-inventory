from flaskblog import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    # below we create a default arg where we mention the default profile picture
    image_file = db.Column(db.String(20), nullable=False, default='56c6632a3ab0abec.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    # These are also called the magic methods or dunder methods
    def __repr__(self):
        return f"User(' {self.name}', '{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.String(50), nullable=False)
    numbers_issued = db.Column(db.Integer)
    unit = db.Column(db.String(10))
    person = db.Column(db.String(20))
    location = db.Column(db.String(50))
    type_issued = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __repr__(self):
        return f"Inventory('{self.material_id}', '{self.date_posted}')"



class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_type = db.Column(db.String(50))
    teeth = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    units = db.Column(db.Integer)
    diameter_size = db.Column(db.Integer)
    dp = db.Column(db.Integer)
    pitch = db.Column(db.Integer)
    module_value = db.Column(db.String(20))
    storage_location = db.Column(db.String(100))
    unique_id = db.Column(db.String(100))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
