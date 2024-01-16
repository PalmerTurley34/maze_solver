import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, YES, TOP, X, SUCCESS, WARNING, EW, OUTLINE, CENTER
from maze import Maze, Point
from animation import Animator

class MazeSolver:
    def __init__(self, master: ttk.Window, **kwargs) -> None:
        self.master = master
        self.master.protocol('WM_DELETE_WINDOW', self.close)
        self.buttons = ttk.Frame(self.master)
        self.buttons.pack(side=TOP)
        self.canvas = ttk.Canvas(self.master)
        self.canvas.pack(side=TOP, fill=BOTH, expand=YES, padx=20, pady=20)
        self.animator = Animator(self.canvas, self.redraw)

        ttk.Label(self.buttons, text='Columns: ', bootstyle=WARNING).grid(row=0, column=2, padx=5, pady=2) # type: ignore
        self.num_rows = ttk.IntVar(value=10)
        self.num_rows_choice = ttk.OptionMenu(self.buttons, self.num_rows, 10, *list(range(10, 110, 10)), bootstyle=(OUTLINE, SUCCESS)) # type: ignore
        self.num_rows_choice.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(self.buttons, text='Rows: ', bootstyle=(WARNING)).grid(row=0, column=0, padx=5, pady=2) # type: ignore
        self.num_cols = ttk.IntVar(value=10)
        self.num_cols_choice = ttk.OptionMenu(self.buttons, self.num_cols, 10, *list(range(10, 110, 10)), bootstyle=(OUTLINE, SUCCESS)) # type: ignore
        self.num_cols_choice.grid(row=0, column=3, padx=5, pady=2)

        self.create_maze_button = ttk.Button(self.buttons, text='Create Maze', command=self.create_maze, bootstyle=(OUTLINE, SUCCESS)) # type: ignore
        self.create_maze_button.grid(row=1, column=0, sticky=EW, columnspan=2, padx=5, pady=2)
        self.solve_maze_button = ttk.Button(self.buttons, text='Sovle!', command=self.solve_maze, bootstyle=(OUTLINE, WARNING)) # type: ignore
        self.solve_maze_button.grid(row=1, column=2, sticky=EW, columnspan=2, padx=5, pady=2)
        self.running = False

    def create_maze(self):
        if self.running:
            return
        self.running = True
        self.canvas.delete('all')
        cell_size = min((self.canvas.winfo_width()//self.num_cols.get(), self.canvas.winfo_height()//self.num_rows.get()))
        self.maze = Maze(Point(0, 0), self.num_cols.get(), self.num_rows.get(), cell_size)
        self.animator.animate_maze_creation(self.maze)
        self.running = False

    def solve_maze(self):
        if self.running:
            return
        self.running = True
        self.animator.animate_maze_solution(self.maze)
        self.running = False

    def redraw(self):
        self.master.update_idletasks()
        self.master.update()

    def close(self):
        self.running = False
        self.master.quit()
        self.master.destroy()

if __name__ == '__main__':
    width = 1000
    height = 1200
    window = ttk.Window(
        title="Maze Solver",
        themename="darkly",
        size=(width, height)
    )
    app = MazeSolver(window)
    window.mainloop()