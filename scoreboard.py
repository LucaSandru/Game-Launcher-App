from turtle import Turtle

ALIGNMENT = "center"
FONT = ('Courier', 24, 'normal')


class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.high_score = self.load_high_score()  # Load high score from file on initialization

        self.color("white")
        self.penup()
        self.goto(0, 260)  # Position to display at the top center
        self.hideturtle()
        self.update_scoreboard()

    def load_high_score(self):
        """Loads the high score from 'highscore.txt' or initializes to 0 if not found."""
        try:
            with open("highscore.txt", 'r') as file:
                return int(file.read())
        except (FileNotFoundError, ValueError):
            return 0  # Default to 0 if file is missing or corrupted

    def save_high_score(self):
        """Saves the current high score to 'highscore.txt'."""
        with open("highscore.txt", 'w') as file:
            file.write(str(self.high_score))

    def update_scoreboard(self):
        """Clears the screen and displays the current score and high score."""
        self.clear()  # Clear previous score display to avoid overlaps

    def increase_score(self):
        """Increases the score by 1 and updates the scoreboard. Saves the new high score if achieved."""
        self.score += 1
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()  # Save new high score immediately
        self.update_scoreboard()

    def reset(self):
        """Resets the current score without affecting the high score."""
        self.score = 0
        self.update_scoreboard()

    def game_over(self):
        """Displays 'Game Over' message in the center of the screen."""
        self.goto(0, 0)
        self.write("GAME OVER", align=ALIGNMENT, font=('Arial', 24, 'normal'))

    def reload_high_score(self):
        """Reloads the high score from 'highscore.txt' and updates the scoreboard display."""
        self.high_score = self.load_high_score()
        self.update_scoreboard()  # Update the scoreboard display to show the latest high score
