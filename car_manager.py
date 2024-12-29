# car_manager.py

from turtle import Turtle
import random

COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]
STARTING_MOVE_DISTANCE = 5
MOVE_INCREMENT = 2

class CarManager:
    def __init__(self):
        self.list_cars = []
        self.car_speed = STARTING_MOVE_DISTANCE

    def create_car(self):
        # Only create a new car randomly, ensuring it doesn't spawn too frequently
        if random.randint(1, 6) == 1:
            new_car = Turtle("square")
            new_car.shapesize(stretch_wid=1, stretch_len=2)
            new_car.penup()
            new_car.color(random.choice(COLORS))

            # Ensure the car spawns just outside the right edge of the screen
            new_car.goto(280, random.randint(-250, 250))
            self.list_cars.append(new_car)

    def move(self):
        # Move each car and remove any that go off-screen
        for car in self.list_cars:
            car.backward(self.car_speed)
            if car.xcor() < -250:  # Remove cars once they go off-screen to the left
                car.hideturtle()
                self.list_cars.remove(car)

    def increase_speed(self):
        # Increase the speed when level advances
        self.car_speed += MOVE_INCREMENT
