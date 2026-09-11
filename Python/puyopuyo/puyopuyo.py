import tkinter as tk
import random
import math
import os
from tkinter import messagebox

# --- 定数定義 ---
GRID_COLS = 6       # フィールドの横マス数
GRID_ROWS = 12      # フィールドの縦マス数
BLOCK_SIZE = 40     # 1マスのピクセルサイズ

SCREEN_WIDTH = GRID_COLS * BLOCK_SIZE               # 画面の横幅 (240px)
SCORE_AREA_HEIGHT = 60                              # スコア表示エリアの高さ
SCREEN_HEIGHT = (GRID_ROWS * BLOCK_SIZE) + SCORE_AREA_HEIGHT # 画面の総高さ (540px)

NORMAL_SPEED = 2.5  # 通常時のぷよの落下速度
FAST_SPEED = 12.0   # 下キー入力時の高速落下速度

# 画像が読み込めなかった場合の代用色
COLORS = {
    0: "#2A1D67",  # 背景色（濃い紫）
    1: "#ff3d3d",  # 赤
    2: "#3d3dff",  # 青
    3: "#3dff3d",  # 緑
    4: "#ffff3d",   # 黄
    5: "#00FFDD",
    6: "#FFC800"
}

# 連鎖数に応じた得点倍率（ボーナス）
CHAIN_BONUS = {
    1: 0, 2: 8, 3: 16, 4: 32, 5: 64, 6: 96, 7: 128, 8: 160,
    9: 192, 10: 224, 11: 256, 12: 288, 13: 320, 14: 352,
    15: 384, 16: 416, 17: 448, 18: 480, 19: 512
}

# 同時に消した「色数」に応じたボーナス
COLOR_BONUS = {
    1: 0, 2: 3, 3: 6, 4: 12, 5: 24
}

def get_connect_bonus(count):
    # 同一色で4個以上繋がった際、5個目以降の「連結数ボーナス」を返す
    if count <= 3: return 0
    if count == 4: return 0
    if count == 5: return 2
    if count == 6: return 3
    if count == 7: return 4
    if count == 8: return 5
    if count == 9: return 6
    if count == 10: return 7
    return 10

class PuyoBgImageGame:
    def __init__(self, root):
        # ゲームの初期化、ウィンドウ設定、キーバインドの設定
        self.root = root
        self.root.title("Python言語でぷよぷよ")
        self.root.resizable(False, False) # ウィンドウサイズ固定

        # 描画用キャンバスの生成
        self.canvas = tk.Canvas(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg=COLORS[0], highlightthickness=0)
        self.canvas.pack()

        self.current_fall_speed = NORMAL_SPEED # 現在の落下速度

        # 操作用キーイベントの登録 (キーバインド)
        self.root.bind("<Left>", lambda e: self.move_puyo(-1))          # 左矢印：左移動
        self.root.bind("<Right>", lambda e: self.move_puyo(1))          # 右矢印：右移動
        self.root.bind("<Up>", lambda e: self.rotate_puyo())            # 上矢印：回転
        self.root.bind("<space>", lambda e: self.hard_drop())           # スペース：一瞬で落とす
        self.root.bind("<KeyPress-Down>", self.start_fast_drop)         # 下矢印（押しっぱなし）：高速落下
        self.root.bind("<KeyRelease-Down>", self.stop_fast_drop)        # 下矢印（離す）：通常落下に戻す

        # フィールド管理用2次元配列 (0は空、1〜4はぷよの色番号)
        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        
        # 操作中ぷよの情報
        self.puyo_colors = [0, 0]   # [軸ぷよの色, 子ぷよの色]
        self.puyo_x = 3             # 軸ぷよの現在マスX座標
        self.puyo_y = BLOCK_SIZE * 1.0 # 軸ぷよの現在のY座標 (ピクセル単位)
        self.rot_state = 0          # 子ぷよの回転状態 (0:上, 1:右, 2:下, 3:左)
        
        # 各マスの演出アニメーション用状態管理（着地時のバウンド、消滅時の点滅）
        self.anim_grid = [[{"frame": 0, "erase_frame": 0, "color": 0} for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

        # フラグ管理
        self.is_gameover = False    # ゲームオーバー中か
        self.is_chaining = False    # 連鎖・消滅・自由落下の処理中か（操作不能にする）

        # スコア・連鎖数管理
        self.score = 0
        self.chain_count = 0
        self.display_chain_msg = "" # 画面表示用の「〇連鎖！」の文字列

        # 画像読み込み処理の実行
        self.puyo_images = {}
        self.bg_image = None
        self.load_images()

        self.puyo_queue = []
        for _ in range(2):
            self.puyo_queue.append

        # 最初のぷよを生成して、メインループを開始
        self.spawn_puyo()
        self.game_loop()

    def load_images(self):
        # プログラムの場所を基準にして画像を読み込む処理
        # プログラム（puyopuyo.py）があるフォルダの絶対パスを自動取得
        base_dir = os.path.dirname(os.path.abspath(__file__))

        """
        外部のぷよ画像を読み込む（ファイルがない場合は色で表示） 
        推奨画像サイズ:40×40ピクセル
        """
        # 基準フォルダと画像フォルダのパスを正しく結合する
        file_mapping = {
            1: os.path.join(base_dir, "puyo", "puyo_red.png"),
            2: os.path.join(base_dir, "puyo", "puyo_blue.png"),
            3: os.path.join(base_dir, "puyo", "puyo_green.png"),
            4: os.path.join(base_dir, "puyo", "puyo_yellow.png"),
            5: os.path.join(base_dir, "puyo", "whitepuyo.png"),
            6: os.path.join(base_dir, "puyo", "oogonpuyo.png")
        }
        
        for color_code, filename in file_mapping.items():
            if os.path.exists(filename):
                try:
                    self.puyo_images[color_code] = tk.PhotoImage(file=filename)
                except Exception as e:
                    self.puyo_images[color_code] = None
            else:
                self.puyo_images[color_code] = None

        # 背景画像（background.png）も同じように位置を合わせる
        bg_filename = os.path.join(base_dir, "background.png")
        if os.path.exists(bg_filename):
            try:
                self.bg_image = tk.PhotoImage(file=bg_filename)
            except Exception as e:
                self.bg_image = None
        else:
            self.bg_image = None
        """
        背景画像の読み込み
        推奨サイズ:240×540ピクセル（横：6マス×40px＝240px、縦：12マス×40px＋スコア領域60px＝540px）
        """
        bg_filename = "background.png"
        if os.path.exists(bg_filename):
            try:
                self.bg_image = tk.PhotoImage(file=bg_filename)
            except Exception as e:
                self.bg_image = None
        else:
            self.bg_image = None

    def start_fast_drop(self, event):
        # 下キーが押された時、連鎖中でなければ落下速度を高速にする
        if not self.is_chaining: self.current_fall_speed = FAST_SPEED

    def stop_fast_drop(self, event):
        # 下キーが離された時、落下速度を通常に戻す
        self.current_fall_speed = NORMAL_SPEED

    def get_sub_puyo_offset(self):
        # 回転状態 (0〜3) に応じて、軸ぷよから見た子ぷよの相対位置 (X, Y) を返す
        offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)] # 0:上, 1:右, 2:下, 3:左
        return offsets[self.rot_state]

    def spawn_puyo(self):
        # 新しいぷよを画面最上部に出現させる。上部が詰まっていたらゲームオーバー
        self.puyo_colors = [random.randint(1, 4), random.randint(1, 4)] # ランダムに2色決定
        self.puyo_x = 3
        self.puyo_y = BLOCK_SIZE * 1.0
        self.rot_state = 0
        self.is_chaining = False
        self.chain_count = 0
        self.display_chain_msg = ""
        self.current_fall_speed = NORMAL_SPEED
        
        # ぷよの出現位置（上から2マス目の真ん中）がすでに埋まっていたら死亡
        if self.grid[1][3] != 0:
            self.is_gameover = True
            messagebox.showinfo("Game Over", f"ゲームオーバー！\n最終スコア: {self.score}")
            self.root.destroy()

    def move_puyo(self, dx):
        # 操作中ぷよを左右に移動させる (dx: -1が左、1が右)
        if self.is_gameover or self.is_chaining: return
        
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        next_ax = self.puyo_x + dx          # 移動後の軸ぷよのX
        next_sx = next_ax + sub_dx          # 移動後の子ぷよのX
        
        # 壁判定：画面外にはみ出るなら移動不可
        if next_ax < 0 or next_ax >= GRID_COLS or next_sx < 0 or next_sx >= GRID_COLS: return
        
        # 衝突判定：移動先のマスに既存のぷよがないかチェック（ピクセル単位のY座標から該当マスを算出）
        ay1, ay2 = int(self.puyo_y // BLOCK_SIZE), int((self.puyo_y + BLOCK_SIZE - 1) // BLOCK_SIZE)
        sy1, sy2 = ay1 + sub_dy, ay2 + sub_dy
        if (self.grid[ay1][next_ax] == 0 and self.grid[ay2][next_ax] == 0 and
            0 <= sy1 < GRID_ROWS and self.grid[sy1][next_sx] == 0 and
            0 <= sy2 < GRID_ROWS and self.grid[sy2][next_sx] == 0):
            self.puyo_x = next_ax # すべてクリアなら移動確定

    def rotate_puyo(self):
        # 操作中ぷよを時計回りに90度回転させる
        if self.is_gameover or self.is_chaining: return
        
        old_rot = self.rot_state
        self.rot_state = (self.rot_state + 1) % 4 # 状態を1進める
        
        # 回転先が壁や他のぷよにめり込まないかチェック
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        sx = self.puyo_x + sub_dx
        sy1 = int(self.puyo_y // BLOCK_SIZE) + sub_dy
        sy2 = int((self.puyo_y + BLOCK_SIZE - 1) // BLOCK_SIZE) + sub_dy
        
        # もしめり込む場合は回転をキャンセルし元の状態に戻す (簡易的な壁蹴りは無し)
        if (sx < 0 or sx >= GRID_COLS or 
            sy1 < 0 or sy1 >= GRID_ROWS or self.grid[sy1][sx] != 0 or
            sy2 < 0 or sy2 >= GRID_ROWS or self.grid[sy2][sx] != 0):
            self.rot_state = old_rot

    def check_collision(self, next_y):
        # ぷよが指定したY座標(next_y)に下がったとき、地面や他のぷよに衝突するかを判定
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        ax = self.puyo_x
        ay = int((next_y + BLOCK_SIZE - 1) // BLOCK_SIZE) # 軸ぷよの下端マス
        sx = ax + sub_dx
        sy = ay + sub_dy # 子ぷよの下端マス
        
        if ay >= GRID_ROWS or sy >= GRID_ROWS: return True                # 最下層（地面）に達した
        if self.grid[ay][ax] != 0: return True                            # 軸ぷよの位置が埋まっている
        if sy >= 0 and self.grid[sy][sx] != 0: return True                # 子ぷよの位置が埋まっている
        return False

    def handle_gravity(self):
        # フィールド全体を見回り、宙に浮いているぷよを1マス下に自由落下させる
        moved = False
        # 下から順にスキャン（最下段の1個上から開始）
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS - 2, -1, -1):
                # 自分がぷよで、下が空マスで、かつ現在消滅アニメ中ではない場合
                if self.grid[y][x] != 0 and self.grid[y+1][x] == 0 and self.anim_grid[y][x]["erase_frame"] == 0:
                    self.grid[y+1][x] = self.grid[y][x] # 下に移動
                    self.grid[y][x] = 0                  # 元の場所を空に
                    self.anim_grid[y+1][x]["frame"] = 1  # 着地バウンド用のアニメーションフラグをON
                    moved = True
        return moved # 1つでも移動が発生した場合はTrueを返す

    def check_connections(self):
        # 同じ色のぷよが4個以上繋がっているかを幅優先探索 (BFS) で検出し、スコア計算・消滅予約を行う
        visited = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        to_erase = set() # 消去するぷよの座標リスト
        groups = []      # 今回消えるグループの情報 [(色, 連結数), ...]

        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                color = self.grid[y][x]
                # まだ調べていないぷよがある場合
                if color != 0 and not visited[y][x] and self.anim_grid[y][x]["erase_frame"] == 0:
                    queue = [(x, y)]
                    connected = [(x, y)]
                    visited[y][x] = True
                    
                    # 近隣を探す（幅優先探索）
                    while queue:
                        cx, cy = queue.pop(0)
                        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]: # 上下左右
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
                                if not visited[ny][nx] and self.grid[ny][nx] == color and self.anim_grid[ny][nx]["erase_frame"] == 0:
                                    visited[ny][nx] = True
                                    queue.append((nx, ny))
                                    connected.append((nx, ny))
                    
                    # 4個以上繋がっていれば消滅リストに追加
                    if len(connected) >= 4:
                        groups.append((color, len(connected)))
                        for p in connected: to_erase.add(p)
        
        # もし消えるぷよがあった場合の処理
        if to_erase:
            self.chain_count += 1
            self.display_chain_msg = f"{self.chain_count} 連鎖！"
            total_puyo_cleared = len(to_erase) # 今回消した総ぷよ数
            
            # ぷよぷよ公式準拠のスコア計算
            c_bonus_sum = sum(get_connect_bonus(g[1]) for g in groups) # 連結ボーナス合計
            unique_colors = len(set(g[0] for g in groups))              # 何色同時に消したか
            color_bonus_val = COLOR_BONUS.get(unique_colors, 24)       # 多色(同消し)ボーナス
            chain_bonus_val = CHAIN_BONUS.get(self.chain_count, 512)   # 連鎖ボーナス

            total_bonus = chain_bonus_val + c_bonus_sum + color_bonus_val
            if total_bonus == 0: total_bonus = 1

            # 得点 ＝ 消した総数 × ボーナス合計 × 10
            step_score = total_puyo_cleared * total_bonus * 10
            self.score += step_score

            # 対象のぷよに消滅アニメーション（点滅）を開始させる
            for x, y in to_erase:
                self.anim_grid[y][x]["erase_frame"] = 1
            return True
        return False # 何も消えなかった

    def lock_puyo(self):
        # 操作中ぷよが着地した時、フィールドのマス（配列）にその色を固定する
        self.is_chaining = True # 連鎖チェックモード（操作不能）に移行
        ax = self.puyo_x
        ay = int(round(self.puyo_y / BLOCK_SIZE))
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        sx = ax + sub_dx
        sy = ay + sub_dy
        
        # 軸ぷよの配置
        if 0 <= ay < GRID_ROWS and 0 <= ax < GRID_COLS:
            self.grid[ay][ax] = self.puyo_colors[0]
            self.anim_grid[ay][ax]["frame"] = 1 # 着地時アニメをON
        # 子ぷよの配置
        if 0 <= sy < GRID_ROWS and 0 <= sx < GRID_COLS:
            self.grid[sy][sx] = self.puyo_colors[1]
            self.anim_grid[sy][sx]["frame"] = 1 # 着地時アニメをON
            
        # 0.1秒後に連鎖・自由落下処理のループを開始
        self.root.after(100, self.chain_loop)

    def chain_loop(self):
        # 連鎖→自由落下→再判定 を自動で繰り返すための中核ループ処理
        # まず宙に浮いているぷよがあれば落とす（落ちきるまで繰り返す）
        if self.handle_gravity():
            self.root.after(150, self.chain_loop)
            return

        # 消滅アニメーション（点滅）が走っている最中なら、終わるまで待つ
        erasing = False
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                if self.anim_grid[y][x]["erase_frame"] > 0:
                    erasing = True
        if erasing:
            self.root.after(50, self.chain_loop)
            return

        # 4個以上繋がっているぷよがあれば消す（消えたら再度chain_loopを呼んで落下に戻る）
        if self.check_connections():
            self.root.after(50, self.chain_loop)
            return
            
        # 落下するものも消えるものも無くなったら連鎖終了。次のぷよを出す
        self.spawn_puyo()

    def hard_drop(self):
        # スペースキー用：一瞬で衝突する最下部までぷよを落として固定する
        if self.is_gameover or self.is_chaining: return
        while not self.check_collision(self.puyo_y + 1):
            self.puyo_y += 1
        self.lock_puyo()

    def update_animations(self):
        # 各マスの演出アニメーションのフレーム数を毎フレーム進める処理
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                # 着地時のぷよぷよとしたバウンドアニメの進行
                if self.anim_grid[y][x]["frame"] > 0:
                    self.anim_grid[y][x]["frame"] += 1
                    if self.anim_grid[y][x]["frame"] > 20: # 20フレームで終了
                        self.anim_grid[y][x]["frame"] = 0

                # ぷよが消える時の点滅アニメの進行
                if self.anim_grid[y][x]["erase_frame"] > 0:
                    self.anim_grid[y][x]["erase_frame"] += 1
                    if self.anim_grid[y][x]["erase_frame"] > 18: # 18フレームで終了
                        self.anim_grid[y][x]["erase_frame"] = 0
                        self.grid[y][x] = 0 # アニメが終わったら実際にデータを消す

    def game_loop(self):
        # 約16ミリ秒ごとに呼ばれる、ゲーム全体のメインリアルタイム処理
        if self.is_gameover: return

        # プレイヤーが操作中の場合、一定速度で自動自由落下させる
        if not self.is_chaining:
            if not self.check_collision(self.puyo_y + self.current_fall_speed):
                self.puyo_y += self.current_fall_speed
            else:
                self.lock_puyo() # 下に衝突したら配置確定

        self.update_animations() # アニメーションの更新
        self.draw()              # 画面の再描画
        self.root.after(16, self.game_loop) # 約60FPS (16ms後) に自分を再アナウンス

    def draw_x_marks(self):
        # 窒息ライン（ゲームオーバーライン）である左から3番目(インデックス2)の最上段にバツ印を描画
        target_cols = [2]
        for col in target_cols:
            x1 = col * BLOCK_SIZE + 8
            y1 = 0 * BLOCK_SIZE + 8
            x2 = (col + 1) * BLOCK_SIZE - 8
            y2 = (0 + 1) * BLOCK_SIZE - 8
            self.canvas.create_line(x1, y1, x2, y2, fill="#cc3333", width=3)
            self.canvas.create_line(x2, y1, x1, y2, fill="#cc3333", width=3)

    def draw(self):
        # キャンバス上のオブジェクトを全て消去し、最新の状態に描き直す
        self.canvas.delete("all")

        # 最背面に背景画像を描画
        if self.bg_image is not None:
            self.canvas.create_image(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, image=self.bg_image)

        # バツ印の描画
        self.draw_x_marks()

        # 配置済みのフィールド上のぷよを順に描画
        for y in range(GRID_ROWS):
            for x in range(GRID_COLS):
                color_code = self.grid[y][x]
                if color_code != 0:
                    frame = self.anim_grid[y][x]["frame"]
                    e_frame = self.anim_grid[y][x]["erase_frame"]
                    # 点滅ロジック：フレーム数を3で割った偶奇で白表示にするか決める
                    is_flash = True if (e_frame > 0 and (e_frame // 3) % 2 == 0) else False
                    self.draw_puyo_smart(x * BLOCK_SIZE, y * BLOCK_SIZE, color_code, frame, is_flash)

        # 現在操作している「移動中のぷよ（2個1組）」を描画
        if not self.is_gameover and not self.is_chaining:
            ax_pixel = self.puyo_x * BLOCK_SIZE
            # 軸ぷよの描画
            self.draw_puyo_smart(ax_pixel, self.puyo_y, self.puyo_colors[0], 0, False)
            # 子ぷよの描画 (オフセット位置を計算して加算)
            sub_dx, sub_dy = self.get_sub_puyo_offset()
            self.draw_puyo_smart(ax_pixel + (sub_dx * BLOCK_SIZE), self.puyo_y + (sub_dy * BLOCK_SIZE), self.puyo_colors[1], 0, False)

        # 画面下部（フィールド外）のスコア・連鎖情報エリアの描画
        border_y = GRID_ROWS * BLOCK_SIZE
        # スコア背景の黒い長方形
        self.canvas.create_rectangle(0, border_y, SCREEN_WIDTH, SCREEN_HEIGHT, fill="#0f0f0f", outline="")
        self.canvas.create_line(0, border_y, SCREEN_WIDTH, border_y, fill="#444444", width=2)
        
        # スコアテキスト
        score_text = f"SCORE: {self.score:06d}"
        self.canvas.create_text(
            SCREEN_WIDTH / 2, border_y + 20, 
            text=score_text, fill="#ffffff", font=("Helvetica", 16, "bold")
        )

        # 連鎖数が1以上のときは「〇連鎖！」の文字を出す
        if self.display_chain_msg:
            self.canvas.create_text(
                SCREEN_WIDTH / 2, border_y + 45, 
                text=self.display_chain_msg, fill="#ffcc00", font=("Helvetica", 12, "bold")
            )

    def draw_puyo_smart(self, px, py, color_code, frame, is_flash):
        # 1個のぷよを賢くきれいに描画する（画像、図形代用、バウンド・点滅エフェクト対応）
        if py + BLOCK_SIZE <= 0: return # 画面より上にはみ出ている場合は描画スキップ
        cx = px + BLOCK_SIZE / 2
        cy = py + BLOCK_SIZE / 2

        # 消滅時の「白フラッシュ」点滅状態
        if is_flash:
            r = BLOCK_SIZE / 2 - 2
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#ffffff", outline="")
            return

        # 画像ファイルが存在する場合の描画
        if self.puyo_images.get(color_code) is not None:
            offset_y = 0
            if frame > 0: # 着地バウンド時の縦揺れをサイン波と減衰関数(math.exp)で計算
                decay = math.exp(-frame * 0.15)
                offset_y = 5 * math.sin(frame * 0.5) * decay
            self.canvas.create_image(cx, cy + offset_y, image=self.puyo_images[color_code])
        
        # 画像ファイルが無い場合の代替描画（Tkinterの綺麗な楕円とハイライトの白丸でぷよっぽく見せる）
        else:
            color_str = COLORS[color_code]
            r = BLOCK_SIZE / 2 - 2
            scale_x, scale_y = 1.0, 1.0
            if frame > 0: # 着地バウンド時の潰れる（横に広がり縦に縮む）変形をコサイン波で表現
                decay = math.exp(-frame * 0.15)
                wave = -0.3 * math.cos(frame * 0.5) * decay
                scale_x = 1.0 - wave
                scale_y = 1.0 + wave

            # ぷよ本体の円形
            self.canvas.create_oval(cx - r * scale_x, cy - r * scale_y, cx + r * scale_x, cy + r * scale_y, fill=color_str, outline="")
            # ぷよの「ハイライト（光沢）」の白丸
            if scale_x > 0.5 and scale_y > 0.5:
                self.canvas.create_oval(cx - r*0.4*scale_x, cy - r*0.5*scale_y, cx - r*0.1*scale_x, cy - r*0.2*scale_y, fill="white", outline="")

# プログラムの開始処理
if __name__ == "__main__":
    root = tk.Tk()
    game = PuyoBgImageGame(root)
    root.mainloop() # Tkinterのイベント待機ループ（アプリが閉じられるまで持続）
