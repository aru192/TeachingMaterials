# Python初心者向け教材「NEXTぷよを表示してみよう！」

パズルゲームで次に出てくるぷよを予測するために欠かせない**「NEXTぷよ」の表示機能**を追加していきます。

---

## ① 今回追記・修正するコード

既存コードに以下の変更・追記を行います。

<pre style="background-color: #1e1e1e; color: #f8f8f2; padding: 16px; border-radius: 8px; font-family: 'Consolas', 'Courier New', monospace; line-height: 1.5; overflow-x: auto;">
# 1. NEXT表示エリアの幅を追加設定（定数部分）
NEXT_AREA_WIDTH = 120
TOTAL_WIDTH = SCREEN_WIDTH + NEXT_AREA_WIDTH

class MinimumPuyoGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Python言語でぷよぷよ風ゲーム")
        self.root.resizable(False, False)

        # ★【ここを修正】キャンバスの幅を TOTAL_WIDTH に変更
        self.canvas = tk.Canvas(root, width=TOTAL_WIDTH, height=SCREEN_HEIGHT, bg=COLORS[0], highlightthickness=0)
        self.canvas.pack()

        # （中略）

        # ★【ここを追記】あらかじめNEXT（次のぷよ）を用意しておく
        self.next_puyo = [random.randint(1, 4), random.randint(1, 4)]
        # ★【追記ここまで】

        self.spawn_puyo()
        self.game_loop()

    def spawn_puyo(self):
        # ★【ここを修正】NEXTから現在のぷよを受け取り、新しいNEXTを生成する
        self.puyo_colors = self.next_puyo
        self.next_puyo = [random.randint(1, 4), random.randint(1, 4)]
        # ★【修正ここまで】

        self.puyo_x = 3
        self.puyo_y = 0
        self.rot_state = 0
        self.is_chaining = False

    def draw(self):
        self.canvas.delete("all")

        # ★【ここを追記】フィールドとNEXTエリアを区切る縦線を描く
        self.canvas.create_line(SCREEN_WIDTH, 0, SCREEN_WIDTH, SCREEN_HEIGHT, fill="#555588", width=2)

        # （中略：既存のぷよ描画処理）

        # ★【ここを追記】NEXT 描画処理の呼び出し
        self.draw_next_puyo()

    # ★【ここを追記】NEXTエリア描画用のメソッドを新規追加
    def draw_next_puyo(self):
        base_x = SCREEN_WIDTH + 60  # NEXTエリアの中央X座標
        self.canvas.create_text(base_x, 30, text="NEXT", fill="white", font=("Arial", 12, "bold"))
        self.draw_single_puyo(base_x, 60, self.next_puyo[0])   # 軸ぷよ（上）
        self.draw_single_puyo(base_x, 100, self.next_puyo[1])  # 子ぷよ（下）

    def draw_single_puyo(self, cx, cy, color_code):
        """ 指定した中心座標 (cx, cy) にぷよを1つ描画する補助メソッド """
        if self.puyo_images.get(color_code) is not None:
            self.canvas.create_image(cx, cy, image=self.puyo_images[color_code])
        else:
            r = BLOCK_SIZE // 2 - 2
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=COLORS[color_code], outline="")
</pre>

---

## ② コード解説

* **`NEXT_AREA_WIDTH = 120` / `TOTAL_WIDTH = SCREEN_WIDTH + NEXT_AREA_WIDTH`**：画面右側にNEXTを表示するためのスペース（120px）を元の幅に足し出して全体の幅を計算しています。
* **`self.canvas = tk.Canvas(..., width=TOTAL_WIDTH, ...)`**：Tkinter画面の横幅を `TOTAL_WIDTH` に拡張し、表示領域を広げています。
* **`self.next_puyo = [random.randint(1, 4), random.randint(1, 4)]`**：次に降ってくるぷよの色番号2つをリスト形式（例: `[1, 3]`）で事前に作成しています。リストの1つ目の値は `self.next_puyo[0]` で取得できます。
* **`self.puyo_colors = self.next_puyo`**：新しいぷよが出現する際、準備していた `next_puyo` を操作ぷよへ渡し、その後に新しいNEXTを生成します。（※順番を逆にするとデータが上書きされて消えてしまいます）
* **`self.canvas.create_text(...)`**：Tkinterの Canvas 上に「NEXT」の文字を描画します。
* **`self.canvas.create_line(...)`**：プレイ画面とNEXT表示欄を区切る仕切り線を描画します。

---

## ③ 完成イメージ

実行すると、右側に枠線と仕切り線が表示され、次のぷよが確認できるようになります。

```text
  【プレイ領域】        【NEXT領域】
+-----------------------+------------+
|                       |  NEXT      |
|           ○           |   [ Red ]  |
|           ●           |   [ Blue]  |
|                       |            |
|   ●                   |            |
|   ○ ○                 |            |
+-----------------------+------------+