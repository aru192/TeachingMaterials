import arcade
import random
import math

# 画面サイズとゲーム設定
SCREEN_WIDTH = 450
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Python Tsumu Tsumu - Skill Edition"

TSUMU_RADIUS = 24
MAX_TSUMUS = 45  # 画面内に維持するツムの数
GAME_TIME = 60   # 制限時間（秒）

# スキル発動に必要なツム消去数
SKILL_REQUIREMENT = 10 

# ツムの種類（色と名前）
TSUMU_TYPES = [
    {"name": "Mickey", "color": arcade.color.RED},
    {"name": "Minnie", "color": arcade.color.PINK},
    {"name": "Donald", "color": arcade.color.LIGHT_BLUE},
    {"name": "Pooh", "color": arcade.color.YELLOW},
    {"name": "Alien", "color": arcade.color.GREEN}
]

class TsumuGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        
        self.tsumu_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        
        # 物理エンジン
        self.physics_engine = arcade.PymunkPhysicsEngine(gravity=(0, -800))
        
        # ゲーム状態の変数
        self.score = 0
        self.time_left = GAME_TIME
        self.game_over = False
        
        # チェインの管理用
        self.current_chain = []
        self.current_type = None

        # スキル関連の変数
        self.my_tsumu_type = random.randint(0, len(TSUMU_TYPES) - 1)
        self.skill_count = 0
        self.skill_ready = False

        # 【新規】シャッフルのクールダウン（連打防止用）
        self.shuffle_cooldown = 0.0

    def setup(self):
        """ ゲームの初期設定 """
        # 壁の作成（底、左、右）
        floor = arcade.SpriteSolidColor(SCREEN_WIDTH, 20, color=arcade.color.GRAY)
        floor.center_x = SCREEN_WIDTH / 2
        floor.center_y = 40 # 下部にスキルUIを置くため少し上に設置
        self.wall_list.append(floor)
        self.physics_engine.add_sprite(floor, body_type=arcade.PymunkPhysicsEngine.STATIC, friction=1.0)
        
        left_wall = arcade.SpriteSolidColor(20, SCREEN_HEIGHT, color=arcade.color.GRAY)
        left_wall.center_x = 10
        left_wall.center_y = SCREEN_HEIGHT / 2
        self.wall_list.append(left_wall)
        self.physics_engine.add_sprite(left_wall, body_type=arcade.PymunkPhysicsEngine.STATIC, friction=0.1)
        
        right_wall = arcade.SpriteSolidColor(20, SCREEN_HEIGHT, color=arcade.color.GRAY)
        right_wall.center_x = SCREEN_WIDTH - 10
        right_wall.center_y = SCREEN_HEIGHT / 2
        self.wall_list.append(right_wall)
        self.physics_engine.add_sprite(right_wall, body_type=arcade.PymunkPhysicsEngine.STATIC, friction=0.1)

        # 最初のツムを一気に降らせる
        for _ in range(MAX_TSUMUS):
            self.spawn_tsumu(is_start=True)

    def spawn_tsumu(self, is_start=False):
        """ ツムを上空から生成 """
        type_idx = random.randint(0, len(TSUMU_TYPES) - 1)
        tsumu_info = TSUMU_TYPES[type_idx]
        
        tsumu = arcade.SpriteCircle(TSUMU_RADIUS, color=tsumu_info["color"])
        tsumu.center_x = random.randint(50, SCREEN_WIDTH - 50)
        tsumu.center_y = random.randint(SCREEN_HEIGHT, SCREEN_HEIGHT + 200) if is_start else SCREEN_HEIGHT + 50
        
        tsumu.tsumu_type = type_idx
        tsumu.is_selected = False
        
        self.tsumu_list.append(tsumu)
        self.physics_engine.add_sprite(tsumu, mass=1.0, elasticity=0.1, friction=0.6)

    def trigger_center_skill(self):
        """ 【新規】画面中央のツムを一気消去するスキル """
        if not self.skill_ready or self.game_over:
            return

        center_x = SCREEN_WIDTH / 2
        center_y = SCREEN_HEIGHT / 2
        skill_range = 130  # 消去する中央からの半径（ピクセル）

        # 消去対象のツムをリストアップ
        to_delete = []
        for tsumu in self.tsumu_list:
            dist = math.sqrt((tsumu.center_x - center_x)**2 + (tsumu.center_y - center_y)**2)
            if dist <= skill_range:
                to_delete.append(tsumu)

        # 対象を消去
        deleted_count = len(to_delete)
        if deleted_count > 0:
            self.score += deleted_count * 150  # スキル消去は少し高得点
            for tsumu in to_delete:
                self.physics_engine.remove_sprite(tsumu)
                self.tsumu_list.remove(tsumu)

        # スキル状態のリセットと、次のマイツムをランダム決定
        self.skill_count = 0
        self.skill_ready = False
        self.my_tsumu_type = random.randint(0, len(TSUMU_TYPES) - 1)

    def on_draw(self):
        """ 画面描画 """
        self.clear()
        
        self.wall_list.draw()
        self.tsumu_list.draw()
        
        # なぞっている最中の線
        if len(self.current_chain) > 1:
            points = [(t.center_x, t.center_y) for t in self.current_chain]
            arcade.draw_line_strip(points, arcade.color.WHITE, 5)
            
        for tsumu in self.current_chain:
            arcade.draw_circle_outline(tsumu.center_x, tsumu.center_y, TSUMU_RADIUS + 3, arcade.color.WHITE, 3)

# --- UI表示 ---
        # スコアとタイマー
        arcade.draw_text(f"SCORE: {self.score}", 30, SCREEN_HEIGHT - 40, arcade.color.WHITE, 18)
        arcade.draw_text(f"TIME: {int(max(0, self.time_left))}", SCREEN_WIDTH - 130, SCREEN_HEIGHT - 40, arcade.color.WHITE, 18)

        # 【新規】下部のスキル表示エリア
        target_info = TSUMU_TYPES[self.my_tsumu_type]
        arcade.draw_text(f"MY TSUMU:", 20, 13, arcade.color.WHITE, 12)
        arcade.draw_circle_filled(120, 20, 12, target_info["color"])

        # 【新規】スキルゲージの描画
        gauge_width = 180
        gauge_ratio = min(1.0, self.skill_count / SKILL_REQUIREMENT)
        
        # 枠線：第3引数を「10（下）」、第4引数を「30（上）」にします
        arcade.draw_lrbt_rectangle_outline(160, 160 + gauge_width, 10, 30, arcade.color.WHITE, 2)
        
        # 中身：第3引数を「12（下）」、第4引数を「28（上）」にします
        gauge_color = arcade.color.ORANGE if self.skill_ready else arcade.color.YELLOW
        if gauge_ratio > 0:
            arcade.draw_lrbt_rectangle_filled(162, 162 + int((gauge_width-4) * gauge_ratio), 12, 28, gauge_color)

        # 【新規】シャッフル（扇風機）ボタンの描画
        # COOL_GRAY ➔ LIGHT_GRAY に変更
        shuffle_btn_color = arcade.color.GRAY if self.shuffle_cooldown > 0 else arcade.color.LIGHT_GRAY
        arcade.draw_lrbt_rectangle_filled(20, 100, 5, 35, shuffle_btn_color)
        arcade.draw_text("SHUFFLE", 32, 13, arcade.color.BLACK, 11, bold=True)

        # 【新規】スキル発動ボタン：第3引数を「5（下）」、第4引数を「35（上）」にします
        btn_color = arcade.color.GOLDENROD if self.skill_ready else arcade.color.GRAY
        arcade.draw_lrbt_rectangle_filled(360, 440, 5, 35, btn_color)
        arcade.draw_text("SKILL", 375, 13, arcade.color.BLACK, 12, bold=True)
        if self.game_over:
            # 確実かつシンプルな記述に変更
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 0, 0, 150))
            arcade.draw_text("TIME UP", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.YELLOW, 36, align="center", anchor_x="center", anchor_y="center")
    
    def on_update(self, delta_time):
        """ ゲームロジックの更新 """
        if self.game_over: return

        self.physics_engine.step()

        if self.shuffle_cooldown > 0:
            self.shuffle_cooldown -= delta_time
        
        self.time_left -= delta_time
        if self.time_left <= 0:
            self.game_over = True

        if len(self.tsumu_list) < MAX_TSUMUS:
            self.spawn_tsumu()

    def get_tsumu_at_position(self, x, y):
        for tsumu in self.tsumu_list:
            distance = math.sqrt((tsumu.center_x - x)**2 + (tsumu.center_y - y)**2)
            if distance <= TSUMU_RADIUS + 10:
                return tsumu
        return None

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_over: return

        # 【新規】SHUFFLEボタンがクリックされたか判定
        if 20 <= x <= 100 and 5 <= y <= 35:
            if self.shuffle_cooldown <= 0:
                # 全てのツムに上方向＋ランダムな横方向の力を加える（風を送る）
                for tsumu in self.tsumu_list:
                    physics_object = self.physics_engine.get_physics_object(tsumu)
                    if physics_object and physics_object.body:
                        # 上向きの力(400〜600)と、左右に散らす力(-150〜150)
                        force_x = random.randint(-150, 150)
                        force_y = random.randint(400, 600)
                        # 一瞬だけ衝撃（Impulse）を与える
                        physics_object.body.apply_impulse_at_local_point((force_x, force_y))
                
                self.shuffle_cooldown = 0.5 # 0.5秒間は再発動不可に
            return
        
        # 【新規】SKILLボタンがクリックされたか判定
        if 360 <= x <= 440 and 5 <= y <= 35:
            self.trigger_center_skill()
            return

        tsumu = self.get_tsumu_at_position(x, y)
        if tsumu:
            self.current_chain = [tsumu]
            self.current_type = tsumu.tsumu_type
            tsumu.is_selected = True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.game_over or self.current_type is None: return
        
        tsumu = self.get_tsumu_at_position(x, y)
        if tsumu and tsumu not in self.current_chain:
            if tsumu.tsumu_type == self.current_type:
                last_tsumu = self.current_chain[-1]
                dist = math.sqrt((tsumu.center_x - last_tsumu.center_x)**2 + (tsumu.center_y - last_tsumu.center_y)**2)
                if dist < TSUMU_RADIUS * 3:
                    self.current_chain.append(tsumu)
                    tsumu.is_selected = True

    def on_mouse_release(self, x, y, button, modifiers):
        if self.game_over: return
        
        chain_count = len(self.current_chain)
        
        if chain_count >= 3:
            self.score += chain_count * 100 + (chain_count - 3) * 50
            
            # 【新規】消したツムが「指定されたマイツム」ならゲージを増やす
            if self.current_type == self.my_tsumu_type and not self.skill_ready:
                self.skill_count += chain_count
                if self.skill_count >= SKILL_REQUIREMENT:
                    self.skill_ready = True
            
            for tsumu in self.current_chain:
                self.physics_engine.remove_sprite(tsumu)
                self.tsumu_list.remove(tsumu)
        
        for tsumu in self.current_chain:
            tsumu.is_selected = False
        self.current_chain = []
        self.current_type = None

def main():
    window = TsumuGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
