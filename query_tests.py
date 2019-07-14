from flaskblog import db
from flaskblog.models import User, Post
from datetime import timedelta, date, datetime
from sqlalchemy import desc

posts = Post.query.order_by(desc(Post.date_posted))
posts = posts.filter(Post.date_posted > (datetime.now()-timedelta(hours=5))).all()

print(posts)
