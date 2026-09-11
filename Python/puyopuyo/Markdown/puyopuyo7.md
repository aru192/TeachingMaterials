# 改造回：ぷよぷよに新しい色を追加してみよう！

## 1. コードの追記・変更

コードのマス目（インデント）を揃えながら、下記の**「★【ここを変更】」**や**「★【ここを追記】」**がついている行をプログラムに反映させましょう。

今回の改造では、紫色のぷよを新しく追加して、5色のぷよがランダムで登場するようにします！

```python
COLORS = {
    0: "#2A1D67",  # 背景色
    1: "#ff3d3d", 2: "#3d3dff", 3: "#3dff3d", 4: "#ffff3d",
    5: "#a03dff"   # ★【ここを追記】
}

class MinimumPuyoGame:

    def load_images(self):
        file_mapping = {
            1: "puyo_red.png", 2: "puyo_blue.png", 3: "puyo_green.png", 4: "puyo_yellow.png",
            5: "puyo_purple.png"  # ★【ここを追記】
        }
        for color_code, filename in file_mapping.items():
            if os.path.exists(filename):
                try:
                    self.puyo_images[color_code] = tk.PhotoImage(file=filename)
                except Exception:
                    self.puyo_images[color_code] = None
            else:
                self.puyo_images[color_code] = None

    def spawn_puyo(self):
        self.puyo_colors = [random.randint(1, 5), random.randint(1, 5)]  # ★【ここを変更】
        self.puyo_x = 3
        self.puyo_y = 0
        self.rot_state = 0
        self.is_chaining = False
        
        if self.grid[0][3] != 0:
            print("GAME OVER")
            self.root.destroy()
```
コード入力後は実行してみましょう。エラーが出た場合は行数とインデント（マス目）を見直してみましょう。

---

## 2. コード解説
`random.randint(a, b)`：指定した範囲の整数をランダムに1つ選んでくれる仕組み（乱数生成）です。  
(※ random.randint(1, 5) と書くと、1, 2, 3, 4, 5 のいずれかの整数が均等な確率で返されます。指定した終わりの数（5）も含まれるのが特徴です。)

`COLORS` などの「辞書（dict）」：キー（Key）と値（Value）をペアにして管理するデータの構造です。  
(※ `5: "#a03dff"` のように「5という数字が指定されたらこの紫色を使う」という対応関係を登録できます。COLORS[5] と呼び出すことで、対応する値を取り出すことができます。)

`file_mapping.items()`：「辞書」の中に登録されているキーと値のペアを1つずつ取り出して処理するための文法です。  
(※ for color_code, filename in file_mapping.items(): と書くことで、1〜5の色コードとそれぞれの画像ファイル名を順番に取り出し、繰り返し画像読み込み処理を行っています。)

---

## 3.完成イメージ
赤・青・緑・黄に加え、紫色のぷよが画面上に登場するようになっていたら完成です！

---

## 4. 確認問題
**Q1. 次のプログラムを実行したとき、画面に出力される値として正しいものを1つ選びましょう。**

```python
import random

num = random.randint(1, 5)
print(num)
```

ア：1、2、3、4 のどれかが選ばれる

イ：1、2、3、4、5 のどれかが選ばれる

ウ：2、3、4 のどれかが選ばれる

エ：1 から 5 までの小数（例：3.14など）が選ばれる

A.＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿

**Q2. Pythonの「辞書（dict）」に関する説明として、正しいものを1つ選びましょう。**

ア：辞書は [1, 2, 3] のように角カッコを使って書く。

イ：辞書は「キー（Key）」と「値（Value）」をペアにしてデータを管理する。

ウ：辞書の中にあるデータは、一度作ったら後から追加や変更ができない。

エ：`COLORS[5]` と書くと、5番目の位置にあるデータを順番に読み出す。

A.＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿

**Q3. `random.randint(1, 5)` の部分を `random.randint(1, 3)` に書き換えると、登場するぷよの色数はいくつになりますか？また、ゲームは難しくなりますか、それとも簡単になりますか？**

A.＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿ 

---

## 5. 発展課題
自分なりのゲームを作るための新たな挑戦！

* **さらに色を追加してみよう！：**
  まずは今回覚えた手順を使って、6番目の色 `6: "#ff8c00"`（オレンジ色）を追加してみよう。

* **出現する色を「3色だけ」にして「激甘モード」を作ってみよう！：**
  `spawn_puyo` 内の `random.randint(1, 5)` を書き換えて、3色しか出ない超イージーモードを作って連鎖をたくさん発生させてみよう。