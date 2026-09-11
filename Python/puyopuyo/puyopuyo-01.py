import tkinter as tk

GRID_COLS = 6
GRID_ROWS = 12
BLOCK_SIZE = 40

SCREEN_WIDTH = GRID_COLS * BLOCK_SIZE
SCREEN_HEIGHT = GRID_ROWS * BLOCK_SIZE

COLORS = {   
    0: "cyan"
}

class  PuyoPuyoStyleGame:

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

if __name__ == "__main__":
    root = tk.Tk()
    game = PuyoPuyoStyleGame(root)
    root.mainloop()
