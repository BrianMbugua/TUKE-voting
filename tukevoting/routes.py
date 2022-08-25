import secrets
import os
from PIL import Image
from flask import render_template,url_for, flash, redirect, request
from tukevoting import app, db, bcrypt
from tukevoting.models import Voter, Admin, Candidate
from tukevoting.forms import AdminForm, RegistrationForm, LoginForm, CandidateForm, SchoolForm, UpdateAccountForm
from flask_login import login_user, login_required, current_user, logout_user



@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title='Home')

@app.route("/about")
def about():
    return render_template("about.html", title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Voter(voter_id=form.voter_id.data, first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your Account has been created! You can now login','success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.is_submitted():
        user = Voter.query.filter_by(voter_id=form.voter_id.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if current_user.voter_id == 'admin001':
                flash('Logged in as Administrator', 'success')
                #return render_template('home.html')
                return redirect(url_for('admin'))
            else:
                flash('Log in Successful!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Log in unsuccessful. Check Voter ID or password', 'danger')
            return render_template('login.html', title='Login', form=form)
    return render_template('login.html', title='Login', form=form)
     
  

@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    form = CandidateForm()
    admin_id = current_user.voter_id
    if admin_id == 'admin001':
        if form.is_submitted():
            if form.photo.data:
                picture_file = save_picture(form.photo.data)
                current_user.image_file = picture_file
            candidate = Candidate(candidate_id=form.candidate_id.data, first_name=form.first_name.data, last_name=form.last_name.data, school=form.school.data, description=form.description.data, position=form.position.data)
            db.session.add(candidate)
            db.session.commit()
            flash('Candidate Registered Successfully','success')
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        return render_template('admin.html', form=form, imae_fiel=image_file)
    else:
        flash("You must be the Admin to access this page", 'danger')
        return render_template('home.html', title='Dashboard')




@app.route("/vote")
@login_required
def vote():
    form = SchoolForm()
    form.school.choices = [(Candidate.candidate_id, Candidate.position) for school in School.query.filter_by(school='SCIT').all()]
    return render_template("vote.html", title='Vote')

@app.route("/info", methods=['GET', 'POST'])
@login_required
def info():
    candidate = Candidate.query.all()
    return render_template("info.html", title='Info', candidate=candidate)

@app.route("/counter")
@login_required
def counter():
    return render_template("counter.html", title='Counter')

@app.route("/logout")
def logout():
    logout_user()
    flash('Log Out Successful!', 'success')
    return redirect('login')

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file) 
    return render_template("account.html", title='Account', image_file=image_file, form=form)