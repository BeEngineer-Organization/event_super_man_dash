# オブジェクトの枠表示とかできる？

import pyxel

WIDTH, HEIGHT = 128, 128
TRANSPARENT_COLOR = 12
SCENE_TITLE = 0
SCENE_GAME = 1
SCENE_RESULT = 2
BOY_STATUS_LIVE = 0
BOY_STATUS_DEAD = 1
SCROLL_BORDER_X = 80
GRAVITY = 1
JUMP_VELOCITY = -10
# CHECK_POINTS = [
#     (-1, -1),
#     (16, -1),
#     (16, 16),
#     (-1, 16),
#     (8, -1),
#     (16, 8),
#     (8, 16),
#     (-1, 8),
# ]
CHECK_POINTS = [
    [-1, -1],
    [16, -1],
    [16, 16],
    [-1, 16],
    [8, -1],
    [16, 8],
    [8, 16],
    [-1, 8],
]

# LIFE = 1

scroll_x = 0
velocity_x = 0
coins = []
enemies = []
# question_blocks = [[48, 32], [64, 32]]
question_blocks = []

fire = None


def get_tile(x, y):
    return pyxel.tilemap(0).pget(x, y)


def detect_collision(x, y):
    # coll_flags = [False, False, False, False, False, False, False, False]
    # for i, (px, py) in enumerate(CHECK_POINTS):
    #     if get_tile((x + px) // 8, (y + py) // 8)[1] == 6:
    #         coll_flags[i] = True
    # return coll_flags
    
    # coll_flags = []
    # for (px, py) in CHECK_POINTS:
    #     if get_tile((x + px) // 8, (y + py) // 8)[1] == 6:
    #         coll_flags.append(True)
    #     else:
    #         coll_flags.append(False)
    # return coll_flags

    coll_flags = []
    for [px, py] in CHECK_POINTS:
        if get_tile((x + px) // 8, (y + py) // 8)[1] == 6:
            coll_flags.append(True)
        else:
            coll_flags.append(False)
    return coll_flags


def check_goal(x, y):
    flag = False
    for px, py in CHECK_POINTS:
        if get_tile((x + px) // 8, (y + py) // 8)[1] == 14:
            flag = True
            break
    return flag


def spawn_coin(left_x, right_x):
    left_x = pyxel.ceil(left_x / 8)
    right_x = pyxel.floor(right_x / 8)
    for x in range(left_x, right_x + 1):
        for y in range(16):
            tile = get_tile(x, y)
            if tile == (0, 10):
                coins.append(Coin(x * 8, y * 8))


def spawn_enemy(left_x, right_x):
    left_x = pyxel.ceil(left_x / 8)
    right_x = pyxel.floor(right_x / 8)
    for x in range(left_x, right_x + 1):
        for y in range(16):
            tile = get_tile(x, y)
            if tile == (1, 10):
                enemies.append(Enemy(x * 8, y * 8))


class Coin:
    def __init__(self, x, y, w=16, h=16):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def draw(self):
        u = pyxel.frame_count // 3 % 2 * 16
        pyxel.blt(self.x, self.y, 0, u, 64, self.w, self.h, TRANSPARENT_COLOR)

class Fire:
    def __init__(self, x, y, w=16, h=16):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.time = 0

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 0, 120, self.w, self.h, TRANSPARENT_COLOR)
    
    def check_enemy_collision(self):
        global fire
        for enemy in enemies:
            if (
                self.x < enemy.x + enemy.w
                and self.x + self.w > enemy.x
                and self.y < enemy.y + enemy.h
                and self.y + self.h > enemy.y
            ):
                enemies.remove(enemy)
                fire = None

    def update(self):
        global fire
        self.time += 1
        if self.time > 10:
            fire = None
        else:
            self.x += 3
        self.check_enemy_collision()

class QuestionBlock:
    def __init__(self, x, y, w=16, h=16):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.breaked = False
    
    def draw_unbreaked_block(self):
        pyxel.blt(self.x, self.y, 0, 48, 48, 16, 16, TRANSPARENT_COLOR)

    def draw_breaked_block(self):
        pyxel.blt(self.x, self.y, 0, 16, 48, 16, 16, TRANSPARENT_COLOR)

    def draw(self):
        if self.breaked:
            self.draw_breaked_block()
        else:
            self.draw_unbreaked_block()

# class Item:

# class Mushroom(Item):

# class Flower(Item):



class Boy:
    def __init__(self, x, y, w=16, h=16, score=0):
        # 書き方
        self.x, self.y, self.w, self.h, self.score = x, y, w, h, score
        self.v_y, self.status, self.jump_status = 0, BOY_STATUS_LIVE, 1
        self.prev_x, self.prev_y = x, y

    def check_coin_collision(self):
        for coin in coins:
            # 書き方に対する説明足す
            if (
                self.x < coin.x + coin.w
                and self.x + self.w > coin.x
                and self.y < coin.y + coin.h
                and self.y + self.h > coin.y
            ):
                self.score += 1
                pyxel.play(2, 3)
                coins.remove(coin)

    def check_enemy_collision(self):
        for enemy in enemies:
            if (
                self.x < enemy.x + enemy.w
                and self.x + self.w > enemy.x
                and self.y < enemy.y + enemy.h
                and self.y + self.h > enemy.y
            ):
                if (
                    self.v_y > 0
                ):
                    enemies.remove(enemy)
                else:
                    pyxel.play(3, 4)
                    self.status = BOY_STATUS_DEAD
    
    # 当たり判定に関して
    # https://note.com/syun77/n/n88d78b0957dd
    def check_question_block_collision(self):
        for question_block in question_blocks:
            if (
                (self.x + self.w / 2) - (question_block.x + question_block.w / 2) < question_block.w / 2
                and (self.x + self.w / 2) - (question_block.x + question_block.w / 2) > -question_block.w / 2
                and self.y < question_block.y + question_block.h
                and self.y + self.h > question_block.y - 1
            ):
                if self.prev_y >= question_block.y + question_block.h:
                    question_blocks.remove(question_block)
                    

    def update(self):
        # グローバルに関する説明
        # 引数で処理できない？

        global scroll_x, fire
        if self.status != BOY_STATUS_LIVE:
            return
        self.prev_x = self.x
        self.prev_y = self.y
        coll_flags = detect_collision(self.x, self.y)
        # 条件縦で書いた方がよくね？
        if pyxel.btn(pyxel.KEY_LEFT) and self.x > scroll_x and not coll_flags[7]:
            self.x -= 2
            # print(2)
        if (
            pyxel.btn(pyxel.KEY_RIGHT)
            and self.x < scroll_x + WIDTH - self.w
            and not coll_flags[5]
        ):
            self.x += 2


        # 慣性つけたVer
        # global scroll_x, velocity_x
        # if self.status != BOY_STATUS_LIVE:
        #     return
        # coll_flags = detect_collision(self.x, self.y)
        # if (
        #     pyxel.btn(pyxel.KEY_RIGHT)
        #     and self.x < scroll_x + WIDTH - self.w
        #     and not coll_flags[5]
        #     and velocity_x < 2
        # ):
        #     # self.x += 2
        #     velocity_x += 0.1
        # elif (
        #     pyxel.btn(pyxel.KEY_LEFT) 
        #     and self.x > scroll_x 
        #     and not coll_flags[7] 
        #     and velocity_x > -2
        # ):
        #     # self.x -= 2
        #     velocity_x -= 0.1
        # else:
        #     if velocity_x > 0:
        #         velocity_x -= 0.2
        #     elif velocity_x < 0:
        #         velocity_x += 0.2
        #     if velocity_x < 0.1 and velocity_x > -0.1:
        #         velocity_x = 0
        # self.x += velocity_x

        # 物理の話必要？
        # https://www2.nhk.or.jp/school/watch/clip/?das_id=D0005401443_00000
        # https://www2.nhk.or.jp/school/watch/clip/?das_id=D0005401452_00000
        # https://wakariyasui.sakura.ne.jp/p/mech/rakutai/rakkabiseki-img/3121-40-a.gif
        self.v_y += GRAVITY
        new_y = self.y + self.v_y

        if self.v_y > 0:  # Falling
            while self.y < new_y:
                self.y += 1
                coll_flags = detect_collision(self.x, self.y)
                if coll_flags[2] or coll_flags[3]:
                    self.y = (self.y // 8) * 8
                    self.v_y = 0
                    self.jump_status = 0
                    break
        elif self.v_y < 0:  # Jumping
            while self.y > new_y:
                self.y -= 1
                coll_flags = detect_collision(self.x, self.y)
                if coll_flags[0] or coll_flags[1]:
                    self.y = (self.y // 8 + 1) * 8
                    self.v_y = 0
                    break
        
        

        self.check_coin_collision()
        self.check_enemy_collision()
        self.check_question_block_collision()

        if pyxel.btnp(pyxel.KEY_SPACE) and (coll_flags[2] or coll_flags[3]):
            # print("jump")
            self.v_y = JUMP_VELOCITY  # Jump velocity
            self.jump_status = 1
        
        if pyxel.btnp(pyxel.KEY_F) and (coll_flags[2] or coll_flags[3]):
            if not fire:
                fire = Fire(self.x, self.y)



        if self.y > 128:
            self.status = BOY_STATUS_DEAD
            pyxel.play(3, 4)

        if self.x > scroll_x + SCROLL_BORDER_X:
            last_scroll_x = scroll_x
            scroll_x = min(self.x - SCROLL_BORDER_X, 240 * 8)
            spawn_coin(last_scroll_x + 128, scroll_x + 127)
            spawn_enemy(last_scroll_x + 128, scroll_x + 127)
        
        # print(self.jump_status)
        
    def draw(self):
        u = 3 * 16 if self.jump_status else pyxel.frame_count // 3 % 2 * 16
        pyxel.blt(self.x, self.y, 0, u, 16, self.w, self.h, TRANSPARENT_COLOR)


class Enemy:
    def __init__(self, x, y, w=16, h=16):
        self.x, self.y, self.w, self.h = x, y, w, h
        # xじゃね？
        self.v_y = 0.5

    def update(self):
        self.x -= self.v_y

    def draw(self):
        u = pyxel.frame_count // 6 % 2 * 16
        pyxel.blt(self.x, self.y, 0, u, 88, self.w, self.h, TRANSPARENT_COLOR)


class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT)
        pyxel.load("./scene.pyxres")
        self.scene = SCENE_TITLE
        # BGM
        pyxel.sounds[0].set(
            "e3 e3 e3 c3 e3 g3 g2 "  # Super Mario Bros. theme intro
            "c3 g2 e2 a2 b2 a#2 a2 g2 e3 g3 a3 f3 g3 e3 c3 d3 b2 ", 
            "p", "6", "vffn fnff vffs vfnn", 25,
        )
        
        pyxel.sounds[1].set(
            "c3 c4 a2 a3 a#2 a3 g2 e3 g3 a3 f3 g3 e3 c3 d3 b2 "  # Super Mario Bros. theme continuation
            "c3 g2 e2 a2 b2 a#2 a2 g2 e3 g3 a3 f3 g3 e3 c3 d3 b2 ",
            "s", "6", "nnff vfff vvvv vfff svff vfff vvvv svnn", 25,
        )
        pyxel.sounds[2].set(
            "f0ra4r f0ra4r f0ra4r f0f0a4r", "n", "6622 6622 6622 6422", "f", 25
        )
        # コイン
        pyxel.sounds[3].set(
            "c3e3g3e4g4", # ノート（音の高さ）
            "t", # トーン（音色）
            "6", # ボリューム
            "f", # エフェクト（フェードイン）
            5 # スピード
        )
        # ゲームオーバーの効果音
        pyxel.sounds[4].set(
            "g2f2e2d2c2", # ノート（音の高さ）
            "t", # トーン（音色）
            "76543", # ボリューム
            "fffnn", # エフェクト（n=ノーマル、f=ファーストディケイ）
            10 # スピード
        )
        # 成功時の効果音
        pyxel.sounds[5].set(
            "c3e3g3c4e4", # ノート（音の高さ）
            "p", # トーン（音色）
            "66443", # ボリューム
            "nnffn", # エフェクト（n=ノーマル、f=ファーストディケイ）
            10 # スピード
        )
        # 失敗時の効果音
        pyxel.sounds[6].set(
            "g2f2e2d2c2", # ノート（音の高さ）
            "t", # トーン（音色）
            "76543", # ボリューム
            "fffnn", # エフェクト（n=ノーマル、f=ファーストディケイ）
            10 # スピード
        )
        pyxel.play(1, 4, loop=True)
        self.game_settings()

    def game_settings(self):
        pyxel.image(0).rect(0, 80, 16, 8, TRANSPARENT_COLOR)
        self.boy = Boy(0, 0)
        spawn_coin(0, 127)
        spawn_enemy(0, 127)
        question_blocks.append(QuestionBlock(48, 40))
        question_blocks.append(QuestionBlock(64, 40))
        pyxel.run(self.update, self.draw)

    def game_over(self):
        self.scene = SCENE_RESULT

    def clean_game_scene(self):
        global enemies, coins, scroll_x
        self.boy = None
        enemies = []
        coins = []
        scroll_x = 0

    def restart_game(self):
        self.boy = Boy(0, 0)

    def update_title_scene(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.scene = SCENE_GAME
            self.clean_game_scene()
            pyxel.stop(1)
            pyxel.play(0, [0, 1], loop=True)
            self.game_settings()

    def update_game_scene(self):
        if self.boy.status == BOY_STATUS_LIVE:
            self.boy.update()
            for enemy in enemies:
                enemy.update()
            # for question_block in question_blocks:
            #     question_block.update()
            if fire:
                fire.update()
            if check_goal(self.boy.x, self.boy.y):
                # ゴールした際のy座標をスコア化
                # print(self.boy.y)
                self.scene = SCENE_RESULT
                pyxel.play(3, 5)
                pyxel.stop(0)
                pyxel.play(1, 2, loop=True)
        elif self.boy.status == BOY_STATUS_DEAD:
            self.game_over()
            pyxel.stop(0)
            pyxel.play(1, 2, loop=True)

    def update_result(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.scene = SCENE_GAME
            self.clean_game_scene()
            pyxel.stop(1)
            pyxel.play(0, [0, 1], loop=True)
            self.game_settings()
        elif pyxel.btnp(pyxel.KEY_R):
            self.scene = SCENE_TITLE

    def update(self):
        if self.scene == SCENE_TITLE:
            self.update_title_scene()
        elif self.scene == SCENE_GAME:
            self.update_game_scene()
        elif self.scene == SCENE_RESULT:
            self.update_result()

    def draw_title_scene(self):
        pyxel.text(scroll_x + 36, 40, "SUPER MAN DASH", 7)
        # スペース開けた方が読みやすい
        # 日本語入れたかったらできる？
        pyxel.text(scroll_x + 28, 80, "- START [ SPACE ] -", 7)

    def draw_game_scene(self):
        if self.boy.status == BOY_STATUS_LIVE:
            pyxel.camera()
            pyxel.bltm(0, 0, 0, scroll_x, 0, WIDTH, HEIGHT)
            pyxel.camera(scroll_x, 0)
            self.boy.draw()
        for coin in coins:
            coin.draw()
        for enemy in enemies:
            enemy.draw()
        for question_block in question_blocks:
            question_block.draw()

        
        if fire:
            fire.draw()
        score_text = "Score:{:>4}".format(self.boy.score)
        pyxel.text(scroll_x + 5, 4, score_text, 7)

    def draw_result(self):
        score_text = "Score:{:>4}".format(self.boy.score)
        pyxel.text(scroll_x + 5, 4, score_text, 7)
        if self.boy.status == BOY_STATUS_LIVE:
            pyxel.text(scroll_x + 36, 40, "YOU SUCCESSED", 7)
        else:
            pyxel.text(scroll_x + 36, 40, "YOU FAILED", 7)
        pyxel.text(scroll_x + 32, 60, "- RESTART[R] -", 7)
        pyxel.text(scroll_x + 32, 80, "- RETURN[SPACE] -", 7)

    def draw(self):
        pyxel.cls(0)
        if self.scene == SCENE_TITLE:
            self.draw_title_scene()
        elif self.scene == SCENE_GAME:
            self.draw_game_scene()
        elif self.scene == SCENE_RESULT:
            self.draw_result()


App()


# class Enemy:

#     def __init__(self, x, y, w=16, h=16, v_x=0.5):
#         self.x, self.y, self.w, self.h, self.v_x = x, y, w, h, v_x

#     def draw(self):
#         u = pyxel.frame_count // 6 % 2 * 16
#         pyxel.blt(self.x, self.y, 0, u, 88, self.w, self.h, TRANSPARENT_COLOR)