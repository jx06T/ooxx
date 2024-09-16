import curses
from curses import wrapper
import random
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import model_from_json
import time

def draw_board(stdscr, board):
    for i in range(3):
        for j in range(3):
            y = 2 + i * 2
            x = 4 + j * 4
            stdscr.addstr(y, x, board[i*3 + j])
    
    # Draw grid
    for i in range(1, 3):
        stdscr.addstr(2, 4+i*4-1, "|")
        stdscr.addstr(4, 4+i*4-1, "|")
        stdscr.addstr(6, 4+i*4-1, "|")
    for i in range(1, 3):
        stdscr.addstr(1+i*2, 4, "-"*11)

def check_win(board):
    # Check rows, columns and diagonals
    win_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]  # Diagonals
    ]

    for combo in win_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != " ":
            return True
    return False

@tf.function
def predict_move2(state):
    return model(state, training=False)

def get_computer_move(board):
    state = [-1 if cell == " O" else 1 if cell == " X" else 0 for cell in board]
    action_probs = predict_move2(tf.convert_to_tensor([state], dtype=tf.float32))[0].numpy()
    valid_actions = [i for i in range(9) if state[i] == 0]
    return max(valid_actions, key=lambda x: action_probs[x])

# def get_computer_move(board):
#     empty_cells = [i for i, cell in enumerate(board) if cell == " "]
#     if not empty_cells:
#         return None 
#     return random.choice(empty_cells)

def select_game_mode(stdscr):
    stdscr.clear()
    stdscr.addstr(0, 4, "Select game mode:")
    stdscr.addstr(1, 4, "1. Play against computer")
    stdscr.addstr(2, 4, "2. Play against player")
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord('1'):
            return "computer"
        elif key == ord('2'):
            return "player"
        
def main(stdscr,game_mode):
    curses.curs_set(0)  # Hide cursor
    curses.mousemask(1)  # Enable mouse events

    board = [" " for _ in range(9)]
    current_player = "X"
    computer_player = "O" if random.randint(0,1) == 1 else "X"

    while True:
        stdscr.clear()
        draw_board(stdscr, board)
        
        if game_mode == "computer":
            if current_player == computer_player:
                stdscr.addstr(0, 0, "The computer is thinking...")
            else:
                stdscr.addstr(0, 0, "Your turn. Click to place your mark.")
                
        else:
            stdscr.addstr(0, 0, f"Player {current_player}'s turn. Click to place your mark.")
        
        stdscr.refresh()


        if game_mode == "computer" and current_player == computer_player:
            time.sleep(0.5)
            position = get_computer_move(board)
            board[position] = " " + computer_player
            current_player = "O" if current_player == "X" else "X"

        else:
            event = stdscr.getch()

            if event == ord("q"):
                break
            
            elif event == curses.KEY_MOUSE:
                _, mx, my, _, _  = curses.getmouse()

                if not (my == 2 or my == 4 or my == 6):
                    continue

                cell_y, cell_x = (my - 2) // 2, (mx - 4) // 4
                if 0 <= cell_y < 3 and 0 <= cell_x < 3:
                    position = cell_y * 3 + cell_x
                    if board[position] == " ":
                        board[position] = " " + current_player
                        current_player = "O" if current_player == "X" else "X"

        if check_win(board):
            stdscr.clear()
            draw_board(stdscr, board)
            current_player = "O" if current_player == "X" else "X"

            if game_mode == "computer":
                if current_player == computer_player:
                    stdscr.addstr(8, 0, "The computer wins! Press any key twice to play again, or 'q' twice to quit.")
                else:
                    stdscr.addstr(8, 0, "You wins! Press any key twice to play again, or 'q' twice to quit.")
            else:
                stdscr.addstr(8, 0, f"Player {current_player} wins! Press any key twice to play again, or 'q' twice to quit.")

            stdscr.refresh()
            stdscr.getch()
            break

        if " " not in board:
            stdscr.clear()
            draw_board(stdscr, board)
            stdscr.addstr(8, 0, "It's a draw! Press any key twice to play again, or 'q' twice to quit.")
            stdscr.refresh()
            stdscr.getch()
            break

def import_model(n):
    global model
    with open(n + ".json", "r") as json_file:
        loaded_model_json = json_file.read()
    model = model_from_json(loaded_model_json)

    model.load_weights(n + "_weights.h5")

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
def while_main(stdscr):
    game_mode = select_game_mode(stdscr)
    while True:
        main(stdscr,game_mode)

        event = stdscr.getch()
        if event == ord("q"):
            break
    
model = None

if __name__ == "__main__":
    import_model('ooxx7')
    wrapper(while_main)
