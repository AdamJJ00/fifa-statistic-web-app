import pandas as pd
import plotly.express as px
import plotly
import json
import sqlite3
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

auth = Blueprint("auth", __name__)


def require_login(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "email" and "username" in session:
            return f(*args, **kwargs)
        else:
            flash("You need to be logged in to see this page.", category="error")
            return redirect(url_for("auth.login"))

    return wrap


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Connect to the database
        conn = sqlite3.connect("db/fifa_app.db")
        c = conn.cursor()

        # Get the form data
        email = request.form["email"]
        password = request.form["password"]

        # Query the user from the database
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()

        # Close the cursor and the connection
        c.close()
        conn.close()

        # If the user exists and the password is correct
        if user and check_password_hash(user[3], password):
            # Log the user in
            session["email"] = email
            session["username"] = user[1]

            flash("Successfuly logged in!", category="success")
            return redirect("/")
        else:
            # Return an error message
            flash("The login details provided are incorrect.", category="error")
            return render_template("login.html")
    else:
        return render_template("login.html")


@auth.route("/logout")
def logout():
    if "email" in session:
        # Remove the user's details from the session
        session.pop("email", None)
        session.pop("username", None)

        flash("You have been logged out successfully", category="info")

    return redirect("/")


@auth.route("/stats")
@require_login
def stats():
    return render_template("stats.html")


@auth.route("/matches")
@require_login
def matches():
    return render_template("matches.html")


@auth.route("/stadiums")
@require_login
def stadiums():
    # Connect to the SQLite database
    conn = sqlite3.connect("db/fifa_app.db")
    c = conn.cursor()

    # Retrieve the data from the table
    c.execute("SELECT * FROM Stadiums")
    stadiums = c.fetchall()

    # Convert the data to a dataframe
    stadiums_df = pd.DataFrame(
        stadiums,
        columns=[
            "Stadium_ID",
            "Stadium_name",
            "City",
            "Capacity",
            "Stadium_description",
        ],
    )

    stadiums_df.sort_values(by="Capacity", ascending=True, inplace=True)

    # Close the cursor and connection
    c.close()
    conn.close()

    # Generate the plotly figure
    fig = px.bar(
        stadiums_df,
        x="Capacity",
        y="Stadium_name",
        barmode="group",
        template="plotly_white",
        title="Capacity of stadiums (Qatar)",
        text=stadiums_df.City,
    )
    fig.update_xaxes(title_text="Capacity")
    fig.update_yaxes(title_text="Stadium name")
    fig.update_traces(
        marker_color=[
            "#636EFA",
            "#EF553B",
            "#00CC96",
            "#AB63FA",
            "#FFA15A",
            "#19D3F3",
            "#FF6692",
            "#B6E880",
        ],
        marker_line_color="rgb(0,0,0)",
        marker_line_width=1.5,
        opacity=0.95,
    )

    # convert the figure to an HTML format
    html_string = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("stadiums.html", stadiums=stadiums, html_string=html_string)


@auth.route("/teams")
@require_login
def teams():
    return render_template("teams.html")


@auth.route("/players")
@require_login
def players():
    return render_template("players.html")


@auth.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        password_conf = request.form.get("password_conf")

        if len(email) < 5:
            flash(
                "Your email is too short. It must contain least 5 characters.",
                category="error",
            )
        elif len(username) < 2:
            flash(
                "Your username is too short. It must contain least 2 characters.",
                category="error",
            )
        elif password != password_conf:
            flash("Your passwords don't match.", category="error")
        elif len(password) < 8:
            flash(
                "Your password is too short. It must contain least 8 characters.",
                category="error",
            )
        else:
            # Connect to the database
            conn = sqlite3.connect("db/fifa_app.db")
            c = conn.cursor()

            # Hash the password
            hashed_password = generate_password_hash(password)

            # Insert the new user into the users table
            c.execute(
                "INSERT INTO Users (Username, Email, Password) VALUES (?, ?, ?)",
                (username, email, hashed_password),
            )
            conn.commit()

            # Close the cursor and the connection
            c.close()
            conn.close()

            flash("Congratulations! Account created!", category="success")
            return redirect("/")

    return render_template("sign_up.html")
