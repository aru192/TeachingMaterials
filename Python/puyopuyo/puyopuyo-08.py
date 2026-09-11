import tkinter as tk
import random

GRID_COLS = 6
GRID_ROWS = 12
BLOCK_SIZE = 40
NORMAL_SPEED = 2.5  # 追記箇所１

SCREEN_WIDTH = GRID_COLS * BLOCK_SIZE
SCREEN_HEIGHT = GRID_ROWS * BLOCK_SIZE

COLORS = {   
    0: "cyan",
    1: "red",
    2: "blue",
    3: "green",
    4: "yellow"
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
        
        self.root.bind(
            "<Left>",
            lambda e: self.move_puyo(-1)
        )

        self.root.bind(
            "<Right>",
            lambda e: self.move_puyo(1)
        )
        
        self.root.bind(
            "<Up>",
            lambda e: self.rotate_puyo()
        )
        
        self.puyo_x = 3
        self.puyo_y = BLOCK_SIZE * 1.0  # コード書き換え１

        self.puyo_colors = [
            random.randint(1, 4),
            random.randint(1, 4)
        ]                   

        self.rot_state = 0
        self.is_chaining = False

        self.game_loop()

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
        sub_dx, sub_dy = self.get_sub_puyo_offset()

        sx = self.puyo_x + sub_dx
        sy = self.puyo_y + (sub_dy * BLOCK_SIZE)   # コード書き換え２
                                  
        self.canvas.create_oval(
            self.puyo_x * BLOCK_SIZE + 2,
            self.puyo_y + 2,   # コード書き換え３
            (self.puyo_x + 1) * BLOCK_SIZE - 2,
            self.puyo_y + BLOCK_SIZE - 2,   # コード書き換え４
            fill = COLORS[self.puyo_colors[0]],
            outline = "white"
        )

        self.canvas.create_oval(
            sx * BLOCK_SIZE + 2,        
            sy + 2,    #
            (sx + 1) * BLOCK_SIZE - 2,
            sy + BLOCK_SIZE - 2,    # コード書き換え５
            fill = COLORS[self.puyo_colors[1]],
            outline = "white"
        )

    def game_loop(self):
        if not self.is_chaining:
            self.puyo_y += NORMAL_SPEED         # コード書き換え６

            if self.puyo_y > SCREEN_HEIGHT:
                self.puyo_y = BLOCK_SIZE * 1.0  # コード書き換え６-ここまで

        self.canvas.delete("all")

        self.draw()

        self.root.after(
            16, 
            self.game_loop
        )
    
    def move_puyo(self, dx):
        next_x = self.puyo_x + dx

        if 0 <= next_x < GRID_COLS:
            self.puyo_x = next_x
    
    def get_sub_puyo_offset(self):
        offsets = [
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, 0)
        ]

        return offsets[self.rot_state]
    
    def rotate_puyo(self):
        self.rot_state = (
            self.rot_state + 1
        ) % 4

if __name__ == "__main__":
    root = tk.Tk()
    game = PuyoPuyoStyleGame(root)
    root.mainloop()
