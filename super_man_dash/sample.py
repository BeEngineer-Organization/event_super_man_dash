import pyxel
import time

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

# scroll_x = 0

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

def get_tile(x, y):
    return pyxel.tilemap(0).pget(x, y)

def detect_collision(x, y):
    coll_flags = []
    for [px, py] in CHECK_POINTS:
        if get_tile( (x + px) // 8, (y + py) // 8 )[1] == 6:
            coll_flags.append(True)
        else:
            coll_flags.append(False)
    return coll_flags

class Boy:
    def __init__(self, x, y, w=16, h=16):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.status = BOY_STATUS_LIVE
        self.v_y = 0
        self.jump_status = 1
        self.prev_x, self.prev_y = x, y
        self.score = 0

    def update(self, scroll_x, enemies, game_scene, coins, itemblocks):
        # global scroll_x

        coll_flags = detect_collision(self.x, self.y)
        self.prev_x = self.x
        self.prev_y = self.y

        if pyxel.btn(pyxel.KEY_LEFT) and self.x > scroll_x and not(coll_flags[7]):
            self.x -= 2
        if pyxel.btn(pyxel.KEY_RIGHT) and self.x < scroll_x + WIDTH - self.w and not(coll_flags[5]):
            self.x += 2
            # print(self.x)

        if self.x > scroll_x + SCROLL_BORDER_X:
            scroll_x = min(self.x - SCROLL_BORDER_X, 240 * 8)

        self.v_y += GRAVITY
        coll_flags = detect_collision(self.x, self.y)

        if self.v_y < 0:
            jumping_distance = 0
            while jumping_distance >= self.v_y:
                jumping_coll_flags = detect_collision(self.x, self.y + jumping_distance - 8)
                if jumping_coll_flags[0] or jumping_coll_flags[1] or jumping_coll_flags[4]:
                    self.v_y = 0
                    self.y += jumping_distance
                    break
                jumping_distance -= 1
        else:
            falling_distance = 0
            while falling_distance <= self.v_y:
                falling_coll_flags = detect_collision(self.x, self.y + falling_distance)
                if falling_coll_flags[2] or falling_coll_flags[3] or falling_coll_flags[6]:
                    self.v_y = 0
                    self.y += falling_distance
                    self.jump_status = 0
                    break
                falling_distance += 1
        self.y += self.v_y 

        if pyxel.btnp(pyxel.KEY_SPACE) and (coll_flags[2] or coll_flags[3]):
            self.v_y = JUMP_VELOCITY
            self.jump_status = 1
        
        enemies, game_scene = self.check_enemy_collision(enemies, game_scene)

        coins = self.check_coin_collision(coins)

        itemblocks, coins = self.check_item_block_collision(itemblocks, coins)

        if self.y > 128:
            game_scene = SCENE_RESULT
            pyxel.play(1, 4)
            pyxel.play(0, 2, loop=True)
            self.status = BOY_STATUS_DEAD

        return scroll_x, enemies, game_scene, coins, itemblocks

    def draw(self):
        if self.jump_status:
            u = 3 * 16
        else:
            u = pyxel.frame_count // 3 % 2 * 16
        pyxel.blt(self.x, self.y, 0, u, 16, self.w, self.h, TRANSPARENT_COLOR)

    def check_enemy_collision(self, enemies, game_scene):
        for enemy in enemies:
            if (
                self.x < enemy.x + enemy.w
                and self.x > enemy.x - self.w
                and self.y < enemy.y + enemy.h
                and self.y > enemy.y - self.h
            ):
                if (
                    self.prev_x < enemy.x + enemy.w
                    and self.prev_x > enemy.x - self.w
                    and self.prev_y < enemy.y - self.h
                ):
                    enemies.remove(enemy)
                    pyxel.play(1, 3)
                    self.score += 1
                else:
                    game_scene = SCENE_RESULT
                    pyxel.play(1, 4)
                    pyxel.play(0, 2, loop=True)
                    self.status = BOY_STATUS_DEAD
        return enemies, game_scene
    
    def check_coin_collision(self, coins):
        for coin in coins:
            if (
                self.x < coin.x + coin.w
                and self.x > coin.x - self.w
                and self.y < coin.y + coin.h
                and self.y > coin.y - self.h
            ):

                coins.remove(coin)
                pyxel.play(1, 3)
                self.score += 1

        return coins

    def check_item_block_collision(self, itemblocks, coins):
        for itemblock in itemblocks:
            if (
                (self.x + self.w / 2) - (itemblock.x + itemblock.w / 2) < itemblock.w / 2
                and (self.x + self.w / 2) - (itemblock.x + itemblock.w / 2) > -itemblock.w / 2
                and self.y < itemblock.y + itemblock.h + 1
                and self.y + self.h > itemblock.y
            ):
                if self.prev_y >= itemblock.y + itemblock.h:
                    itemblocks.remove(itemblock)
                    coins.append(Coin(itemblock.x, itemblock.y - 16))

        return itemblocks, coins

class Enemy:
    def __init__(self, x, y, w=16, h=16, v_x=0.5):
        self.x, self.y, self.w, self.h, self.v_x, self.v_y = x, y, w, h, v_x, 0
    
    def update(self):
        self.x -= self.v_x

        self.v_y += GRAVITY
        falling_distance = 0
        while falling_distance <= self.v_y:
            coll_flags = detect_collision(self.x, self.y + falling_distance)
            if coll_flags[2] or coll_flags[3] or coll_flags[6]:
                self.v_y = 0
                self.y += falling_distance
                self.jump_status = 0
                break
            falling_distance += 1

        self.y += self.v_y 

    def draw(self):
        u = pyxel.frame_count // 6 % 2 * 16
        pyxel.blt(self.x, self.y, 0, u, 88, self.w, self.h, TRANSPARENT_COLOR)

class Coin:
    def __init__(self, x, y, w=16, h=16):
        self.x, self.y, self.w, self.h = x, y, w, h

    def draw(self):
        u = pyxel.frame_count // 6 % 2 * 16
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
    
    def update(self):
        self.x += 3

    def check_enemy_collision(self, enemies):
        is_beat = False
        for enemy in enemies:
            if (
                self.x < enemy.x + enemy.w
                and self.x + self.w > enemy.x
                and self.y < enemy.y + enemy.h
                and self.y + self.h > enemy.y
            ):
                enemies.remove(enemy)
                is_beat = True

        return enemies, is_beat

class ItemBlock:
    def __init__(self, x, y, w=16, h=16, item=Coin):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.item = Coin(x, y + 16)

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 48, 48, 16, 16, TRANSPARENT_COLOR)

class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT)
        pyxel.load("./scene.pyxres")
        self.scene = SCENE_TITLE
        # BGM
        pyxel.sounds[0].set(
            "e3 e3 e3 c3 e3 g3 g2 c3 g2 e2 a2 b2 a#2 a2 g2 e3 g3 a3 f3 g3 e3 c3 d3 b2 ",
            "p", 
            "6", 
            "vffn fnff vffs vfnn", 
            25,
        )
        pyxel.sounds[1].set(
            "c3 c4 a2 a3 a#2 a3 g2 e3 g3 a3 f3 g3 e3 c3 d3 b2 c3 g2 e2 a2 b2 a#2 a2 g2 e3 g3 a3 f3 g3 e3 c3 d3 b2 ",
            "s", 
            "6", 
            "nnff vfff vvvv vfff svff vfff vvvv svnn", 
            25,
        )
        pyxel.sounds[2].set(
            "f0ra4r f0ra4r f0ra4r f0f0a4r", 
            "n", 
            "6622 6622 6622 6422", 
            "f", 
            25,
        )
        # コイン獲得時の効果音
        pyxel.sounds[3].set(
            "c3e3g3e4g4",
            "t",
            "6",
            "f",
            5,
        )
        # ゲームオーバー時の効果音
        pyxel.sounds[4].set(
            "g2f2e2d2c2",
            "t",
            "76543",
            "fffnn",
            10,
        )
        # 成功時の効果音
        pyxel.sounds[5].set(
            "c3e3g3c4e4",
            "p",
            "66443",
            "nnffn",
            10,
        )
        pyxel.play(0, 2, loop=True)
        self.game_settings()

    def game_settings(self):
        # global scroll_x
        self.scroll_x = 0
        pyxel.camera(self.scroll_x, 0)
        # pyxel.image(0).rect(0, 80, 16, 8, TRANSPARENT_COLOR)
        self.boy = Boy(0, 0)
        self.enemies = []
        self.coins = [
            Coin(120, 96),
        ]

        self.enemy_line = [
            {
                "x": 100,
                "appear": False,
            },
            {
                "x": 200,
                "appear": False,
            },
        ]
        self.start_time = time.time()
        self.end_flag = False
        self.fire = None
        self.fire_time = 0
        self.itemblocks = [
            ItemBlock(56, 40),
        ]
        pyxel.run(self.update, self.draw)

    def update_title_scene(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.scene = SCENE_GAME
            pyxel.play(0, [0, 1], loop=True)
            self.start_time = time.time()

    def update_game_scene(self):
        if self.boy.status == BOY_STATUS_LIVE:
            for enemy_line in self.enemy_line:
                if self.boy.x > enemy_line["x"] and not enemy_line["appear"]:
                    self.enemies.append(Enemy(enemy_line["x"] + 100, 0))
                    enemy_line["appear"] = True

            self.scroll_x, self.enemies, self.scene, self.coins, self.itemblocks = self.boy.update(self.scroll_x, self.enemies, self.scene, self.coins, self.itemblocks)
            for enemy in self.enemies:
                enemy.update()
            if self.check_goal():
                pyxel.play(1, 5)
                pyxel.play(0, 2, loop=True)
                self.scene = SCENE_RESULT
            if not self.fire:
                if pyxel.btnp(pyxel.KEY_F):
                    self.fire = Fire(self.boy.x, self.boy.y)
                    pyxel.play(1, 3)
            else:
                self.fire.update()
                self.fire_time += 1
                if self.fire_time > 10:
                    self.fire = None
                    self.fire_time = 0
                self.enemies, is_beat = self.fire.check_enemy_collision(self.enemies)
                if is_beat:
                    self.fire = None
                    self.fire_time = 0
                    pyxel.play(1, 3)
                    self.boy.score += 1

    def update_result(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.scene = SCENE_GAME
            pyxel.play(0, [0, 1], loop=True)
        elif pyxel.btnp(pyxel.KEY_R):
            self.scene = SCENE_TITLE
        self.game_settings()

    def update(self):
        if self.scene == SCENE_TITLE:
            self.update_title_scene()
        elif self.scene == SCENE_GAME:
            self.update_game_scene()
        elif self.scene == SCENE_RESULT:
            self.update_result()

    def draw_title_scene(self):
        # global scroll_x
        pyxel.text(self.scroll_x + 36, 40, "SUPER MAN DASH", 7)
        pyxel.text(self.scroll_x + 28, 80, "- START [ SPACE ] -", 7)

    def draw_game_scene(self):
        if self.boy.status == BOY_STATUS_LIVE:
            pyxel.camera()
            pyxel.bltm(0, 0, 0, self.scroll_x, 0, WIDTH, HEIGHT)
            pyxel.camera(self.scroll_x, 0)
            self.boy.draw()
            # self.enemy.draw()
            for enemy in self.enemies:
                enemy.draw()
            for coin in self.coins:
                coin.draw()
            score_text = f"Score:{self.boy.score}"
            pyxel.text(self.scroll_x + 5, 4, score_text, 7)
            time_text = round(time.time() - self.start_time, 1)
            pyxel.text(self.scroll_x + 80, 4, f"Time: {time_text}", 7)
            if self.fire:
                self.fire.draw()
            for itemblock in self.itemblocks:
                itemblock.draw()

    def draw_result(self):
        if self.boy.status == BOY_STATUS_LIVE:
            pyxel.text(self.scroll_x + 36, 40, "YOU SUCCESSED", 7)
        else:
            pyxel.text(self.scroll_x + 36, 40, "YOU FAILED", 7)
        pyxel.text(self.scroll_x + 28, 60, "- RESTART [ R ] -", 7)
        pyxel.text(self.scroll_x + 28, 80, "- RETURN [ SPACE ] -", 7)
        score_text = f"Score:{self.boy.score}"
        pyxel.text(self.scroll_x + 5, 4, score_text, 7)
        time_text = round(self.end_time - self.start_time, 1)
        pyxel.text(self.scroll_x + 80, 4, f"Time: {time_text}", 7)

    def draw(self):
        pyxel.cls(0)
        if self.scene == SCENE_TITLE:
            self.draw_title_scene()
        elif self.scene == SCENE_GAME:
            self.draw_game_scene()
        elif self.scene == SCENE_RESULT:
            if self.end_flag == False:
                self.end_time = time.time()
                self.end_flag = True
            self.draw_result()
    
    def check_goal(self):

        # 座標を使用する場合
        if self.boy.x > 1176:
            return True
        else:
            return False

        # 旗との当たり判定を使用する場合
        for x, y in CHECK_POINTS:
            if get_tile((self.boy.x + x) // 8, (self.boy.y + y) // 8)[1] == 14:
                return True
        return False

App()