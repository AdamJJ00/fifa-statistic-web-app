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
    conn = sqlite3.connect("db/fifa_app.db")
    c = conn.cursor()

    c.execute(
        "SELECT p.name, SUM(e.type = 'G') as Goals \
        FROM events e \
        JOIN players p ON e.player_id = p.player_id \
        GROUP BY e.player_id \
        ORDER BY Goals DESC LIMIT 10;")
    query_1 = c.fetchall()

    c.execute(
        "SELECT teams.team_name, COUNT(players.team_id) as Left_foot_players \
        FROM teams \
        JOIN players ON teams.team_id = players.team_id \
        WHERE players.better_foot = 'L' \
        GROUP BY teams.team_name \
        HAVING left_foot_players >= 1 \
        ORDER BY Left_foot_players DESC LIMIT 5;")
    query_2 = c.fetchall()

    c.execute(
        "SELECT teams.team_name, SUM(CASE WHEN events.type = 'G' THEN 1 ELSE 0 END) as Goals \
        FROM teams \
        JOIN players ON teams.team_id = players.team_id \
        JOIN events ON players.player_id = events.player_id \
        GROUP BY teams.team_name \
        ORDER BY Goals DESC;")
    query_3 = c.fetchall()

    c.execute(
        "SELECT teams.team_name, SUM(players.market_value) as Market_value \
        FROM teams \
        JOIN players ON teams.team_id = players.team_id \
        GROUP BY teams.team_name \
        ORDER BY Market_value DESC;")
    query_4 = c.fetchall()

    c.execute(
        "SELECT teams.team_name, COUNT(CASE WHEN events.type = 'Y' THEN 1 ELSE 0 END) as yellow_cards \
        FROM teams \
        JOIN players ON teams.team_id = players.team_id \
        JOIN events ON players.player_id = events.player_id \
        WHERE events.type = 'Y' \
        GROUP BY teams.team_name \
        ORDER BY yellow_cards DESC \
        LIMIT 5;")
    query_5 = c.fetchall()

    c.execute(
        "SELECT teams.team_name, ROUND(AVG((julianday('now') - julianday(players.date_of_birth))/365), 2) as average_age \
        FROM teams \
        JOIN players ON teams.team_id = players.team_id \
        GROUP BY teams.team_name \
        ORDER BY average_age DESC \
        LIMIT 4;")
    query_6 = c.fetchall()

    c.execute(
        "SELECT teams.team_name, ROUND(AVG((julianday('now') - julianday(players.date_of_birth))/365), 2) as average_age \
        FROM teams \
        JOIN players ON teams.team_id = players.team_id \
        GROUP BY teams.team_name \
        ORDER BY average_age ASC \
        LIMIT 4;")
    query_7 = c.fetchall()

    c.execute(
        "SELECT teams.team_name, ROUND(AVG(players.height_cm), 2) as height \
        FROM teams \
        JOIN players ON teams.team_id = players.team_id \
        GROUP BY teams.team_name \
        ORDER BY height DESC \
        LIMIT 4;")
    query_8 = c.fetchall()

    c.execute(
        "SELECT teams.team_name, ROUND(AVG(players.height_cm), 2) as height \
                FROM teams \
                JOIN players ON teams.team_id = players.team_id \
                GROUP BY teams.team_name \
                ORDER BY height ASC \
                LIMIT 4;")
    query_9 = c.fetchall()

    c.execute(
        "SELECT stadiums.stadium_name, stadiums.capacity \
        FROM stadiums \
        ORDER BY capacity DESC;")
    query_10 = c.fetchall()

    c.execute(
        "SELECT players.name, a.team_name || ' - ' || b.team_name as 'Game', matches.date, events.minute as fastest_goal \
        FROM players \
        JOIN events ON players.player_id = events.player_id \
        JOIN matches ON matches.match_id = events.match_id \
        JOIN teams a ON a.team_id = matches.home_team_id \
        JOIN teams b ON b.team_id = matches.away_team_id \
        WHERE events.type = 'G' \
        GROUP BY players.player_id \
        ORDER BY fastest_goal \
        LIMIT 10;")
    query_11 = c.fetchall()

    c.execute(
        "SELECT teams.team_name,  a.team_name || ' - ' || b.team_name as 'Game', matches.date, events.minute as earliest_yellow_card \
        FROM teams \
        JOIN players ON teams.team_id = players.team_id \
        JOIN events ON players.player_id = events.player_id \
        JOIN matches ON matches.match_id = events.match_id \
        JOIN teams a ON a.team_id = matches.home_team_id \
        JOIN teams b ON b.team_id = matches.away_team_id \
        WHERE events.type = 'Y' \
        GROUP BY teams.team_name \
        ORDER BY earliest_yellow_card \
        LIMIT 5;")
    query_12 = c.fetchall()

    c.execute(
        "SELECT players.name, teams.team_name, players.date_of_birth as Date_of_birth \
        FROM players \
        JOIN teams ON teams.team_id = players.team_id \
        ORDER BY Date_of_birth DESC \
        LIMIT 10;")
    query_13 = c.fetchall()

    c.execute(
        "SELECT players.name, teams.team_name, players.date_of_birth as Date_of_birth \
        FROM players \
        JOIN teams ON teams.team_id = players.team_id \
        ORDER BY Date_of_birth ASC \
        LIMIT 10;")
    query_14 = c.fetchall()

    c.execute(
        "SELECT players.name, teams.team_name, players.position, players.height_cm as height \
        FROM players \
        JOIN teams ON teams.team_id = players.team_id \
        ORDER BY height DESC \
        LIMIT 10;")
    query_15 = c.fetchall()

    c.execute(
        "SELECT players.name, teams.team_name, players.position, players.height_cm as height \
        FROM players \
        JOIN teams ON teams.team_id = players.team_id \
        ORDER BY height ASC \
        LIMIT 10;")
    query_16 = c.fetchall()

    c.close()
    conn.close()
    return render_template("stats.html", query_1=query_1, query_2=query_2, query_3=query_3, query_4=query_4,
                           query_5=query_5, query_6=query_6, query_7=query_7, query_8=query_8, query_9=query_9,
                           query_10=query_10, query_11=query_11, query_12=query_12, query_13=query_13, query_14=query_14,
                           query_15=query_15, query_16=query_16)


@auth.route("/matches")
@require_login
def matches():
    conn = sqlite3.connect("db/fifa_app.db")
    c = conn.cursor()

    c.execute(
        "SELECT matches.Date, matches.Time, stadiums.Stadium_name, teams.Team_name as Home_team, a.Team_name as Away_team, matches.home_goals || ':' || matches.away_goals as Score \
        FROM matches \
        JOIN teams ON matches.home_team_id=teams.team_id \
        JOIN teams a ON matches.away_team_id=a.team_id \
        JOIN stadiums ON stadiums.stadium_id = matches.stadium_id \
        WHERE teams.group_letter='E'")
    matches_query_1 = c.fetchall()

    c.execute(
        "SELECT matches.Date, matches.Time, stadiums.Stadium_name, teams.Team_name as Home_team, a.Team_name as Away_team, matches.home_goals || ':' || matches.away_goals as Score \
        FROM matches \
        JOIN teams ON matches.home_team_id=teams.team_id \
        JOIN teams a ON matches.away_team_id=a.team_id \
        JOIN stadiums ON stadiums.stadium_id = matches.stadium_id \
        WHERE teams.group_letter='C'")
    matches_query_2 = c.fetchall()

    c.execute(
        "SELECT a.team_name || ' - ' || b.team_name as 'Match', matches.home_goals + matches.away_goals as total_goals \
        FROM matches \
        JOIN teams a ON a.team_id = matches.home_team_id \
        JOIN teams b ON b.team_id = matches.away_team_id \
        ORDER BY total_goals DESC \
        LIMIT 10;")
    matches_query_3 = c.fetchall()

    c.execute(
        "SELECT a.team_name || ' - ' || b.team_name as 'Match', COUNT(events.type) as cards \
        FROM matches \
        JOIN events ON matches.match_id = events.match_id \
        JOIN teams a ON a.team_id = matches.home_team_id \
        JOIN teams b ON b.team_id = matches.away_team_id \
        WHERE events.type IN ('Y', 'R') \
        GROUP BY matches.match_id \
        ORDER BY cards DESC \
        LIMIT 10;")
    matches_query_4 = c.fetchall()

    c.execute(
        "SELECT matches.Date, matches.Time, stadiums.Stadium_name, teams.Team_name as Home_team, a.Team_name as Away_team, matches.home_goals || ':' || matches.away_goals as Score \
        FROM matches \
        JOIN teams ON matches.home_team_id=teams.team_id \
        JOIN teams a ON matches.away_team_id=a.team_id \
        JOIN stadiums ON stadiums.stadium_id = matches.stadium_id \
        WHERE stadiums.stadium_name = 'Lusail Stadium';")
    matches_query_5 = c.fetchall()

    c.execute(
        "SELECT matches.Date, matches.Time, stadiums.Stadium_name, teams.Team_name as Home_team, a.Team_name as Away_team, matches.home_goals || ':' || matches.away_goals as Score \
        FROM matches \
        JOIN teams ON matches.home_team_id=teams.team_id \
        JOIN teams a ON matches.away_team_id=a.team_id \
        JOIN stadiums ON stadiums.stadium_id = matches.stadium_id \
        WHERE stadiums.stadium_name = 'Al Bayt Stadium';")
    matches_query_6 = c.fetchall()

    c.close()
    conn.close()
    return render_template("matches.html", matches_query_1=matches_query_1, matches_query_2=matches_query_2, matches_query_3=matches_query_3, matches_query_4=matches_query_4,
                           matches_query_5=matches_query_5, matches_query_6=matches_query_6)



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
