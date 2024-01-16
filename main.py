import tkinter
from typing import Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, YES, TOP
import time
from dataclasses import dataclass, field
import random

@dataclass
class Point:
    x: int
    y: int

@dataclass
class Line:
    pointA: Point
    pointB: Point

    def draw(self, canvas: ttk.Canvas, fill_color: str):
        line_id = canvas.create_line(
            self.pointA.x,
            self.pointA.y,
            self.pointB.x,
            self.pointB.y,
            fill=fill_color,
            width=2
        )
        canvas.pack(fill=BOTH, expand=YES)
        return line_id

@dataclass
class Cell:
    top_left: Point
    bottom_right: Point
    top_right: Point = field(init=False)
    bottom_left: Point = field(init=False)
    center: Point = field(init=False)
    has_left_wall: bool = True
    has_right_wall: bool = True
    has_top_wall: bool = True
    has_bottom_wall: bool = True
    left_wall: Line = field(init=False)
    right_wall: Line = field(init=False)
    top_wall: Line = field(init=False)
    bottom_wall: Line = field(init=False)
    left_wall_id: Optional[int] = field(init=False)
    right_wall_id: Optional[int] = field(init=False)
    top_wall_id: Optional[int] = field(init=False)
    bottom_wall_id: Optional[int] = field(init=False)
    visited: bool = False

    def __post_init__(self):
        self.top_right = Point(self.bottom_right.x, self.top_left.y)
        self.bottom_left = Point(self.top_left.x, self.bottom_right.y)
        self.left_wall = Line(self.top_left, self.bottom_left)
        self.right_wall = Line(self.top_right, self.bottom_right)
        self.top_wall = Line(self.top_left, self.top_right)
        self.bottom_wall = Line(self.bottom_left, self.bottom_right)
        self.center = Point((self.top_right.x + self.top_left.x)//2, (self.bottom_right.y + self.top_right.y)//2)

    def draw(self, canvas: ttk.Canvas, fill_color: str):
        if self.has_left_wall:
            self.left_wall_id = self.left_wall.draw(canvas, fill_color)
        if self.has_right_wall:
            self.right_wall_id = self.right_wall.draw(canvas, fill_color)
        if self.has_top_wall:
            self.top_wall_id = self.top_wall.draw(canvas, fill_color)
        if self.has_bottom_wall:
            self.bottom_wall_id = self.bottom_wall.draw(canvas, fill_color)

    def draw_move(self, canvas: ttk.Canvas, to_cell: 'Cell', undo=False):
        if not undo:
            fill_color = 'white'
        else:
            fill_color = 'red'
        Line(self.center, to_cell.center).draw(canvas, fill_color)

@dataclass
class Maze:
    top_left_corner: Point
    num_rows: int
    num_cols: int
    cell_size: int
    _cells: list[list[Cell]] = field(init=False)

    def __post_init__(self):
        self._create_cells()

    def _create_cells(self):
        self._cells = [[] for _ in range(self.num_rows)]
        for i, x in enumerate(range(self.top_left_corner.x, self.top_left_corner.x + self.num_rows * self.cell_size, self.cell_size)):
            for y in range(self.top_left_corner.y, self.top_left_corner.y + self.num_cols * self.cell_size, self.cell_size):
                self._cells[i].append(Cell(Point(x, y), Point(x+self.cell_size, y+self.cell_size)))
        
    def draw_maze(self, canvas: ttk.Canvas, animation_func, fill_color='orange'):
        for row in self._cells:
            for cell in row:
                cell.draw(canvas, fill_color)
                animation_func()
                time.sleep(0.00005)
        self.create_openings(canvas)
        self.break_walls(canvas, animation_func)

    def create_openings(self, canvas: ttk.Canvas):
        canvas.delete(self._cells[0][0].top_wall_id)
        canvas.delete(self._cells[-1][-1].bottom_wall_id)

    def break_walls(self, canvas: ttk.Canvas, animation_func):
        visited = set()
        to_visit = [(0, 0)]
        curr = to_visit[0]
        while True:
            visited.add(curr)
            curr_cell = self._cells[curr[0]][curr[1]]
            adjacent_not_visited = []
            for movement in self.get_movements(curr):
                if 0 <= movement[0] < self.num_rows and 0 <= movement[1] < self.num_cols:
                    if movement not in visited:
                        adjacent_not_visited.append(movement)
            if not adjacent_not_visited:
                if not to_visit:
                    break
                curr = to_visit.pop()
                continue
            next_move = random.choice(adjacent_not_visited)
            next_cell = self._cells[next_move[0]][next_move[1]]
            self.break_walls_between_cells(canvas, curr_cell, next_cell)
            animation_func()
            time.sleep(0.00005)
            to_visit.append(next_move)
            curr = next_move


    def get_movements(self, curr_pos: tuple[int, int]) -> list[tuple[int, int]]:
        return [
            (curr_pos[0]-1, curr_pos[1]),
            (curr_pos[0]+1, curr_pos[1]),
            (curr_pos[0], curr_pos[1]-1),
            (curr_pos[0], curr_pos[1]+1)
        ]
    
    def break_walls_between_cells(self, canvas: ttk.Canvas, curr_cell: Cell, next_cell: Cell):
        for curr_dir, next_dir in [('left', 'right'), ('right', 'left'), ('top', 'bottom'), ('bottom', 'top')]:
            if getattr(curr_cell, f'{curr_dir}_wall') == getattr(next_cell, f'{next_dir}_wall'):
                canvas.delete(getattr(curr_cell, f'{curr_dir}_wall_id'))
                canvas.delete(getattr(next_cell, f'{next_dir}_wall_id'))
                setattr(curr_cell, f'has_{curr_dir}_wall', False)
                setattr(next_cell, f'has_{next_dir}_wall', False)
                return

    def solve(self, canvas: ttk.Canvas, animation_func) -> bool:
        return self.solve_r(0, 0, canvas, animation_func)

    def solve_r(self, i: int, j: int, canvas: ttk.Canvas, animation_func) -> bool:
        cell = self._cells[i][j]
        if cell is self._cells[-1][-1]:
            return True
        cell.visited = True
        for movement in self.get_movements((i, j)):
            if 0 <= movement[0] < self.num_rows and 0 <= movement[1] < self.num_cols:
                next_cell = self._cells[movement[0]][movement[1]]
                if self.can_move_to_cell(cell, next_cell) and not next_cell.visited:
                    cell.draw_move(canvas, next_cell)
                    animation_func()
                    path_found = self.solve_r(movement[0], movement[1], canvas, animation_func)
                    if path_found:
                        return True
                    cell.draw_move(canvas, next_cell, undo=True)
                    animation_func()
        return False

    def can_move_to_cell(self, from_cell: Cell, to_cell: Cell) -> bool:
        for from_dir, to_dir in [('left', 'right'), ('right', 'left'), ('top', 'bottom'), ('bottom', 'top')]:
            if getattr(from_cell, f'{from_dir}_wall') == getattr(to_cell, f'{to_dir}_wall'):
                # breakpoint()
                if not getattr(from_cell, f'has_{from_dir}_wall') and not getattr(to_cell, f'has_{to_dir}_wall'):
                    return True
        return False


class MazeSolver:
    def __init__(self, master: ttk.Window, **kwargs) -> None:
        self.master = master
        self.master.protocol('WM_DELETE_WINDOW', self.close)
        self.canvas = ttk.Canvas(self.master)
        self.canvas.pack(fill=BOTH, expand=YES)
        self.running = False

        self.maze = Maze(Point(10, 10), 20, 20, 30)
        self.draw_cells()
        self.maze.solve(self.canvas, animation_func=self.redraw)

    def draw_line(self, line: Line, fill_color='black'):
        line.draw(self.canvas, fill_color)

    def draw_cells(self):
        self.maze.draw_maze(self.canvas, self.redraw)

    def redraw(self):
        self.master.update_idletasks()
        self.master.update()

    def wait_for_close(self):
        # self.draw_cells()
        self.running = True
        while self.running:
            self.redraw()
            time.sleep(1)
        

    def close(self):
        self.running = False

if __name__ == '__main__':
    width = 800
    height = 800
    window = ttk.Window(
        title="Maze Solver",
        themename="darkly",
        size=(width, height)
    )
    app = MazeSolver(window)
    app.wait_for_close()