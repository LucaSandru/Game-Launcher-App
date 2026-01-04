# Game Launcher App

## Project Overview

The **Game Launcher App** is a Python-based application with a *Graphical User Interface (GUI)* that allows users to:

- Browse and launch built-in mini-games
- Track high scores and leaderboards
- Manage multiple games from a single dashboard


---

## Key Features

- A clean and user‑friendly graphical interface
- Multiple games playable from a single launcher
- Highscore tracking and leaderboard supporting
- Modular code structure, separating UI, game logic, and persistent storage - using a DB also
- Demonstrates Python, GUI frameworks, and event‑driven programming

---

## Motivation

This project was created to combine my interest in game development and application interfaces. I wanted to build a *centralized game platform* where users can launch and play small games while their progress and achievements are tracked. This also helped me enhance skills on *Python*, *software architecture*, and *data handling*.

---

## Main Repository Contents 


- `launcher.py`: Main application entry point
- `sql.py`: Database interactions for highscores
- `snake.py`, `turtle_race.py`, etc.: Individual game modules
- `scoreboard.py`: Leaderboard logic (active in Python GUI)

---

## Installation & Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/LucaSandru/Game-Launcher-App.git
   cd Game-Launcher-App

2. Install Python dependencies:

   ```bash
   pip install tkinter...

3. Run the application (with `launcher.py`):

   ```bash
   python launcher.py

---

## Features - available also on `REQUIREMENTS.txt`

1. **User Authentication**
   a) *Login Page*
     - Login with username & password
     - "Forgot Password?" option using SMTP email recovery (Gmail only)

   b) *Signup Page*
     - Register with:
     - *Username* (no spaces)
     - *Gmail address* only
     - *Password* (min. 4 characters)
    - *Two-Factor Authentication*: 6-digit code sent to Gmail, verified during sign-up

2. **Games available**
   a) *Turtle Race* - Race with turtles in a randomized finish contest
   b) *Turtle Road* - Cross the road avoiding traffic using turtle graphics
   c) *Snake* - Classic snake game with score and growth logic

All games include:
- Game description
- In-game **Main Menu** button to return to launcher
- Styled UI for better experience
- Instructions ("How to Play")
- **Real-time leaderboard** (top 5 users per game)


3. **Database Design (MySQL)**

- *users*
  - `id`, `username`, `email`, `password`, `highscore_turtle`, `highscore_snake`, etc.

- *games*
  - `game_id`, `game_name`

- *play*
  - `play_id`, `user_id`, `username`, `game_id`, `score`, `date`

All data is visualized in `MySQL Workbench` and stored using secure queries.


4. **Environment Variables**

For security, sensitive data is stored in a `.env` file and loaded using `python-dotenv`:

- `DB_NAME` —  MySQL database name
- `DB_USER` — MySQL user
- `DB_PASSWORD` — MySQL password
- `GMAIL_PASSWORD` — App password for your Gmail account used in SMTP


5. **Technologies Used**

- *Python 3.10+*
- different python tools (especially for GUI styling)
- *Tkinter* for GUI
- *MySQL & MySQL Workbench* for persistent data
- *SMTP (smtplib)* for email authentication
- *dotenv* for environment management

---

## Future Improvements

- Web-based version using Flask or Django
- OAuth login (Google or GitHub)
- More games with AI-powered opponents
- store all scores in cloud DB
