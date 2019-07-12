from flask import render_template, request, redirect, url_for, abort, flash
from . import auth
from werkzeug.urls import url_parse
from .forms import RegistrationForm, LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from ..models import *
from app import db
from ..email import mail_message

@auth.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                  fullname=form.fullname.data,
                password=form.password.data,
                email=form.email.data)
        db.session.add(user)
        db.session.commit() 
        mail_message("Welcome to Book Grao","email/welcome_user",user.email,user=user)       
        return redirect(url_for('auth.login'))

    return render_template('register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page=request.args.get('next')
        if not next_page or url_parse(next_page).netloc!='':
            next_page=url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
