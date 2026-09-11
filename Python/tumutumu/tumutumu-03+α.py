import arcade
import random
import math

WIDTH = 450
HEIGHT = 700
RADIUS = 24
MAX_TSUMU = 45
GAME_TIME = 60
WALL = 30 # ★発展課題2
FIELD_LEFT = 45
FIELD_RIGHT = 405
FIELD_BOTTOM = 30
FIELD_TOP = 625

COLORS = [
    arcade.color.RED,
    arcade.color.PINK,
    arcade.color.LIGHT_BLUE,
    arcade.color.YELLOW,
    arcade.color.GREEN
]

class TsumuGame(arcade.Window):
    def __init__(self):
        super().__init__(
            WIDTH,
            HEIGHT,
            "Python言語でツムツム風ゲーム"
        )
        self.tsumus = arcade.SpriteList()
        self.selected = []
        self.game_time = GAME_TIME
        self.game_over = False
        self.physics = arcade.PymunkPhysicsEngine(
            gravity=(0, -10000) # ★発展課題1
        )
        self.add_tsumu()
        for _ in range(MAX_TSUMU - 1):
            self.add_tsumu()

        left_wall = arcade.SpriteSolidColor(
            WALL,
            FIELD_TOP - FIELD_BOTTOM,
            arcade.color.GRAY
        )

        left_wall.center_x = FIELD_LEFT
        left_wall.center_y = (
            FIELD_BOTTOM + FIELD_TOP
        ) / 2

        right_wall = arcade.SpriteSolidColor(
            WALL,
            FIELD_TOP - FIELD_BOTTOM,
            arcade.color.GRAY
        )

        right_wall.center_x = FIELD_RIGHT
        right_wall.center_y = (
            FIELD_BOTTOM + FIELD_TOP
        ) / 2

        bottom_wall = arcade.SpriteSolidColor(
            FIELD_RIGHT - FIELD_LEFT,
            WALL,
            arcade.color.GRAY
        )

        bottom_wall.center_x = (
            FIELD_LEFT + FIELD_RIGHT
        ) / 2
        bottom_wall.center_y = FIELD_BOTTOM

        self.physics.add_sprite(
            left_wall,
            body_type=arcade.PymunkPhysicsEngine.STATIC
        )

        self.physics.add_sprite(
            right_wall,
            body_type=arcade.PymunkPhysicsEngine.STATIC
        )

        self.physics.add_sprite(
            bottom_wall,
            body_type=arcade.PymunkPhysicsEngine.STATIC
        )

    def add_tsumu(self):
        tsumu = arcade.SpriteCircle(
            RADIUS,
            random.choice(COLORS)
        )
        tsumu.center_x = WIDTH / 2
        tsumu.center_y = HEIGHT / 2
        self.tsumus.append(tsumu)
        
        tsumu.center_x = random.randint(
            FIELD_LEFT + WALL + RADIUS,
            FIELD_RIGHT - WALL - RADIUS
        )

        tsumu.center_y = random.randint(
            FIELD_BOTTOM + WALL + RADIUS + 20,
            FIELD_TOP - RADIUS
        )

        tsumu.type = tsumu.color

        self.physics.add_sprite(
            tsumu,
            mass=1,
            elasticity=0.05,
            friction=0.8,
            damping=1.2
        )

    def on_draw(self):
        self.clear(arcade.color.SKY_BLUE)

        arcade.draw_lbwh_rectangle_filled(
            FIELD_LEFT,
            FIELD_BOTTOM,
            FIELD_RIGHT - FIELD_LEFT,
            FIELD_TOP - FIELD_BOTTOM,
            arcade.color.WHITE
        )
        self.tsumus.draw()

        arcade.draw_lbwh_rectangle_filled(
            FIELD_LEFT - WALL / 2,
            FIELD_BOTTOM,
            WALL,
            FIELD_TOP - FIELD_BOTTOM,
            arcade.color.GRAY
        )

        arcade.draw_lbwh_rectangle_filled(
            FIELD_RIGHT - WALL / 2,
            FIELD_BOTTOM,
            WALL,
            FIELD_TOP - FIELD_BOTTOM,
            arcade.color.GRAY
        )

        arcade.draw_lbwh_rectangle_filled(
            FIELD_LEFT,
            FIELD_BOTTOM - WALL / 2,
            FIELD_RIGHT - FIELD_LEFT,
            WALL,
            arcade.color.GRAY
        )

    def on_update(self, dt):
        if self.game_over:
            return

        self.physics.step()

        for tsumu in self.tsumus:

            tsumu.center_x = max(
                FIELD_LEFT + WALL / 2 + RADIUS,
                min(
                    tsumu.center_x,
                    FIELD_RIGHT - WALL / 2 - RADIUS
                )
            )

            tsumu.center_y = max(
                FIELD_BOTTOM + WALL / 2 + RADIUS,
                tsumu.center_y
            )

game = TsumuGame()
arcade.run()