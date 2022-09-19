from enum import unique
from tukevoting import db, login_manager
from flask_login import UserMixin
import datetime

#Reloads the voter in the session 
@login_manager.user_loader 
def load_user(user_id):
    return Voter.query.get(int(user_id))



#Create Voter table
class Voter(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    roll_num = db.Column(db.Integer, nullable=False, unique=True)
    voter_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    school = db.Column(db.String(6), nullable=False)
    voted = db.Column(db.Boolean, default=False, nullable=False)
    #Define how the tables data should be represented during querying
    def __repr__(self):
        return f"Voter('{self.first_name}', '{self.email}','{self.voter_id}','{self.voted}' )"


#Create Candidate table
class CandidateModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.String(20),unique=True, nullable=False)
    roll_num = db.Column(db.Integer, nullable=False, unique=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    position = db.Column(db.String(40), nullable=False)
    image_file = db.Column(db.String(60), nullable=True, default='default.jpg')
    school = db.Column(db.String(6), nullable=False)

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"

class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    voter_id = db.Column(db.String(20), db.ForeignKey('voter.voter_id'), nullable=False)
    roll_num = db.Column(db.Integer, nullable=False, unique=True)
    post_1 = db.Column(db.String(20), nullable=False )
    post_2 = db.Column(db.String(20), nullable=False)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"{self.created}"

class VoterFaces(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_num = db.Column(db.Integer, db.ForeignKey('voter.voter_id'), nullable=False, unique=True)
    allow_vote = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"{self.roll_num}"

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(20),unique=True, nullable=False)
    admin_name = db.Column(db.String(20), nullable=False)
    admin_password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Admin('{self.admin_id}', '{self.admin_name}')"
    def get_id(self):
           return (self.admin_id)