from tukevoting import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader 
def load_user(user_id):
    return Voter.query.get(int(user_id))


class Voter(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Voter('{self.first_name}', '{self.email}','{self.voter_id}' )"

class Admin(db.Model, UserMixin):
    
    admin_id = db.Column(db.String(20),unique=True, nullable=False, primary_key=True)
    admin_name = db.Column(db.String(20), nullable=False)
    admin_password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Admin('{self.admin_id}', '{self.admin_name}')"
    def get_id(self):
           return (self.admin_id)

class Candidate(db.Model):
    candidate_id = db.Column(db.String(20),unique=True, nullable=False, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    position = db.Column(db.String(40), nullable=False)
    image_file = db.Column(db.String(60), nullable=True, default='default.jpg')
    school = db.Column(db.String(6), nullable=False)

    def __repr__(self):
        return f"Candidate('{self.first_name}', '{self.position}','{self.candidate_id}' )"


