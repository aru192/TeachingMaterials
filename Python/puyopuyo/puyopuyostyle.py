import tkinter as tk
import random
import os

GRID_COLS = 6
GRID_ROWS = 12
BLOCK_SIZE = 40
SCORE_PANEL_HEIGHT = 40
SCREEN_WIDTH = GRID_COLS * BLOCK_SIZE
SCREEN_HEIGHT = (GRID_ROWS * BLOCK_SIZE) + SCORE_PANEL_HEIGHT

class PuyoPuyoStyleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("「ぷよぷよ風ゲーム」をPython言語で作ってみよう")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg="#2A1D67", highlightthickness=0)
        self.canvas.pack()

        self.root.bind("<Left>", lambda e: self.move_puyo(-1))
        self.root.bind("<Right>", lambda e: self.move_puyo(1))
        self.root.bind("<Up>", lambda e: self.rotate_puyo())
        self.root.bind("<Down>", lambda e: self.hard_drop_puyo())

        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.is_chaining = False 
        self.score = 0

        self.bounce_puyos = {}
        self.erasing_puyos = {}

        self.puyo_images = {}
        self.load_images()

        self.spawn_puyo()
        self.game_loop()

    def load_images(self):
        file_mapping = {
            1: os.path.join("puyo", "puyo_red.png"), 
            2: os.path.join("puyo", "puyo_blue.png"), 
            3: os.path.join("puyo", "puyo_green.png"), 
            4: os.path.join("puyo", "puyo_yellow.png")
        }
        for color_code, filepath in file_mapping.items():
            if os.path.exists(filepath):
                try:
                    self.puyo_images[color_code] = tk.PhotoImage(file=filepath)
                except Exception:
                    self.puyo_images[color_code] = None
            else:
                self.puyo_images[color_code] = None

    def get_sub_puyo_offset(self):
        return [(0, -1), (1, 0), (0, 1), (-1, 0)][self.rot_state]

    def spawn_puyo(self):
        self.puyo_colors = [random.randint(1, 4), random.randint(1, 4)]
        self.puyo_x = 3
        self.puyo_y = 1
        self.rot_state = 0
        self.is_chaining = False
        
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        if self.grid[self.puyo_y][self.puyo_x] != 0 or self.grid[self.puyo_y + sub_dy][self.puyo_x + sub_dx] != 0:
            print("GAME OVER")
            self.root.quit()
            return

    def move_puyo(self, dx):
        if self.is_chaining: return
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        nx, nsx = self.puyo_x + dx, self.puyo_x + dx + sub_dx
        ny, nsy = self.puyo_y, self.puyo_y + sub_dy

        if 0 <= nx < GRID_COLS and 0 <= nsx < GRID_COLS:
            if self.grid[ny][nx] == 0 and 0 <= nsy < GRID_ROWS and self.grid[nsy][nsx] == 0:
                self.puyo_x = nx
                self.draw()

    def rotate_puyo(self):
        if self.is_chaining: return
        old_rot = self.rot_state
        self.rot_state = (self.rot_state + 1) % 4
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        sx, sy = self.puyo_x + sub_dx, self.puyo_y + sub_dy
        
        if not (0 <= sx < GRID_COLS and 0 <= sy < GRID_ROWS and self.grid[sy][sx] == 0):
            if 0 <= self.puyo_x - 1 < GRID_COLS and 0 <= sx - 1 < GRID_COLS and self.grid[self.puyo_y][self.puyo_x - 1] == 0 and (sy < 0 or self.grid[sy][sx - 1] == 0):
                self.puyo_x -= 1
            elif 0 <= self.puyo_x + 1 < GRID_COLS and 0 <= sx + 1 < GRID_COLS and self.grid[self.puyo_y][self.puyo_x + 1] == 0 and (sy < 0 or self.grid[sy][sx + 1] == 0):
                self.puyo_x += 1
            else:
                self.rot_state = old_rot
        self.draw()

    def drop_one_step(self):
        if self.is_chaining: return
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        ny, nsy = self.puyo_y + 1, self.puyo_y + 1 + sub_dy

        if ny >= GRID_ROWS or nsy >= GRID_ROWS or self.grid[ny][self.puyo_x] != 0 or (nsy >= 0 and self.grid[nsy][self.puyo_x + sub_dx] != 0):
            self.lock_puyo()
        else:
            self.puyo_y += 1

    def hard_drop_puyo(self):
        if self.is_chaining: return
        self.is_chaining = True
        
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        
        while True:
            ny, nsy = self.puyo_y + 1, self.puyo_y + 1 + sub_dy
            is_collide = False
            if ny >= GRID_ROWS or self.grid[ny][self.puyo_x] != 0:
                is_collide = True
            if nsy >= GRID_ROWS or (nsy >= 0 and self.grid[nsy][self.puyo_x + sub_dx] != 0):
                is_collide = True
                
            if is_collide:
                break
            self.puyo_y += 1
        
        self.lock_puyo()

    def lock_puyo(self):
        self.is_chaining = True
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        
        locked_puyos = []
        if 0 <= self.puyo_y < GRID_ROWS:
            self.grid[self.puyo_y][self.puyo_x] = self.puyo_colors[0]
            locked_puyos.append((self.puyo_x, self.puyo_y))
        if 0 <= self.puyo_y + sub_dy < GRID_ROWS:
            self.grid[self.puyo_y + sub_dy][self.puyo_x + sub_dx] = self.puyo_colors[1]
            locked_puyos.append((self.puyo_x + sub_dx, self.puyo_y + sub_dy))
            
        for x, y in locked_puyos:
            self.bounce_puyos[(x, y)] = 4

        self.draw()
        self.root.after(30, self.animate_bounce)

    def animate_bounce(self):
        active = False
        for pos in list(self.bounce_puyos.keys()):
            self.bounce_puyos[pos] -= 1
            if self.bounce_puyos[pos] <= -4:
                del self.bounce_puyos[pos]
            else:
                active = True
        self.draw()
        if active:
            self.root.after(30, self.animate_bounce)
        else:
            self.chain_loop()

    def chain_loop(self):
        moved = False
        dropped_puyos = []
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS - 2, -1, -1):
                if self.grid[y][x] != 0 and self.grid[y+1][x] == 0:
                    self.grid[y+1][x] = self.grid[y][x]
                    self.grid[y][x] = 0
                    moved = True
                    dropped_puyos.append((x, y+1))
        if moved:
            for x, y in dropped_puyos:
                self.bounce_puyos[(x, y)] = 3
            self.draw()
            self.root.after(60, self.animate_bounce)
            return

        if self.check_connections():
            self.root.after(40, self.animate_erase)
            return
            
        self.spawn_puyo()
        self.draw()

    def animate_erase(self):
        active = False
        for pos in list(self.erasing_puyos.keys()):
            self.erasing_puyos[pos] -= 4
            if self.erasing_puyos[pos] <= 0:
                del self.erasing_puyos[pos]
            else:
                active = True
        self.draw()
        if active:
            self.root.after(40, self.animate_erase)
        else:
            self.chain_loop()

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
            self.score += len(to_erase) * 10
            for x, y in to_erase:
                self.erasing_puyos[(x, y)] = BLOCK_SIZE - 4
                self.grid[y][x] = 0
            return True
        return False

    def game_loop(self):
        if not self.is_chaining:
            self.drop_one_step()
            self.draw()
        self.root.after(500, self.game_loop)

    def draw(self):
        try:
            self.canvas.delete("all")
        except tk.TclError:
            return

        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                color = self.grid[y][x]
                if color != 0:
                    offset_y = 0
                    if (x, y) in self.bounce_puyos:
                        state = self.bounce_puyos[(x, y)]
                        if state > 0:
                            offset_y = -state * 2
                        else:
                            offset_y = state * 2

                    cx, cy = x * BLOCK_SIZE + BLOCK_SIZE / 2, y * BLOCK_SIZE + BLOCK_SIZE / 2 + offset_y
                    if self.puyo_images.get(color) is not None:
                        self.canvas.create_image(cx, cy, image=self.puyo_images[color])

        for pos, size in self.erasing_puyos.items():
            x, y = pos
            cx, cy = x * BLOCK_SIZE + BLOCK_SIZE / 2, y * BLOCK_SIZE + BLOCK_SIZE / 2
            half = size / 2
            self.canvas.create_oval(cx - half, cy - half, cx + half, cy + half, fill="#FFFFFF", outline="")

        if not self.is_chaining:
            sub_dx, sub_dy = self.get_sub_puyo_offset()

            if 0 <= self.puyo_y < GRID_ROWS:
                acx, acy = self.puyo_x * BLOCK_SIZE + BLOCK_SIZE / 2, self.puyo_y * BLOCK_SIZE + BLOCK_SIZE / 2
                if self.puyo_images.get(self.puyo_colors[0]) is not None:
                    self.canvas.create_image(acx, acy, image=self.puyo_images[self.puyo_colors[0]])
            
            sx, sy = self.puyo_x + sub_dx, self.puyo_y + sub_dy
            if 0 <= sy < GRID_ROWS:
                scx, scy = sx * BLOCK_SIZE + BLOCK_SIZE / 2, sy * BLOCK_SIZE + BLOCK_SIZE / 2
                if self.puyo_images.get(self.puyo_colors[1]) is not None:
                    self.canvas.create_image(scx, scy, image=self.puyo_images[self.puyo_colors[1]])

        game_end_y = GRID_ROWS * BLOCK_SIZE
        self.canvas.create_line(0, game_end_y, SCREEN_WIDTH, game_end_y, fill="#FFFFFF", width=2)
        self.canvas.create_text(SCREEN_WIDTH / 2, game_end_y + (SCORE_PANEL_HEIGHT / 2),
                                text=f"SCORE: {self.score}", fill="#FFFFFF", font=("Arial", 16, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    game = PuyoPuyoStyleGame(root)
    root.mainloop()
