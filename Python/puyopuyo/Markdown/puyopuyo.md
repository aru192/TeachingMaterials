# 改造回：ゲームの動きと連鎖をスムーズにしよう！

## 1. コードの追記
コードのマス目（インデント）を揃えながら、下記の**「★【ここを追記】」**がついている行をプログラムに追加しましょう。
```python
    def move_puyo(self, dx):
        if self.is_chaining: return
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        nx, nsx = self.puyo_x + dx, self.puyo_x + dx + sub_dx
        ny, nsy = self.puyo_y, self.puyo_y + sub_dy

        if 0 <= nx < GRID_COLS and 0 <= nsx < GRID_COLS:
            if self.grid[ny][nx] == 0 and 0 <= nsy < GRID_ROWS and self.grid[nsy][nsx] == 0:
                self.puyo_x = nx
================================================================================
                self.draw()  # ★【ここを追記】
================================================================================

    def rotate_puyo(self):
        if self.is_chaining: return
        old_rot = self.rot_state
        self.rot_state = (self.rot_state + 1) % 4
        sub_dx, sub_dy = self.get_sub_puyo_offset()
        sx, sy = self.puyo_x + sub_dx, self.puyo_y + sub_dy

        if not (0 <= sx < GRID_COLS and 0 <= sy < GRID_ROWS and self.grid[sy][sx] == 0):
            self.rot_state = old_rot

================================================================================
        self.draw()  # ★【ここを追記】
================================================================================

    def chain_loop(self):
        moved = False
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS - 2, -1, -1):
                if self.grid[y][x] != 0 and self.grid[y+1][x] == 0:
                    self.grid[y+1][x] = self.grid[y][x]
                    self.grid[y][x] = 0
                    moved = True

================================================================================
        self.draw()  # ★【ここを追記】
================================================================================

        if moved:
            self.root.after(150, self.chain_loop)
            return
```
コード入力後は実行してみましょう。エラーが出た場合は行数とインデント（マス目）を見直してみましょう。

---
<!-- ===== ここで 2 ページ目へ移行 ===== -->

## 2. コード解説

`self.draw()`：決めておいた手順を「今すぐ実行して！」と命令するトリガー（引き金）です。キーを押した瞬間や、ぷよが1マス落ちた瞬間にこのスイッチを押すことで、画面が最新の状態に更新されます。  
*(※ `def draw(self)` には「画面を一度きれいに消して、最新のぷよの絵を配置する」という処理が書かれています。)*

`if self.is_chaining: return`：「現在、ぷよが連鎖（消滅中や自動落下中）している最中かどうか」を判定し、連鎖中であればその先のキー操作や通常落下をすべて無視して処理を中断（ロック）します。  
*(※連鎖中にプレイヤーが勝手にぷよを動かしてしまい、データが壊れてエラーが起きるのを防ぐ大切な仕組みです。)*

---

## 3. 確認問題

**Q1. 今回複数箇所に追加した `self.draw()` は、ゲームの中でどのような「役割」を持っていますか？**  
( A.                                                                                              )

**Q2. `chain_loop` の中で `self.draw()` を書く位置（インデント）を間違えて、`for` ループの内側（`moved = True` のすぐ下など）に書いてしまうと、ゲームの動きはどうなってしまうでしょうか？**  
( A.                                                                                              )

**Q3. なぜキー操作や自動落下の関数の先頭には、`if self.is_chaining: return` という記述が必要なのでしょうか？**  
( A.                                                                                              )

---

## 4. 発展課題

自分なりのゲームを作るための新たな挑戦！

* **普段の落下速度をアップ：**  
  `self.root.after(500, self.game_loop)` の数値（500）を小さく変更してみよう。

* **連鎖落下のスピードを調整：**  
  `chain_loop` 内の `self.root.after(150, self.chain_loop)` の数値（150）を変更して、連鎖時の落下を「素早く」したり「ゆっくり」にしてみよう。