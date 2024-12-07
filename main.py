import csv
import os
import random
import time
from tkinter import *

import numpy as np
import pandas as pd
import pygame
from matplotlib import pyplot as plt

GAME_WIDTH = 600
GAME_HEIGHT = 600
SPEED = 150
SPACE_SIZE = 30
FOOD_SIZE = 15
BODY_PARTS = 3
HEAD_COLOR = "#00FF00"
BODY_COLOR = "#00FF00"
FOOD_COLOR = "#FF0000"
BACKGROUND_COLOR = "#000000"
GRID_COLOR = "#333333"


class Snake:
    def __init__(self):
        self.body_size = BODY_PARTS
        self.coordinates = []
        self.shapes = []

        for i in range(0, BODY_PARTS):
            self.coordinates.append([0, 0])

        for i, (x, y) in enumerate(self.coordinates):
            if i == 0:
                shape = canvas.create_oval(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=HEAD_COLOR, tag="snake")
            else:
                shape = canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=BODY_COLOR, tag="snake")
            self.shapes.append(shape)


class Food:
    def __init__(self):
        x = random.randint(0, (GAME_WIDTH / SPACE_SIZE) - 1) * SPACE_SIZE
        y = random.randint(0, (GAME_HEIGHT / SPACE_SIZE) - 1) * SPACE_SIZE

        x_centered = x + (SPACE_SIZE / 2) - (FOOD_SIZE / 2)
        y_centered = y + (SPACE_SIZE / 2) - (FOOD_SIZE / 2)

        self.coordinates = [x, y]

        canvas.create_oval(x_centered, y_centered, x_centered + FOOD_SIZE, y_centered + FOOD_SIZE,
                           fill=FOOD_COLOR, tag="food")


def game_start():
    global direction, score, start
    direction = 'down'
    score = 0
    menu_frame.pack_forget()
    label.pack()
    canvas.pack()

    snake = Snake()
    food = Food()
    draw_grid()

    next_turn(snake, food)
    start = time.time()
    snake_song.set_volume(0.2)
    player_name_entry.config(state=DISABLED)


def show_leaderboard():
    leaderboard_window = Toplevel(window)
    leaderboard_window.title("Leaderboard")
    leaderboard_window.geometry("780x350")
    leaderboard_window.resizable(False, False)

    leaderboard_frame = Frame(leaderboard_window, bg=BACKGROUND_COLOR)
    leaderboard_frame.pack(fill=BOTH, expand=True)

    headers = ["Date", "Player Name", "Score", "Food Eaten", "Game Duration", "Grid Size", "Collision", "Rank"]
    for col, header in enumerate(headers):
        Label(leaderboard_frame, text=header, font=("Fixedsys", 12), bg=BACKGROUND_COLOR, fg="white").grid(
            row=0, column=col, padx=5, pady=5
        )

    if os.path.exists('game_data_csv/leaderboard_dense_rank.csv'):
        with open('game_data_csv/leaderboard_dense_rank.csv', 'r') as file:
            reader = csv.reader(file)
            data = list(reader)

        for i, row in enumerate(data[1:11], start=1):
            for col, value in enumerate(row):
                Label(leaderboard_frame, text=value, font=("Fixedsys", 10), bg=BACKGROUND_COLOR, fg="white").grid(
                    row=i, column=col, padx=5, pady=5
                )


def game_quit():
    window.quit()


def draw_grid():
    for x in range(0, GAME_WIDTH, SPACE_SIZE):
        canvas.create_line(x, 0, x, GAME_HEIGHT, fill=GRID_COLOR, tag="grid")

    for y in range(0, GAME_HEIGHT, SPACE_SIZE):
        canvas.create_line(0, y, GAME_WIDTH, y, fill=GRID_COLOR, tag="grid")


def next_turn(snake, food):
    x, y = snake.coordinates[0]

    if direction == "up":
        y -= SPACE_SIZE
    elif direction == "down":
        y += SPACE_SIZE
    elif direction == "left":
        x -= SPACE_SIZE
    elif direction == "right":
        x += SPACE_SIZE

    snake.coordinates.insert(0, (x, y))
    new_head = canvas.create_oval(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=HEAD_COLOR, tag="snake")
    snake.shapes.insert(0, new_head)

    if x == food.coordinates[0] and y == food.coordinates[1]:
        global score

        score += 50
        label.config(text="Score: {}".format(score))
        canvas.delete("food")
        food = Food()
    else:
        del snake.coordinates[-1]
        canvas.delete(snake.shapes[-1])
        del snake.shapes[-1]

    if len(snake.shapes) > 1:
        previous_head = snake.shapes[1]
        px, py = snake.coordinates[1]
        canvas.delete(previous_head)
        body_part = canvas.create_rectangle(px, py, px + SPACE_SIZE, py + SPACE_SIZE, fill=BODY_COLOR, tag="snake")
        snake.shapes[1] = body_part

    if check_collisions(snake):
        snake_game_over_song.play(loops=-1)
        game_over()
    else:
        window.after(SPEED, next_turn, snake, food)


def change_direction(new_direction):
    global direction

    if new_direction == 'left':
        if direction != 'right':
            direction = new_direction
    elif new_direction == 'right':
        if direction != 'left':
            direction = new_direction
    elif new_direction == 'up':
        if direction != 'down':
            direction = new_direction
    elif new_direction == 'down':
        if direction != 'up':
            direction = new_direction


def check_collisions(snake):
    global collision
    x, y = snake.coordinates[0]

    if x < 0 or x >= GAME_WIDTH:
        collision = "Wall"
        snake_song.stop()
        snake_game_over.play()
        return True
    elif y < 0 or y >= GAME_HEIGHT:
        collision = "Wall"
        snake_song.stop()
        snake_game_over.play()
        return True

    for body_part in snake.coordinates[1:]:
        if x == body_part[0] and y == body_part[1]:
            collision = "Self"
            snake_song.stop()
            snake_game_over.play()
            return True

    return False


def add_data():
    global score, collision, start
    end = time.time()
    time_length = end - start
    player_name = player_name_entry.get()
    if player_name == "Enter Player Name":
        player_name = "Anonymous"

    game_data = {
        'Date': [pd.Timestamp("today").strftime('%Y/%m/%d %H:%M:%S')],
        'Player Name': [player_name],
        'Score': [score],
        'Food_Eaten': [score // 50],
        'Game_Duration': [f"{time_length:.1f}s"],
        'Grid_Size': [f'{GAME_WIDTH}x{GAME_HEIGHT}'],
        'Collision': [collision],
    }

    df = pd.DataFrame(game_data)

    if not os.path.exists('game_data_csv/leaderboard.csv'):
        df.to_csv('game_data_csv/leaderboard.csv', index=False, header=True)
    else:
        df.to_csv('game_data_csv/leaderboard.csv', mode='a', header=False, index=False)

    df_rank = pd.read_csv('game_data_csv/leaderboard.csv')
    df_rank['Rank'] = df_rank['Score'].rank(ascending=False, method='dense').astype(int)
    df_rank = df_rank.sort_values(by='Score', ascending=False)

    df_rank.to_csv('game_data_csv/leaderboard_dense_rank.csv', index=False)


def game_over():
    canvas.delete("snake", "food", "grid")
    add_data()

    df_file = pd.DataFrame(pd.read_csv('game_data_csv/leaderboard.csv'))
    score_array = df_file['Score'].values
    high_score = np.max(score_array)
    print(f"Score: {score_array}")
    print(f"High Score: {high_score}")

    canvas.create_text(canvas.winfo_width() / 2, canvas.winfo_height() / 2,
                       font=('Fixedsys', 70), text="GAME OVER", fill="red", tag="gameover")
    canvas.create_text(300, 375,
                       font=('Fixedsys', 20), text=f"HIGH SCORE: {high_score}", fill="red", tag="gameover")

    data = pd.read_csv('game_data_csv/leaderboard.csv')

    player_scores = data.groupby('Player Name')['Score'].sum().sort_values(ascending=False)

    plt.figure(figsize=(12, 6))
    player_scores.plot(kind='bar', color='skyblue')
    plt.title('Player Scores', fontsize=16)
    plt.xlabel('Player Name', fontsize=12)
    plt.ylabel('Total Score', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('game_data_plot/player_scores.png')


window = Tk()
window.title("Pixel Sssnack")
window.resizable(False, False)

score = 0
direction = 'down'
collision = ""

label = Label(window, text="Score: {}".format(score), font=('Fixedsys', 40), fg='black')

canvas = Canvas(window, bg=BACKGROUND_COLOR, height=GAME_HEIGHT, width=670)

menu_image_path = "images/pixel_sssnack_menu_image.png"
menu_background_image = PhotoImage(file=menu_image_path)

menu_frame = Frame(window, bg=BACKGROUND_COLOR, width=GAME_WIDTH, height=670)
menu_frame.pack()

menu_background_label = Label(menu_frame, image=menu_background_image)
menu_background_label.place(relwidth=1, relheight=1)

player_name_entry = Entry(menu_frame, font=("Fixedsys", 24), width=20, bg="#333333", fg="white")
player_name_entry.insert(0, "Enter Player Name")
player_name_entry.place(relx=0.5, rely=0.50, anchor=CENTER)

start_button = Button(menu_frame, text="Start", font=("Fixedsys", 24), command=game_start, width=12, bg="#77C914",
                      fg="white")
start_button.place(relx=0.5, rely=0.60, anchor=CENTER)

leaderboard_button = Button(menu_frame, text="Leaderboard", font=("Fixedsys", 24), command=show_leaderboard, width=12,
                            bg="#FFB200", fg="white")
leaderboard_button.place(relx=0.5, rely=0.70, anchor=CENTER)

quit_button = Button(menu_frame, text="Quit", font=("Fixedsys", 24), command=game_quit, width=12, bg="#FC5658",
                     fg="white")
quit_button.place(relx=0.5, rely=0.80, anchor=CENTER)

pygame.mixer.init()
snake_song = pygame.mixer.Sound("sounds/snake_song.mp3")
snake_game_over = pygame.mixer.Sound("sounds/snake_game_over_sfx.mp3")
snake_food = pygame.mixer.Sound("sounds/snake_food_sfx.mp3")
snake_game_over_song = pygame.mixer.Sound("sounds/snake_game_over_song.mp3")

snake_song.play(loops=-1)

window.update()

window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))

window.geometry(f"{window_width}x{window_height}+{x}+{y}")

window.bind('<Left>', lambda event: change_direction('left'))
window.bind('<Right>', lambda event: change_direction('right'))
window.bind('<Up>', lambda event: change_direction('up'))
window.bind('<Down>', lambda event: change_direction('down'))
window.bind('<a>', lambda event: change_direction('left'))
window.bind('<d>', lambda event: change_direction('right'))
window.bind('<w>', lambda event: change_direction('up'))
window.bind('<s>', lambda event: change_direction('down'))

window.mainloop()
