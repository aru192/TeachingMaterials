# 第5回：ツムを消して、制限時間付きゲームを完成させよう！

## 1. コードの追記

第4回では、マウスで同じ色のツムを選び、白い線でつなげられるようになりました。

今回は、**3個以上つないだツムを消す処理・消えたツムの補充・60秒の制限時間**を追加して、ツムツム風ゲームを完成させます。

第1回から第4回までのコードは書き換えず、指定された場所に**追記**してください。

### ① 消えたツムを補充する関数を追加

`add_tsumu()`の処理が終わった後、クラス内に追記します。

<pre style="background-color: #1e1e1e; color: #f8f8f2; padding: 16px; border-radius: 8px; font-family: 'Consolas', 'Courier New', monospace; line-height: 1.5; overflow-x: auto;">
87 |     # ★【ここから追記】
88 |     def add_new_tsumu(self):
89 |
90 |         tsumu = arcade.SpriteCircle(
91 |             RADIUS,
92 |             random.choice(COLORS)
93 |         )
94 |
95 |         tsumu.center_x = random.randint(
96 |             FIELD_LEFT + WALL + RADIUS,
97 |             FIELD_RIGHT - WALL - RADIUS
98 |         )
99 |
100|         tsumu.center_y = FIELD_TOP - RADIUS
101|
102|         tsumu.type = tsumu.color
103|
104|         self.tsumus.append(tsumu)
105|
106|         self.physics.add_sprite(
107|             tsumu,
108|             mass=1,
109|             elasticity=0.05,
110|             friction=0.8,
111|             damping=1.2
112|         )
113|     # ★【ここまで追記】
</pre>

`add_new_tsumu()`では、消えたツムを補充するため、新しいツムをフィールド上部に作成します。

### ② 残り時間を画面に表示

`on_draw()`内の選択したツムを表示する処理の後に追記します。

<pre style="background-color: #1e1e1e; color: #f8f8f2; padding: 16px; border-radius: 8px; font-family: 'Consolas', 'Courier New', monospace; line-height: 1.5; overflow-x: auto;">
187|         # ★【ここから追記】
188|         arcade.draw_text(
189|             f"TIME: {int(self.game_time)}",
190|             WIDTH / 2,
191|             655,
192|             arcade.color.BLACK,
193|             22,
194|             anchor_x="center"
195|         )
196|         # ★【ここまで追記】
</pre>

### ③ 制限時間を減らす

第3回で作成した`on_update()`内の位置補正処理が終わった後に追記します。

<pre style="background-color: #1e1e1e; color: #f8f8f2; padding: 16px; border-radius: 8px; font-family: 'Consolas', 'Courier New', monospace; line-height: 1.5; overflow-x: auto;">
197|         # ★【ここから追記】
198|         self.game_time -= dt
199|
200|         if self.game_time <= 0:
201|
202|             self.game_time = 0
203|             self.game_over = True
204|             self.close()
205|
206|             return
207|         # ★【ここまで追記】
</pre>

`self.game_time`から`dt`を引くことで、ゲームを実行している間に残り時間が減っていきます。

### ④ 消えた分だけ新しいツムを補充

③の処理の下に追記します。

<pre style="background-color: #1e1e1e; color: #f8f8f2; padding: 16px; border-radius: 8px; font-family: 'Consolas', 'Courier New', monospace; line-height: 1.5; overflow-x: auto;">
208|         # ★【ここから追記】
209|         while len(self.tsumus) < MAX_TSUMU:
210|             self.add_new_tsumu()
211|         # ★【ここまで追記】
</pre>

ツムの数が`MAX_TSUMU`より少なくなると、`add_new_tsumu()`を使って不足分を補充します。

### ⑤ 3個以上つないだツムを消す

第4回で作成した`on_mouse_drag()`の処理が終わった後、クラス内に追記します。

<pre style="background-color: #1e1e1e; color: #f8f8f2; padding: 16px; border-radius: 8px; font-family: 'Consolas', 'Courier New', monospace; line-height: 1.5; overflow-x: auto;">
242|     # ★【ここから追記】
243|     def on_mouse_release(
244|         self,
245|         x,
246|         y,
247|         button,
248|         modifiers
249|     ):
250|
251|         if len(self.selected) >= 3:
252|
253|             for tsumu in self.selected:
254|
255|                 self.tsumus.remove(tsumu)
256|                 self.physics.remove_sprite(tsumu)
257|
258|         self.selected = []
259|     # ★【ここまで追記】
</pre>

コード入力後は実行してみましょう！

同じ色のツムを3個以上つないでマウスを離すとツムが消え、上から新しいツムが落ちてきます。画面上部には残り時間が表示され、`60`秒経過するとゲーム画面が閉じれば完成です。

---

## 2. コード解説

・`add_new_tsumu()`：消したツムの代わりとなる新しいツムを、フィールド上部に作成します。

・`f"TIME: {int(self.game_time)}"`：現在の残り時間を文字列に入れて表示します。

・`int()`：小数を整数に変換します。残り時間を見やすく表示するために使用します。

・`self.game_time -= dt`：前回の更新から経過した時間を引いて、残り時間を減らします。

・`self.game_time <= 0`：残り時間が`0`以下になったかを調べます。

・`self.close()`：ゲームのウィンドウを閉じます。

・`while len(self.tsumus) < MAX_TSUMU`：ツムが`45`個より少ない間、新しいツムを追加します。

・`on_mouse_release()`：マウスのボタンを離したときに実行される処理です。

・`len(self.selected) >= 3`：選択したツムが3個以上あるかを調べます。

・`remove()`：リストから指定したツムを削除します。

・`remove_sprite()`：物理演算からもツムを削除します。

・`self.selected = []`：選択状態を空にして、次の操作に備えます。

---

## 3. 完成イメージ（今回の動く様子）

同じ色のツムをマウスで3個以上つないで離すと、選択したツムが消えます。

消えた分だけフィールド上部から新しいツムが追加され、重力によって下へ落下します。

また、画面上部の`TIME`が`60`秒から減っていき、`0`になるとゲームが終了します。

第4回：同じ色のツムをつなげる
↓
第5回：3個以上で消す → 新しいツムを補充 → 制限時間でゲーム終了

これで全5回を通して、**ツムツム風ゲームが完成**しました。

---

## 4. 確認問題

**① ツムが消える条件として正しいものを選びなさい。**

1. 1個以上選択する
2. 2個以上選択する
3. 3個以上選択する
4. 5個以上選択する

A.＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿

<!--
解答：③
解説：`len(self.selected) >= 3`によって、3個以上選択されている場合に削除します。
-->

**② ○×問題：`len()`を使うと、リストに入っている要素の数を取得できる。**

A.＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿

<!--
解答：○
解説：`len(self.tsumus)`では、現在存在しているツムの数を取得できます。
-->

**③ `self.close()`は何をする処理ですか？**

1. ツムを削除する
2. ゲームウィンドウを閉じる
3. ツムを追加する
4. 残り時間を増やす

A.＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿

<!--
解答：②
解説：`self.close()`を実行すると、ゲームウィンドウが閉じます。
-->

**④ Python3エンジニア認定基礎試験レベル：次のコードを実行した後の`items`として正しいものを選びなさい。**

`items = [10, 20, 30]`
`items.remove(20)`

1. `[10, 20]`
2. `[20, 30]`
3. `[10, 30]`
4. `[]`

A.＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿

<!--
解答：③
解説：`remove(20)`によって、リストから値`20`が削除されます。
-->

**⑤ `while len(self.tsumus) < MAX_TSUMU:`の役割として正しいものを選びなさい。**

1. ツムをすべて削除する
2. ツムの色を変更する
3. ツムが最大数になるまで補充する
4. ゲーム時間を増やす

A.＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿

<!--
解答：③
解説：ツムの数が`MAX_TSUMU`より少ない間、`add_new_tsumu()`を繰り返して補充します。
-->

---

## 5. 発展課題

### 課題1：2個から消せるようにしてみよう

現在は3個以上のツムをつなぐと消えます。2個以上で消えるように変更してみましょう。

ヒント：選択数を確認している`len(self.selected) >= 3`の数値を変更します。

<!--
参考コード例：
if len(self.selected) >= 2:
-->

### 課題2：ゲーム時間を30秒にしてみよう

現在のゲーム時間を`60`秒から`30`秒に変更してみましょう。

ヒント：第2回で設定した`GAME_TIME`の値を変更します。

<!--
参考コード例：
GAME_TIME = 30
-->

### 課題3：ツムの最大数を増やしてみよう

ツムを消した後、常に`50`個まで補充されるゲームに変更してみましょう。

ヒント：ツムの最大数を管理している`MAX_TSUMU`を変更します。画面内が混雑しすぎる場合は元の値に戻しましょう。

<!--
参考コード例：
MAX_TSUMU = 50
-->
