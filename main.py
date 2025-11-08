import pygame
import random
import sys
import os
import json

# 初始化pygame
pygame.init()
pygame.mixer.init()

# 游戏窗口设置
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python版植物大战僵尸")

# 颜色定义
GREEN = (0, 128, 0)
LIGHT_GREEN = (100, 200, 100)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GREEN = (0, 100, 0)
GREY = (127, 128, 131)

# 字体设置
def get_font(size):
    font_paths = [
        "simkai.ttf",
        "msyh.ttc",
        "simhei.ttf",
        "simsun.ttc",
        "C:/Windows/Fonts/simkai.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc"
    ]
    
    for font_path in font_paths:
        try:
            return pygame.font.Font(font_path, size)
        except:
            continue
    
    return pygame.font.SysFont(None, size)

font = get_font(24)
title_font = get_font(48)

# 游戏参数
GRID_SIZE = 80
GRID_ROWS = 5
GRID_COLS = 9
LAWN_LEFT = 100
LAWN_TOP = 100
FPS = 60  # 固定帧率

# 创建数据文件夹
if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.exists("assets/image"):
    os.makedirs("assets/image")
if not os.path.exists("assets/sound"):
    os.makedirs("assets/sound")

# 加载游戏数据
def load_game_data(difficulty="normal"):
    data_file = f"data/game_save_{difficulty}.json"
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        "current_level": 1,
        "score": 0,
        "unlocked_levels": 1,
        "total_sun_collected": 0,
        "total_zombies_killed": 0
    }

def save_game_data(game_data, difficulty="normal"):
    data_file = f"data/game_save_{difficulty}.json"
    try:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(game_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存游戏数据失败: {e}")

# 加载贴图函数
def load_image(path, default_color=None, default_size=(40, 40)):
    try:
        image = pygame.image.load(path)
        return pygame.transform.scale(image, default_size)
    except:
        print(f"警告：无法加载贴图 {path}，使用默认图形")
        surf = pygame.Surface(default_size, pygame.SRCALPHA)
        if default_color:
            pygame.draw.circle(surf, default_color, (default_size[0]//2, default_size[1]//2), default_size[0]//2 - 5)
        return surf

# 加载音效函数
def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except:
        print(f"警告：无法加载音效 {path}")
        return None

# 加载所有贴图
PLANT_IMAGES = {
    "peashooter": load_image("assets/image/peashooter.png", GREEN, (60, 60)),
    "sunflower": load_image("assets/image/sunflower.png", YELLOW, (60, 60)),
    "nut_wall": load_image("assets/image/nut_wall.png", BROWN, (60, 60)),
    "cherry_bomb": load_image("assets/image/cherry_bomb.png", RED, (60, 60)),
    "pea": load_image("assets/image/pea.png", GREEN, (16, 16)),
    "zombie": load_image("assets/image/zombie.png", BLUE, (40, 60)),
    "roadblock_zombie": load_image("assets/image/roadblock_zombie.png", (100, 100, 100), (40, 60)),
    "buckethead_zombie": load_image("assets/image/buckethead_zombie.png", (50, 50, 50), (40, 60)),
    "sun": load_image("assets/image/sun.png", YELLOW, (40, 40))
}

# 加载所有音效
SOUNDS = {
    "button_click": load_sound("assets/sound/Button_click.ogg"),
    "cherry_bomb": load_sound("assets/sound/cherrybomb.ogg"),
    "zombie_attack": load_sound("assets/sound/Sfx.wav"),
    "pea_hit": load_sound("assets/sound/Hit.wav")
}

# 游戏状态
class GameState:
    MAIN_MENU = 0
    LEVEL_SELECT = 1
    SETTINGS = 2
    PLAYING = 3
    PAUSED = 4
    LEVEL_COMPLETE = 5

current_state = GameState.MAIN_MENU
game_settings = {
    "difficulty": "normal",
    "fullscreen": False,
    "music_volume": 0.5,
    "sound_volume": 0.5
}

# 加载音乐
try:
    if not os.path.exists("lawnbgm(1).mp3"):
        music_loaded = False
    else:
        main_menu_music = pygame.mixer.Sound("lawnbgm(1).mp3")
        settings_music = pygame.mixer.Sound("lawnbgm(2).mp3")
        game_music = pygame.mixer.Sound("lawnbgm(3).mp3")
        music_loaded = True
except:
    print("警告：无法加载音乐文件")
    music_loaded = False

# 播放音乐函数
def play_music(music_type, loop=True):
    if not music_loaded:
        return
    pygame.mixer.stop()
    if music_type == "main_menu":
        main_menu_music.play(-1 if loop else 0)
        main_menu_music.set_volume(game_settings["music_volume"])
    elif music_type == "settings":
        settings_music.play(-1 if loop else 0)
        settings_music.set_volume(game_settings["music_volume"])
    elif music_type == "game":
        game_music.play(-1 if loop else 0)
        game_music.set_volume(game_settings["music_volume"])

# 播放音效函数
def play_sound(sound_name):
    sound = SOUNDS.get(sound_name)
    if sound:
        sound.set_volume(game_settings["sound_volume"])
        sound.play()

# 更新所有音效音量
def update_sound_volumes():
    for sound in SOUNDS.values():
        if sound:
            sound.set_volume(game_settings["sound_volume"])

# 植物基类
class Plant:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = LAWN_LEFT + col * GRID_SIZE
        self.y = LAWN_TOP + row * GRID_SIZE
        self.health = 300  # 普通植物300点生命值
        self.max_health = 300
        self.attack_cooldown = 0
        self.cost = 0
        self.cooldown_time = 0
        self.cooldown_timer = 0
        
    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (self.x + GRID_SIZE//2, self.y + GRID_SIZE//2), 20)
        
    def update(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def is_on_cooldown(self):
        return self.cooldown_timer > 0

    def start_cooldown(self):
        self.cooldown_timer = self.cooldown_time

    def update_cooldown(self):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1

# 向日葵类
class Sunflower(Plant):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.sun_cooldown = 5 * FPS  # 5秒
        self.cost = 50
        self.cooldown_time = 5 * FPS  # 5秒冷却
        
    def draw(self, screen):
        screen.blit(PLANT_IMAGES["sunflower"], (self.x + 10, self.y + 10))
        
    def update(self):
        self.sun_cooldown -= 1
        if self.sun_cooldown <= 0:
            global SUN_COUNT
            SUN_COUNT += 25
            game_data["total_sun_collected"] += 25
            self.sun_cooldown = 5 * FPS  # 重置为5秒

# 豌豆射手类
class Peashooter(Plant):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.attack_cooldown = 1.5 * FPS  # 1.5秒攻击间隔
        self.cost = 100
        self.cooldown_time = 6 * FPS  # 6秒冷却
        
    def draw(self, screen):
        screen.blit(PLANT_IMAGES["peashooter"], (self.x + 10, self.y + 10))
        
    def update(self):
        self.attack_cooldown -= 1
        if self.attack_cooldown <= 0:
            for zombie in zombies:
                if zombie.row == self.row and zombie.x > self.x:
                    peas.append(Pea(self.x + GRID_SIZE//2, self.y + GRID_SIZE//2, self.row))
                    self.attack_cooldown = 1.5 * FPS  # 重置攻击间隔
                    break

# 坚果墙类
class NutWall(Plant):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.health = 4000  # 坚果墙4000点生命值
        self.max_health = 4000
        self.cost = 50
        self.cooldown_time = 30 * FPS  # 30秒冷却
        
    def draw(self, screen):
        screen.blit(PLANT_IMAGES["nut_wall"], (self.x + 10, self.y + 10))
        
        # 绘制生命条
        bar_width = 40
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x, self.y - 15, bar_width, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 15, bar_width * health_ratio, 5))
        
    def update(self):
        # 坚果墙不攻击，只作为障碍物
        pass

# 樱桃炸弹类
class CherryBomb(Plant):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.health = 300
        self.max_health = 300
        self.cost = 150
        self.cooldown_time = 50 * FPS  # 50秒冷却
        self.explode_timer = 2 * FPS  # 2秒后爆炸
        self.has_exploded = False
        self.marked_for_removal = False
        
    def draw(self, screen):
        screen.blit(PLANT_IMAGES["cherry_bomb"], (self.x + 10, self.y + 10))
        
    def update(self):
        self.explode_timer -= 1
        if self.explode_timer <= 0 and not self.has_exploded:
            self.explode()
            
    def explode(self):
        self.has_exploded = True
        play_sound("cherry_bomb")
        
        # 爆炸范围：3x3的格子
        center_row, center_col = self.row, self.col
        
        # 对范围内的僵尸造成伤害
        zombies_to_remove = []
        for zombie in zombies:
            if (abs(zombie.row - center_row) <= 1 and 
                abs(zombie.col - center_col) <= 1):
                zombies_to_remove.append(zombie)
        
        # 在循环外移除僵尸
        for zombie in zombies_to_remove:
            if zombie in zombies:
                zombies.remove(zombie)
                global zombies_killed, score
                zombies_killed += 1
                score += 10
                game_data["total_zombies_killed"] += 1
        
        # 标记樱桃炸弹为待移除
        self.marked_for_removal = True

# 豌豆类
class Pea:
    def __init__(self, x, y, row):
        self.x = x
        self.y = y
        self.row = row
        self.speed = 8  # 增加豌豆速度
        self.damage = 20
        
    def draw(self, screen):
        screen.blit(PLANT_IMAGES["pea"], (self.x - 8, self.y - 8))
        
    def update(self):
        self.x += self.speed
        for zombie in zombies:
            if (zombie.row == self.row and 
                abs(zombie.x - self.x) < 30 and 
                abs(zombie.y + GRID_SIZE//2 - self.y) < 30):
                zombie.health -= self.damage
                play_sound("pea_hit")
                return True
        if self.x > WIDTH:
            return True
        return False

# 僵尸基类
class Zombie:
    def __init__(self, row, difficulty="normal"):
        self.row = row
        self.x = WIDTH
        self.y = LAWN_TOP + row * GRID_SIZE
        self.health = 100
        self.speed = 1.0  # 增加基础速度
        self.attack_cooldown = 0
        self.attack_sound_playing = False
        self.attack_damage = 50  # 每次攻击造成50点伤害
        
        # 根据难度调整属性
        if difficulty == "easy":
            self.health = 80
            self.speed = 0.8
        elif difficulty == "hard":
            self.health = 150
            self.speed = 1.2
        
    def draw(self, screen):
        screen.blit(PLANT_IMAGES["zombie"], (self.x, self.y))
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, 40, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, 40 * (self.health / self.max_health), 5))
        
    def update(self):
        plant_in_front = False
        for plant in plants:
            if plant.row == self.row and abs(plant.x - self.x) < GRID_SIZE:
                plant_in_front = True
                if self.attack_cooldown <= 0:
                    plant.health -= self.attack_damage  # 每次攻击50点伤害
                    self.attack_cooldown = 1 * FPS  # 1秒攻击间隔
                    if not self.attack_sound_playing:
                        play_sound("zombie_attack")
                        self.attack_sound_playing = True
                break
                
        if not plant_in_front:
            self.x -= self.speed
            self.attack_sound_playing = False
            
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        if self.x < LAWN_LEFT:
            return True
            
        return False

# 普通僵尸
class NormalZombie(Zombie):
    def __init__(self, row, difficulty="normal"):
        super().__init__(row, difficulty)
        self.max_health = self.health
        
    def draw(self, screen):
        screen.blit(PLANT_IMAGES["zombie"], (self.x, self.y))
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, 40, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, 40 * (self.health / self.max_health), 5))

# 路障僵尸
class RoadblockZombie(Zombie):
    def __init__(self, row, difficulty="normal"):
        super().__init__(row, difficulty)
        self.health = 560  # 28个豌豆 * 20伤害
        self.max_health = self.health
        self.speed = 0.6  # 稍微慢一点
        
    def draw(self, screen):
        screen.blit(PLANT_IMAGES["roadblock_zombie"], (self.x, self.y))
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, 40, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, 40 * (self.health / self.max_health), 5))

# 铁桶僵尸
class BucketheadZombie(Zombie):
    def __init__(self, row, difficulty="normal"):
        super().__init__(row, difficulty)
        self.health = 2600  # 130个豌豆 * 20伤害
        self.max_health = self.health
        self.speed = 0.4  # 更慢
        
    def draw(self, screen):
        screen.blit(PLANT_IMAGES["buckethead_zombie"], (self.x, self.y))
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, 40, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, 40 * (self.health / self.max_health), 5))

# 阳光类
class Sun:
    def __init__(self):
        self.x = random.randint(LAWN_LEFT, WIDTH - 50)
        self.y = 0
        self.target_y = random.randint(100, 400)
        self.speed = 2  # 增加阳光下落速度
        self.value = 25
        self.timer = 10 * FPS  # 10秒存在时间
        
    def draw(self, screen):
        screen.blit(PLANT_IMAGES["sun"], (self.x - 20, self.y - 20))
        
    def update(self):
        if self.y < self.target_y:
            self.y += self.speed
        self.timer -= 1
        return self.timer <= 0

# 按钮类
class Button:
    def __init__(self, x, y, width, height, text, color=GREEN, hover_color=LIGHT_GREEN):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                play_sound("button_click")
                return True
        return False

# 滑动条类
class Slider:
    def __init__(self, x, y, width, height, min_val=0, max_val=100, initial_val=50, text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.text = text
        self.dragging = False
        self.knob_radius = 10
        self.knob_x = x + (initial_val - min_val) / (max_val - min_val) * width
        
    def draw(self, screen):
        # 绘制滑动条背景
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # 绘制滑动条填充
        fill_width = (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(screen, GREEN, fill_rect)
        
        # 绘制滑块
        knob_rect = pygame.Rect(self.knob_x - self.knob_radius, self.rect.centery - self.knob_radius, 
                               self.knob_radius * 2, self.knob_radius * 2)
        pygame.draw.circle(screen, BLUE, (int(self.knob_x), self.rect.centery), self.knob_radius)
        pygame.draw.circle(screen, BLACK, (int(self.knob_x), self.rect.centery), self.knob_radius, 2)
        
        # 绘制文本
        text_surface = font.render(f"{self.text}: {int(self.value)}%", True, BLACK)
        screen.blit(text_surface, (self.rect.x, self.rect.y - 30))
        
    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            knob_rect = pygame.Rect(self.knob_x - self.knob_radius, self.rect.centery - self.knob_radius, 
                                   self.knob_radius * 2, self.knob_radius * 2)
            if knob_rect.collidepoint(mouse_pos) or self.rect.collidepoint(mouse_pos):
                self.dragging = True
                self.update_value(mouse_pos[0])
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value(mouse_pos[0])
            return True
            
        return False
        
    def update_value(self, mouse_x):
        mouse_x = max(self.rect.left, min(self.rect.right, mouse_x))
        self.knob_x = mouse_x
        self.value = self.min_val + (mouse_x - self.rect.left) / self.rect.width * (self.max_val - self.min_val)
        return self.value

# 植物卡片类
class PlantCard:
    def __init__(self, x, y, plant_type, cost, cooldown_time):
        self.rect = pygame.Rect(x, y, 50, 70)
        self.plant_type = plant_type
        self.cost = cost
        self.cooldown_time = cooldown_time
        self.cooldown_timer = 0
        self.is_locked = False
        
    def draw(self, screen):
        # 绘制卡片背景
        if self.is_locked:
            color = GRAY
        elif self.cooldown_timer > 0:
            color = DARK_GREEN
        else:
            color = GREEN
            
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # 绘制植物图标
        screen.blit(PLANT_IMAGES[self.plant_type], (self.rect.x + 5, self.rect.y + 5))
        
        # 绘制阳光消耗
        cost_font = get_font(14)
        cost_text = cost_font.render(str(self.cost), True, BLACK)
        screen.blit(cost_text, (self.rect.x + 25 - cost_text.get_width()//2, self.rect.y + 50))
        
        # 绘制冷却时间
        if self.cooldown_timer > 0:
            cooldown_font = get_font(16)
            cooldown_seconds = (self.cooldown_timer + FPS - 1) // FPS  # 向上取整
            cooldown_text = cooldown_font.render(f"{cooldown_seconds}s", True, RED)
            screen.blit(cooldown_text, (self.rect.x + 25 - cooldown_text.get_width()//2, self.rect.y + 20))
    
    def update(self):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
            self.is_locked = True
        else:
            self.is_locked = False
    
    def can_plant(self):
        return not self.is_locked and SUN_COUNT >= self.cost
    
    def start_cooldown(self):
        self.cooldown_timer = self.cooldown_time

# 初始化游戏变量
def init_game():
    global plants, zombies, peas, suns, SUN_COUNT, game_over, last_sun_time, selected_plant
    global zombies_spawned, zombies_killed, total_zombies_for_level, plant_cards
    
    plants = []
    zombies = []
    peas = []
    suns = []
    SUN_COUNT = 150  # 初始阳光增加
    game_over = False
    last_sun_time = pygame.time.get_ticks()
    selected_plant = None
    zombies_killed = 0
    
    # 计算当前关卡僵尸总数
    if game_settings["difficulty"] == "easy":
        total_zombies_for_level = current_level * 5
    elif game_settings["difficulty"] == "normal":
        total_zombies_for_level = current_level * 15
    else:  # hard
        total_zombies_for_level = current_level * 25
    
    zombies_spawned = 0
    
    # 初始化植物卡片 - 修复冷却时间
    plant_cards = [
        PlantCard(20, 20, "peashooter", 100, 3 * FPS),      # 3秒冷却
        PlantCard(20, 100, "sunflower", 50, 3 * FPS),       # 3秒冷却
        PlantCard(20, 180, "nut_wall", 50, 10 * FPS),       # 10秒冷却
        PlantCard(20, 260, "cherry_bomb", 150, 20 * FPS)    # 20秒冷却
    ]

# 切换难度时更新游戏数据
def update_game_data_for_difficulty(new_difficulty):
    global game_data, current_level, score
    if 'game_data' in globals():
        save_game_data(game_data, game_settings["difficulty"])
    game_data = load_game_data(new_difficulty)
    current_level = game_data["current_level"]
    score = game_data["score"]

# 初始化游戏数据
game_data = load_game_data(game_settings["difficulty"])
current_level = game_data["current_level"]
score = game_data["score"]

# 创建按钮
adventure_button = Button(WIDTH//2 - 100, 200, 200, 50, "冒险模式")
settings_button = Button(WIDTH//2 - 100, 270, 200, 50, "设置")
quit_button = Button(WIDTH//2 - 100, 340, 200, 50, "退出游戏")
back_button = Button(20, 20, 100, 40, "返回")

level_buttons = []
for i in range(30):
    row = i // 6
    col = i % 6
    level_buttons.append(Button(150 + col * 120, 100 + row * 60, 100, 40, f"关卡 {i+1}"))

difficulty_button = Button(WIDTH//2 - 150, 150, 300, 40, f"难度: {game_settings['difficulty']}")
fullscreen_button = Button(WIDTH//2 - 150, 210, 300, 40, f"全屏: {'开' if game_settings['fullscreen'] else '关'}")

# 音量滑动条
music_slider = Slider(WIDTH//2 - 150, 270, 300, 20, 0, 100, game_settings["music_volume"] * 100, "音乐音量")
sound_slider = Slider(WIDTH//2 - 150, 320, 300, 20, 0, 100, game_settings["sound_volume"] * 100, "音效音量")

restart_button = Button(WIDTH//2 - 100, HEIGHT//2 - 80, 200, 40, "重新开始游戏")
settings_from_pause_button = Button(WIDTH//2 - 100, HEIGHT//2 - 20, 200, 40, "更改游戏设置")
resume_button = Button(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 40, "回到游戏")
main_menu_button = Button(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 40, "返回主菜单")

next_level_button = Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 40, "下一关")
main_menu_from_complete_button = Button(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 40, "返回主菜单")

# 绘制函数
def draw_main_menu():
    screen.fill((135, 206, 235))
    title_text = title_font.render("植物大战僵尸", True, GREEN)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
    
    adventure_button.draw(screen)
    settings_button.draw(screen)
    quit_button.draw(screen)
    
    level_text = font.render(f"当前进度: 第{current_level}关", True, BLACK)
    screen.blit(level_text, (WIDTH - 250, 20))
    
    score_text = font.render(f"总分数: {score}", True, BLACK)
    screen.blit(score_text, (WIDTH - 250, 50))
    
    difficulty_text = font.render(f"当前难度: {game_settings['difficulty']}", True, BLACK)
    screen.blit(difficulty_text, (WIDTH - 250, 80))
    
    version_text = font.render("当前版本号：0.12a正式版", True, GREEN)
    screen.blit(version_text, (20, HEIGHT - 60))
    
    warning_text = font.render("本游戏免费，若需要付费，请找商家退还钱财并举报该商家", True, RED)
    screen.blit(warning_text, (20, HEIGHT - 30))

    author_text = font.render("游戏作者：Find 1134/小墨", Ture, GREY)
    screen.blit(author_text, (20, HEIGHT - 30))

def draw_level_select():
    screen.fill((135, 206, 235))
    title_text = font.render("选择关卡", True, GREEN)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
    
    difficulty_text = font.render(f"难度: {game_settings['difficulty']}", True, BLACK)
    screen.blit(difficulty_text, (WIDTH - 200, 20))
    
    back_button.draw(screen)
    
    for i, level_button in enumerate(level_buttons):
        if i + 1 <= game_data["unlocked_levels"]:
            level_button.draw(screen)
        else:
            locked_rect = pygame.Rect(level_button.rect)
            pygame.draw.rect(screen, GRAY, locked_rect)
            pygame.draw.rect(screen, BLACK, locked_rect, 2)
            lock_text = font.render(f"关卡 {i+1}", True, BLACK)
            text_rect = lock_text.get_rect(center=locked_rect.center)
            screen.blit(lock_text, text_rect)

def draw_settings():
    screen.fill((135, 206, 235))
    title_text = font.render("游戏设置", True, GREEN)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
    
    back_button.draw(screen)
    difficulty_button.draw(screen)
    fullscreen_button.draw(screen)
    music_slider.draw(screen)
    sound_slider.draw(screen)
    
    tip_text = font.render("切换难度不会丢失进度，每个难度有独立的存档", True, BLUE)
    screen.blit(tip_text, (WIDTH//2 - tip_text.get_width()//2, 400))

def draw_pause_menu():
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 128))
    screen.blit(s, (0, 0))
    
    menu_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 150, 300, 300)
    pygame.draw.rect(screen, WHITE, menu_rect)
    pygame.draw.rect(screen, BLACK, menu_rect, 2)
    
    title_text = font.render("游戏暂停", True, BLACK)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 120))
    
    restart_button.draw(screen)
    settings_from_pause_button.draw(screen)
    resume_button.draw(screen)
    main_menu_button.draw(screen)

def draw_level_complete():
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 128))
    screen.blit(s, (0, 0))
    
    menu_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 300)
    pygame.draw.rect(screen, WHITE, menu_rect)
    pygame.draw.rect(screen, GREEN, menu_rect, 4)
    
    title_text = font.render("关卡完成！", True, GREEN)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 120))
    
    level_text = font.render(f"恭喜通过第 {current_level} 关", True, BLACK)
    screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 - 70))
    
    stats_text = font.render(f"本关击杀僵尸: {zombies_killed}/{total_zombies_for_level}", True, BLACK)
    screen.blit(stats_text, (WIDTH//2 - stats_text.get_width()//2, HEIGHT//2 - 30))
    
    next_level_button.draw(screen)
    main_menu_from_complete_button.draw(screen)

def draw_game():
    screen.fill((135, 206, 235))
    
    # 绘制草地
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            rect = pygame.Rect(LAWN_LEFT + col * GRID_SIZE, LAWN_TOP + row * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, LIGHT_GREEN, rect)
            pygame.draw.rect(screen, GREEN, rect, 1)
    
    # 绘制植物卡片
    for card in plant_cards:
        card.draw(screen)
    
    # 绘制选中的植物边框
    if selected_plant:
        for card in plant_cards:
            if card.plant_type == selected_plant and not card.is_locked:
                pygame.draw.rect(screen, WHITE, (card.rect.x - 5, card.rect.y - 5, 60, 80), 3)
    
    # 绘制游戏元素
    for plant in plants:
        plant.draw(screen)
    for zombie in zombies:
        zombie.draw(screen)
    for pea in peas:
        pea.draw(screen)
    for sun in suns:
        sun.draw(screen)
    
    # 绘制UI
    sun_text = font.render(f"阳光: {SUN_COUNT}", True, BLACK)
    screen.blit(sun_text, (20, 350))
    
    score_text = font.render(f"分数: {score}", True, BLACK)
    screen.blit(score_text, (20, 380))
    
    level_text = font.render(f"关卡: {current_level}", True, BLACK)
    screen.blit(level_text, (20, 410))
    
    zombies_text = font.render(f"僵尸: {zombies_killed}/{total_zombies_for_level}", True, BLACK)
    screen.blit(zombies_text, (20, 440))
    
    difficulty_text = font.render(f"难度: {game_settings['difficulty']}", True, BLACK)
    screen.blit(difficulty_text, (20, 470))
    
    if game_over:
        game_over_text = font.render("游戏结束! 僵尸吃掉了你的脑子!", True, RED)
        screen.blit(game_over_text, (WIDTH//2 - 180, HEIGHT//2))

# 初始化游戏
init_game()
if music_loaded:
    play_music("main_menu")

# 游戏主循环
clock = pygame.time.Clock()
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    current_time = pygame.time.get_ticks()
    
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game_data(game_data, game_settings["difficulty"])
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and current_state == GameState.PLAYING:
                current_state = GameState.PAUSED
            elif event.key == pygame.K_ESCAPE and current_state == GameState.PAUSED:
                current_state = GameState.PLAYING
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == GameState.MAIN_MENU:
                if adventure_button.is_clicked(mouse_pos, event):
                    current_state = GameState.LEVEL_SELECT
                    if music_loaded:
                        play_music("settings")
                elif settings_button.is_clicked(mouse_pos, event):
                    current_state = GameState.SETTINGS
                    if music_loaded:
                        play_music("settings")
                elif quit_button.is_clicked(mouse_pos, event):
                    save_game_data(game_data, game_settings["difficulty"])
                    running = False
                    
            elif current_state == GameState.LEVEL_SELECT:
                if back_button.is_clicked(mouse_pos, event):
                    current_state = GameState.MAIN_MENU
                    if music_loaded:
                        play_music("main_menu")
                else:
                    for i, level_button in enumerate(level_buttons):
                        if i + 1 <= game_data["unlocked_levels"] and level_button.is_clicked(mouse_pos, event):
                            current_level = i + 1
                            init_game()
                            current_state = GameState.PLAYING
                            if music_loaded:
                                play_music("game")
                            
            elif current_state == GameState.SETTINGS:
                if back_button.is_clicked(mouse_pos, event):
                    current_state = GameState.MAIN_MENU
                    if music_loaded:
                        play_music("main_menu")
                elif difficulty_button.is_clicked(mouse_pos, event):
                    old_difficulty = game_settings["difficulty"]
                    if game_settings["difficulty"] == "easy":
                        game_settings["difficulty"] = "normal"
                    elif game_settings["difficulty"] == "normal":
                        game_settings["difficulty"] = "hard"
                    else:
                        game_settings["difficulty"] = "easy"
                    update_game_data_for_difficulty(game_settings["difficulty"])
                    difficulty_button.text = f"难度: {game_settings['difficulty']}"
                elif fullscreen_button.is_clicked(mouse_pos, event):
                    game_settings["fullscreen"] = not game_settings["fullscreen"]
                    if game_settings["fullscreen"]:
                        pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        pygame.display.set_mode((WIDTH, HEIGHT))
                    fullscreen_button.text = f"全屏: {'开' if game_settings['fullscreen'] else '关'}"
                else:
                    # 处理音量滑动条
                    if music_slider.handle_event(event, mouse_pos):
                        game_settings["music_volume"] = music_slider.value / 100
                        if music_loaded:
                            play_music(get_current_music())
                    if sound_slider.handle_event(event, mouse_pos):
                        game_settings["sound_volume"] = sound_slider.value / 100
                        update_sound_volumes()
                    
            elif current_state == GameState.PAUSED:
                if restart_button.is_clicked(mouse_pos, event):
                    init_game()
                    current_state = GameState.PLAYING
                elif settings_from_pause_button.is_clicked(mouse_pos, event):
                    current_state = GameState.SETTINGS
                    if music_loaded:
                        play_music("settings")
                elif resume_button.is_clicked(mouse_pos, event):
                    current_state = GameState.PLAYING
                elif main_menu_button.is_clicked(mouse_pos, event):
                    save_game_data(game_data, game_settings["difficulty"])
                    current_state = GameState.MAIN_MENU
                    if music_loaded:
                        play_music("main_menu")
            
            elif current_state == GameState.LEVEL_COMPLETE:
                if next_level_button.is_clicked(mouse_pos, event):
                    current_level += 1
                    if current_level > 30:
                        current_level = 30
                    init_game()
                    current_state = GameState.PLAYING
                    if music_loaded:
                        play_music("game")
                elif main_menu_from_complete_button.is_clicked(mouse_pos, event):
                    save_game_data(game_data, game_settings["difficulty"])
                    current_state = GameState.MAIN_MENU
                    if music_loaded:
                        play_music("main_menu")
                    
            elif current_state == GameState.PLAYING and not game_over:
                x, y = mouse_pos
                
                # 检查是否点击了阳光
                for sun in suns[:]:
                    if ((x - sun.x)**2 + (y - sun.y)**2) <= 400:
                        SUN_COUNT += sun.value
                        game_data["total_sun_collected"] += sun.value
                        suns.remove(sun)
                
                # 检查是否点击了植物卡片
                for card in plant_cards:
                    if card.rect.collidepoint(x, y) and card.can_plant():
                        selected_plant = card.plant_type
                        break
                    
                # 检查是否在草地上放置植物
                if selected_plant and LAWN_LEFT <= x <= LAWN_LEFT + GRID_COLS * GRID_SIZE and LAWN_TOP <= y <= LAWN_TOP + GRID_ROWS * GRID_SIZE:
                    col = (x - LAWN_LEFT) // GRID_SIZE
                    row = (y - LAWN_TOP) // GRID_SIZE
                    
                    position_empty = True
                    for plant in plants:
                        if plant.row == row and plant.col == col:
                            position_empty = False
                            break
                    
                    if position_empty:
                        plant_created = False
                        for card in plant_cards:
                            if card.plant_type == selected_plant and card.can_plant():
                                if selected_plant == "peashooter":
                                    plants.append(Peashooter(row, col))
                                elif selected_plant == "sunflower":
                                    plants.append(Sunflower(row, col))
                                elif selected_plant == "nut_wall":
                                    plants.append(NutWall(row, col))
                                elif selected_plant == "cherry_bomb":
                                    plants.append(CherryBomb(row, col))
                                
                                SUN_COUNT -= card.cost
                                card.start_cooldown()
                                plant_created = True
                                break
                        
                        if plant_created:
                            selected_plant = None
    
    # 更新按钮悬停状态
    adventure_button.check_hover(mouse_pos)
    settings_button.check_hover(mouse_pos)
    quit_button.check_hover(mouse_pos)
    back_button.check_hover(mouse_pos)
    for level_button in level_buttons:
        level_button.check_hover(mouse_pos)
    difficulty_button.check_hover(mouse_pos)
    fullscreen_button.check_hover(mouse_pos)
    restart_button.check_hover(mouse_pos)
    settings_from_pause_button.check_hover(mouse_pos)
    resume_button.check_hover(mouse_pos)
    main_menu_button.check_hover(mouse_pos)
    next_level_button.check_hover(mouse_pos)
    main_menu_from_complete_button.check_hover(mouse_pos)
    
    # 更新游戏状态
    if current_state == GameState.PLAYING and not game_over:
        # 生成阳光
        if current_time - last_sun_time > 5000:  # 5秒生成一个阳光
            suns.append(Sun())
            last_sun_time = current_time
            
        # 更新植物卡片冷却
        for card in plant_cards:
            card.update()
            
        # 生成僵尸（根据关卡进度和难度）
        if zombies_spawned < total_zombies_for_level:
            zombie_rate = 0.01  # 增加生成率
            if game_settings["difficulty"] == "easy":
                zombie_rate = 0.006
            elif game_settings["difficulty"] == "hard":
                zombie_rate = 0.015
                
            progress = zombies_spawned / total_zombies_for_level
            adjusted_rate = zombie_rate * (1 + progress * 2)
            
            if random.random() < adjusted_rate:
                row = random.randint(0, GRID_ROWS - 1)
                
                # 根据关卡决定生成什么类型的僵尸
                rand = random.random()
                if current_level >= 7 and rand < 0.1:  # 第7关后10%概率生成铁桶僵尸
                    zombies.append(BucketheadZombie(row, game_settings["difficulty"]))
                elif current_level >= 3 and rand < 0.3:  # 第3关后30%概率生成路障僵尸
                    zombies.append(RoadblockZombie(row, game_settings["difficulty"]))
                else:
                    zombies.append(NormalZombie(row, game_settings["difficulty"]))
                
                zombies_spawned += 1
            
        # 更新植物
        plants_to_remove = []
        for plant in plants:
            plant.update()
            # 检查樱桃炸弹是否需要移除
            if hasattr(plant, 'marked_for_removal') and plant.marked_for_removal:
                plants_to_remove.append(plant)
        
        # 移除标记的植物（樱桃炸弹）
        for plant in plants_to_remove:
            if plant in plants:
                plants.remove(plant)
            
        # 更新豌豆
        for pea in peas[:]:
            if pea.update():
                peas.remove(pea)
                
        # 更新僵尸
        for zombie in zombies[:]:
            if zombie.update():
                game_over = True
            if zombie.health <= 0:
                zombies.remove(zombie)
                zombies_killed += 1
                score += 10
                game_data["total_zombies_killed"] += 1
                
        # 更新阳光
        for sun in suns[:]:
            if sun.update():
                suns.remove(sun)
                
        # 移除死亡的植物
        for plant in plants[:]:
            if plant.health <= 0:
                plants.remove(plant)
        
        # 检查是否完成关卡
        if zombies_killed >= total_zombies_for_level and len(zombies) == 0:
            current_state = GameState.LEVEL_COMPLETE
            save_game_data(game_data, game_settings["difficulty"])
    
    # 绘制当前界面
    if current_state == GameState.MAIN_MENU:
        draw_main_menu()
    elif current_state == GameState.LEVEL_SELECT:
        draw_level_select()
    elif current_state == GameState.SETTINGS:
        draw_settings()
    elif current_state == GameState.PLAYING:
        draw_game()
    elif current_state == GameState.PAUSED:
        draw_game()
        draw_pause_menu()
    elif current_state == GameState.LEVEL_COMPLETE:
        draw_game()
        draw_level_complete()
    
    pygame.display.flip()
    clock.tick(FPS)  # 固定帧率

pygame.quit()
sys.exit()

# 辅助函数
def get_current_music():
    """获取当前播放的音乐类型"""
    if music_loaded:
        if pygame.mixer.music.get_busy():
            # 这里需要根据当前状态判断音乐类型
            if current_state == GameState.MAIN_MENU:
                return "main_menu"
            elif current_state in [GameState.LEVEL_SELECT, GameState.SETTINGS]:
                return "settings"
            elif current_state == GameState.PLAYING:
                return "game"
    return "main_menu"