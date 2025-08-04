import random, os
from enum import Enum
from collections import deque

class Grid:
    """Grid class that handles the game board, bomb placement and cell state."""
    def __init__(self, size: int, bomb_quantity: int):
        if (bomb_quantity >= size * size):
            raise Exception("Can't have more bombs than cells.")
        elif (bomb_quantity <= 0):
            raise Exception ("You need at least one bomb to be able to play.")
        self.size = size
        self.cells = [[None for y in range(size)] for x in range(size)]
        self.bombs = bomb_quantity
        self.bombs_coords = set()
        self.empty_cells = set()
        self.randomize_bombs()
        self._populate_empty_cells()
        self.count_neighbor_bombs()


    def get_cell(self, x: int, y: int):
        """Returns the cell value on a given position."""
        return self.cells[x][y]


    def _populate_empty_cells(self):
        for x in range(self.size):
            for y in range(self.size):
                self.empty_cells.add((x, y))


    def randomize_bombs(self):
        """Place a given number of bombs in random cells of the grid."""
        placed = 0
        while placed < self.bombs:
            x_pos = random.randint(0, self.size - 1)
            y_pos = random.randint(0, self.size - 1)
            if (self.get_cell(x_pos, y_pos) is None):
                self.cells[x_pos][y_pos] = 'B'
                self.bombs_coords.add((x_pos, y_pos))
                placed += 1


    def get_neighbors(self, x, y) -> list:
        """Returns a list with the valid neighbors of a given cell."""
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 1), (1, 0)]
        return [(x + dx, y + dy) for dx, dy in directions if x + dx >= 0 and x + dx < self.size and y + dy >= 0 and y + dy < self.size]


    def count_neighbor_bombs(self):
        for x in range(self.size):
            for y in range(self.size):
                bombs = 0
                if self.cells[x][y] is None:
                    neighbors = self.get_neighbors(x, y)
                    for cell in range(len(neighbors)):
                        if self.get_cell(neighbors[cell][0], neighbors[cell][1]) == 'B': bombs += 1 
                    self.cells[x][y] = bombs


    def __str__(self):
        str_grid = ""
        for x in range(self.size):
            for y in range(self.size):
                str_grid += (str(self.cells[y][x]) + " ") if self.cells[y][x] is not None else "  " # Flip x and y because fuck you
            str_grid += "\n"
        return str_grid


class MineSweeperGame:
    """MineSweeper main game class. Manages the game state, observable grid for the player, 
    user moves (clicks and flags), win/loss detection and cell revealing logic."""
    number_emoji = {-1: "⬜", 0:"⬛", 1:"1️ ", 2:"2️ ", 3:"3️ ", 4:"4️ ", 5:"5️ ", 6:"6️ ", 7:"7️ ", 8:"8️ ", "B":"💣", "F": "❓"}
    
    
    class States(Enum):
        """Enum states to be used for game logic."""
        EMPTY_CELL = 1
        BOMB = 2
        FLAG = 3
        WIN = 4
        INVALID = 5


    def __init__(self, size, bomb_quantity) -> None:
        self.grid = Grid(size, bomb_quantity)
        self.observableGrid = [[None for _ in range(size)] for _ in range(size)]
        self.visited_cells = set()


    def click(self, x: int, y: int) -> States:
        """Reveals the cell on a given position, if valid.
        If valid:
        - Clear the cells around the origin that have no bombs
        - Detect win 

        Else:
        - Returns game state with more information
        - Loses the game if the revealed cell has a bomb
        """
        cell = self.grid.get_cell(x, y)
        obs_cell = self.observableGrid[x][y]
        if cell != 'B' and obs_cell is None:
            self.reveal_area_around(x, y)

            if (self.validate_win()): # All non bomb cells cleared
                return self.States.WIN

            return self.States.EMPTY_CELL # Reveal cell
        elif obs_cell == 'F':
            return self.States.INVALID # Can't click on a flag
        elif obs_cell is not None:
            return self.States.INVALID # Can't click on an revealed cell
        else:
            self.observableGrid = self.grid.cells
            for x in range(self.grid.size):
                for y in range(self.grid.size):
                    cell = self.grid.cells[x][y]
                    self.observableGrid[x][y] = self.number_emoji[cell]
            return self.States.BOMB # Game over, clicked on a bomb


    def flag(self, x: int, y: int) -> States:
        """Handles the flag logic"""
        cell = self.observableGrid[x][y]
        if cell is None: # Add flag
            self.observableGrid[x][y] = self.number_emoji['F']
            return self.States.FLAG
        elif cell == self.number_emoji['F']: # Remove flag
            self.observableGrid[x][y] = None
            return self.States.FLAG
        else:
            return self.States.INVALID # Nothing to flag here


    def validate_win(self) -> bool:
        """Validates if the current game state can be considered a win"""
        return len(self.grid.bombs_coords) == len(self.grid.empty_cells)


    def make_move(self, suffix: str, x: int, y: int) -> States:
        """Handles the moves logic"""
        if suffix.upper() == 'F':
            return self.flag(x, y)
        elif suffix.upper() == 'C':
            return self.click(x, y)
        else:
            raise ValueError("Invalid suffix! Use either C or F")


    def reveal_area_around(self, x: int, y: int) -> None:
        """Clear all the empty (0) cells around the origin."""
        visited = self.visited_cells
        queue = deque()
        queue.append((x, y))

        while queue:
            crr_x, crr_y = queue.popleft()
            if (crr_x, crr_y) in visited:
                continue
            visited.add((crr_x, crr_y))
            self.grid.empty_cells.remove((crr_x, crr_y))

            cell = self.grid.get_cell(crr_x, crr_y)
            if (cell == 0):
                self.observableGrid[crr_x][crr_y] = self.number_emoji[0]
                neighbors = self.grid.get_neighbors(crr_x, crr_y)
                for nx, ny in neighbors:
                    if (nx, ny) not in visited:
                        queue.append((nx, ny))
            else:
                self.observableGrid[crr_x][crr_y] = self.number_emoji[cell]


    def __str__(self) -> str:
        str_grid = ""
        for x in range(self.grid.size):
            for y in range(self.grid.size):
                str_grid += (str(self.observableGrid[y][x]) + " ") if self.observableGrid[y][x] is not None else f"{self.number_emoji[-1]} " # Flip x and y because fuck you
            str_grid += "\n"
        return str_grid


def clear_console():
    """Clears the terminal for better visibility"""
    os.system('cls')


def playGame(game_size: int, bomb_amount: int):
    """Runs the MineSweeper game in the terminal.

    Will continuously prompt the user to enter moves, then processes them.
    
    - (int) game_size = How big is the grid (N * N).
    - (int) bomb_amount = How many bombs will be placed randomly through the cells."""
    game = MineSweeperGame(game_size, bomb_amount)

    while True:
        print(game)
        print("Your play (S X Y): ", end="")
        pos = input().split(' ')
        state = ""
        clear_console()
        try:
            state = game.make_move(pos[0], int(pos[1]), int(pos[2]))
        except:
            print("Invalid input! Use the following format: s x y, s being the suffix C to click or F to flag the given cell.")
        
        if state == game.States.BOMB:
            print(game)
            print("You lost! RIP bozo.")
            break
        elif state == game.States.WIN:
            print(game)
            print("You won! GG EZ")
            break


if __name__ == '__main__':
    clear_console()
    playGame(10, 5)