'''
-- SQL query to retrieve the schedule of matches for Group E
SELECT matches.Date, matches.Time, stadiums.Stadium_name, teams.Team_name as Home_team, a.Team_name as Away_team, matches.home_goals || ':' || matches.away_goals as Score
FROM matches JOIN teams ON matches.home_team_id=teams.team_id JOIN teams a ON matches.away_team_id=a.team_id JOIN stadiums ON stadiums.stadium_id = matches.stadium_id
WHERE teams.group_letter='E'


-- SQL query to retrieve the top 10 goal scorers in the tournament
SELECT p.name, SUM(e.type = 'G') as goals
FROM events e
JOIN players p ON e.player_id = p.player_id
GROUP BY e.player_id
ORDER BY goals DESC
LIMIT 10;


-- SQL query to retrive top 5 teams with most left-footed players
SELECT teams.team_name, COUNT(players.team_id) as left_foot_players
FROM teams
JOIN players ON teams.team_id = players.team_id
WHERE players.better_foot = "L"
GROUP BY teams.team_name
HAVING left_foot_players >= 1
ORDER BY left_foot_players DESC
LIMIT 5;


-- SQL query to calculate the number of goals scored by each team
SELECT teams.team_name, SUM(CASE WHEN events.type = 'G' THEN 1 ELSE 0 END) as goals
FROM teams
JOIN players ON teams.team_id = players.team_id
JOIN events ON players.player_id = events.player_id
GROUP BY teams.team_name
ORDER BY goals DESC;


-- SQL query to retrieve top 10 teams with highest market value
SELECT teams.team_name, SUM(players.market_value) as market_value
FROM teams
JOIN players ON teams.team_id = players.team_id
GROUP BY teams.team_name
ORDER BY market_value DESC;


-- SQL query to retrieve the top 5 teams with the most yellow cards
SELECT teams.team_name, COUNT(CASE WHEN events.type = 'Y' THEN 1 ELSE 0 END) as yellow_cards
FROM teams
JOIN players ON teams.team_id = players.team_id
JOIN events ON players.player_id = events.player_id
WHERE events.type = 'Y'
GROUP BY teams.team_name
ORDER BY yellow_cards DESC
LIMIT 5;


-- SQL query to retrieve the top 10 oldest teams (based on players age)
SELECT teams.team_name, AVG((julianday('now') - julianday(players.date_of_birth))/365) as average_age
FROM teams
JOIN players ON teams.team_id = players.team_id
GROUP BY teams.team_name
ORDER BY average_age DESC
LIMIT 10;

-- SQL query to retrieve the top 10 youngest teams (based on players age)
SELECT teams.team_name, AVG((julianday('now') - julianday(players.date_of_birth))/365) as average_age
FROM teams
JOIN players ON teams.team_id = players.team_id
GROUP BY teams.team_name
ORDER BY average_age ASC
LIMIT 10;

-- SQL query to retrieve top 5 teams with tallest players (on average)
SELECT teams.team_name, AVG(players.height_cm) as height
FROM teams
JOIN players ON teams.team_id = players.team_id
GROUP BY teams.team_name
ORDER BY height DESC
LIMIT 5;


-- SQL query to retrieve top 5 teams with shortest players (on average)
SELECT teams.team_name, AVG(players.height_cm) as height
FROM teams
JOIN players ON teams.team_id = players.team_id
GROUP BY teams.team_name
ORDER BY height ASC
LIMIT 5;

-- SQL query to retrieve sadiums with the highest capacity
SELECT stadiums.stadium_name, stadiums.capacity
FROM stadiums
ORDER BY capacity DESC
LIMIT 10;

-- SQL query to retrieve top 10 fastest scoring players
SELECT players.name, a.team_name || ' - ' || b.team_name as 'Game', matches.date, events.minute as fastest_goal
FROM players
JOIN events ON players.player_id = events.player_id
JOIN matches ON matches.match_id = events.match_id
JOIN teams a ON a.team_id = matches.home_team_id
JOIN teams b ON b.team_id = matches.away_team_id
WHERE events.type = 'G'
GROUP BY players.player_id
ORDER BY fastest_goal
LIMIT 10;

-- SQL query to retrieve the top 5 teams which recived the earliest yellow cards on tournament
SELECT teams.team_name,  a.team_name || ' - ' || b.team_name as 'Game', matches.date, events.minute as earliest_yellow_card
FROM teams
JOIN players ON teams.team_id = players.team_id
JOIN events ON players.player_id = events.player_id
JOIN matches ON matches.match_id = events.match_id
JOIN teams a ON a.team_id = matches.home_team_id
JOIN teams b ON b.team_id = matches.away_team_id
WHERE events.type = 'Y'
GROUP BY teams.team_name
ORDER BY earliest_yellow_card
LIMIT 5;

-- SQL query to retrieve the top 10 matches with the highest scores
SELECT a.team_name || ' - ' || b.team_name as 'Match', matches.home_goals + matches.away_goals as total_goals
FROM matches
JOIN teams a ON a.team_id = matches.home_team_id
JOIN teams b ON b.team_id = matches.away_team_id
ORDER BY total_goals DESC
LIMIT 10;

-- SQL query to retrieve top 5 matches with most yellow/red cards
SELECT a.team_name || ' - ' || b.team_name as 'Match', COUNT(events.type) as cards
FROM matches
JOIN events ON matches.match_id = events.match_id
JOIN teams a ON a.team_id = matches.home_team_id
JOIN teams b ON b.team_id = matches.away_team_id
WHERE events.type IN ('Y', 'R')
GROUP BY matches.match_id
ORDER BY cards DESC
LIMIT 5;

-- SQL query to retrieve all matches which took place at selected stadium
SELECT matches.Date, matches.Time, stadiums.Stadium_name, teams.Team_name as Home_team, a.Team_name as Away_team, matches.home_goals || ':' || matches.away_goals as Score
FROM matches JOIN teams ON matches.home_team_id=teams.team_id JOIN teams a ON matches.away_team_id=a.team_id JOIN stadiums ON stadiums.stadium_id = matches.stadium_id
WHERE stadiums.stadium_name = 'Lusail Stadium';


-- SQL query to retrieve top 5 youngest players
SELECT players.name, teams.team_name, players.date_of_birth as Date_of_birth
FROM players
JOIN teams ON teams.team_id = players.team_id
ORDER BY Date_of_birth DESC
LIMIT 5;


-- SQL query to retrieve top 5 oldest players
SELECT players.name, teams.team_name, players.date_of_birth as Date_of_birth
FROM players
JOIN teams ON teams.team_id = players.team_id
ORDER BY Date_of_birth ASC
LIMIT 5;


-- SQL query to retrieve the top 5 tallest players
SELECT players.name, teams.team_name, players.position, players.height_cm as height
FROM players
JOIN teams ON teams.team_id = players.team_id
ORDER BY height DESC
LIMIT 5;


-- SQL query to retrieve the top 5 shortest players
SELECT players.name, teams.team_name, players.position, players.height_cm as height
FROM players
JOIN teams ON teams.team_id = players.team_id
ORDER BY height ASC
LIMIT 5;
'''
