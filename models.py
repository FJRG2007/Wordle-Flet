from sqlalchemy import Column, Integer, Boolean, String
import db

class User(db.Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    wins = Column(Integer)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
        self.wins = 0