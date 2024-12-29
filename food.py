# food.py
from turtle import Turtle
import random

class Food(Turtle):
    def __init__(self, food_color="red"):  # Default color as red
        super().__init__()
        self.shape("circle")
        self.color(food_color)  # Set food color
        self.penup()
        self.shapesize(0.5, 0.5)
        self.speed("fastest")
        self.refresh()

    def refresh(self):
        random_x = random.randint(-280, 280)
        random_y = random.randint(-280, 280)
        self.goto(random_x, random_y)
