from datetime import datetime
from email.mime import image
import secrets
import os
import json
from PIL import Image
from flask import render_template,url_for, flash, redirect, request, abort, make_response, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from tukevoting import app, db, bcrypt
from tukevoting.models import Voter, CandidateModel, VoterFaces, Votes
from tukevoting.forms import AdminForm, RegistrationForm, LoginForm, CandidateForm, VoteForm, UpdateAccountForm
from flask_login import login_user, login_required, current_user, logout_user
from tukevoting.face_rec  import run_face_rec
from tukevoting.__init__ import photos

#Define the home page route url 
@app.route("/")
@app.route("/home")
#A flask-login function that restricts access to a page if the voter has not logged in
@login_required
def home():
    
    return render_template("home.html", title='Home')

#Defines the register voter url 
@app.route("/register", methods=['GET', 'POST'])
def register():
    #redirects user to home route if theyve logged in already
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    #Defines the form to be rendered on this page
    form = RegistrationForm()
    if form.validate_on_submit():
        #hashes the passwords to ensure even one viewing the database cannot see the actual password value
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Voter(voter_id=form.voter_id.data,roll_num=form.roll_num.data, first_name=form.first_name.data, last_name=form.last_name.data, school=form.school.data, email=form.email.data, password=hashed_password)
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
            reg_candidate = CandidateModel(candidate_id=form.candidate_id.data,roll_num=form.roll_num.data, first_name=form.first_name.data, last_name=form.last_name.data, school=form.school.data, description=form.description.data, position=form.position.data)
            db.session.add(reg_candidate)
            db.session.commit()
            flash('Candidate Registered Successfully','success')
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        return render_template('admin.html', form=form, image_file=image_file, legend='Register Candidate')
    else:
        flash("You must be the Admin to access this page", 'danger')
        return render_template('home.html', title='Home')




@app.route("/vote/", methods=['GET', 'POST'])
@login_required
def vote():

    
    v = current_user.roll_num
    x = VoterFaces.query.filter(VoterFaces.roll_num == v).first()
    if x:
        flash("Face Verified", "info") 
        form = VoteForm()
        flash('We suggest you visit the Candidate Information page, to learn about your aspirants before you proceed to vote. Thankyou.', 'info')
        if current_user.voted == False:
            flash('You Have Not Voted','danger')
            if form.is_submitted():
                my_vote = Votes(id=current_user.id, roll_num=current_user.roll_num, voter_id=current_user.voter_id, post_1=form.delegate.data, post_2=form.school_rep.data)
                has_voted = current_user.voted=True
                db.session.add(my_vote, has_voted)
                db.session.commit()
                flash('Vote Cast Successfully!', 'success')
                return render_template("vote.html", form=form)
        else:
            flash('You Have Already Voted','success')
            return render_template('vote.html')
        return render_template('vote.html',title='Vote', form=form)
    else:
        flash("Face Not Verified", "danger")
        return render_template('home.html')
        
@app.route("/counter", methods=['GET','POST'])
@login_required
def counter():
    delegate = CandidateModel.query.filter_by(position="Delegate").all()

    school_rep = CandidateModel.query.filter_by(position="School Rep").all()
    labels=[]
    school_label=[]
    data=[]
    labels1=[]
    data1=[]    

    for candidate in delegate:
        name = candidate.first_name+" "+candidate.last_name
        school = candidate.school
        labels.append(name)
        school_label.append(school)
        vote = Votes.query.filter(Votes.post_1==name).count()
        data.append(vote)
    

    for candidate in school_rep:
        name = candidate.first_name+" "+candidate.last_name
        labels1.append(name)
        vote = Votes.query.filter(Votes.post_2==name).count()
        data1.append(vote)    
    

    output = {"data": data,
            "labels": labels,
            "data1": data1,
            "labels1": labels1}
    response = app.response_class(
        response=json.dumps(output),
        status=200,
        mimetype='application/json'
    )

    return render_template('counter.html', title='Results',labels=labels,data=data,labels1=labels1,data1=data1)


@app.route("/counter/live", methods=['GET','POST'])
@login_required
def counter_live():
    delegate = CandidateModel.query.filter_by(position="Delegate").all()

    school_rep = CandidateModel.query.filter_by(position="School Rep").all()
    labels=[]
    school_label=[]
    data=[]
    labels1=[]
    data1=[]    

    for candidate in delegate:
        name = candidate.first_name+" "+candidate.last_name
        school = candidate.school
        labels.append(name)
        school_label.append(school)
        vote = Votes.query.filter(Votes.post_1==name).count()
        data.append(vote)
    

    for candidate in school_rep:
        name = candidate.first_name+" "+candidate.last_name
        labels1.append(name)
        vote = Votes.query.filter(Votes.post_2==name).count()
        data1.append(vote)    
    

    output = {"data": data,
            "labels": labels,
            "data1": data1,
            "labels1": labels1}
    response = app.response_class(
        response=json.dumps(output),
        status=200,
        mimetype='application/json'
    )

    return response


@app.route("/info", methods=['GET', 'POST'])
@login_required
def info():
    display_candidate = CandidateModel.query.all()
    return render_template("info.html", title='Candidate Info', candidate=display_candidate)




@app.route("/logout")
def logout():
    logout_user()
    flash('Log Out Successful!', 'success')
    return redirect('login')

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    #get image file extension inorder to later save it with the same extension
    _, f_ext = os.path.splitext(form_picture.filename)
    #combine random hex with extension to create new filename for saving
    picture_fn = random_hex + f_ext
    #path to save uploaded picture, joined with rootpath folder location, joined with filename
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/images/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'],filename)



@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.is_submitted():
        filename = photos.save(form.picture.data)
        file_url = url_for('get_file', filename=filename)
        flash(file_url)
        current_user.image_file = filename
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.school = form.school.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account  has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        file_url = None
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.school.data = current_user.school
        form.email.data = current_user.email
    return render_template("account.html", title='Account', form=form, file_url=file_url)

    #image_file = url_for('static', filename='profile_pics/' + current_user.image_file) 
@app.route('/info/<string:first_name>')
@login_required
def candidate(first_name):
    edit_candidate = CandidateModel.query.filter_by(first_name=first_name).first()
    return render_template('candidate.html', title='Edit Candidate Information', candidate=edit_candidate)



@app.route('/info/<string:first_name>/update', methods=['GET', 'POST'])
@login_required
def update_candidate(first_name):
    candidate = CandidateModel.query.filter_by(first_name=first_name).first()
    if current_user.first_name != 'Admin' :
        abort(403)
    form = CandidateForm()
    if form.validate_on_submit():
        candidate.candidate_id = form.candidate_id.data
        candidate.first_name = form.first_name.data  
        candidate.last_name = form.last_name.data   
        candidate.school = form.school.data      
        candidate.position = form.position.data    
        candidate.description = form.description.data 
        if form.photo.data:
            picture_file = save_picture(form.photo.data)
            candidate.image_file = picture_file
        db.session.commit()
        flash('Candidate information updated successfully', 'success')
        return render_template('candidate.html', candidate=candidate)
    elif request.method == 'GET':
        form.candidate_id.data = candidate.candidate_id
        form.first_name.data   = candidate.first_name
        form.last_name.data    = candidate.last_name
        form.school.data       = candidate.school
        form.position.data     = candidate.position
        form.description.data  = candidate.description
    image_file = url_for('static', filename='profile_pics/' + candidate.image_file) 
    return render_template('admin.html', title = 'Update Candidate Information', form=form, legend='Update Candidate Information', image_file=image_file)

@app.route('/info/<string:first_name>/delete', methods=['POST'])
@login_required
def delete_candidate(first_name):
    candidate = CandidateModel.query.filter_by(first_name=first_name).first()
    if current_user.first_name != 'Admin' :
        abort(403)
    db.session.delete(candidate)
    db.session.commit()
    flash('Candidate Successfully Deleted', 'success')
    return redirect(url_for('home'))

@app.route("/faces")
@login_required
def faces():
    v = current_user.roll_num
    x = VoterFaces.query.filter(VoterFaces.roll_num == v).first()
    if x: 
        flash('Identity Already Verified','info')
        return redirect(url_for('vote'))
    else:
        run_face_rec()
        if x:
            flash('Identity Verified', 'success')
        return redirect(url_for('vote'))
    
@app.route("/transactions")
@login_required
def transactions():
    show_dates = Votes.query.all()
    return render_template("transactions.html",title='Votes Ledger', date=show_dates)