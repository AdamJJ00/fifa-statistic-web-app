from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    data = request.form
    print(data)
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return render_template("login.html")

@auth.route('/stats')
def stats():
    return render_template("stats.html")

@auth.route('/matches')
def matches():
    return render_template("matches.html")

@auth.route('/stadiums')
def stadiums():
    return render_template("stadiums.html")

@auth.route('/teams')
def teams():
    return render_template("teams.html")

@auth.route('/players')
def players():
    return render_template("players.html")


@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 5:
            flash('Your email is too short. It must contain least 5 characters.', category='error')
        elif len(username) < 2:
            flash('Your username is too short. It must contain least 2 characters.', category='error')
        elif password1 != password2:
            flash('Your passwords don\'t match.', category='error')
        elif len(password1) < 8:
            flash('Your password is too short. It must contain least 8 characters.', category='error')
        else:
            flash('Congratulations! Account created!', category='success')

    return render_template("sign_up.html")
