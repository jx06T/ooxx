import curses
from curses import wrapper

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

def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    curses.mousemask(1)  # Enable mouse events

    board = [" " for _ in range(9)]
    current_player = "X"

    while True:
        stdscr.clear()
        draw_board(stdscr, board)
        stdscr.addstr(0, 0, f"Player {current_player}'s turn. Click to place your mark.")
        stdscr.refresh()

        event = stdscr.getch()
        if event == ord("q"):
            break
        elif event == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()

            if not (my == 2 or my == 4 or my == 6):
                continue
                
            cell_y, cell_x = (my - 2) // 2, (mx - 4) // 4
            if 0 <= cell_y < 3 and 0 <= cell_x < 3:
                position = cell_y * 3 + cell_x
                if board[position] == " ":
                    board[position] = " " + current_player
                    if check_win(board):
                        stdscr.clear()
                        draw_board(stdscr, board)
                        stdscr.addstr(8, 0, f"Player {current_player} wins! Press any key to exit.")
                        stdscr.refresh()
                        stdscr.getch()
                        break
                    if " " not in board:
                        stdscr.clear()
                        draw_board(stdscr, board)
                        stdscr.addstr(8, 0, "It's a tie! Press any key to exit.")
                        stdscr.refresh()
                        stdscr.getch()
                        break
                    current_player = "O" if current_player == "X" else "X"

if __name__ == "__main__":
    wrapper(main)
