import tkinter as tk
import random   # コード追記箇所１

GRID_COLS = 6
GRID_ROWS = 12
BLOCK_SIZE = 40

SCREEN_WIDTH = GRID_COLS * BLOCK_SIZE
SCREEN_HEIGHT = GRID_ROWS * BLOCK_SIZE

COLORS = {   
    0: "cyan",
    1: "red",
    2: "blue",  # コード追記箇所２
    3: "green",
    4: "yellow" # コード追記箇所２-ここまで
}

class PuyoPuyoStyleGame:

    def __init__(self, root):
        self.root = root
        
        self.root.title("「ぷよぷよ風ゲーム」をPython言語で作ってみよう！")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width = SCREEN_WIDTH,
            height = SCREEN_HEIGHT,
            bg = COLORS[0],
            highlightthickness = 0
        )

        self.canvas.pack()

        self.puyo_x = 3
        self.puyo_y = 1

        self.puyo_color = random.randint(1,4)   # コード追記箇所３

        self.draw()

    def draw(self):
        self.draw_x_mark()
        self.draw_puyo()
        
    def draw_x_mark(self):
        x1 = 2 * BLOCK_SIZE + 8
        y1 = 8
        x2 = 3 * BLOCK_SIZE - 8
        y2 = BLOCK_SIZE - 8

        self.canvas.create_line(
            x1, y1, x2, y2,
            fill = "red",
            width = 3
        )

        self.canvas.create_line(
            x2, y1, x1, y2,
            fill = "red",
            width = 3
        )

    def draw_puyo(self):
        self.canvas.create_oval(
            self.puyo_x * BLOCK_SIZE + 2,
            self.puyo_y * BLOCK_SIZE + 2,
            (self.puyo_x + 1) * BLOCK_SIZE - 2,
            (self.puyo_y + 1) * BLOCK_SIZE - 2,
            fill = COLORS[self.puyo_color],   # コード書き換え
            outline = "white"
        )    

if __name__ == "__main__":
    root = tk.Tk()
    game = PuyoPuyoStyleGame(root)
    root.mainloop()
