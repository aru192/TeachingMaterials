import tkinter as tk
import random
import os

# 定数
GRID_COLS = 6
GRID_ROWS = 12
BLOCK_SIZE = 40
SCREEN_WIDTH = GRID_COLS * BLOCK_SIZE
SCREEN_HEIGHT = GRID_ROWS * BLOCK_SIZE

COLORS = {
    0: "#2A1D67",  # 背景色
    1: "#ff3d3d", 2: "#3d3dff", 3: "#3dff3d", 4: "#ffff3d"  # ぷよの色
}

class MinimumPuyoGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Python言語でぷよぷよ風ゲーム")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg=COLORS[0], highlightthickness=0)
        self.canvas.pack()

        # キー入力による動き
        self.root.bind("<Left>", lambda e: self.move_puyo(-1))
        self.root.bind("<Right>", lambda e: self.move_puyo(1))
        self.root.bind("<Up>", lambda e: self.rotate_puyo())

        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.is_chaining = False 

        # ぷよ画像の読み込み
        self.puyo_images = {}
        self.load_images()

        self.spawn_puyo()
        self.game_loop()

    def load_images(self):
        """
        外部のぷよ画像を読み込む（ファイルがない場合は色で表示） 
        推奨画像サイズ:40×40ピクセル
        """
        file_mapping = {1: "puyo_red.png", 2: "puyo_blue.png", 3: "puyo_green.png", 4: "puyo_yellow.png"}
        for color_code, filename in file_mapping.items():
            if os.path.exists(filename):
                try:
                    self.puyo_images[color_code] = tk.PhotoImage(file=filename)
                except Exception:
                    self.puyo_images[color_code] = None
            else:
                self.puyo_images[color_code] = None

    def get_sub_puyo_offset(self):
        return [(0, -1), (1, 0), (0, 1), (-1, 0)][self.rot_state]

    def spawn_puyo(self):
        self.puyo_colors = [random.randint(1, 4), random.randint(1, 4)]
        self.puyo_x = 3
        self.puyo_y = 0
        self.rot_state = 0
        self.is_chaining = False
        
        if self.grid[0][3] != 0:
            print("GAME OVER")
            self.root.destroy()

    def move_puyo(self, dx):
        if self.is_chaining: return
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        nx, nsx = self.puyo_x + dx, self.puyo_x + dx + sub_dx
        ny, nsy = self.puyo_y, self.puyo_y + sub_dy

        if 0 <= nx < GRID_COLS and 0 <= nsx < GRID_COLS:
            if self.grid[ny][nx] == 0 and 0 <= nsy < GRID_ROWS and self.grid[nsy][nsx] == 0:
                self.puyo_x = nx

    def rotate_puyo(self):
        if self.is_chaining: return
        old_rot = self.rot_state
        self.rot_state = (self.rot_state + 1) % 4
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        sx, sy = self.puyo_x + sub_dx, self.puyo_y + sub_dy
        
        if not (0 <= sx < GRID_COLS and 0 <= sy < GRID_ROWS and self.grid[sy][sx] == 0):
            self.rot_state = old_rot

    def drop_one_step(self):
        """ ぷよを1マス下に落とす """
        if self.is_chaining: return
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        ny, nsy = self.puyo_y + 1, self.puyo_y + 1 + sub_dy

        if ny >= GRID_ROWS or nsy >= GRID_ROWS or self.grid[ny][self.puyo_x] != 0 or (nsy >= 0 and self.grid[nsy][self.puyo_x + sub_dx] != 0):
            self.lock_puyo()
        else:
            self.puyo_y += 1

    def lock_puyo(self):
        self.is_chaining = True
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        
        self.grid[self.puyo_y][self.puyo_x] = self.puyo_colors[0]
        if 0 <= self.puyo_y + sub_dy < GRID_ROWS:
            self.grid[self.puyo_y + sub_dy][self.puyo_x + sub_dx] = self.puyo_colors[1]
            
        self.root.after(150, self.chain_loop)

    def chain_loop(self):
        # 自由落下
        moved = False
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS - 2, -1, -1):
                if self.grid[y][x] != 0 and self.grid[y+1][x] == 0:
                    self.grid[y+1][x] = self.grid[y][x]
                    self.grid[y][x] = 0
                    moved = True
        if moved:
            self.root.after(150, self.chain_loop)
            return

        # 4個連結消去
        if self.check_connections():
            self.root.after(150, self.chain_loop)
            return
            
        self.spawn_puyo()

    def check_connections(self):
        visited = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        to_erase = set()

        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                color = self.grid[y][x]
                if color != 0 and not visited[y][x]:
                    queue, connected = [(x, y)], [(x, y)]
                    visited[y][x] = True
                    while queue:
                        cx, cy = queue.pop(0)
                        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
                                if not visited[ny][nx] and self.grid[ny][nx] == color:
                                    visited[ny][nx] = True
                                    queue.append((nx, ny))
                                    connected.append((nx, ny))
                    if len(connected) >= 4:
                        for p in connected: to_erase.add(p)
        
        if to_erase:
            for x, y in to_erase: self.grid[y][x] = 0
            return True
        return False

    def game_loop(self):
        if not self.is_chaining:
            self.drop_one_step()
        self.draw()
        self.root.after(500, self.game_loop) # 0.5秒ごとに自動落下

    def draw(self):
        self.canvas.delete("all")

        # 画面上のぷよを描画
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                color = self.grid[y][x]
                if color != 0:
                    cx, cy = x * BLOCK_SIZE + BLOCK_SIZE / 2, y * BLOCK_SIZE + BLOCK_SIZE / 2
                    if self.puyo_images.get(color) is not None:
                        self.canvas.create_image(cx, cy, image=self.puyo_images[color])
                    else:
                        self.canvas.create_oval(x*BLOCK_SIZE+2, y*BLOCK_SIZE+2,
                                                (x+1)*BLOCK_SIZE-2, (y+1)*BLOCK_SIZE-2, fill=COLORS[color], outline="")

        # 操作中のぷよを描画
        if not self.is_chaining:
            sub_dx, sub_dy = self.get_sub_puyo_offset()

            acx, acy = self.puyo_x * BLOCK_SIZE + BLOCK_SIZE / 2, self.puyo_y * BLOCK_SIZE + BLOCK_SIZE / 2
            if self.puyo_images.get(self.puyo_colors[0]) is not None:
                self.canvas.create_image(acx, acy, image=self.puyo_images[self.puyo_colors[0]])
            else:
                self.canvas.create_oval(self.puyo_x*BLOCK_SIZE+2,
                                        self.puyo_y*BLOCK_SIZE+2,
                                        (self.puyo_x+1)*BLOCK_SIZE-2, (self.puyo_y+1)*BLOCK_SIZE-2,
                                        fill=COLORS[self.puyo_colors[0]], outline="white")
            
            sx, sy = self.puyo_x + sub_dx, self.puyo_y + sub_dy
            if 0 <= sy < GRID_ROWS:
                scx, scy = sx * BLOCK_SIZE + BLOCK_SIZE / 2, sy * BLOCK_SIZE + BLOCK_SIZE / 2
                if self.puyo_images.get(self.puyo_colors[1]) is not None:
                    self.canvas.create_image(scx, scy, image=self.puyo_images[self.puyo_colors[1]])
                else:
                    self.canvas.create_oval(sx*BLOCK_SIZE+2, sy*BLOCK_SIZE+2, (sx+1)*BLOCK_SIZE-2,
                                            (sy+1)*BLOCK_SIZE-2, fill=COLORS[self.puyo_colors[1]], outline="white")

if __name__ == "__main__":
    root = tk.Tk()
    game = MinimumPuyoGame(root)
    root.mainloop()
    