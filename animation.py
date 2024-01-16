from typing import Callable
from ttkbootstrap import Canvas
from maze import Point, Line, Cell, Maze
from dataclasses import dataclass

@dataclass
class CellDrawing:
    left_wall_id: int
    right_wall_id: int
    top_wall_id: int
    bottom_wall_id: int

class Animator:
    def __init__(self, canvas: Canvas, animation_func: Callable) -> None:
        self.canvas = canvas
        self._animate = animation_func
        self.cell_drawings: dict[Point, CellDrawing] = {}


    def draw_line(self, line: Line, fill_color: str) -> int:
        line_id = self.canvas.create_line(
            line.pointA.x,
            line.pointA.y,
            line.pointB.x,
            line.pointB.y,
            fill=fill_color,
            width=2
        )
        return line_id
    
    def delete_line(self, line_id: int):
        self.canvas.delete(line_id)

    def get_cell_drawing(self, cell: Cell):
        return self.cell_drawings[cell.top_left]

    def draw_cell(self, cell: Cell, fill_color: str):
        left_wall_id = self.draw_line(cell.left_wall, fill_color)
        right_wall_id = self.draw_line(cell.right_wall, fill_color)
        top_wall_id = self.draw_line(cell.top_wall, fill_color)
        bottom_wall_id = self.draw_line(cell.bottom_wall, fill_color)
        self.cell_drawings[cell.top_left] = CellDrawing(left_wall_id, right_wall_id, top_wall_id, bottom_wall_id)

    def draw_cell_move(self, from_cell: Cell, to_cell: Cell, undo=False):
        fill_color = 'red'
        if not undo:
            fill_color = 'white'
        self.draw_line(Line(from_cell.center, to_cell.center), fill_color)

    def animate_maze_creation(self, maze: Maze):
        fill_color = 'orange'
        cells_positions = maze.get_cell_positions()
        for i, (x, y) in enumerate(cells_positions):
            self.draw_cell(maze.get_cell(x, y), fill_color)
            if i % (len(cells_positions)//100) == 0:
                self._animate()

        line_id = self.get_cell_drawing(maze._cells[0][0]).top_wall_id
        self.delete_line(line_id)
        line_id = self.get_cell_drawing(maze._cells[-1][-1]).bottom_wall_id
        self.delete_line(line_id)
        self.animate_maze_wall_breaks(maze)

    def animate_maze_wall_breaks(self, maze: Maze):
        visited = set()
        to_visit = [(0,0)]
        curr = to_visit[0]
        counter = 0
        num_cells = maze.num_cols * maze.num_rows
        while True:
            next = maze._break_single_wall(visited, to_visit, curr)
            if next is None:
                break
            curr_cell = maze.get_cell(*curr)
            next_cell = maze.get_cell(*next)
            if curr_cell.is_right_neighbor(next_cell):
                self.delete_line(self.get_cell_drawing(curr_cell).left_wall_id)
                self.delete_line(self.get_cell_drawing(next_cell).right_wall_id)
            if curr_cell.is_left_neighbor(next_cell):
                self.delete_line(self.get_cell_drawing(curr_cell).right_wall_id)
                self.delete_line(self.get_cell_drawing(next_cell).left_wall_id)
            if curr_cell.is_top_neighbor(next_cell):
                self.delete_line(self.get_cell_drawing(curr_cell).bottom_wall_id)
                self.delete_line(self.get_cell_drawing(next_cell).top_wall_id)
            if curr_cell.is_bottom_neighbor(next_cell):
                self.delete_line(self.get_cell_drawing(curr_cell).top_wall_id)
                self.delete_line(self.get_cell_drawing(next_cell).bottom_wall_id)
            if counter % (num_cells//100) == 0:
                self._animate()
            curr = next
            counter += 1

    def animate_maze_solution(self, maze: Maze):
        target = maze.get_cell(-1, -1)
        num_cells = maze.num_cols * maze.num_rows
        stack = [(0,0)]
        counter = 0
        while stack:
            cell, found_move = maze.solution_take_next_step(stack)
            if cell is target:
                return True
            undo = not found_move
            self.draw_cell_move(cell, maze.get_cell(*stack[-1]), undo)
            if counter % (num_cells//100) == 0:
                self._animate()

            counter += 1