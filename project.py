from tkinter import *
import tkinter as tk
from tkinter import messagebox  # Import messagebox for pop-up
import subprocess
import os
import pymysql
import sys
import smtplib
from email.mime.text import MIMEText
import random  # For generating the verification code

from dotenv import find_dotenv, load_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

logged_in_user_id = None
logged_in_username = None


def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        passwd=os.getenv("passwd"),
        database=os.getenv("database")
    )

# Define colors and dimensions for the menu bar
MENU_BAR_COLOR = '#383838'
MENU_BAR_COLLAPSED_WIDTH = 50
MENU_BAR_EXPANDED_WIDTH = 200

def initialize_gui():
    root = tk.Tk()
    root.geometry('800x680')
    root.title("Games Zone")
    return root

root = initialize_gui()

def generate_verification_code():
    """
    Generates a 6-character alphanumeric code.
    """
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=6))

def send_verification_code(email, code):
    """
    Sends the verification code to the user's email address.
    """
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "sandruluca04@gmail.com"  # Your Gmail address
    sender_password = os.getenv("sender_password")  # Your Gmail App Password

    subject = "Games Zone Signup Verification Code"
    body = f"""
    <html>
    <body>
        <p>Dear user,</p>
        <p>Thank you for signing up for Games Zone!</p>
        <p>Here is your verification code:</p>
        <p style="font-size: 20px; font-weight: bold; color: green;">{code}</p>
        <p>Please enter this code to complete your signup.</p>
        <p>Best regards,<br>Games Zone Team</p>
    </body>
    </html>
    """

    try:
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = email

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())

        messagebox.showinfo("Verification Code Sent", "A verification code has been sent to your email.")
    except smtplib.SMTPAuthenticationError:
        messagebox.showerror("Authentication Error",
                             "Unable to authenticate with the email server. Check sender credentials.")
    except smtplib.SMTPException as e:
        messagebox.showerror("SMTP Error", f"Failed to send email: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")


# Load icons for menu buttons
toggle_icon = tk.PhotoImage(file= resource_path("images\\toggle_btn_icon.png"))
home_icon = tk.PhotoImage(file=resource_path("images\\home_icon.png"))
turtle_race_icon = tk.PhotoImage(file=resource_path("images\\turtle_race.png"))
turtle_road_icon = tk.PhotoImage(file=resource_path("images\\turle_road.png"))
snake_icon = tk.PhotoImage(file=resource_path("images\\snake.png"))
close_icon = tk.PhotoImage(file=resource_path("images\\close_btn_icon.png"))

# Frame for the menu bar
menu_bar_frame = tk.Frame(root, bg=MENU_BAR_COLOR, width=MENU_BAR_COLLAPSED_WIDTH, height=680)
menu_bar_frame.pack_propagate(False)  # Prevent frame from resizing with widgets
menu_bar_frame.pack(side=tk.LEFT, fill=tk.Y)

# Frame for main content (page frame)
page_frame = tk.Frame(root, bg="white")
page_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


def send_password_email(email, password):
    """
    Sends the password to the user's email address with enhanced formatting.
    """
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "sandruluca04@gmail.com"  # Your Gmail address
    sender_password = "fhra qecn wrld cdxu"  # Your Gmail App Password

    subject = "Your Games Zone Password"
    # Using HTML to format the email
    body = f"""
    <html>
    <body>
        <p>Dear user,</p>
        <p>As per your request, here is the password for your Games Zone account:</p>
        <p style="font-size: 20px; font-weight: bold; color: blue;">{password}</p>
        <p>Please keep this information secure.</p>
        <p>Best regards,<br>Games Zone Team</p>
    </body>
    </html>
    """

    try:
        # Creating a MIMEText object with HTML content
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = email

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())

        messagebox.showinfo("Success", "Your password has been sent to your email address.")
    except smtplib.SMTPAuthenticationError:
        messagebox.showerror("Authentication Error", "Unable to authenticate with the email server. Check sender credentials.")
    except smtplib.SMTPException as e:
        messagebox.showerror("SMTP Error", f"Failed to send email: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")



def forgot_password_form():
    """
    Displays the forgot password form.
    """
    clear_forms()

    forgot_password_frame = tk.Frame(page_frame, bg="white")
    forgot_password_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=(30, 50))

    tk.Label(forgot_password_frame, text="Forgot Password", font=("Arial", 24), bg="white").pack(pady=10)

    tk.Label(forgot_password_frame, text="Enter your email address:", bg="white").pack(anchor="w")
    email_entry = tk.Entry(forgot_password_frame, width=40)
    email_entry.pack(fill=tk.X, pady=5)

    def send_password():
        email = email_entry.get().strip()
        if not email:
            messagebox.showerror("Error", "Please enter your email address.")
            return

        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            # Check if the email exists in the database and fetch the password
            cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()

            if result:
                password = result[0]
                send_password_email(email, password)  # Send the password via email
                forgot_password_frame.destroy()
                show_login_form()  # Return to the login form
            else:
                messagebox.showerror("Error", "No account found for the entered email address.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            cursor.close()
            connection.close()

    # Buttons for sending email and going back
    button_frame = tk.Frame(forgot_password_frame, bg="white")
    button_frame.pack(pady=20)

    send_button = tk.Button(button_frame, text="Send Password", command=send_password, bg="blue", fg="white", width=15)
    back_button = tk.Button(button_frame, text="Back",
                            command=lambda: [forgot_password_frame.destroy(), show_login_form()],
                            bg="gray", fg="white", width=15)

    send_button.pack(side="left", padx=10)
    back_button.pack(side="right", padx=10)

def show_verification_form(username, email, password):
    """
    Shows the verification form for entering the code sent via email.
    """
    clear_forms()
    verification_code = generate_verification_code()
    send_verification_code(email, verification_code)

    verification_frame = tk.Frame(page_frame, bg="white")
    verification_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=(30, 50))

    tk.Label(verification_frame, text="Enter Verification Code", font=("Arial", 24), bg="white").pack(pady=10)

    tk.Label(verification_frame, text="Code sent to your email:", bg="white").pack(anchor="w")
    code_entry = tk.Entry(verification_frame, width=40)
    code_entry.pack(fill=tk.X, pady=5)

    def verify_code():
        code_entered = code_entry.get().strip()
        if code_entered != verification_code:
            messagebox.showerror("Invalid Code", "The code you entered is incorrect.")
            verification_frame.destroy()
            show_signup_form()
        else:
            # Create the account in the database
            connection = get_db_connection()
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, password)
                )
                connection.commit()
                messagebox.showinfo("Signup Successful", "Your account has been created successfully!")
                verification_frame.destroy()
                show_login_form()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create account: {e}")
                show_signup_form()
            finally:
                cursor.close()
                connection.close()

    button_frame = tk.Frame(verification_frame, bg="white")
    button_frame.pack(pady=20)

    verify_button = tk.Button(button_frame, text="Verify Code", command=verify_code, bg="green", fg="white", width=15)
    back_button = tk.Button(button_frame, text="Back to Signup",
                            command=lambda: [verification_frame.destroy(), show_signup_form()],
                            bg="gray", fg="white", width=15)

    verify_button.pack(side="left", padx=10)
    back_button.pack(side="right", padx=10)

def show_login_form():
    global login_frame
    clear_forms()
    login_frame = tk.Frame(page_frame, bg="white")
    login_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=(30, 50))

    # Grid layout to centralize the form
    login_frame.grid_columnconfigure(0, weight=1)
    login_frame.grid_columnconfigure(1, weight=0)
    login_frame.grid_columnconfigure(2, weight=1)

    # Title label on the right of the entry fields
    title_label = tk.Label(login_frame, text="Login", font=("Arial", 20), bg="white")
    title_label.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="w")

    # Username and password labels and entry fields
    tk.Label(login_frame, text="Username", bg="white").grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(5, 0))
    username_entry = tk.Entry(login_frame, width=20)
    username_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

    tk.Label(login_frame, text="Password", bg="white").grid(row=3, column=1, sticky="w", padx=(0, 10), pady=(5, 0))
    password_entry = tk.Entry(login_frame, show="*", width=20)
    password_entry.grid(row=4, column=1, sticky="ew", padx=10, pady=5)

    def submit_login():
        username = username_entry.get()
        password = password_entry.get()
        login_user(username, password)

    # Buttons aligned
    button_frame = tk.Frame(login_frame, bg="white")
    button_frame.grid(row=5, column=1, pady=10, sticky="e")

    login_button = tk.Button(button_frame, text="Login", command=submit_login, bg="blue", fg="white", width=10)
    back_button = tk.Button(button_frame, text="Back", command=lambda: [clear_main_content(), load_home_page()],
                            bg="gray", fg="white", width=10)
    forgot_button = tk.Button(button_frame, text="Forgot Password?", command=lambda: [login_frame.destroy(), forgot_password_form()],
                               bg="orange", fg="white", width=15)

    login_button.pack(side="left", padx=5, ipadx=5)
    forgot_button.pack(side="left", padx=5, ipadx=5)
    back_button.pack(side="right", padx=5, ipadx=5)


def update_all_high_scores():
    """
    Updates the high scores for all games for all users in the `users` table
    based on the `play` table.
    """
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Query to get the maximum score per user and game
        query = """
        SELECT user_id, game_id, MAX(score) AS max_score
        FROM play
        GROUP BY user_id, game_id;
        """
        cursor.execute(query)
        scores = cursor.fetchall()

        # Update the high scores for each game in the `users` table
        for user_id, game_id, max_score in scores:
            if game_id == 3:  # Snake Game
                update_query = "UPDATE users SET highscore_snake_game = %s WHERE id = %s"
                cursor.execute(update_query, (max_score, user_id))
            elif game_id == 1:  # Turtle Road Game
                update_query = "UPDATE users SET highscore_road_game = %s WHERE id = %s"
                cursor.execute(update_query, (max_score, user_id))
            elif game_id == 2:  # Turtle Race Game
                update_query = "UPDATE users SET highscore_race_game = %s WHERE id = %s"
                cursor.execute(update_query, (max_score, user_id))

        connection.commit()
        print("High scores updated successfully for all users.")
    except Exception as e:
        print(f"Error updating high scores: {e}")
        messagebox.showerror("Error", f"Failed to update high scores: {e}")
    finally:
        cursor.close()
        connection.close()



def show_signup_form():
    """
    Displays the signup form with validations.
    """
    global signup_frame
    clear_forms()
    signup_frame = tk.Frame(page_frame, bg="white")
    signup_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=(30, 50))

    signup_frame.grid_columnconfigure(0, weight=1)
    signup_frame.grid_columnconfigure(1, weight=0)
    signup_frame.grid_columnconfigure(2, weight=1)

    title_label = tk.Label(signup_frame, text="Signup", font=("Arial", 20), bg="white")
    title_label.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="w")

    tk.Label(signup_frame, text="Username", bg="white").grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(5, 0))
    username_entry = tk.Entry(signup_frame, width=20)
    username_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

    tk.Label(signup_frame, text="Email", bg="white").grid(row=3, column=1, sticky="w", padx=(0, 10), pady=(5, 0))
    email_entry = tk.Entry(signup_frame, width=20)
    email_entry.grid(row=4, column=1, sticky="ew", padx=10, pady=5)

    tk.Label(signup_frame, text="Password", bg="white").grid(row=5, column=1, sticky="w", padx=(0, 10), pady=(5, 0))
    password_entry = tk.Entry(signup_frame, show="*", width=20)
    password_entry.grid(row=6, column=1, sticky="ew", padx=10, pady=5)

    def submit_signup():
        username = username_entry.get().strip()
        email = email_entry.get().strip()
        password = password_entry.get().strip()

        if validate_signup_form(username, email, password):
            signup_frame.destroy()
            show_verification_form(username, email, password)

    button_frame = tk.Frame(signup_frame, bg="white")
    button_frame.grid(row=7, column=1, pady=10, sticky="e")

    signup_button = tk.Button(button_frame, text="Signup", command=submit_signup, bg="green", fg="white", width=10)
    back_button = tk.Button(button_frame, text="Back", command=lambda: [clear_main_content(), load_home_page()],
                            bg="gray", fg="white", width=10)

    signup_button.pack(side="left", padx=5, ipadx=5)
    back_button.pack(side="right", padx=5, ipadx=5)




def save_snake_score(user_id, username, score):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Save the play session
        cursor.execute("SELECT game_id FROM games WHERE game_name = 'Snake Game'")
        snake_game_id = cursor.fetchone()[0]

        query = "INSERT INTO play (user_id, username, game_id) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_id, username, snake_game_id))

        # Update the user's high score if the new score is higher
        cursor.execute("SELECT highscore_snake_game FROM users WHERE id = %s", (user_id,))
        current_highscore = cursor.fetchone()[0]
        if score > current_highscore:
            cursor.execute("UPDATE users SET highscore_snake_game = %s WHERE id = %s", (score, user_id))

        connection.commit()
        messagebox.showinfo("Score Saved", f"Your score of {score} has been saved!")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving score: {e}")
    finally:
        cursor.close()
        connection.close()

def validate_signup_form(username, email, password):
    """
    Validates the signup form inputs.
    """
    if " " in username:
        messagebox.showerror("Invalid Username", "Username must not contain spaces.")
        return False
    if not email.endswith("@gmail.com"):
        messagebox.showerror("Invalid Email", "Email must end with '@gmail.com'.")
        return False
    if len(password) < 4:
        messagebox.showerror("Invalid Password", "Password must be at least 4 characters long.")
        return False
    return True


def get_high_scores(limit=10):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Retrieve top scores with username and date
        query = """
        SELECT username, score, DATE_FORMAT(date, '%Y-%m-%d %H:%i:%s') AS formatted_date
        FROM snake_game_scores
        ORDER BY score DESC
        LIMIT %s
        """
        cursor.execute(query, (limit,))
        scores = cursor.fetchall()
        return scores
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve scores: {e}")
        return []
    finally:
        cursor.close()
        connection.close()



def toggle_login_form():
    clear_forms()
    show_login_form()

def toggle_signup_form():
    clear_forms()
    show_signup_form()

def clear_forms():
    if 'login_frame' in globals():
        login_frame.destroy()
    if 'signup_frame' in globals():
        signup_frame.destroy()

# Login functionality
def login_user(username, password):
    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Check if username and password are correct
        cursor.execute("SELECT id, username FROM users WHERE username = %s AND password = %s", (username, password))
        result = cursor.fetchone()
        if result:
            global logged_in_user_id, logged_in_username
            logged_in_user_id = result[0]  # Assuming the ID is the first column in the result
            logged_in_username = result[1]  # Assuming the username is the second column in the result
            messagebox.showinfo("Login Successful", f"Welcome back, {username}!")
        else:
            logged_in_user_id = None
            logged_in_username = None
            messagebox.showerror("Login Failed", "Incorrect username or password.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        connection.close()



def show_login():
    clear_main_content()
    login_frame = tk.Frame(page_frame, bg="white")
    login_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)

    tk.Label(login_frame, text="Login", font=("Arial", 24), bg="white").pack(pady=10)

    tk.Label(login_frame, text="Username", bg="white").pack(anchor="w")
    username_entry = tk.Entry(login_frame)
    username_entry.pack(fill=tk.X, pady=5)

    tk.Label(login_frame, text="Password", bg="white").pack(anchor="w")
    password_entry = tk.Entry(login_frame, show="*")
    password_entry.pack(fill=tk.X, pady=5)

    def submit_login():
        username = username_entry.get()
        password = password_entry.get()
        login_user(username, password)

    tk.Button(login_frame, text="Login", command=submit_login, bg="blue", fg="white").pack(pady=20)
    tk.Button(login_frame, text="Back", command=load_home_page).pack(pady=10)

# Signup functionality
def signup_user(username, email, password):
    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            messagebox.showerror("Signup Failed", "Username already exists. Please choose another one.")
            return

        # Insert the new user into the database
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password)
        )
        connection.commit()
        messagebox.showinfo("Signup Successful", f"Account created for {username}!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        connection.close()


def show_signup():
    clear_main_content()
    signup_frame = tk.Frame(page_frame, bg="white")
    signup_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)

    tk.Label(signup_frame, text="Signup", font=("Arial", 24), bg="white").pack(pady=10)

    tk.Label(signup_frame, text="Username", bg="white").pack(anchor="w")
    username_entry = tk.Entry(signup_frame)
    username_entry.pack(fill=tk.X, pady=5)

    tk.Label(signup_frame, text="Email", bg="white").pack(anchor="w")
    email_entry = tk.Entry(signup_frame)
    email_entry.pack(fill=tk.X, pady=5)

    tk.Label(signup_frame, text="Password", bg="white").pack(anchor="w")
    password_entry = tk.Entry(signup_frame, show="*")
    password_entry.pack(fill=tk.X, pady=5)

    def submit_signup():
        username = username_entry.get()
        email = email_entry.get()
        password = password_entry.get()
        signup_user(username, email, password)

    tk.Button(signup_frame, text="Signup", command=submit_signup, bg="green", fg="white").pack(pady=20)
    tk.Button(signup_frame, text="Back", command=load_home_page).pack(pady=10)

# Functions for expanding and collapsing the menu bar with labels
def switch_indicator(indicator_lb, page_func):
    home_button_indicator.config(bg=MENU_BAR_COLOR)
    turtle_race_indicator.config(bg=MENU_BAR_COLOR)
    turtle_road_indicator.config(bg=MENU_BAR_COLOR)
    snake_indicator.config(bg=MENU_BAR_COLOR)
    indicator_lb.config(bg='white')

    # Clear main content and load new page
    clear_main_content()
    page_func()

    # Collapse menu bar if expanded
    if menu_bar_frame.winfo_width() > MENU_BAR_COLLAPSED_WIDTH:
        fold_menu_bar()


def extended_animation():
    current_width = menu_bar_frame.winfo_width()
    if current_width < MENU_BAR_EXPANDED_WIDTH:
        current_width += 10
        menu_bar_frame.config(width=current_width)
        root.after(ms=8, func=extended_animation)
    else:
        # Show labels when fully expanded
        home_label.place(x=50, y=210)
        turtle_race_label.place(x=50, y=280)
        turtle_road_label.place(x=50, y=340)
        snake_label.place(x=50, y=410)

def folding_animation():
    current_width = menu_bar_frame.winfo_width()
    if current_width > MENU_BAR_COLLAPSED_WIDTH:
        current_width -= 10
        menu_bar_frame.config(width=current_width)
        root.after(ms=8, func=folding_animation)
    else:
        # Hide labels when fully collapsed
        home_label.place_forget()
        turtle_race_label.place_forget()
        turtle_road_label.place_forget()
        snake_label.place_forget()

def extend_menu_bar():
    extended_animation()
    toggle_button.config(image=close_icon)
    toggle_button.config(command=fold_menu_bar)

def fold_menu_bar():
    folding_animation()
    toggle_button.config(image=toggle_icon)
    toggle_button.config(command=extend_menu_bar)

def clear_main_content():
    """Clears all canvas elements except the menu bar."""
    for widget in page_frame.winfo_children():
        widget.destroy()


# Page-specific functions
def load_home_page():
    home_frame = tk.Frame(page_frame, bg="white", width=740, height=730)
    home_frame.pack(fill=tk.BOTH, expand=True)

    home_label = tk.Label(home_frame, text="Welcome to Games Zone Home!", font=("Arial", 24), bg="white")
    home_label.pack(pady=70)  # Reduced padding for the label to move it up

    # Create a frame for the buttons to align them side-by-side
    button_frame = tk.Frame(home_frame, bg="white")
    button_frame.pack(pady=(0, 30))

    # Adjust padding to move buttons up and place them inside button_frame
    login_button = tk.Button(button_frame, text="Login", font=("Arial", 14), command=show_login_form, bg="blue", fg="white")
    signup_button = tk.Button(button_frame, text="Signup", font=("Arial", 14), command=show_signup_form, bg="green", fg="white")

    login_button.grid(row=0, column=0, padx=20, ipadx=50, ipady=5)
    signup_button.grid(row=0, column=1, padx=20, ipadx=50, ipady=5)



def load_turtle_race():
    turtle_race_frame = tk.Frame(page_frame, bg="lightblue", width=740, height=730)
    turtle_race_frame.pack(fill=tk.BOTH, expand=True)

    # Title Label
    title_label = tk.Label(turtle_race_frame, text="Welcome to Turtle Race Game!", font=("Arial", 24),
                           bg="lightblue", fg="green")
    title_label.pack(pady=100)

    # Button frame
    button_frame = tk.Frame(turtle_race_frame, bg="lightblue")
    button_frame.pack(pady=20)

    # Turtle Race Description
    description_text = (
        "Join the excitement of the Turtle Race! Pick a turtle, set the scene with a background theme, "
        "and watch them race to the finish line. Will your chosen turtle win? "
        "Guess correctly to progress to the next level – but be prepared, each race is a new adventure!"
    )

    # Description Button
    instructions_button = tk.Button(button_frame, text="Description", font=("Arial", 14),
                                    command=lambda: messagebox.showinfo("Turtle Race Game", description_text))

    # Play Game Button
    def play_turtle_race_game():
        # Ensure logged_in_user_id exists
        if logged_in_user_id is not None and logged_in_username is not None:
            subprocess.Popen([sys.executable, resource_path("turtle_race.py"), str(logged_in_user_id), logged_in_username])
        else:
            messagebox.showerror("Error", "No user is logged in. Please log in first.")

    # Button to start the turtle_race game script
    play_button = tk.Button(button_frame, text="Play Game", font=("Arial", 14), command=play_turtle_race_game)

    # Main Menu Button
    main_menu_button = tk.Button(button_frame, text="Main Menu", font=("Arial", 14),
                                 command=lambda: switch_indicator(home_button_indicator, load_home_page))

    # Pack buttons with padding
    instructions_button.pack(pady=10, ipadx=75, ipady=5, fill=tk.X, expand=True)
    play_button.pack(pady=10, ipadx=10, ipady=5, fill=tk.X, expand=True)
    main_menu_button.pack(pady=10, ipadx=10, ipady=5, fill=tk.X, expand=True)




def load_turtle_road():
    turtle_road_frame = tk.Frame(page_frame, bg="lightgreen", width=740, height=730)
    turtle_road_frame.pack(fill=tk.BOTH, expand=True)

    title_label = tk.Label(turtle_road_frame, text="Welcome to Turtle Road Game!", font=("Arial", 24),
                           bg="lightgreen", fg="green")
    title_label.pack(pady=100)

    # Button frame
    button_frame = tk.Frame(turtle_road_frame, bg="lightgreen")
    button_frame.pack(pady=20)

    description_text = (
        "Navigate the turtle across the road while avoiding moving cars! "
        "Reach the finish line to advance levels, but watch out – the cars get faster as you progress."
    )

    description_button = tk.Button(button_frame, text="Description", font=("Arial", 14),
                                   command=lambda: messagebox.showinfo("Turtle Road Game", description_text))
    def play_turtle_road_game():
        # Ensure logged_in_user_id exists
        if logged_in_user_id is not None and logged_in_username is not None:
            subprocess.Popen([sys.executable, resource_path("turtle_road.py"), str(logged_in_user_id), logged_in_username])
        else:
            messagebox.showerror("Error", "No user is logged in. Please log in first.")

    # Button to start the turtle_road game script
    play_button = tk.Button(button_frame, text="Play Game", font=("Arial", 14), command=play_turtle_road_game)

    main_menu_button = tk.Button(button_frame, text="Main Menu", font=("Arial", 14),
                                 command=lambda: switch_indicator(home_button_indicator, load_home_page))

    # Pack buttons vertically
    description_button.pack(pady=10, ipadx=75, ipady=5, fill=tk.X, expand=True)
    play_button.pack(pady=10, ipadx=10, ipady=5, fill=tk.X, expand=True)
    main_menu_button.pack(pady=10, ipadx=10, ipady=5, fill=tk.X, expand=True)

# Add button and label for Turtle Road in the side menu bar
turtle_road_button = tk.Button(menu_bar_frame, image=turtle_road_icon,
                               bg=MENU_BAR_COLOR, bd=0, activebackground=MENU_BAR_COLOR,
                               command=lambda: switch_indicator(turtle_road_indicator, load_turtle_road))
turtle_road_button.place(x=11, y=340, width=30, height=40)
turtle_road_indicator = tk.Label(menu_bar_frame, bg=MENU_BAR_COLOR)
turtle_road_indicator.place(x=3, y=340, height=35, width=3)
turtle_road_label = tk.Label(menu_bar_frame, text="Turtle Road", bg=MENU_BAR_COLOR, fg="white", font=("Arial", 15),
                             anchor=tk.W)
turtle_road_label.bind("<Button-1>", lambda e: switch_indicator(turtle_road_indicator, load_turtle_road))


def load_snake_page():
    snake_frame = tk.Frame(page_frame, bg="black", width=740, height=730)
    snake_frame.pack(fill=tk.BOTH, expand=True)

    # Title Label
    title_label = tk.Label(snake_frame, text="Welcome to Snake Game!", font=("Arial", 24), bg="black", fg="green")
    title_label.pack(pady=100)

    # Button frame
    button_frame = tk.Frame(snake_frame, bg="black")
    button_frame.pack(pady=20)

    description_text = (
        "Embark on a journey with a tiny, hungry snake who’s always on the lookout for tasty treats!"
        " Guide your slithery friend to food, watch it grow longer, and see if you can dodge walls and obstacles."
        " Just remember – stay nimble and avoid becoming your own lunch!"
    )

    description_button = tk.Button(button_frame, text="Description", font=("Arial", 14),
                                   command=lambda: messagebox.showinfo("The Hungry Snake Adventure", description_text))

    def play_snake_game():
        # Ensure logged_in_user_id exists
        if logged_in_user_id is not None and logged_in_username is not None:
            subprocess.Popen([sys.executable, resource_path("main_snake.py"), str(logged_in_user_id), logged_in_username])
        else:
            messagebox.showerror("Error", "No user is logged in. Please log in first.")

    play_button = tk.Button(button_frame, text="Play Game", font=("Arial", 14), command=play_snake_game)

    main_menu_button = tk.Button(button_frame, text="Main Menu", font=("Arial", 14),
                                 command=lambda: switch_indicator(home_button_indicator, load_home_page))

    description_button.pack(pady=10, ipadx=75, ipady=5, fill=tk.X, expand=True)
    play_button.pack(pady=10, ipadx=10, ipady=5, fill=tk.X, expand=True)
    main_menu_button.pack(pady=10, ipadx=10, ipady=5, fill=tk.X, expand=True)



toggle_button = tk.Button(menu_bar_frame, image=toggle_icon,
                          bg=MENU_BAR_COLOR, bd=0, activebackground=MENU_BAR_COLOR, command=extend_menu_bar)
toggle_button.place(x=4, y=10)

home_button = tk.Button(menu_bar_frame, image=home_icon,
                        bg=MENU_BAR_COLOR, bd=0, activebackground=MENU_BAR_COLOR,
                        command=lambda: switch_indicator(home_button_indicator, load_home_page))
home_button.place(x=9, y=210, width=30, height=40)
home_button_indicator = tk.Label(menu_bar_frame, bg='white')
home_button_indicator.place(x=3, y=210, height=35, width=3)
home_label = tk.Label(menu_bar_frame, text="Home", bg=MENU_BAR_COLOR, fg="white", font=("Arial", 15), anchor=tk.W)
home_label.bind("<Button-1>", lambda e: switch_indicator(home_button_indicator, load_home_page))

turtle_race_button = tk.Button(menu_bar_frame, image=turtle_race_icon,
                               bg=MENU_BAR_COLOR, bd=0, activebackground=MENU_BAR_COLOR,
                               command=lambda: switch_indicator(turtle_race_indicator, load_turtle_race))
turtle_race_button.place(x=11, y=280, width=30, height=40)
turtle_race_indicator = tk.Label(menu_bar_frame, bg=MENU_BAR_COLOR)
turtle_race_indicator.place(x=3, y=280, height=35, width=3)
turtle_race_label = tk.Label(menu_bar_frame, text="Turtle Race", bg=MENU_BAR_COLOR, fg="white", font=("Arial", 15),
                             anchor=tk.W)
turtle_race_label.bind("<Button-1>", lambda e: switch_indicator(turtle_race_indicator, load_turtle_race))

turtle_road_button = tk.Button(menu_bar_frame, image=turtle_road_icon,
                               bg=MENU_BAR_COLOR, bd=0, activebackground=MENU_BAR_COLOR,
                               command=lambda: switch_indicator(turtle_road_indicator, load_turtle_road))
turtle_road_button.place(x=11, y=340, width=30, height=40)
turtle_road_indicator = tk.Label(menu_bar_frame, bg=MENU_BAR_COLOR)
turtle_road_indicator.place(x=3, y=340, height=35, width=3)
turtle_road_label = tk.Label(menu_bar_frame, text="Crossy Turtle", bg=MENU_BAR_COLOR, fg="white", font=("Arial", 15),
                             anchor=tk.W)
turtle_road_label.bind("<Button-1>", lambda e: switch_indicator(turtle_road_indicator, load_turtle_road))

snake_button = tk.Button(menu_bar_frame, image=snake_icon,
                         bg=MENU_BAR_COLOR, bd=0, activebackground=MENU_BAR_COLOR,
                         command=lambda: switch_indicator(snake_indicator, load_snake_page))
snake_button.place(x=11, y=410, width=30, height=40)
snake_indicator = tk.Label(menu_bar_frame, bg=MENU_BAR_COLOR)
snake_indicator.place(x=3, y=410, height=35, width=3)
snake_label = tk.Label(menu_bar_frame, text="Snake Game", bg=MENU_BAR_COLOR, fg="white", font=("Arial", 15),
                       anchor=tk.W)
snake_label.bind("<Button-1>", lambda e: switch_indicator(snake_indicator, load_snake_page))


if __name__ == "__main__":
    load_home_page()
    root.mainloop()
