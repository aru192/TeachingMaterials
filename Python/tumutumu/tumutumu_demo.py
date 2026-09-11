import arcade
import random
import math

SCREEN_WIDTH = 450
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Python Tsumu Tsumu - Minimal Edition"

TSUMU_RADIUS = 24
MAX_TSUMUS = 45  # 画面内に維持するツムの数

# ツムの種類（色）
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
        
        # チェインの管理用
        self.current_chain = []
        self.current_type = None

    def setup(self):
        """ 外枠（床・左右の壁）の作成と初期ツムの生成 """
        # 床
        floor = arcade.SpriteSolidColor(SCREEN_WIDTH, 20, color=arcade.color.GRAY)
        floor.center_x = SCREEN_WIDTH / 2
        floor.center_y = 10
        self.wall_list.append(floor)
        self.physics_engine.add_sprite(floor, body_type=arcade.PymunkPhysicsEngine.STATIC, friction=1.0)
        
        # 左壁
        left_wall = arcade.SpriteSolidColor(20, SCREEN_HEIGHT, color=arcade.color.GRAY)
        left_wall.center_x = 10
        left_wall.center_y = SCREEN_HEIGHT / 2
        self.wall_list.append(left_wall)
        self.physics_engine.add_sprite(left_wall, body_type=arcade.PymunkPhysicsEngine.STATIC, friction=0.1)
        
        # 右壁
        right_wall = arcade.SpriteSolidColor(20, SCREEN_HEIGHT, color=arcade.color.GRAY)
        right_wall.center_x = SCREEN_WIDTH - 10
        right_wall.center_y = SCREEN_HEIGHT / 2
        self.wall_list.append(right_wall)
        self.physics_engine.add_sprite(right_wall, body_type=arcade.PymunkPhysicsEngine.STATIC, friction=0.1)

        # 初期ツムを生成
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
        
        self.tsumu_list.append(tsumu)
        self.physics_engine.add_sprite(tsumu, mass=1.0, elasticity=0.1, friction=0.6)

    def on_draw(self):
        """ 画面描画 """
        self.clear()
        
        self.wall_list.draw()
        self.tsumu_list.draw()
        
        # なぞっている最中の線と選択中のハイライト描画
        if len(self.current_chain) > 1:
            points = [(t.center_x, t.center_y) for t in self.current_chain]
            arcade.draw_line_strip(points, arcade.color.WHITE, 5)
            
        for tsumu in self.current_chain:
            arcade.draw_circle_outline(tsumu.center_x, tsumu.center_y, TSUMU_RADIUS + 3, arcade.color.WHITE, 3)

    def on_update(self, delta_time):
        """ 物理計算の更新と不足ツムの補充 """
        self.physics_engine.step()

        if len(self.tsumu_list) < MAX_TSUMUS:
            self.spawn_tsumu()

    def get_tsumu_at_position(self, x, y):
        """ 指定位置にあるツムを取得 """
        for tsumu in self.tsumu_list:
            distance = math.sqrt((tsumu.center_x - x)**2 + (tsumu.center_y - y)**2)
            if distance <= TSUMU_RADIUS + 10:
                return tsumu
        return None

    def on_mouse_press(self, x, y, button, modifiers):
        """ つかみ始め（チェイン開始） """
        tsumu = self.get_tsumu_at_position(x, y)
        if tsumu:
            self.current_chain = [tsumu]
            self.current_type = tsumu.tsumu_type

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """ なぞり動作（チェイン追加） """
        if self.current_type is None:
            return
        
        tsumu = self.get_tsumu_at_position(x, y)
        if tsumu and tsumu not in self.current_chain:
            if tsumu.tsumu_type == self.current_type:
                last_tsumu = self.current_chain[-1]
                dist = math.sqrt((tsumu.center_x - last_tsumu.center_x)**2 + (tsumu.center_y - last_tsumu.center_y)**2)
                if dist < TSUMU_RADIUS * 3:
                    self.current_chain.append(tsumu)

    def on_mouse_release(self, x, y, button, modifiers):
        """ 離したとき（3つ以上なら消去） """
        if len(self.current_chain) >= 3:
            for tsumu in self.current_chain:
                self.physics_engine.remove_sprite(tsumu)
                self.tsumu_list.remove(tsumu)
        
        self.current_chain = []
        self.current_type = None

def main():
    window = TsumuGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
