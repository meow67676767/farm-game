import random
import pgzrun

# =======================================================================
#                      НАСТРОЙКИ ОКНА И ИГРЫ
# =======================================================================
WIDTH = 864       # 18 колонок по 48 пикселей
HEIGHT = 672      # 14 строк по 48 пикселей
TITLE = "Весёлая ферма (Kenney Tiny Farm)"
FPS = 60

TILE_SIZE = 48
BG_COLOR = (132, 198, 105)  # Зеленый цвет лужайки

# =======================================================================
#                      СПРАВОЧНИК КУЛЬТУР И ХОТБАР
# =======================================================================
CROPS = {
    'carrot': {
        'name': 'Морковь',
        'stages': ['tile_0004', 'tile_0005', 'tile_0006'],
        'grow_time': 4.5,
        'price': 10
    },
    'tomato': {
        'name': 'Томат',
        'stages': ['tile_0040', 'tile_0041', 'tile_0042'],
        'grow_time': 6.5,
        'price': 15
    },
    'corn': {
        'name': 'Кукуруза',
        'stages': ['tile_0028', 'tile_0029', 'tile_0030'],
        'grow_time': 8.5,
        'price': 20
    }
}

HOTBAR = [
    {'type': 'seed', 'crop': 'carrot', 'icon': 'tile_0010'},
    {'type': 'seed', 'crop': 'tomato', 'icon': 'tile_0046'},
    {'type': 'seed', 'crop': 'corn',   'icon': 'tile_0034'},
    {'type': 'tool', 'tool': 'water',  'icon': 'tile_0084'},
    {'type': 'tool', 'tool': 'hand',   'icon': 'tile_0076'},
]
active_slot = 0

# =======================================================================
#                      ИГРОК, ЭКОНОМИКА И ИНВЕНТАРЬ
# =======================================================================
player = Actor('tile_0109', (312, 330))
player_dir = 'right'
player_speed = 3

coins = 50
inventory = {
    'carrot': 0,
    'tomato': 0,
    'corn': 0,
    'milk': 0,
    'egg': 0
}

floating_notes = []

def add_note(text, x, y, color=(255, 255, 255)):
    floating_notes.append({
        'text': text,
        'x': x,
        'y': y,
        'color': color,
        'timer': 1.6
    })

# =======================================================================
#                      ПОСТРОЙКИ, ДЕКОРАЦИИ И ПРЕПЯТСТВИЯ
# =======================================================================
BARN_POS = (5 * TILE_SIZE, 2 * TILE_SIZE)
PEN_POS = (12 * TILE_SIZE, 2 * TILE_SIZE)

DECORATIONS = [
    # Окружение амбара
    ('tile_0085', 4 * TILE_SIZE, 5 * TILE_SIZE),  # Бочка с водой
    ('tile_0096', 4 * TILE_SIZE, 4 * TILE_SIZE),  # Тюк сена
    ('tile_0089', 8 * TILE_SIZE, 5 * TILE_SIZE),  # Валун
    ('tile_0076', 8 * TILE_SIZE, 6 * TILE_SIZE),  # Ящик скупщика
    ('tile_0074', 9 * TILE_SIZE, 6 * TILE_SIZE),  # Мешок с зерном
    ('tile_0123', 7 * TILE_SIZE, 6 * TILE_SIZE),  # Бидон
    # Поилка и кормушка загона
    ('tile_0110', 12 * TILE_SIZE, 1 * TILE_SIZE),
    ('tile_0111', 13 * TILE_SIZE, 1 * TILE_SIZE),
    ('tile_0112', 14 * TILE_SIZE, 1 * TILE_SIZE),
    ('tile_0113', 15 * TILE_SIZE, 1 * TILE_SIZE),
    # Сосны
    ('tree_pine', 1 * TILE_SIZE, 0),
    ('tree_pine', 2 * TILE_SIZE, 0),
    ('tree_pine', 3 * TILE_SIZE, 0),
    ('tree_pine', 16 * TILE_SIZE, 0),
    ('tree_pine', 17 * TILE_SIZE, 0),
    ('tree_pine', 0, 1 * TILE_SIZE),
    ('tree_pine', 0, 4 * TILE_SIZE),
    ('tree_pine', 0, 7 * TILE_SIZE),
    # Кусты
    ('tile_0039', 0, 3 * TILE_SIZE),
    ('tile_0039', 0, 6 * TILE_SIZE),
    ('tile_0039', 0, 9 * TILE_SIZE),
    # Подсолнухи вдоль грядок
    ('tile_0083', 1 * TILE_SIZE, 9 * TILE_SIZE),
    ('tile_0083', 1 * TILE_SIZE, 10 * TILE_SIZE),
    ('tile_0083', 1 * TILE_SIZE, 11 * TILE_SIZE),
    # Ягодные кустики и трава
    ('tile_0078', 8 * TILE_SIZE, 9 * TILE_SIZE),
    ('tile_0078', 8 * TILE_SIZE, 10 * TILE_SIZE),
    ('tile_0080', 8 * TILE_SIZE, 11 * TILE_SIZE),
    # Пенёк
    ('tile_0079', 16 * TILE_SIZE, 8 * TILE_SIZE),
]

OBSTACLES = [
    Rect(5 * TILE_SIZE, 2 * TILE_SIZE, 3 * TILE_SIZE, 4 * TILE_SIZE),  # Амбар
    Rect(4 * TILE_SIZE, 4 * TILE_SIZE, 1 * TILE_SIZE, 2 * TILE_SIZE),  # Бочка и сено
    Rect(7 * TILE_SIZE, 5 * TILE_SIZE, 3 * TILE_SIZE, 2 * TILE_SIZE),  # Валун, ящик, мешок
    Rect(12 * TILE_SIZE, 1 * TILE_SIZE, 4 * TILE_SIZE, 1 * TILE_SIZE), # Поилки загона
    # Ограда загона с открытым входом внизу (колонка 13 свободна)
    Rect(12 * TILE_SIZE, 2 * TILE_SIZE, 4 * TILE_SIZE, 18),
    Rect(12 * TILE_SIZE, 2 * TILE_SIZE, 18, 4 * TILE_SIZE),
    Rect(16 * TILE_SIZE - 18, 2 * TILE_SIZE, 18, 4 * TILE_SIZE),
    Rect(12 * TILE_SIZE, 6 * TILE_SIZE - 22, 1 * TILE_SIZE, 22),
    Rect(14 * TILE_SIZE, 6 * TILE_SIZE - 22, 2 * TILE_SIZE, 22),
    # Деревья сверху и слева
    Rect(0, 0, 1 * TILE_SIZE, 10 * TILE_SIZE),
    Rect(1 * TILE_SIZE, 0, 3 * TILE_SIZE, 2 * TILE_SIZE),
    Rect(16 * TILE_SIZE, 0, 2 * TILE_SIZE, 2 * TILE_SIZE),
    Rect(16 * TILE_SIZE, 8 * TILE_SIZE, 1 * TILE_SIZE, 1 * TILE_SIZE), # Пенёк
]

MARKET_RECT = Rect(8 * TILE_SIZE, 6 * TILE_SIZE, TILE_SIZE, TILE_SIZE)

# =======================================================================
#                      ОГОРОД (ГРЯДКИ И КУЛЬТУРЫ)
# =======================================================================
plots = []
for r in [9, 10, 11]:
    for start_c, end_c in [(2, 6), (10, 14)]:
        for c in range(start_c, end_c + 1):
            if c == start_c:
                dry, wet = 'tile_0048', 'tile_0060'
            elif c == end_c:
                dry, wet = 'tile_0051', 'tile_0063'
            else:
                dry = 'tile_0049' if (c % 2 == 0) else 'tile_0050'
                wet = 'tile_0061' if (c % 2 == 0) else 'tile_0062'
            plots.append({
                'col': c,
                'row': r,
                'x': c * TILE_SIZE,
                'y': r * TILE_SIZE,
                'rect': Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                'dry_tile': dry,
                'wet_tile': wet,
                'crop': None,
                'stage': 0,
                'grow_timer': 0.0,
                'watered': False,
                'ripe': False
            })

# Стартовые растения
for p in plots:
    if p['col'] == 3 and p['row'] == 9:
        p['crop'], p['stage'], p['watered'], p['ripe'] = 'carrot', 2, True, True
    elif p['col'] == 4 and p['row'] == 9:
        p['crop'], p['stage'], p['watered'], p['grow_timer'] = 'carrot', 1, True, 2.0
    elif p['col'] == 3 and p['row'] == 10:
        p['crop'], p['stage'], p['watered'], p['ripe'] = 'tomato', 2, True, True
    elif p['col'] == 11 and p['row'] == 9:
        p['crop'], p['stage'], p['watered'], p['ripe'] = 'corn', 2, True, True

# =======================================================================
#                      ЖИВОТНЫЕ ФЕРМЫ
# =======================================================================
def create_animal(kind, sprite, pos, bounds):
    animal = Actor(sprite, pos)
    animal.kind = kind
    animal.base_sprite = sprite
    animal.bounds = bounds
    animal.vx = 0
    animal.vy = 0
    animal.move_timer = random.uniform(1.0, 3.0)
    animal.product_ready = True
    animal.product_timer = 0.0
    animal.heart_timer = 0.0
    return animal

animals = [
    create_animal('cow', 'tile_0121', (640, 160), (610, 135, 710, 225)),
    create_animal('sheep', 'tile_0120', (690, 170), (610, 135, 710, 225)),
    create_animal('chicken', 'tile_0122', (630, 200), (610, 135, 710, 225)),
    create_animal('chicken', 'tile_0122', (350, 360), (280, 340, 420, 400)),
]

# =======================================================================
#                      ВЗАИМОДЕЙСТВИЕ
# =======================================================================
def get_front_point():
    offset = 32
    if player_dir == 'right':
        return player.x + offset, player.y
    elif player_dir == 'left':
        return player.x - offset, player.y
    elif player_dir == 'down':
        return player.x, player.y + offset
    elif player_dir == 'up':
        return player.x, player.y - offset
    return player.x, player.y

def get_action_hint():
    fx, fy = get_front_point()
    player_rect = Rect(player.x - 16, player.y - 16, 32, 32)
    front_rect = Rect(fx - 16, fy - 16, 32, 32)

    # 1. Продажа скупщику
    if player_rect.colliderect(MARKET_RECT) or front_rect.colliderect(MARKET_RECT):
        if sum(inventory.values()) > 0:
            return "[E / Пробел] Продать все продукты торговцу"
        return "Ящик скупщика (В инвентаре пока пусто)"

    # 2. Животные
    for a in animals:
        if a.colliderect(player_rect) or a.colliderect(front_rect):
            if a.kind == 'cow':
                return "[E / Пробел] Подоить корову" if a.product_ready else "Погладить коровку"
            elif a.kind == 'chicken':
                return "[E / Пробел] Собрать яйцо" if a.product_ready else "Погладить курочку"
            elif a.kind == 'sheep':
                return "[E / Пробел] Погладить овечку"

    # 3. Грядки
    curr_slot = HOTBAR[active_slot]
    for p in plots:
        if p['rect'].collidepoint(fx, fy) or p['rect'].collidepoint(player.x, player.y):
            if p['crop'] is None:
                if curr_slot['type'] == 'seed':
                    cname = CROPS[curr_slot['crop']]['name']
                    return f"[E / Пробел] Посадить {cname}"
                return "Пустая грядка (выберите семена 1, 2 или 3)"
            else:
                cname = CROPS[p['crop']]['name']
                if p['ripe']:
                    return f"[E / Пробел] Собрать спелый урожай ({cname})!"
                elif not p['watered']:
                    if curr_slot['type'] == 'tool' and curr_slot['tool'] == 'water':
                        return f"[E / Пробел] Полить {cname}"
                    return f"Растет {cname} (нужен полив лейкой [4])"
                else:
                    return f"Растет {cname} (полито, зреет...)"

    return "[WASD / Стрелки] Ходьба  |  [1-5] Инструменты  |  [E / Пробел] Действие"

def interact():
    global coins
    fx, fy = get_front_point()
    player_rect = Rect(player.x - 16, player.y - 16, 32, 32)
    front_rect = Rect(fx - 16, fy - 16, 32, 32)

    # 1. Продажа скупщику
    if player_rect.colliderect(MARKET_RECT) or front_rect.colliderect(MARKET_RECT):
        earned = (
            inventory['carrot'] * CROPS['carrot']['price'] +
            inventory['tomato'] * CROPS['tomato']['price'] +
            inventory['corn'] * CROPS['corn']['price'] +
            inventory['milk'] * 25 +
            inventory['egg'] * 12
        )
        if earned > 0:
            coins += earned
            for k in inventory:
                inventory[k] = 0
            add_note(f"+{earned} монет! Торговец купил всё!", MARKET_RECT.centerx, MARKET_RECT.y - 20, (255, 220, 50))
        else:
            add_note("Нечего продавать!", MARKET_RECT.centerx, MARKET_RECT.y - 20, (220, 220, 220))
        return

    # 2. Животные
    for a in animals:
        if a.colliderect(player_rect) or a.colliderect(front_rect):
            a.heart_timer = 2.0
            if a.kind == 'cow':
                if a.product_ready:
                    a.product_ready = False
                    inventory['milk'] += 1
                    add_note("+1 Молоко! (Му-у-у!)", a.x, a.y - 25, (255, 255, 120))
                else:
                    add_note("Коровка отдыхает...", a.x, a.y - 25, (220, 220, 220))
            elif a.kind == 'chicken':
                if a.product_ready:
                    a.product_ready = False
                    inventory['egg'] += 1
                    add_note("+1 Яйцо! (Ко-ко-ко!)", a.x, a.y - 25, (255, 240, 180))
                else:
                    add_note("Курочка еще не снесла яйцо", a.x, a.y - 25, (220, 220, 220))
            elif a.kind == 'sheep':
                add_note("Овечка рада! (Бе-е-е!)", a.x, a.y - 25, (255, 200, 240))
            return

    # 3. Грядки
    curr_slot = HOTBAR[active_slot]
    for p in plots:
        if p['rect'].collidepoint(fx, fy) or p['rect'].collidepoint(player.x, player.y):
            # Сбор урожая
            if p['crop'] and p['ripe']:
                crop_name = p['crop']
                inventory[crop_name] += 1
                cname = CROPS[crop_name]['name']
                add_note(f"+1 {cname}!", p['rect'].centerx, p['y'] - 10, (100, 255, 120))
                p['crop'] = None
                p['stage'] = 0
                p['grow_timer'] = 0.0
                p['watered'] = False
                p['ripe'] = False
                return

            # Полив растения
            if p['crop'] and not p['watered']:
                if curr_slot['type'] == 'tool' and curr_slot['tool'] == 'water':
                    p['watered'] = True
                    add_note("Полито! Всходит быстрее!", p['rect'].centerx, p['y'] - 10, (120, 200, 255))
                    return

            # Посадка семян
            if p['crop'] is None and curr_slot['type'] == 'seed':
                crop_type = curr_slot['crop']
                p['crop'] = crop_type
                p['stage'] = 0
                p['grow_timer'] = 0.0
                p['watered'] = False
                p['ripe'] = False
                cname = CROPS[crop_type]['name']
                add_note(f"Посажена {cname}!", p['rect'].centerx, p['y'] - 10, (255, 255, 150))
                return

# =======================================================================
#                      ОБРАБОТКА ВВОДА (КЛАВИАТУРА И МЫШЬ)
# =======================================================================
def on_key_down(key):
    global active_slot
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
    elif key in (keys.SPACE, keys.E):
        interact()

def on_mouse_down(button, pos):
    global active_slot
    if button == mouse.LEFT:
        # Проверяем клик по хотбару
        slot_w = 54
        gap = 10
        total_bar_w = 5 * slot_w + 4 * gap
        start_x = (WIDTH - total_bar_w) // 2
        bar_y = HEIGHT - 68
        for i in range(5):
            sx = start_x + i * (slot_w + gap)
            slot_rect = Rect(sx, bar_y, slot_w, 52)
            if slot_rect.collidepoint(pos):
                active_slot = i
                return
        # Клик в мире — выполняем действие
        interact()

# =======================================================================
#                      ОБНОВЛЕНИЕ ИГРЫ (UPDATE)
# =======================================================================
def update(dt):
    global player_dir

    # 1. Движение фермера
    dx = 0
    dy = 0
    if keyboard.left or keyboard.a:
        dx -= 1
        player_dir = 'left'
        player.image = 'tile_0109_left'
    if keyboard.right or keyboard.d:
        dx += 1
        player_dir = 'right'
        player.image = 'tile_0109'
    if keyboard.up or keyboard.w:
        dy -= 1
        player_dir = 'up'
    if keyboard.down or keyboard.s:
        dy += 1
        player_dir = 'down'

    if dx != 0 or dy != 0:
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        nx = max(24, min(WIDTH - 24, player.x + dx * player_speed))
        ny = max(24, min(HEIGHT - 24, player.y + dy * player_speed))

        feet_x = Rect(nx - 14, player.y + 6, 28, 14)
        if not any(feet_x.colliderect(obs) for obs in OBSTACLES):
            player.x = nx

        feet_y = Rect(player.x - 14, ny + 6, 28, 14)
        if not any(feet_y.colliderect(obs) for obs in OBSTACLES):
            player.y = ny

    # 2. Рост политых культур
    for p in plots:
        if p['crop'] and p['watered'] and not p['ripe']:
            cfg = CROPS[p['crop']]
            p['grow_timer'] += dt
            time_per_stage = cfg['grow_time'] / 2.0
            stage = int(p['grow_timer'] / time_per_stage)
            if stage >= 2:
                p['stage'] = 2
                p['ripe'] = True
            else:
                p['stage'] = stage

    # 3. Животные
    for a in animals:
        a.move_timer -= dt
        if a.move_timer <= 0:
            if a.vx == 0 and a.vy == 0:
                a.move_timer = random.uniform(1.5, 3.0)
                spd = 0.8 if a.kind != 'chicken' else 1.2
                dx_choice = random.choice([-1, 0, 1])
                dy_choice = random.choice([-1, 0, 1])
                a.vx = dx_choice * spd
                a.vy = dy_choice * spd
                if dx_choice < 0:
                    a.image = a.base_sprite + '_left'
                elif dx_choice > 0:
                    a.image = a.base_sprite
            else:
                a.move_timer = random.uniform(2.0, 4.0)
                a.vx = 0
                a.vy = 0

        if a.vx != 0 or a.vy != 0:
            min_x, min_y, max_x, max_y = a.bounds
            nx = a.x + a.vx
            ny = a.y + a.vy
            if min_x <= nx <= max_x:
                a.x = nx
            else:
                a.vx = -a.vx
                a.image = a.base_sprite + ('_left' if a.vx < 0 else '')
            if min_y <= ny <= max_y:
                a.y = ny
            else:
                a.vy = -a.vy

        if not a.product_ready and a.kind in ('cow', 'chicken'):
            a.product_timer += dt
            cooldown = 12.0 if a.kind == 'chicken' else 15.0
            if a.product_timer >= cooldown:
                a.product_ready = True
                a.product_timer = 0.0

        if a.heart_timer > 0:
            a.heart_timer -= dt

    # 4. Всплывающий текст
    for note in floating_notes[:]:
        note['timer'] -= dt
        note['y'] -= 20 * dt
        if note['timer'] <= 0:
            floating_notes.remove(note)

# =======================================================================
#                      ОТРИСОВКА (DRAW)
# =======================================================================
def draw():
    # 1. Травяной фон
    screen.fill(BG_COLOR)

    # 2. Грядки
    for p in plots:
        tile = p['wet_tile'] if p['watered'] else p['dry_tile']
        screen.blit(tile, (p['x'], p['y']))
        if p['crop']:
            sprite = CROPS[p['crop']]['stages'][p['stage']]
            screen.blit(sprite, (p['x'], p['y']))

    # 3. Постройки и загон
    screen.blit('barn_clean', BARN_POS)
    screen.blit('animal_pen_fence', PEN_POS)

    # 4. Декорации
    for sprite_name, dx, dy in DECORATIONS:
        screen.blit(sprite_name, (dx, dy))

    # 5. Животные
    for a in animals:
        a.draw()
        if a.heart_timer > 0:
            screen.blit('heart', (a.x - 12, a.top - 20))
        elif a.product_ready and a.kind in ('cow', 'chicken'):
            icon = 'tile_0124' if a.kind == 'cow' else 'tile_0125'
            screen.blit(icon, (a.x - 24, a.top - 24))

    # 6. Фермер с тенью
    screen.draw.filled_rect(Rect(player.x - 14, player.y + 16, 28, 8), (80, 140, 60))
    player.draw()

    # 7. Всплывающие уведомления
    for note in floating_notes:
        screen.draw.text(
            note['text'],
            center=(int(note['x']), int(note['y'])),
            fontsize=20,
            color=note['color'],
            owidth=1.5,
            ocolor=(20, 20, 20)
        )

    # 8. Строка контекстной подсказки
    hint_text = get_action_hint()
    hint_box = Rect((WIDTH - 540) // 2, HEIGHT - 108, 540, 32)
    screen.draw.filled_rect(hint_box, (30, 45, 30))
    screen.draw.rect(hint_box, (180, 220, 100))
    screen.draw.text(hint_text, center=hint_box.center, fontsize=18, color=(255, 255, 240))

    # 9. Панель хотбара (слоты 1-5)
    slot_w = 54
    gap = 10
    total_bar_w = 5 * slot_w + 4 * gap
    start_x = (WIDTH - total_bar_w) // 2
    bar_y = HEIGHT - 68

    bar_bg = Rect(start_x - 10, bar_y - 6, total_bar_w + 20, 64)
    screen.draw.filled_rect(bar_bg, (25, 35, 25))
    screen.draw.rect(bar_bg, (100, 150, 80))

    for i, item in enumerate(HOTBAR):
        sx = start_x + i * (slot_w + gap)
        slot_rect = Rect(sx, bar_y, slot_w, 52)
        if i == active_slot:
            screen.draw.filled_rect(slot_rect, (60, 100, 50))
            screen.draw.rect(slot_rect, (255, 230, 80))
        else:
            screen.draw.filled_rect(slot_rect, (40, 55, 40))
            screen.draw.rect(slot_rect, (80, 110, 70))

        screen.blit(item['icon'], (sx + 3, bar_y + 2))
        screen.draw.text(str(i + 1), bottomright=(sx + slot_w - 4, bar_y + 50), fontsize=16, color=(240, 240, 200))

    # 10. Верхний HUD: Монеты
    coin_box = Rect(14, 12, 150, 48)
    screen.draw.filled_rect(coin_box, (30, 40, 30))
    screen.draw.rect(coin_box, (200, 180, 60))
    screen.blit('coin', (22, 24))
    screen.draw.text(f"{coins}", topleft=(56, 25), fontsize=24, color=(255, 225, 80))

    # Верхний HUD: Инвентарь
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
#                      ТОЧКА ВХОДА PGZERO
# =======================================================================
pgzrun.go()
