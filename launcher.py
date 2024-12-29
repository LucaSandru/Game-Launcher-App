import subprocess
import time

def start_game():
    # Wait briefly to ensure the previous instance fully closes
    time.sleep(0.5)
    # Start a new instance of main_snake.py
    subprocess.Popen(["python", "main_snake.py"])

if __name__ == "__main__":
    start_game()
