from flaskblog import db
from flaskblog.models import User, Post, Stock
from datetime import timedelta, date, datetime
from sqlalchemy import desc
import pandas as pd


# posts = Post.query.order_by(desc(Post.date_posted))
# posts = posts.filter(Post.date_posted > (datetime.now()-timedelta(hours=5))).all()

# posts = Post.query.paginate(per_page=5, page=3)
# for post in posts.items:
# print(post)

def create_table():
    from sqlalchemy import create_engine
    from sqlalchemy import MetaData
    from sqlalchemy import Table
    from sqlalchemy import Column
    from sqlalchemy import Integer, String


    db_uri = 'sqlite:///flaskblog/site.db'
    engine = create_engine(db_uri)

    meta = MetaData(engine)

    t2 = Table('stock', meta,
    Column('id', Integer, primary_key=True),
    Column('material_type', String(50)),
    Column('teeth', db.Float),
    Column('quantity', Integer),
    Column('units', Integer),
    Column('diameter_size', Integer),
    Column('dp', Integer),
    Column('pitch', Integer),
    Column('module_value', String),
    Column('storage_location', String),
    Column('unique_id', String),
    Column('date_posted', db.DateTime, nullable=False, default=datetime.now)
    )

    t2.create()


def fill_stock():
    Stock.query.delete()

    # To test if the user is being added or not
    df = pd.read_csv('csvs/stock.csv')
    # print(df.head(10).to_string())
    df.drop(df.columns[-1], inplace=True, axis=1)
    for row in df.values.tolist():
        entry = Stock(material_type=row[0],
                        teeth=row[1],
                        quantity=row[2],
                        units=row[3],
                        diameter_size=row[4],
                        dp=row[5],
                        pitch=row[6],
                        module_value=row[7],
                        storage_location=row[8],
                        unique_id=row[-1])

        db.session.add(entry)
        db.session.commit()

fill_stock()
