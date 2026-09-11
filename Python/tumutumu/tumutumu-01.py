import arcade
import random
import math

WIDTH = 450
HEIGHT = 700
RADIUS = 24
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
        self.add_tsumu()

    def add_tsumu(self):
        tsumu = arcade.SpriteCircle(
            RADIUS,
            random.choice(COLORS)
        )
        tsumu.center_x = WIDTH / 2
        tsumu.center_y = HEIGHT / 2
        self.tsumus.append(tsumu)

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

game = TsumuGame()
arcade.run()