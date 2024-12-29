from turtle import Turtle, Screen
import random
from tkinter import Button, Label, Frame, Radiobutton, IntVar, Canvas, TclError, messagebox
import time
import os
import pymysql  # For database integration
import sys
from dotenv import find_dotenv, load_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# Database Connection
def get_db_connection():
    """
    Establishes a connection to the MySQL database.
    """
    try:
        return pymysql.connect(
            host="localhost",
            user="root",
            passwd=os.getenv("passwd"),
            database=os.getenv("database")
        )
    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Error connecting to the database: {e}")
        sys.exit(1)

# Global variables for the logged-in user
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


# Save game session to the database
def save_game_session(user_id, username, game_id, score):
    """
    Save the game session to the `play` table and update the high score in `users`.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Insert the play session
        query = """
        INSERT INTO play (user_id, username, game_id, score, date)
        VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (user_id, username, game_id, score))

        # Update the high score if this session's score is higher
        cursor.execute("SELECT highscore_race_game FROM users WHERE id = %s", (user_id,))
        current_highscore = cursor.fetchone()[0]
        if current_highscore is None or score > current_highscore:
            update_query = "UPDATE users SET highscore_race_game = %s WHERE id = %s"
            cursor.execute(update_query, (score, user_id))

        connection.commit()
    except pymysql.MySQLError as e:
        messagebox.showerror("Database Error", f"Failed to save game session: {e}")
    finally:
        cursor.close()
        connection.close()

# Fetch the leaderboard
def fetch_leaderboard(limit=5):
    """
    Fetch the top scores for Turtle Race (game_id = 1) from the database.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = """
        SELECT username, score
        FROM play
        WHERE game_id = 1
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
    top_scores = fetch_leaderboard()

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


# Set up the screen
screen = Screen()
screen.setup(width=1.0, height=1.0)  # Fullscreen setup
screen.title("Turtle Race Game")

def close_race():
    try:
        screen.bye()
        if screen._root:
            screen._root.destroy()
    except TclError:
        pass


# Root setup for fullscreen
root = screen._root
root.attributes('-fullscreen', True)

# Close button in the top-right corner
close_button = Button(root, text="X", font=("Arial", 20), bg="red", fg="white", command=close_race)
close_button.place(relx=0.998, rely=0.005, anchor="ne")

# Colors and setup for turtles and themes
colors = ["red", "orange", "yellow", "green", "blue", "purple"]
all_turtles = []
selected_color_index = IntVar()
selected_theme_index = IntVar()

# Background themes and their colors
theme_colors = {
    "Desert": "navajo white",
    "Ocean": "light blue",
    "Forest": "light green",
}

# Apply the background theme to the racing area only
# Apply the background theme to cover the entire race area
def apply_theme(theme):
    theme_turtle = Turtle()
    theme_turtle.hideturtle()
    theme_turtle.speed("fastest")
    theme_turtle.penup()
    theme_turtle.goto(-208, -290)
    theme_turtle.color(theme_colors[theme])
    theme_turtle.begin_fill()
    for _ in range(2):
        theme_turtle.forward(456)
        theme_turtle.left(90)
        theme_turtle.forward(578)
        theme_turtle.left(90)
    theme_turtle.end_fill()


# Display theme selection options
def create_theme_selection_frame():
    theme_frame = Frame(root, bg="lightgray", padx=10, pady=10)
    theme_frame.place(relx=0.05, rely=0.1, anchor="nw")

    Label(theme_frame, text="Choose Race Theme:", font=("Arial", 12, "bold"), bg="lightgray").pack(pady=5)

    themes = list(theme_colors.keys())

    def create_theme_option(theme_name):
        option_frame = Frame(theme_frame, bg="lightgray")
        option_frame.pack(anchor="w", pady=5)

        theme_label = Label(option_frame, text=theme_name, font=("Arial", 10, "bold"), bg="lightgray")
        theme_label.pack(side="left", padx=5)

        color_preview = Canvas(option_frame, width=20, height=20, bg="lightgray", highlightthickness=0)
        color_preview.pack(side="left", padx=5)
        color_preview.create_oval(2, 2, 18, 18, fill=theme_colors[theme_name])

        Radiobutton(option_frame, text="", variable=selected_theme_index, value=themes.index(theme_name),
                    bg="lightgray", command=lambda: apply_theme(theme_name)).pack(side="left", padx=5)

    for theme in themes:
        create_theme_option(theme)


# Draw race boundaries, labels, paths, etc.
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

# Initialize boundaries and labels
draw_walls()


def draw_finish_line():
    finish_line = Turtle()
    finish_line.hideturtle()
    finish_line.penup()
    finish_line.goto(250, -270)  # Start of the finish line inside the walls
    finish_line.setheading(90)
    for _ in range(19):
        finish_line.color("black")
        finish_line.pendown()
        finish_line.forward(10)
        finish_line.penup()
        finish_line.forward(10)
        finish_line.color("white")
        finish_line.forward(10)

def draw_start_line():
    start_line = Turtle()
    start_line.hideturtle()
    start_line.penup()
    start_line.goto(-210, -270)
    start_line.setheading(90)
    for _ in range(19):
        start_line.color("black")
        start_line.pendown()
        start_line.forward(10)
        start_line.penup()
        start_line.forward(10)
        start_line.color("white")
        start_line.forward(10)

def draw_finish_label():
    finish_label = Turtle()
    finish_label.hideturtle()
    finish_label.penup()
    finish_label.color("black")
    finish_label.goto(275, 70)
    finish_label.setheading(270)
    for letter in "FINISH":
        finish_label.write(letter, align="center", font=("Arial", 20, "bold"))
        finish_label.forward(30)

def draw_start_label():
    start_label = Turtle()
    start_label.hideturtle()
    start_label.penup()
    start_label.color("black")
    start_label.goto(-265, 80)
    start_label.setheading(270)
    for letter in "START":
        start_label.write(letter, align="center", font=("Arial", 20, "bold"))
        start_label.forward(40)

# Draw paths for each turtle lane
def draw_turtle_paths(num_turtles):
    for i in range(num_turtles):
        path_turtle = Turtle()
        path_turtle.hideturtle()
        path_turtle.speed("fastest")
        path_turtle.color(colors[i])
        path_turtle.penup()
        lane_y = -100 + 40 * i
        path_turtle.goto(-230, lane_y)
        path_turtle.setheading(0)
        for _ in range(25):
            path_turtle.pendown()
            path_turtle.forward(10)
            path_turtle.penup()
            path_turtle.forward(10)

# Initialize boundaries and labels
draw_walls()
draw_start_line()
draw_finish_line()
draw_start_label()
draw_finish_label()

# Function to reset turtles if input is invalid
def reset_turtles():
    for turtle in all_turtles:
        turtle.hideturtle()
    all_turtles.clear()

# Set up turtles based on the level
def setup_turtles(num_turtles):
    """
    Sets up the turtles and their respective paths based on the current level.
    """
    reset_turtles()
    draw_turtle_paths(num_turtles)  # Draw paths before placing turtles
    for i in range(num_turtles):
        tim = Turtle(shape="turtle")
        tim.color(colors[i])
        tim.penup()
        tim.goto(-230, -100 + 40 * i)
        all_turtles.append(tim)



# Countdown display
def display_countdown():
    countdown_turtle = Turtle()
    countdown_turtle.hideturtle()
    countdown_turtle.penup()
    countdown_turtle.color("black")
    countdown_turtle.goto(0, 100)
    for count in range(3, 0, -1):
        countdown_turtle.clear()
        countdown_turtle.write(f"{count}", align="center", font=("Arial", 24, "bold"))
        time.sleep(1)
    countdown_turtle.clear()
    countdown_turtle.write("Go!", align="center", font=("Arial", 24, "bold"))
    time.sleep(1)
    countdown_turtle.clear()


# Score label
score_label = Label(root, text="Score: Level 1", font=("Arial", 16), fg="black")
score_label.place(relx=0.5, rely=0.05, anchor="center")

# Update score label
def update_score_label(level):
    score_label.config(text=f"Score: {level}")

# Display instructions in the bottom-left corner using a Turtle
def display_instructions():
    instructions_turtle = Turtle()
    instructions_turtle.hideturtle()
    instructions_turtle.penup()
    instructions_turtle.goto(-620, -140)
    instructions_turtle.color("black")
    instructions_turtle.write("How to Play", align="left", font=("Arial", 14, "bold"))
    instructions_turtle.sety(instructions_turtle.ycor() - 60)  # Add more spacing after the title
    instructions_text = (
        "1. Choose a background theme the top-left corner.\n"
        "2. Pick the color you think will win the race!\n"
        "2. Click 'Start Race' to begin the game!\n"
        "4. Watch as the turtles race toward the finish line!\n"
        "5. Anything can happen, turtles are moving randomly\n"
        "5. If you guessed correctly, you’ll move on to the next level\n"
    )
    for line in instructions_text.split('\n'):
        instructions_turtle.write(line, align="left", font=("Arial", 10, "normal"))
        instructions_turtle.sety(instructions_turtle.ycor() - 25)  # Move down for each line
# Color selection for the turtles
def create_color_selection_frame(level):
    update_score_label(level)
    num_turtles = level + 1
    level_colors = colors[:num_turtles]
    color_frame = Frame(root, bg="lightgray", padx=10, pady=10)
    color_frame.place(relx=0.5, rely=0.5, anchor="center")
    instruction_text = f"Level {level}: Choose the color you think will win this race:"
    Label(color_frame, text=instruction_text, font=("Arial", 12, "bold"), bg="lightgray").pack(pady=10)
    selected_color_index.set(-1)
    for index, color in enumerate(level_colors):
        option_frame = Frame(color_frame, bg="lightgray")
        option_frame.pack(anchor="w", pady=5)
        color_dot = Canvas(option_frame, width=15, height=15, bg="lightgray", highlightthickness=0)
        color_dot.pack(side="left", padx=5)
        color_dot.create_oval(2, 2, 13, 13, fill=color)
        Radiobutton(option_frame, text=color.capitalize(), variable=selected_color_index, value=index,
                    font=("Arial", 12, "bold"), fg=color, bg="lightgray", selectcolor="lightgray").pack(side="left")

    def submit_choice():
        if selected_color_index.get() == -1:
            messagebox.showwarning("No Selection", "Please select a color before starting the race.")
        else:
            chosen_color = level_colors[selected_color_index.get()]
            color_frame.place_forget()
            setup_turtles(num_turtles)
            display_countdown()
            run_race(level, chosen_color)

    submit_button = Button(color_frame, text="Start Race", command=submit_choice, font=("Arial", 12), bg="green", fg="white")
    submit_button.pack(pady=10)

# End game buttons
def show_end_buttons(score):
    """
    Handles the end of the game, saves the score, and updates the leaderboard.
    """
    # Display the game over message
    game_over_label = Label(root, text=f"Game Over!\nYour final score is: {score}", font=("Arial", 16), fg="black")
    game_over_label.place(relx=0.5, rely=0.4, anchor="center")

    # Save the game session to the database and update the leaderboard
    save_game_session(user_id, username, 1, score)  # Game ID = 1 for Turtle Race
    display_top_scores_table()  # Update the leaderboard immediately

    def retry_game():
        """
        Resets the game state for replay when the retry button is pressed.
        """
        game_over_label.place_forget()
        retry_button.place_forget()
        exit_button.place_forget()
        create_color_selection_frame(level=1)

    # Create Retry button
    retry_button = Button(root, text="Retry", font=("Arial", 14), bg="blue", fg="white", command=retry_game, width=8,
                          height=2)
    retry_button.place(relx=0.40, rely=0.6, anchor="center")

    # Create Exit button
    exit_button = Button(root, text="Exit", font=("Arial", 14), bg="red", fg="white", command=close_race, width=8,
                         height=2)
    exit_button.place(relx=0.60, rely=0.6, anchor="center")


# Run the race function
def run_race(level, user_bet):
    """
    Runs the turtle race for the current level and checks for a winner.
    """
    is_race_on = True
    while is_race_on:
        for turtle in all_turtles:
            if turtle.xcor() > 230:
                is_race_on = False
                winning_color = turtle.pencolor()
                if winning_color == user_bet:
                    messagebox.showinfo("Congratulations!", f"You've won! The {winning_color} turtle is the winner.")
                    create_color_selection_frame(level + 1)  # Progress to the next level
                else:
                    final_score = level
                    show_end_buttons(final_score)  # Trigger game over flow
                return  # Exit the race loop
            dist = random.randint(0, 5)
            turtle.forward(dist)

def display_scoreboard():
    scoreboard_turtle = Turtle()
    scoreboard_turtle.hideturtle()
    scoreboard_turtle.penup()
    scoreboard_turtle.goto(490, 260)  # Adjust position for top-right corner placement
    scoreboard_turtle.color("black")
    scoreboard_turtle.write("Scoreboard", align="center", font=("Arial", 16, "bold"))

# Call the display_scoreboard function right after the screen and UI elements are set up


# Start the game
create_theme_selection_frame()
display_instructions()
# Call this function wherever the leaderboard needs to be displayed
display_top_scores_table()
create_color_selection_frame(level=1)
screen.mainloop()