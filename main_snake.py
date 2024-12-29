import subprocess
import sys
import time
from turtle import Screen, Turtle
from tkinter import Tk, Label, Button, StringVar, Frame, OptionMenu, Canvas, TclError
from snake import Snake
from scoreboard import Scoreboard
import random
import pymysql
from tkinter import messagebox
from project import update_all_high_scores
import os
from dotenv import find_dotenv, load_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for development and PyInstaller. """
    try:
        base_path = sys._MEIPASS2
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


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


def save_snake_score(user_id, username, score):
    """
    Saves the snake game score to the database.
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

# Screen setup
screen = Screen()
screen.setup(width=800, height=800)
screen.bgcolor("black")
screen.title("Snake Game with Walls")
screen.tracer(0)

# Initialize game objects
snake = None
food = None
scoreboard = Scoreboard()
game_paused = False
game_speed = 100
food_count = 0  # Counter to track eaten food

# List to hold inner walls
inner_walls = []

# Tkinter root window
root = screen._root
if root:
    root.attributes('-fullscreen', True)


# Define available colors and their hex values for preview
available_colors = {
    "red": "#FF0000",
    "blue": "#0000FF",
    "green": "#008000",
    "yellow": "#FFFF00",
    "purple": "#800080",
    "orange": "#FFA500",
    "pink": "#FFC0CB",
    "white": "#FFFFFF"
}

# Wall Turtle for persistent wall drawing
wall_turtle = Turtle()
wall_turtle.hideturtle()

# Function to draw outer wall
def draw_outer_wall():
    wall_color = wall_color_var.get()
    wall_turtle.clear()
    wall_turtle.speed("fastest")
    wall_turtle.color(available_colors[wall_color])
    wall_turtle.penup()
    wall_turtle.goto(-290, 290)
    wall_turtle.pendown()
    wall_turtle.pensize(3)

    for _ in range(4):
        wall_turtle.forward(580)
        wall_turtle.right(90)

# Selection variables for color options
snake_color_var = StringVar(value="red")
food_color_var = StringVar(value="blue")
wall_color_var = StringVar(value="white")

# Color selection frame at the top left with padding
def create_color_selection_controls():
    color_frame = Frame(root, bg="lightgray", padx=10, pady=10)
    color_frame.place(x=60, y=100)

    def create_color_option(label_text, color_var):
        option_frame = Frame(color_frame, bg="lightgray")
        option_frame.pack(anchor="w", pady=5)

        label = Label(option_frame, text=label_text, font=("Arial", 10, "bold"), bg="lightgray")
        label.pack(side="left")

        color_menu = OptionMenu(option_frame, color_var, *available_colors.keys())
        color_menu.config(width=8)
        color_menu.pack(side="left")

        color_preview = Canvas(option_frame, width=20, height=20, bg="lightgray", highlightthickness=0)
        color_preview.pack(side="left", padx=5)

        def update_preview(*args):
            color_preview.create_oval(2, 2, 18, 18, fill=available_colors[color_var.get()])

        color_var.trace("w", update_preview)
        update_preview()

    create_color_option("Snake Color:", snake_color_var)
    create_color_option("Food Color:", food_color_var)
    create_color_option("Wall Color:", wall_color_var)

def display_instructions():
    instructions_turtle = Turtle()
    instructions_turtle.hideturtle()
    instructions_turtle.penup()
    instructions_turtle.color("white")
    instructions_turtle.goto(-580, 0)  # Position on the left side, adjust as needed

    # Write the title with a larger font
    instructions_turtle.write("How to Play", align="left", font=("Arial", 14, "bold"))
    instructions_turtle.sety(instructions_turtle.ycor() - 50)  # Add more spacing after the title

    # Instructions text
    instructions_text = (
        "→ Right Arrow: Move Right\n"
        "← Left Arrow: Move Left\n"
        "↑ Up Arrow: Move Up\n"
        "↓ Down Arrow: Move Down\n\n"
        "1. Eat the food to grow your snake.\n"
        "2. Avoid hitting the walls or your tail.\n"
        "3. Every 2 foods, a new obstacle will appear.\n"
        "4. Press 'Space' to pause/resume the game.\n"
    )

    # Write each line of instructions with smaller font
    for line in instructions_text.split('\n'):
        instructions_turtle.write(line, align="left", font=("Arial", 10, "normal"))
        instructions_turtle.sety(instructions_turtle.ycor() - 20)  # Move down for each line



# Function to prepare the start button and color options

# Function to prepare the start button, color options, and "How to Play" instructions
def setup_full_screen():
    draw_outer_wall()
    create_color_selection_controls()
    display_instructions()

    # Create "Start Game" button
    start_button = Button(root, text="Start Game", font=("Arial", 18), bg="green", fg="white", command=start_game_with_countdown)
    start_button.place(relx=0.5, rely=0.5, anchor="center")

    # Create "Quit Game" button at the top-right corner
    quit_button = Button(root, text="X", font=("Arial", 20), bg="red", fg="white", width=3, command=close_game)
    quit_button.place(relx=0.998, rely=0.005, anchor="ne")  # Position it in the top-right corner


# Function to fetch top 5 scores for Snake Game (without date)
def fetch_top_scores(limit=5):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Fetch top scores from the database without the date
        query = """
        SELECT username, score
        FROM play
        WHERE game_id = 3
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


# Highscore Table Turtle
highscore_table_turtle = Turtle()
highscore_table_turtle.hideturtle()
highscore_table_turtle.penup()

# Call this function wherever the table needs to be updated
display_top_scores_table()


# Function to start game with countdown
def start_game_with_countdown():
    for widget in root.place_slaves():
        if isinstance(widget, Button) and widget.cget("text") == "Start Game":
            widget.place_forget()
    countdown()
    start_game(snake_color_var.get(), food_color_var.get())

# Countdown before game starts
def countdown():
    countdown_turtle = Turtle()
    countdown_turtle.hideturtle()
    countdown_turtle.color("white")
    countdown_turtle.penup()
    countdown_turtle.goto(0, 75)

    for i in range(3, 0, -1):
        try:
            countdown_turtle.clear()  # Clear previous text
            countdown_turtle.write(f"Starts in: {i}", align="center", font=("Arial", 20, "bold"))
            screen.update()
            time.sleep(1)
        except TclError:
            break  # Break out of loop if turtle screen is not available

    countdown_turtle.clear()  # Final clear after countdown
def end_game():
    """
    Handles the end of the game, saving score and game session.
    """
    global game_paused
    game_paused = True
    scoreboard.game_over()

    if user_id and username:
        # Save the game session first
        save_game_session(user_id, username, 3, scoreboard.score)
        # Then update the high score in the users table
        update_user_highscore(user_id)
    else:
        print("User ID or username missing. Game progress will not be saved.")

    show_buttons()


# Food within wall boundaries
class Food(Turtle):
    def __init__(self, food_color="red"):
        super().__init__()
        self.shape("circle")
        self.color(food_color)
        self.penup()
        self.speed("fastest")
        self.refresh()

    def refresh(self):
        x = random.randint(-270, 270)
        y = random.randint(-270, 270)
        self.goto(x, y)

# Function to create an inner wall at a random position within the game area
def create_inner_wall():
    wall_color = wall_color_var.get()
    new_wall = Turtle()
    new_wall.shape("square")
    new_wall.color(available_colors[wall_color])
    new_wall.penup()
    new_wall.shapesize(stretch_wid=1, stretch_len=1)  # Match the snake's size
    # Position the new wall within boundaries
    new_wall.goto(random.randint(-260, 260), random.randint(-260, 260))
    inner_walls.append(new_wall)

# High score display Turtle
highscore_display = Turtle()
highscore_display.hideturtle()
highscore_display.penup()
highscore_display.color("white")
highscore_display.goto(550, 260)

# Function to update the high score display
def update_high_score():
    highscore_display.clear()
    highscore_display.write("Leaderboard", align="right", font=("Arial", 16, "bold"))

# Function to create score display above the game area
score_display = Turtle()
score_display.hideturtle()
score_display.penup()
score_display.color("white")
score_display.goto(0, 320)

# Function to update the current score display
def update_current_score():
    score_display.clear()
    score_display.write(f"Score: {scoreboard.score}", align="center", font=("Arial", 16, "bold"))

# Start game function
def start_game(snake_clr, food_clr):
    global snake, food, food_count
    snake = Snake(snake_color=snake_clr)
    food = Food(food_color=food_clr)
    draw_outer_wall()
    scoreboard.reload_high_score()  # Reload high score from file at start
    update_high_score()  # Show high score initially
    update_current_score()
    screen.listen()
    set_key_bindings()
    run_game()

# Set key bindings
def set_key_bindings():
    screen.onkey(snake.up, "Up")
    screen.onkey(snake.down, "Down")
    screen.onkey(snake.left, "Left")
    screen.onkey(snake.right, "Right")
    screen.onkey(toggle_pause, "space")

# Toggle pause
def toggle_pause():
    global game_paused
    game_paused = not game_paused
    if game_paused:
        show_pause_message()
    else:
        hide_pause_message()
        screen.ontimer(run_game, game_speed)

# Show pause message
pause_message_turtle = Turtle()
pause_message_turtle.hideturtle()

def show_pause_message():
    pause_message_turtle.clear()
    pause_message_turtle.penup()
    pause_message_turtle.goto(0, 0)
    pause_message_turtle.color("white")
    pause_message_turtle.write("Game Paused - Press Space to Resume", align="center", font=("Arial", 16, "bold"))

def hide_pause_message():
    pause_message_turtle.clear()

# Main game loop with ontimer
def run_game():
    global food_count
    if not game_paused:
        screen.update()
        snake.move()

        # Check collision with food
        if snake.head.distance(food) < 15:  # Increased distance to account for visual overlap
            food.refresh()
            snake.extend()
            scoreboard.increase_score()
            update_current_score()

            # Increase food count and add an inner wall if count is a multiple of 2
            food_count += 1
            if food_count % 2 == 0:
                create_inner_wall()

            # Update high score if it was beaten
            if scoreboard.score > scoreboard.high_score:
                scoreboard.high_score = scoreboard.score
                scoreboard.save_high_score()
                update_high_score()

        # Check collision with outer walls
        if abs(snake.head.xcor()) > 280 or abs(snake.head.ycor()) > 280:
            print(f"Collision with outer wall at {snake.head.position()}")
            end_game()
            return

        # Check collision with inner walls
        for wall in inner_walls:
            if snake.head.distance(wall) < 15:  # Adjust distance for visual accuracy
                print(f"Collision with inner wall at {wall.position()}")
                end_game()
                return

        # Check collision with itself
        for segment in snake.segments[1:]:
            if snake.head.distance(segment) < 15:  # Adjust distance for visual accuracy
                print(f"Collision with self at {segment.position()}")
                end_game()
                return

        # Schedule the next frame
        screen.ontimer(run_game, game_speed)
def save_game_session(user_id, username, game_id, score):
    """
    Saves the game session to the play table.
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        query = """
        INSERT INTO play (user_id, username, game_id, score, date)
        VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (user_id, username, game_id, score))
        connection.commit()
        print(f"Game session saved for user ID {user_id} with score {score}.")
    except Exception as e:
        print(f"Error saving game session: {e}")
        messagebox.showerror("Error", f"Failed to save game session: {e}")
    finally:
        cursor.close()
        connection.close()



# End game and show retry/close options
def end_game():
    global game_paused
    game_paused = True
    scoreboard.game_over()

    if user_id and username:
        save_game_session(user_id, username, 3, scoreboard.score)
        update_all_high_scores()  # Update all high scores
    else:
        print("User ID or username missing. Game progress will not be saved.")

    show_buttons()

def update_user_highscore(user_id):
    """
    Updates the user's high score in the `users` table based on the highest score from the `play` table.
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        query_max_score = """
        SELECT MAX(score) FROM play WHERE user_id = %s AND game_id = 3
        """
        cursor.execute(query_max_score, (user_id,))
        max_score = cursor.fetchone()[0]

        if max_score is not None:
            query_update = """
            UPDATE users SET highscore_snake_game = %s WHERE id = %s
            """
            cursor.execute(query_update, (max_score, user_id))
            connection.commit()
            print(f"Updated high score for user ID {user_id} to {max_score}.")
        else:
            print(f"No scores found for user ID {user_id}. No update performed.")
    except Exception as e:
        print(f"Error updating high scores: {e}")  # Log error, do not show a messagebox
    finally:
        cursor.close()
        connection.close()



# Function to show Retry and Exit buttons
def show_buttons():
    retry_button = Button(root, text="Retry", font=("Arial", 14), bg="gray", fg="white", command=retry_game)
    retry_button.place(relx=0.4, rely=0.6, anchor="center", width=100, height=50)
    exit_button = Button(root, text="Exit", font=("Arial", 14), bg="red", fg="white", command=close_game)
    exit_button.place(relx=0.6, rely=0.6, anchor="center", width=100, height=50)


def retry_game():
    """
    Restarts the game without creating additional blank windows.
    """
    close_game()
    if user_id and username:
        subprocess.Popen([sys.executable, resource_path("main_snake.py"), str(user_id), username])
    else:
        subprocess.Popen([sys.executable, resource_path("main_snake.py"), str(user_id), username])

def close_game():
    """
    Properly closes the game without leaving blank windows or errors.
    """
    try:
        if screen:
            screen.bye()  # Close Turtle graphics
        if screen._root:
            screen._root.destroy()  # Destroy the Tk root window
    except TclError:
        pass


# Initial setup for full screen with Start Game button and color selection
if __name__ == "__main__":
    setup_full_screen()
    screen.mainloop()

