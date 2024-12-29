import subprocess
import time
from turtle import Screen, Turtle
from player import Player, FINISH_LINE_Y
from car_manager import CarManager
from scoreboard_road import Scoreboard
from tkinter import *
import pymysql
from tkinter import messagebox
from project import update_all_high_scores
import sys
import os
from dotenv import find_dotenv, load_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

def get_db_connection():
    """
    Establishes a connection to the MySQL database.
    """
    try:
        connection = pymysql.connect(
            host="localhost",  # Replace with your database host
            user="root",  # Replace with your database username
            passwd=os.getenv("passwd"),
            database=os.getenv("database")
        )
        return connection
    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error connecting to the database: {e}")
        sys.exit(1)

try:
    user_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    username = sys.argv[2] if len(sys.argv) > 2 else None
except ValueError:
    user_id = None
    username = None
    print("Invalid user ID or username passed. Scores will not be saved.")

# Prevent access if the user is not logged in
if not user_id or not username:
    messagebox.showerror("Access Denied", "You must log in to play this game.")
    sys.exit(1)


def save_turtle_road_score(user_id, username, score):
    """
    Saves the turtle road game score to the database.
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        query = """
        INSERT INTO play (user_id, username, score, date)
        VALUES (%s, %s, %s, NOW())
        """
        cursor.execute(query, (user_id, username, score))
        connection.commit()
        print(f"Score {score} for user {username} saved successfully.")
    except pymysql.MySQLError as e:
        print(f"Error saving score: {e}")
        messagebox.showerror("Error", f"Failed to save score: {e}")
    finally:
        cursor.close()
        connection.close()
# Retrieve user ID and username from command-line arguments
try:
    user_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    username = sys.argv[2] if len(sys.argv) > 2 else None
except ValueError:
    user_id = None
    username = None
    print("Invalid user ID or username passed. Scores will not be saved.")


road_colors = {
    "Desert": "navajo white",
    "Forest": "light green",
    "Sea": "light blue"
}

# Function to draw walls around the game area
def draw_walls():
    wall_turtle = Turtle()
    wall_turtle.hideturtle()
    wall_turtle.speed("fastest")
    wall_turtle.color("black")
    wall_turtle.penup()
    wall_turtle.goto(-290, 290)
    wall_turtle.pendown()
    wall_turtle.pensize(3)
    for _ in range(4):
        wall_turtle.forward(580)
        wall_turtle.right(90)

# Function to move the player up
def move_up():
    player.move()

# Function to close the game when the exit button is clicked

def close_game():
    """
    Properly closes the game and ensures no additional blank windows remain.
    """
    try:
        screen.bye()  # Close the Turtle graphics window
        if root:  # Destroy the Tk root window
            root.destroy()
    except TclError:
        pass




screen = Screen()
screen.setup(width=800, height=800)
screen.title("Turtle Road Game")
screen.tracer(0)
root = screen._root  # Use Turtle's internal root
root.attributes('-fullscreen', True)
root.configure(bg="white")  # Ensure consistent background


# Fix Retry and Exit Buttons
retry_exit_buttons = []  # Global list to store retry and exit buttons

selected_theme_index = IntVar()


def fetch_leaderboard(limit=5):
    """
    Fetch the top scores for Turtle Road from the database.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = """
        SELECT username, score
        FROM play
        WHERE game_id = 2
        ORDER BY score DESC
        LIMIT %s
        """
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def display_top_scores_table():
    top_scores = fetch_top_scores()

    # Clear existing table if any
    highscore_table_turtle.clear()

    # Base coordinates for the table
    x_start = 340
    y_start = 140
    line_height = 40

    # Draw the header
    highscore_table_turtle.penup()
    highscore_table_turtle.goto(x_start, y_start)  # Header position
    highscore_table_turtle.color("white")
    highscore_table_turtle.write(
        "Rank    Username           Score",
        align="left",
        font=("Arial", 12, "bold")
    )

    # Draw each row
    for index, (username, score) in enumerate(top_scores, start=1):
        # Calculate positions for rank, username, and score
        rank_x = x_start
        username_x = x_start + 60  # Offset for username
        score_x = x_start + 200   # Offset for score
        row_y = y_start - line_height * index

        # Write Rank
        highscore_table_turtle.goto(rank_x, row_y)
        highscore_table_turtle.write(
            f"{index}",
            align="left",
            font=("Arial", 12, "bold")
        )

        # Write Username
        highscore_table_turtle.goto(username_x, row_y)
        highscore_table_turtle.write(
            f"{username}",
            align="left",
            font=("Arial", 12, "bold")
        )

        # Write Score
        highscore_table_turtle.goto(score_x, row_y)
        highscore_table_turtle.write(
            f"{score}",
            align="left",
            font=("Arial", 12, "bold")
        )
# Apply the selected theme to the road area
def apply_theme(theme):
    theme_turtle = Turtle()
    theme_turtle.hideturtle()
    theme_turtle.speed("fastest")
    theme_turtle.penup()
    theme_turtle.goto(-290, -290)  # Inside the wall limits
    theme_turtle.color(road_colors[theme])
    theme_turtle.begin_fill()
    for _ in range(2):
        theme_turtle.forward(578)  # Match the wall's width
        theme_turtle.left(90)
        theme_turtle.forward(578)  # Match the wall's height
        theme_turtle.left(90)
    theme_turtle.end_fill()

# Display theme selection options
def create_theme_selection_frame():
    theme_frame = Frame(root, bg="lightgray", padx=10, pady=10)
    theme_frame.place(relx=0.05, rely=0.1, anchor="nw")

    Label(theme_frame, text="Choose Road Theme:", font=("Arial", 12, "bold"), bg="lightgray").pack(pady=5)

    themes = list(road_colors.keys())

    def create_theme_option(theme_name):
        option_frame = Frame(theme_frame, bg="lightgray")
        option_frame.pack(anchor="w", pady=5)

        # Theme label text
        theme_label = Label(option_frame, text=theme_name, font=("Arial", 10, "bold"), bg="lightgray")
        theme_label.pack(side="left", padx=5)

        # Theme color preview box
        color_preview = Canvas(option_frame, width=20, height=20, bg="lightgray", highlightthickness=0)
        color_preview.pack(side="left", padx=5)
        color_preview.create_oval(2, 2, 18, 18, fill=road_colors[theme_name])

        # Radio button to select the theme
        Radiobutton(option_frame, text="", variable=selected_theme_index, value=themes.index(theme_name),
                    bg="lightgray", command=lambda: apply_theme(theme_name)).pack(side="left", padx=5)

    for theme in themes:
        create_theme_option(theme)


# Call the theme selection frame function to display it
create_theme_selection_frame()

# Add an exit button in the upper-right corner
close_button = Button(root, text="X", font=("Arial", 20), bg="red", fg="white", command=close_game)
close_button.place(relx=0.998, rely=0.005, anchor="ne")

# Instantiate game objects
car_manager = CarManager()
player = Player()
scoreboard = Scoreboard()

# Game over display setup
game_over_turtle = Turtle()
game_over_turtle.hideturtle()
game_over_turtle.penup()
game_over_turtle.goto(0, 0)

def display_scoreboard():
    scoreboard_turtle = Turtle()
    scoreboard_turtle.hideturtle()
    scoreboard_turtle.penup()
    scoreboard_turtle.goto(490, 260)  # Adjust position for top-right corner placement
    scoreboard_turtle.color("black")
    scoreboard_turtle.write("Scoreboard", align="center", font=("Arial", 16, "bold"))


def fetch_top_scores(limit=5):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Fetch top scores from the database without the date
        query = """
        SELECT username, score
        FROM play
        WHERE game_id = 2
        ORDER BY score DESC
        LIMIT %s
        """
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching top scores: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

# Function to display the top scores table (without date)

def display_top_scores_table():
    top_scores = fetch_top_scores()

    # Clear existing table if any
    highscore_table_turtle.clear()

    # Base coordinates for the table
    x_start = 340
    y_start = 140
    line_height = 40

    # Draw the header
    highscore_table_turtle.penup()
    highscore_table_turtle.goto(x_start, y_start)  # Header position
    highscore_table_turtle.color("black")
    highscore_table_turtle.write(
        "Rank    Username           Score",
        align="left",
        font=("Arial", 12, "bold")
    )

    # Draw each row
    for index, (username, score) in enumerate(top_scores, start=1):
        # Calculate positions for rank, username, and score
        rank_x = x_start
        username_x = x_start + 60  # Offset for username
        score_x = x_start + 200   # Offset for score
        row_y = y_start - line_height * index

        # Write Rank
        highscore_table_turtle.goto(rank_x, row_y)
        highscore_table_turtle.write(
            f"{index}",
            align="left",
            font=("Arial", 12, "bold")
        )

        # Write Username
        highscore_table_turtle.goto(username_x, row_y)
        highscore_table_turtle.write(
            f"{username}",
            align="left",
            font=("Arial", 12, "bold")
        )

        # Write Score
        highscore_table_turtle.goto(score_x, row_y)
        highscore_table_turtle.write(
            f"{score}",
            align="left",
            font=("Arial", 12, "bold")
        )


# Highscore Table Turtle
highscore_table_turtle = Turtle()
highscore_table_turtle.hideturtle()
highscore_table_turtle.penup()

# Call this function wherever the table needs to be updated
display_top_scores_table()

def save_game_session(user_id, username, game_id, score):
    """Save the game session to the play table."""
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = """
        INSERT INTO play (user_id, username, game_id, score, date)
        VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (user_id, username, game_id, score))
        connection.commit()
    except Exception as e:
        print(f"Error saving game session: {e}")
        messagebox.showerror("Error", f"Failed to save game session: {e}")
    finally:
        cursor.close()
        connection.close()


def retry_game():
    """
    Restarts the Turtle Road game without leaving blank windows.
    """
    close_game()
    if user_id and username:
        subprocess.Popen([sys.executable, "turtle_road.py", str(user_id), username])
    else:
        subprocess.Popen([sys.executable, "turtle_road.py"])



def end_game():
    """
    Handles the end of the game, saving score and session, and displays Retry and Exit buttons.
    """
    global retry_exit_buttons

    scoreboard.game_over()

    # Save the score to the database
    if user_id and username:
        score = scoreboard.level  # Use the current level as the score
        save_game_session(user_id, username, 2, score)  # game_id=2 for Turtle Road
        update_user_highscore(user_id)  # Update the user's high score
        display_top_scores_table()  # Refresh the top scores display

    # Create Retry button
    retry_button = Button(root, text="Retry", font=("Arial", 14), bg="gray", fg="black", command=retry_game)
    retry_button.place(relx=0.4, rely=0.6, anchor="center", width=120, height=40)

    # Create Exit button
    exit_button = Button(root, text="Exit", font=("Arial", 14), bg="red", fg="white", command=close_game)
    exit_button.place(relx=0.6, rely=0.6, anchor="center", width=120, height=40)

    retry_exit_buttons = [retry_button, exit_button]




def reset_game():
    """
    Resets the game for replay when the retry button is pressed.
    """
    player.reset_position()
    car_manager.list_cars.clear()  # Clear all cars from the screen
    car_manager.car_speed = 5  # Reset car speed to initial value
    scoreboard.reset()  # Reset scoreboard to level 1



def update_user_highscore(user_id):
    """Update the user's high score in the users table."""
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query_max_score = """
        SELECT MAX(score) FROM play WHERE user_id = %s AND game_id = 2
        """
        cursor.execute(query_max_score, (user_id,))
        max_score = cursor.fetchone()[0]

        if max_score is not None:
            query_update = """
            UPDATE users SET highscore_road_game = %s WHERE id = %s
            """
            cursor.execute(query_update, (max_score, user_id))
            connection.commit()
            print(f"Updated high score for user ID {user_id} to {max_score}.")
        else:
            print(f"No scores found for user ID {user_id}. No update performed.")
    except Exception as e:
        print(f"Error updating high score: {e}")
        messagebox.showerror("Error", f"Failed to update high score: {e}")
    finally:
        cursor.close()
        connection.close()

# Function to display the countdown
def display_countdown():
    countdown_turtle = Turtle()
    countdown_turtle.hideturtle()
    countdown_turtle.penup()
    countdown_turtle.color("black")
    countdown_turtle.goto(0, 0)

    for count in ["3", "2", "1", "Go!"]:
        countdown_turtle.clear()
        countdown_turtle.write(count, align="center", font=("Courier", 36, "normal"))
        screen.update()
        time.sleep(1)
    countdown_turtle.clear()

def display_instructions():
    instructions_turtle = Turtle()
    instructions_turtle.hideturtle()
    instructions_turtle.penup()

    # Adjusted position for the title (higher y-coordinate)
    instructions_turtle.goto(-620, screen.window_height() // -4 + 50)  # Move up by 50 units
    instructions_turtle.color("black")
    instructions_turtle.write("How to Play", align="left", font=("Arial", 14, "bold"))

    instructions_text = (
        "1. Choose a type of road from upper-left corner\n"
        "2. ↑ (Up Arrow): To move the turtle to the finish.\n"
        "3. Avoid the moving cars!\n"
        "4. Reach the top to level up.\n"
        "5. Faster cars at each level!\n"
    )

    # Start writing the instructions below the title
    instructions_turtle.sety(instructions_turtle.ycor() - 50)  # Add spacing below the title
    for line in instructions_text.split('\n'):
        instructions_turtle.write(line, align="left", font=("Arial", 10, "normal"))
        instructions_turtle.sety(instructions_turtle.ycor() - 25)



def run_game():
    """
    Main game loop that updates the screen and checks for collisions or level completion.
    """
    screen.listen()
    screen.onkey(move_up, "Up")

    game_is_on = True
    while game_is_on:
        time.sleep(0.1)
        screen.update()
        car_manager.create_car()
        car_manager.move()

        # Detect collision with cars
        for car in car_manager.list_cars:
            if car.distance(player) < 20:
                game_is_on = False
                end_game()  # End game and show Retry/Exit buttons

        # Detect success (reaching the top)
        if player.ycor() > FINISH_LINE_Y - 10:
            player.reset_position()
            car_manager.increase_speed()
            scoreboard.update_level()
            display_top_scores_table()



# Function to start the game by hiding the start button, drawing walls, showing countdown, and starting the game
def start_game():
    global start_button  # Ensure we're working with the same instance
    start_button.destroy()  # Completely remove the button
    draw_walls()
    # Apply the currently selected theme or default
    theme_index = selected_theme_index.get()
    themes = list(road_colors.keys())
    if 0 <= theme_index < len(themes):
        apply_theme(themes[theme_index])
    else:
        apply_theme(themes[0])  # Default to the first theme
    display_countdown()
    run_game()

display_scoreboard()

# Add Start Game button to initialize the game

# Add Start Game button
start_button = Button(root, text="Start Game", font=("Arial", 14), bg="green", fg="white", command=start_game)
start_button.place(relx=0.5, rely=0.5, anchor="center")

display_top_scores_table()
display_instructions()
screen.mainloop()

