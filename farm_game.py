import pgzrun
import pygame
import math
import random

# =======================================================================
#                      НАСТРОЙКИ ОКНА И ИГРЫ
# =======================================================================
WIDTH = 864       # 18 тайлов по 48 пикселей
HEIGHT = 672      # 14 тайлов по 48 пикселей
TITLE = "Весёлая ферма (Kenney Tiny Farm)"
FPS = 60

TILE_SIZE = 48
BG_COLOR = (132, 198, 105)   # Фирменный зеленый цвет травы Kenney Tiny Farm

# =======================================================================
#                      СПРАВОЧНИК КУЛЬТУР (ОВОЩЕЙ)
# =======================================================================
CROPS_CONFIG = {
    'carrot': {
        'name': 'Морковь',
        'seed_icon': 'tile_0010',
        'stages': ['tile_0004', 'tile_0005', 'tile_0006'],
        'item_icon': 'tile_0008',
        'grow_time': 4.5,
        'price': 10
    },
    'tomato': {
        'name': 'Томат',
        'seed_icon': 'tile_0046',
        'stages': ['tile_0040', 'tile_0041', 'tile_0042'],
        'item_icon': 'tile_0044',
        'grow_time': 6.5,
        'price': 15
    },
    'corn': {
        'name': 'Кукуруза',
        'seed_icon': 'tile_0034',
        'stages': ['tile_0028', 'tile_0029', 'tile_0030'],
        'item_icon': 'tile_0032',
        'grow_time': 8.5,
        'price': 20
    }
}

# Панель инструментов (Хотбар)
HOTBAR_ITEMS = [
    {'type': 'seed', 'crop': 'carrot', 'label': '1: Морковь', 'icon': 'tile_0010'},
    {'type': 'seed', 'crop': 'tomato', 'label': '2: Томат',   'icon': 'tile_0046'},
    {'type': 'seed', 'crop': 'corn',   'label': '3: Кукуруза', 'icon': 'tile_0034'},
    {'type': 'tool', 'tool': 'water',  'label': '4: Лейка',   'icon': 'tile_0084'},
    {'type': 'tool', 'tool': 'hand',   'label': '5: Рука',    'icon': 'tile_0076'},
]

active_slot = 0  # Выбранный слот в хотбаре (0..4)

# =======================================================================
#                      СОСТОЯНИЕ ИГРОКА И ЭКОНОМИКА
# =======================================================================
player = Actor('tile_0109', (312, 330))  # Стартует перед дверью амбара
player_speed = 3.2
player_dir = 'right'
player_walking = False
walk_bob_timer = 0.0

coins = 50
inventory = {
    'carrot': 0,
    'tomato': 0,
    'corn': 0,
    'milk': 0,
    'egg': 0
}

# Всплывающие текстовые сообщения (+10 монет, +1 Морковь и т.д.)
floating_notes = []

def add_floating_text(text, x, y, color=(255, 255, 255)):
    floating_notes.append({
        'text': text,
        'x': x,
        'y': y,
        'color': color,
        'timer': 1.6,
        'max_timer': 1.6
    })

# =======================================================================
#                      КАРТА И ДЕКОРАЦИИ (ДЕКОР ФЕРМЫ)
# =======================================================================
# Координаты декораций и построек:
# 1. Амбар (цельный 144x192 px, 3x4 тайла)
BARN_POS = (5 * TILE_SIZE, 2 * TILE_SIZE)

# 2. Загон для животных (деревянный забор 192x192 px, 4x4 тайла)
PEN_FENCE_POS = (12 * TILE_SIZE, 2 * TILE_SIZE)

# Статичные декоративные тайлы: (имя_спрайта, pixel_x, pixel_y)
STATIC_DECORATIONS = [
    # Окружение амбара
    ('tile_0085', 4 * TILE_SIZE, 5 * TILE_SIZE), # Бочка с водой слева
    ('tile_0096', 4 * TILE_SIZE, 4 * TILE_SIZE), # Тюк сена слева
    ('tile_0089', 8 * TILE_SIZE, 5 * TILE_SIZE), # Валун справа
    ('tile_0076', 8 * TILE_SIZE, 6 * TILE_SIZE), # Торговый ящик (ящик скупщика)
    ('tile_0074', 9 * TILE_SIZE, 6 * TILE_SIZE), # Мешок с зерном
    ('tile_0123', 7 * TILE_SIZE, 6 * TILE_SIZE), # Бидон для молока (аккуратная посуда)

    # Поилка и кормушка загона (ряд 1 над забором)
    ('tile_0110', 12 * TILE_SIZE, 1 * TILE_SIZE), # Поилка с водой (левая часть)
    ('tile_0111', 13 * TILE_SIZE, 1 * TILE_SIZE), # Поилка с водой (правая часть)
    ('tile_0112', 14 * TILE_SIZE, 1 * TILE_SIZE), # Кормушка с зерном (левая часть)
    ('tile_0113', 15 * TILE_SIZE, 1 * TILE_SIZE), # Кормушка с зерном (правая часть)

    # Полноценные хвойные сосны (48x96 px)
    ('tree_pine', 1 * TILE_SIZE, 0),
    ('tree_pine', 2 * TILE_SIZE, 0),
    ('tree_pine', 3 * TILE_SIZE, 0),
    ('tree_pine', 16 * TILE_SIZE, 0),
    ('tree_pine', 17 * TILE_SIZE, 0),
    ('tree_pine', 0, 1 * TILE_SIZE),
    ('tree_pine', 0, 4 * TILE_SIZE),
    ('tree_pine', 0, 7 * TILE_SIZE),

    # Аккуратные круглые кустики между соснами
    ('tile_0039', 0, 3 * TILE_SIZE),
    ('tile_0039', 0, 6 * TILE_SIZE),
    ('tile_0039', 0, 9 * TILE_SIZE),

    # Подсолнухи вдоль огорода слева
    ('tile_0083', 1 * TILE_SIZE, 9 * TILE_SIZE),
    ('tile_0083', 1 * TILE_SIZE, 10 * TILE_SIZE),
    ('tile_0083', 1 * TILE_SIZE, 11 * TILE_SIZE),

    # Ягодные кустики и трава в центре
    ('tile_0078', 8 * TILE_SIZE, 9 * TILE_SIZE),
    ('tile_0078', 8 * TILE_SIZE, 10 * TILE_SIZE),
    ('tile_0080', 8 * TILE_SIZE, 11 * TILE_SIZE),

    # Пенёк справа
    ('tile_0079', 16 * TILE_SIZE, 8 * TILE_SIZE),
]

# Прямоугольники препятствий (коллизии)
OBSTACLES = [
    # Стены амбара
    Rect(5 * TILE_SIZE, 2 * TILE_SIZE, 3 * TILE_SIZE, 4 * TILE_SIZE),
    # Бочка и сено
    Rect(4 * TILE_SIZE, 4 * TILE_SIZE, 1 * TILE_SIZE, 2 * TILE_SIZE),
    # Валун, бидон, ящик и мешок справа от амбара
    Rect(7 * TILE_SIZE, 5 * TILE_SIZE, 3 * TILE_SIZE, 2 * TILE_SIZE),

    # Поилки и кормушки загона
    Rect(12 * TILE_SIZE, 1 * TILE_SIZE, 4 * TILE_SIZE, 1 * TILE_SIZE),

    # Забор загона (ограда с проходом для фермера внизу)
    Rect(12 * TILE_SIZE, 2 * TILE_SIZE, 4 * TILE_SIZE, 18),                    # Верхний забор
    Rect(12 * TILE_SIZE, 2 * TILE_SIZE, 18, 4 * TILE_SIZE),                    # Левый забор
    Rect(16 * TILE_SIZE - 18, 2 * TILE_SIZE, 18, 4 * TILE_SIZE),               # Правый забор
    Rect(12 * TILE_SIZE, 6 * TILE_SIZE - 22, 1 * TILE_SIZE, 22),               # Нижний левый забор
    Rect(14 * TILE_SIZE, 6 * TILE_SIZE - 22, 2 * TILE_SIZE, 22),               # Нижний правый забор
    # Проход в загон свободен на col 13 (x = 624..672)!

    # Деревья по левому краю
    Rect(0, 0, 1 * TILE_SIZE, 10 * TILE_SIZE),
    # Верхние деревья
    Rect(1 * TILE_SIZE, 0, 3 * TILE_SIZE, 2 * TILE_SIZE),
    Rect(16 * TILE_SIZE, 0, 2 * TILE_SIZE, 2 * TILE_SIZE),

    # Пенёк
    Rect(16 * TILE_SIZE, 8 * TILE_SIZE, 1 * TILE_SIZE, 1 * TILE_SIZE),
]

# Координаты ящика скупщика (для продажи)
MARKET_RECT = Rect(8 * TILE_SIZE, 6 * TILE_SIZE, 1 * TILE_SIZE, 1 * TILE_SIZE)

# =======================================================================
#                      ОГОРОД (ГРЯДКИ И КУЛЬТУРЫ)
# =======================================================================
class GardenPlot:
    def __init__(self, col, row, dry_tile, wet_tile):
        self.col = col
        self.row = row
        self.dry_tile = dry_tile
        self.wet_tile = wet_tile
        self.rect = Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

        # Состояние растения
        self.crop = None        # 'carrot', 'tomato', 'corn' или None
        self.stage = 0          # 0, 1, 2
        self.grow_timer = 0.0
        self.watered = False    # Полит ли участок
        self.ripe = False       # Созрел ли урожай

    def plant(self, crop_type):
        if self.crop is None:
            self.crop = crop_type
            self.stage = 0
            self.grow_timer = 0.0
            self.ripe = False
            return True
        return False

    def water(self):
        if not self.watered:
            self.watered = True
            return True
        return False

    def update(self, dt):
        if self.crop and self.watered and not self.ripe:
            cfg = CROPS_CONFIG[self.crop]
            self.grow_timer += dt
            # Вычисляем текущую стадию (всего 3 стадии: 0, 1, 2)
            time_per_stage = cfg['grow_time'] / 2.0
            new_stage = int(self.grow_timer / time_per_stage)
            if new_stage >= 2:
                self.stage = 2
                self.ripe = True
            else:
                self.stage = new_stage

    def harvest(self):
        if self.crop and self.ripe:
            crop_name = self.crop
            self.crop = None
            self.stage = 0
            self.grow_timer = 0.0
            self.watered = False
            self.ripe = False
            return crop_name
        return None

    def draw(self):
        # Рисуем саму землю грядки (сухая или влажная)
        tile_name = self.wet_tile if self.watered else self.dry_tile
        screen.blit(tile_name, (self.col * TILE_SIZE, self.row * TILE_SIZE))

        # Если посажено растение — рисуем спрайт текущей стадии
        if self.crop:
            cfg = CROPS_CONFIG[self.crop]
            crop_sprite = cfg['stages'][self.stage]
            screen.blit(crop_sprite, (self.col * TILE_SIZE, self.row * TILE_SIZE))

# Создаем аккуратные грядки:
# 1. Левая секция огорода: колонки 2..6, ряды 9..11
# 2. Правая секция огорода: колонки 10..14, ряды 9..11
garden_plots = []

def make_bed_row(start_c, end_c, r):
    for c in range(start_c, end_c + 1):
        if c == start_c:
            dry = 'tile_0048' # Закругленный левый край
            wet = 'tile_0060'
        elif c == end_c:
            dry = 'tile_0051' # Закругленный правый край
            wet = 'tile_0063'
        else:
            dry = 'tile_0049' if (c % 2 == 0) else 'tile_0050'
            wet = 'tile_0061' if (c % 2 == 0) else 'tile_0062'
        garden_plots.append(GardenPlot(c, r, dry, wet))

for row in [9, 10, 11]:
    make_bed_row(2, 6, row)   # Левые грядки
    make_bed_row(10, 14, row) # Правые грядки

# Предварительно посадим несколько культур для красивого старта
for p in garden_plots:
    if p.col == 3 and p.row == 9:
        p.plant('carrot')
        p.water()
        p.stage = 2
        p.ripe = True
    elif p.col == 4 and p.row == 9:
        p.plant('carrot')
        p.water()
        p.stage = 1
        p.grow_timer = 2.0
    elif p.col == 3 and p.row == 10:
        p.plant('tomato')
        p.water()
        p.stage = 2
        p.ripe = True
    elif p.col == 11 and p.row == 9:
        p.plant('corn')
        p.water()
        p.stage = 2
        p.ripe = True

# =======================================================================
#                      ЖИВОТНЫЕ (ЖИВОЙ МИР ФЕРМЫ)
# =======================================================================
class FarmAnimal:
    def __init__(self, kind, x, y, bounds):
        self.kind = kind
        self.x = float(x)
        self.y = float(y)
        self.bounds = bounds # (min_x, min_y, max_x, max_y)
        self.direction = 'right'
        self.move_timer = random.uniform(1.0, 3.0)
        self.is_moving = False
        self.vx = 0.0
        self.vy = 0.0
        self.product_ready = True
        self.product_timer = 0.0
        self.heart_timer = 0.0

        if kind == 'cow':
            self.base_sprite = 'tile_0121'
        elif kind == 'sheep':
            self.base_sprite = 'tile_0120'
        elif kind == 'chicken':
            self.base_sprite = 'tile_0122'

    @property
    def sprite(self):
        if self.direction == 'left':
            return self.base_sprite + '_left'
        return self.base_sprite

    def update(self, dt):
        self.move_timer -= dt
        if self.move_timer <= 0:
            self.is_moving = not self.is_moving
            if self.is_moving:
                self.move_timer = random.uniform(1.0, 2.5)
                angle = random.uniform(0, 2 * math.pi)
                spd = 0.7 if self.kind != 'chicken' else 1.0
                self.vx = math.cos(angle) * spd
                self.vy = math.sin(angle) * spd
                self.direction = 'left' if self.vx < 0 else 'right'
            else:
                self.move_timer = random.uniform(2.0, 4.5)
                self.vx = 0
                self.vy = 0

        if self.is_moving:
            new_x = self.x + self.vx
            new_y = self.y + self.vy
            min_x, min_y, max_x, max_y = self.bounds
            if min_x <= new_x <= max_x:
                self.x = new_x
            else:
                self.vx = -self.vx
                self.direction = 'left' if self.vx < 0 else 'right'
            if min_y <= new_y <= max_y:
                self.y = new_y
            else:
                self.vy = -self.vy

        # Таймер готовности продуктов
        if not self.product_ready:
            self.product_timer += dt
            cooldown = 12.0 if self.kind == 'chicken' else 15.0
            if self.product_timer >= cooldown:
                self.product_ready = True
                self.product_timer = 0.0

        # Таймер сердечка
        if self.heart_timer > 0:
            self.heart_timer -= dt

    def interact(self):
        self.heart_timer = 2.0
        if self.kind == 'cow':
            if self.product_ready:
                self.product_ready = False
                inventory['milk'] += 1
                add_floating_text("+1 Молоко! (Му-у-у!)", self.x + 10, self.y - 25, (255, 255, 120))
                return True
            else:
                add_floating_text("Коровка отдыхает...", self.x + 10, self.y - 25, (220, 220, 220))
        elif self.kind == 'chicken':
            if self.product_ready:
                self.product_ready = False
                inventory['egg'] += 1
                add_floating_text("+1 Яйцо! (Ко-ко-ко!)", self.x + 10, self.y - 25, (255, 240, 180))
                return True
            else:
                add_floating_text("Курочка еще не снесла яйцо", self.x + 10, self.y - 25, (220, 220, 220))
        elif self.kind == 'sheep':
            add_floating_text("Овечка рада! (Бе-е-е!)", self.x + 10, self.y - 25, (255, 200, 240))
            return True
        return False

    def draw(self):
        screen.blit(self.sprite, (int(self.x), int(self.y)))
        # Рисуем сердечко или значок готового продукта над головой
        if self.heart_timer > 0:
            screen.blit('heart', (int(self.x) + 12, int(self.y) - 20))
        elif self.product_ready and self.kind in ['cow', 'chicken']:
            icon = 'tile_0124' if self.kind == 'cow' else 'tile_0125'
            screen.blit(icon, (int(self.x), int(self.y) - 30))

# Животные на ферме (гуляют в уютном загоне и во дворе)
animals = [
    FarmAnimal('cow', 620, 140, (590, 115, 730, 235)),       # Коровка в загоне
    FarmAnimal('sheep', 690, 160, (590, 115, 730, 235)),     # Овечка в загоне
    FarmAnimal('chicken', 600, 190, (590, 115, 730, 235)),   # Курочка в загоне
    FarmAnimal('chicken', 350, 360, (260, 320, 440, 420)),   # Курочка во дворе у дома
]

# =======================================================================
#                      ВЗАИМОДЕЙСТВИЕ И УПРАВЛЕНИЕ
# =======================================================================
def get_player_front_point():
    """Точка перед персонажем для проверки взаимодействия"""
    px, py = player.x, player.y
    offset = 32
    if player_dir == 'right':
        return (px + offset, py)
    elif player_dir == 'left':
        return (px - offset, py)
    elif player_dir == 'down':
        return (px, py + offset)
    elif player_dir == 'up':
        return (px, py - offset)
    return (px, py)

def get_context_action():
    """Определяет, какое действие доступно игроку в текущий момент"""
    fx, fy = get_player_front_point()
    player_rect = Rect(player.x - 16, player.y - 16, 32, 32)
    front_rect = Rect(fx - 16, fy - 16, 32, 32)

    # 1. Продажа у ящика скупщика
    if player_rect.colliderect(MARKET_RECT) or front_rect.colliderect(MARKET_RECT):
        total_items = sum(inventory.values())
        if total_items > 0:
            return "[E / Пробел] Продать все продукты торговцу"
        else:
            return "Ящик скупщика (В инвентаре пока пусто)"

    # 2. Животные рядом
    for a in animals:
        a_rect = Rect(a.x, a.y, TILE_SIZE, TILE_SIZE)
        if front_rect.colliderect(a_rect) or player_rect.colliderect(a_rect):
            if a.kind == 'cow':
                return "[E / Пробел] Подоить корову" if a.product_ready else "Погладить коровку"
            elif a.kind == 'chicken':
                return "[E / Пробел] Собрать яйцо" if a.product_ready else "Погладить курочку"
            elif a.kind == 'sheep':
                return "[E / Пробел] Погладить овечку"

    # 3. Грядки
    for p in garden_plots:
        if p.rect.collidepoint(fx, fy) or p.rect.collidepoint(player.x, player.y):
            curr_slot = HOTBAR_ITEMS[active_slot]
            if p.crop is None:
                if curr_slot['type'] == 'seed':
                    c_name = CROPS_CONFIG[curr_slot['crop']]['name']
                    return f"[E / Пробел] Посадить {c_name}"
                else:
                    return "Пустая грядка (выберите семена 1, 2 или 3)"
            else:
                c_name = CROPS_CONFIG[p.crop]['name']
                if p.ripe:
                    return f"[E / Пробел] Собрать спелый урожай ({c_name})!"
                elif not p.watered:
                    if curr_slot['type'] == 'tool' and curr_slot['tool'] == 'water':
                        return f"[E / Пробел] Полить {c_name}"
                    else:
                        return f"Растет {c_name} (нужен полив лейкой [4])"
                else:
                    return f"Растет {c_name} (полито, зреет...)"

    return None

def handle_interact():
    """Основное действие при нажатии Space или E"""
    global coins
    fx, fy = get_player_front_point()
    player_rect = Rect(player.x - 16, player.y - 16, 32, 32)
    front_rect = Rect(fx - 16, fy - 16, 32, 32)

    # 1. Продажа у ящика скупщика
    if player_rect.colliderect(MARKET_RECT) or front_rect.colliderect(MARKET_RECT):
        earned = 0
        earned += inventory['carrot'] * CROPS_CONFIG['carrot']['price']
        earned += inventory['tomato'] * CROPS_CONFIG['tomato']['price']
        earned += inventory['corn'] * CROPS_CONFIG['corn']['price']
        earned += inventory['milk'] * 25
        earned += inventory['egg'] * 12

        if earned > 0:
            coins += earned
            for k in inventory:
                inventory[k] = 0
            add_floating_text(f"+{earned} монет! Торговец купил всё!", MARKET_RECT.centerx, MARKET_RECT.y - 20, (255, 220, 50))
        else:
            add_floating_text("Нечего продавать!", MARKET_RECT.centerx, MARKET_RECT.y - 20, (220, 220, 220))
        return

    # 2. Взаимодействие с животными
    for a in animals:
        a_rect = Rect(a.x, a.y, TILE_SIZE, TILE_SIZE)
        if front_rect.colliderect(a_rect) or player_rect.colliderect(a_rect):
            a.interact()
            return

    # 3. Взаимодействие с грядками
    curr_slot = HOTBAR_ITEMS[active_slot]
    for p in garden_plots:
        if p.rect.collidepoint(fx, fy) or p.rect.collidepoint(player.x, player.y):
            # Сбор созревшего урожая
            if p.crop and p.ripe:
                harvested = p.harvest()
                if harvested:
                    inventory[harvested] += 1
                    c_name = CROPS_CONFIG[harvested]['name']
                    add_floating_text(f"+1 {c_name}!", p.rect.centerx, p.rect.y - 10, (100, 255, 120))
                return

            # Полив растения лейкой
            if p.crop and not p.watered:
                if curr_slot['type'] == 'tool' and curr_slot['tool'] == 'water':
                    p.water()
                    add_floating_text("Полито! Всходит быстрее!", p.rect.centerx, p.rect.y - 10, (120, 200, 255))
                    return

            # Посадка семян
            if p.crop is None and curr_slot['type'] == 'seed':
                crop_to_plant = curr_slot['crop']
                if p.plant(crop_to_plant):
                    c_name = CROPS_CONFIG[crop_to_plant]['name']
                    add_floating_text(f"Посажена {c_name}!", p.rect.centerx, p.rect.y - 10, (255, 255, 150))
                return

def on_key_down(key):
    global active_slot
    # Смена слотов хотбара клавишами 1..5
    if key == keys.K_1:
        active_slot = 0
    elif key == keys.K_2:
        active_slot = 1
    elif key == keys.K_3:
        active_slot = 2
    elif key == keys.K_4:
        active_slot = 3
    elif key == keys.K_5:
        active_slot = 4
    # Клавиша действия
    elif key in (keys.SPACE, keys.E):
        handle_interact()

def on_mouse_down(button, pos):
    global active_slot
    if button == mouse.LEFT:
        # Проверяем клик по слотам хотбара внизу экрана
        slot_w = 54
        start_x = (WIDTH - (5 * slot_w + 4 * 10)) // 2
        bar_y = HEIGHT - 68
        for i in range(5):
            sx = start_x + i * (slot_w + 10)
            slot_rect = Rect(sx, bar_y, slot_w, 54)
            if slot_rect.collidepoint(pos):
                active_slot = i
                return

        # Иначе пробуем выполнить действие перед персонажем
        handle_interact()

# =======================================================================
#                      ОБНОВЛЕНИЕ ИГРОВОГО МИРА (UPDATE)
# =======================================================================
def update(dt):
    global player_walking, player_dir, walk_bob_timer

    # 1. Управление движением игрока (WASD или стрелки)
    dx = 0
    dy = 0
    if keyboard.left or keyboard.a:
        dx -= 1
        player_dir = 'left'
    if keyboard.right or keyboard.d:
        dx += 1
        player_dir = 'right'
    if keyboard.up or keyboard.w:
        dy -= 1
        player_dir = 'up'
    if keyboard.down or keyboard.s:
        dy += 1
        player_dir = 'down'

    player_walking = (dx != 0 or dy != 0)

    if player_walking:
        # Нормализация скорости при движении по диагонали
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        target_x = player.x + dx * player_speed
        target_y = player.y + dy * player_speed

        # Границы экрана
        target_x = max(24, min(WIDTH - 24, target_x))
        target_y = max(24, min(HEIGHT - 24, target_y))

        # Коллизии с препятствиями (хитбокс основания персонажа)
        player_feet_x = Rect(target_x - 14, player.y + 6, 28, 14)
        can_move_x = True
        for obs in OBSTACLES:
            if player_feet_x.colliderect(obs):
                can_move_x = False
                break
        if can_move_x:
            player.x = target_x

        player_feet_y = Rect(player.x - 14, target_y + 6, 28, 14)
        can_move_y = True
        for obs in OBSTACLES:
            if player_feet_y.colliderect(obs):
                can_move_y = False
                break
        if can_move_y:
            player.y = target_y

        walk_bob_timer += dt * 12
    else:
        walk_bob_timer = 0.0

    # Поворот спрайта персонажа (влево или вправо)
    if player_dir == 'left':
        player.image = 'tile_0109_left'
    else:
        player.image = 'tile_0109'

    # 2. Обновление грядок (рост культур)
    for p in garden_plots:
        p.update(dt)

    # 3. Обновление поведения животных
    for a in animals:
        a.update(dt)

    # 4. Обновление всплывающих сообщений
    for note in floating_notes[:]:
        note['timer'] -= dt
        note['y'] -= 20 * dt
        if note['timer'] <= 0:
            floating_notes.remove(note)

# =======================================================================
#                      ОТРИСОВКА ИГРЫ (DRAW)
# =======================================================================
def draw():
    # 1. Заливка фона чистой фирменной травой
    screen.fill(BG_COLOR)

    # 2. Грядки огорода (земля и растения)
    for p in garden_plots:
        p.draw()

    # 3. Живописный цельный амбар фермера
    screen.blit('barn_clean', BARN_POS)

    # 4. Уютный деревянный загон для животных
    screen.blit('animal_pen_fence', PEN_FENCE_POS)

    # 5. Статичные декорации (деревья, поилки, цветы, ящик)
    for sprite_name, px, py in STATIC_DECORATIONS:
        screen.blit(sprite_name, (px, py))

    # 6. Животные
    for a in animals:
        a.draw()

    # 7. Игрок (с легким покачиванием при ходьбе)
    bob_y = int(math.sin(walk_bob_timer) * 3) if player_walking else 0
    shadow_rect = Rect(player.x - 14, player.y + 16, 28, 8)
    screen.draw.filled_rect(shadow_rect, (80, 140, 60))
    screen.blit(player.image, (int(player.x - 24), int(player.y - 24 + bob_y)))

    # 8. Всплывающий текст (уведомления о сборе, продаже и поглаживании)
    for note in floating_notes:
        screen.draw.text(
            note['text'],
            center=(int(note['x']), int(note['y'])),
            fontsize=20,
            color=note['color'],
            owidth=1.5,
            ocolor=(20, 20, 20)
        )

    # 9. Контекстная подсказка действия (над панелью инструментов)
    action_hint = get_context_action()
    if not action_hint:
        action_hint = "[WASD / Стрелки] - Ходьба  |  [1-5] - Слот  |  [E / Пробел] - Действие"

    hint_box = Rect((WIDTH - 540) // 2, HEIGHT - 108, 540, 32)
    screen.draw.filled_rect(hint_box, (30, 45, 30))
    screen.draw.rect(hint_box, (180, 220, 100))
    screen.draw.text(
        action_hint,
        center=hint_box.center,
        fontsize=18,
        color=(255, 255, 240)
    )

    # 10. Нижняя панель инструментов (ХОТБАР 1..5)
    slot_w = 54
    gap = 10
    total_bar_w = 5 * slot_w + 4 * gap
    start_x = (WIDTH - total_bar_w) // 2
    bar_y = HEIGHT - 68

    bar_bg = Rect(start_x - 10, bar_y - 6, total_bar_w + 20, 64)
    screen.draw.filled_rect(bar_bg, (25, 35, 25))
    screen.draw.rect(bar_bg, (100, 150, 80))

    for i, item in enumerate(HOTBAR_ITEMS):
        sx = start_x + i * (slot_w + gap)
        slot_rect = Rect(sx, bar_y, slot_w, 52)

        # Выделение рамкой активного слота
        if i == active_slot:
            screen.draw.filled_rect(slot_rect, (60, 100, 50))
            screen.draw.rect(slot_rect, (255, 230, 80))
        else:
            screen.draw.filled_rect(slot_rect, (40, 55, 40))
            screen.draw.rect(slot_rect, (80, 110, 70))

        # Иконка предмета в слоте
        screen.blit(item['icon'], (sx + 3, bar_y + 2))

        # Цифра слота (1..5)
        screen.draw.text(
            str(i + 1),
            bottomright=(sx + slot_w - 4, bar_y + 50),
            fontsize=16,
            color=(240, 240, 200)
        )

    # 11. Верхняя информационная панель (HUD: монеты и инвентарь)
    # Панель монет (слева сверху)
    coin_box = Rect(14, 12, 150, 48)
    screen.draw.filled_rect(coin_box, (30, 40, 30))
    screen.draw.rect(coin_box, (200, 180, 60))
    screen.blit('coin', (22, 24))
    screen.draw.text(f"{coins}", topleft=(56, 25), fontsize=24, color=(255, 225, 80))

    # Панель собранного урожая и продуктов (справа сверху)
    inv_items = [
        ('tile_0008', inventory['carrot']),
        ('tile_0044', inventory['tomato']),
        ('tile_0032', inventory['corn']),
        ('tile_0124', inventory['milk']),
        ('tile_0125', inventory['egg']),
    ]
    inv_box = Rect(WIDTH - 324, 12, 310, 48)
    screen.draw.filled_rect(inv_box, (30, 40, 30))
    screen.draw.rect(inv_box, (100, 150, 80))

    cur_x = WIDTH - 316
    for icon_name, count in inv_items:
        screen.blit(icon_name, (cur_x, 12))
        screen.draw.text(f"x{count}", topleft=(cur_x + 36, 28), fontsize=18, color=(255, 255, 255))
        cur_x += 60

# =======================================================================
#                      ЗАПУСК PGZRUN
# =======================================================================
pgzrun.go()
