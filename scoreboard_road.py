from turtle import Turtle

FONT = ("Courier", 24, "normal")
ALIGNMENT = "center"

class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()
        self.level = 1
        self.penup()
        self.hideturtle()
        self.color("black")
        self.goto(-280, 260)
        self.update_score()

    def update_score(self):
        self.clear()
        self.goto(0, 300)
        self.write(f"Level: {self.level}", align=ALIGNMENT, font=FONT)

    def update_level(self):
        self.level += 1
        self.update_score()

    def reset(self):
        self.level = 1
        self.update_score()

    def game_over(self):
        # Display "Game Over" in the center of the screen
        self.goto(0, 0)
        self.write("Game Over!", align=ALIGNMENT, font=("Courier", 36, "bold"))
