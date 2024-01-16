from dataclasses import dataclass, field
import random

@dataclass(slots=True, frozen=True)
class Point:
    x: int
    y: int

@dataclass(slots=True, frozen=True)
class Line:
    pointA: Point
    pointB: Point

@dataclass(slots=True)
class Cell:
    top_left: Point
    cell_size: int
    has_left_wall: bool = True
    has_right_wall: bool = True
    has_top_wall: bool = True
    has_bottom_wall: bool = True
    visited: bool = False
    center: Point = field(init=False)
    left_wall: Line = field(init=False)
    right_wall: Line = field(init=False)
    top_wall: Line = field(init=False)
    bottom_wall: Line = field(init=False)

    def __post_init__(self):
        bottom_right = Point(self.top_left.x + self.cell_size, self.top_left.y + self.cell_size)
        top_right = Point(bottom_right.x, self.top_left.y)
        bottom_left = Point(self.top_left.x, bottom_right.y)
        self.left_wall = Line(self.top_left, bottom_left)
        self.right_wall = Line(top_right, bottom_right)
        self.top_wall = Line(self.top_left, top_right)
        self.bottom_wall = Line(bottom_left, bottom_right)
        self.center = Point((top_right.x + self.top_left.x)//2, (bottom_right.y + top_right.y)//2)

    def is_right_neighbor(self, cell: 'Cell'):
        '''
        return `True` if `self` is directly to the right of `cell`
        otherwise, return `False`
        '''
        return self.left_wall == cell.right_wall
    
    def is_left_neighbor(self, cell: 'Cell'):
        '''
        return `True` if `self` is directly to the left of `cell`
        otherwise, return `False`
        '''
        return self.right_wall == cell.left_wall
    
    def is_top_neighbor(self, cell: 'Cell'):
        '''
        return `True` if `self` is directly on top of `cell`
        otherwise, return `False`
        '''
        return self.bottom_wall == cell.top_wall
    
    def is_bottom_neighbor(self, cell: 'Cell'):
        '''
        return `True` if `self` is directly on the bottom of `cell`
        otherwise, return `False`
        '''
        return self.top_wall == cell.bottom_wall
    

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
                self._cells[i].append(Cell(Point(x, y), self.cell_size))

    def _break_walls(self):
        self._cells[0][0].has_top_wall = False
        self._cells[-1][-1].has_bottom_wall = False
        visited = set()
        to_visit = [(0, 0)]
        curr = to_visit[0]
        while True:
            curr = self._break_single_wall(visited, to_visit, curr)
            if curr is None:
                break

    def _break_single_wall(self, visited: set, to_visit: list, curr: tuple[int, int]) -> tuple[int, int] | None:
        visited.add(curr)
        curr_cell = self._cells[curr[0]][curr[1]]
        adjacent_not_visited = []
        for movement in self.get_movements(curr):
            if 0 <= movement[0] < self.num_rows and 0 <= movement[1] < self.num_cols:
                if movement not in visited:
                    adjacent_not_visited.append(movement)
        if not adjacent_not_visited:
            if not to_visit:
                return None
            curr = to_visit.pop()
            return curr
        next_move = random.choice(adjacent_not_visited)
        next_cell = self._cells[next_move[0]][next_move[1]]
        self.break_walls_between_cells(curr_cell, next_cell)
        to_visit.append(next_move)
        curr = next_move
        return curr

    def get_cell_positions(self) -> list[tuple[int, int]]:
        cell_positions = []
        for i in range(len(self._cells)):
            for j in range(len(self._cells[0])):
                cell_positions.append((i, j))
        random.shuffle(cell_positions)
        return cell_positions
    
    def get_cell(self, i, j) -> Cell:
        return self._cells[i][j]

    def get_movements(self, curr_pos: tuple[int, int]) -> list[tuple[int, int]]:
        return [
            (curr_pos[0]-1, curr_pos[1]),
            (curr_pos[0]+1, curr_pos[1]),
            (curr_pos[0], curr_pos[1]-1),
            (curr_pos[0], curr_pos[1]+1)
        ]
    
    def break_walls_between_cells(self, curr_cell: Cell, next_cell: Cell):
        for curr_dir, next_dir in [('left', 'right'), ('right', 'left'), ('top', 'bottom'), ('bottom', 'top')]:
            if getattr(curr_cell, f'{curr_dir}_wall') == getattr(next_cell, f'{next_dir}_wall'):
                setattr(curr_cell, f'has_{curr_dir}_wall', False)
                setattr(next_cell, f'has_{next_dir}_wall', False)
                return
    
    def solve(self, target: Cell) -> bool:
        stack = [(0, 0)]
        while stack:
            cell, found_move = self.solution_take_next_step(stack)
            if cell is target:
                return True
        return False
    
    def solution_take_next_step(self, stack: list) -> tuple[Cell, bool]:
        i, j = stack[-1]
        cell = self._cells[i][j]
        if cell is self._cells[-1][-1]:
            return cell, True
        cell.visited = True
        found_next_move = False
        for movement in self.get_movements((i, j)):
            next_i, next_j = movement
            if 0 <= next_i < self.num_rows and 0 <= next_j < self.num_cols:
                next_cell = self._cells[next_i][next_j]
                if self.can_move_to_cell(cell, next_cell) and not next_cell.visited:
                    stack.append((next_i, next_j))
                    found_next_move = True
                    break
        if not found_next_move:
            stack.pop()
        return cell, found_next_move

    def can_move_to_cell(self, from_cell: Cell, to_cell: Cell) -> bool:
        for from_dir, to_dir in [('left', 'right'), ('right', 'left'), ('top', 'bottom'), ('bottom', 'top')]:
            if getattr(from_cell, f'{from_dir}_wall') == getattr(to_cell, f'{to_dir}_wall'):
                if not getattr(from_cell, f'has_{from_dir}_wall') and not getattr(to_cell, f'has_{to_dir}_wall'):
                    return True
        return False
