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
    # Connect to the SQLite database
    conn = sqlite3.connect("db/fifa_app.db")
    c = conn.cursor()

    # Retrieve the data from the table
    c.execute("SELECT * FROM Teams")
    teams = c.fetchall()

    c.execute("SELECT * FROM Players")
    players = c.fetchall()

    # Convert the data to a dataframe
    teams_df = pd.DataFrame(
        teams,
        columns=[
            "Team_ID",
            "Team_name",
            "Coach",
            "Capitan",
            "Group_letter",
            "Wins",
            "Draws",
            "Losses",
            "Goals_for",
            "Goals_against",
            "Points",
        ],
    )

    players_df = pd.DataFrame(
        players,
        columns=[
            "Player_ID",
            "Name",
            "Date_of_birth",
            "Height_cm",
            "Position",
            "Market_value",
            "Better_foot",
            "Team_ID",
        ],
    )

    # Close the cursor and connection
    c.close()
    conn.close()

    teams_grpd_value = players_df[["Market_value", "Team_ID"]]
    teams_grpd_value = teams_grpd_value.groupby(["Team_ID"]).sum()
    team_names = teams_df["Team_name"]
    teams_grpd_value["Team_Name"] = team_names
    teams_grpd_value = teams_grpd_value.sort_values(by=["Market_value"], ascending=True)

    # Generate figures
    fig = px.bar(
        teams_grpd_value,
        x="Market_value",
        y="Team_Name",
        barmode="group",
        template="plotly_white",
        title="Market value of teams (countries)",
        text=teams_df.Coach,
    )
    fig.update_xaxes(title_text="Market value")
    fig.update_yaxes(title_text="Teams")
    fig.update_traces(
        marker_color=[
            "rgb(102, 197, 204)",
            "rgb(246, 207, 113)",
            "rgb(248, 156, 116)",
            "rgb(220, 176, 242)",
            "rgb(135, 197, 95)",
            "rgb(158, 185, 243)",
            "rgb(254, 136, 177)",
            "rgb(201, 219, 116)",
        ],
        marker_line_color="rgb(0,0,0)",
        marker_line_width=1.5,
        opacity=0.95,
    )

    html_string = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("teams.html", teams=teams, html_string=html_string)


@auth.route("/players")
@require_login
def players():
    # Connect to the SQLite database
    conn = sqlite3.connect("db/fifa_app.db")
    c = conn.cursor()

    # Retrieve the data from the table
    c.execute("SELECT * FROM Teams")
    teams = c.fetchall()

    c.execute("SELECT * FROM Players")
    players = c.fetchall()

    # Convert the data to a dataframe
    teams_df = pd.DataFrame(
        teams,
        columns=[
            "Team_ID",
            "Team_name",
            "Coach",
            "Capitan",
            "Group_letter",
            "Wins",
            "Draws",
            "Losses",
            "Goals_for",
            "Goals_against",
            "Points",
        ],
    )

    players_df = pd.DataFrame(
        players,
        columns=[
            "Player_ID",
            "Name",
            "Date_of_birth",
            "Height_cm",
            "Position",
            "Market_value",
            "Better_foot",
            "Team_ID",
        ],
    )

    # Close the cursor and connection
    c.close()
    conn.close()

    # Generate the plotly figure_1
    players_top_value = players_df.nlargest(15, ["Market_value"])
    fig = px.bar(
        players_top_value,
        x="Name",
        y="Market_value",
        barmode="group",
        template="plotly_white",
        title="Top 15 players with the highest market value",
        text=players_top_value.Position,
    )
    fig.update_xaxes(title_text="Players")
    fig.update_yaxes(title_text="Market value")
    fig.update_traces(
        marker_color="#a1435f",
        marker_line_color="rgb(0,0,0)",
        marker_line_width=1.5,
        opacity=0.95,
    )

    html_string = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Generate the plotly figure_2
    players_tallest = players_df.nlargest(15, ["Height_cm"])
    fig2 = px.bar(
        players_tallest,
        x="Height_cm",
        y="Name",
        barmode="group",
        template="plotly_white",
        title="Top 15 tallest players",
        text=players_top_value.Position,
    )
    fig2.update_xaxes(title_text="Height", range=[185, 200])
    fig2.update_yaxes(title_text="Players")
    fig2.update_traces(
        marker_color="#63C085",
        marker_line_color="rgb(0,0,0)",
        marker_line_width=1.5,
        opacity=0.95,
    )

    html_string_2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    # Format Market_value column to have the € sign and the m or k
    # meaning million or thousands
    def format_value(val):
        if val >= 1000000:
            return "€" + str(val // 1000000) + ".00m"
        else:
            return "€" + str(val // 1000) + "k"

    players_df["Market_value"] = players_df["Market_value"].apply(format_value)

    # Map Team_ID to Team_name and drop Team_ID column
    teams_map = dict(zip(teams_df.Team_ID, teams_df.Team_name))
    players_df["Team"] = players_df["Team_ID"].map(teams_map)
    players_df = players_df.drop(["Team_ID"], axis=1)

    # Map Better_foot to Right, Left or Both based on the value
    players_df["Better_foot"] = players_df["Better_foot"].map(
        {"R": "Right", "L": "Left", "B": "Both"}
    )

    return render_template(
        "players.html",
        players=players_df,
        html_string=html_string,
        html_string_2=html_string_2,
    )


@auth.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        password_conf = request.form.get("password_conf")

        if len(email) < 5:
            flash(
                "Your email is too short. It must contain at least 5 characters.",
                category="error",
            )
        elif len(username) < 2:
            flash(
                "Your username is too short. It must contain at least 2 characters.",
                category="error",
            )
        elif password != password_conf:
            flash("Your passwords don't match.", category="error")
        elif len(password) < 8:
            flash(
                "Your password is too short. It must contain at least 8 characters.",
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
