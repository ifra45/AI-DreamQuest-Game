
import pygame
import random
import math
import json
import os
import re
import threading
import requests

pygame.init()

# ==================================================
# DREAMQUEST AI - FANTASY WORLD CREATOR
# ==================================================

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DreamQuest AI | Fantasy World Creator")
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(BASE_DIR, "my_fantasy_level.json")
HERO_FILE = os.path.join(BASE_DIR, "assets", "heroine.png")

WHITE = (250, 248, 255)
PURPLE = (176, 125, 255)
PINK = (255, 145, 220)
CYAN = (105, 235, 255)
GOLD = (255, 218, 105)
GREEN = (115, 245, 165)
RED = (255, 95, 125)
DARK = (19, 14, 43)
PANEL = (37, 27, 68)
LAVENDER = (205, 180, 255)

font = pygame.font.SysFont("segoeui", 19)
small = pygame.font.SysFont("segoeui", 15)
large = pygame.font.SysFont("segoeui", 32, bold=True)

WORLD_TOP = 65
WORLD_BOTTOM = 545

THEMES = {
    "Dreamy Purple": ((19, 14, 43), (57, 36, 92)),
    "Enchanted Forest": ((10, 38, 37), (28, 91, 70)),
    "Candy Kingdom": ((67, 29, 70), (130, 65, 120)),
    "Ice Palace": ((15, 40, 72), (54, 104, 148)),
}

theme_name = "Dreamy Purple"

# ---------- LOAD HEROINE ----------
hero_image = None

if os.path.exists(HERO_FILE):
    try:
        hero_image = pygame.image.load(HERO_FILE).convert_alpha()
        hero_image = pygame.transform.smoothscale(hero_image, (48, 60))
    except pygame.error:
        hero_image = None

# ---------- LEVEL OBJECTS ----------
# Every object has a type and a rectangle.
objects = [
    {"type": "platform", "x": 0, "y": 520, "w": 1000, "h": 28},
    {"type": "platform", "x": 145, "y": 430, "w": 130, "h": 18},
    {"type": "platform", "x": 335, "y": 355, "w": 125, "h": 18},
    {"type": "platform", "x": 535, "y": 425, "w": 125, "h": 18},
    {"type": "platform", "x": 735, "y": 345, "w": 130, "h": 18},
    {"type": "spike", "x": 290, "y": 492, "w": 34, "h": 28},
    {"type": "spike", "x": 470, "y": 492, "w": 34, "h": 28},
    {"type": "gem", "x": 195, "y": 395, "w": 22, "h": 22},
    {"type": "gem", "x": 380, "y": 320, "w": 22, "h": 22},
    {"type": "gem", "x": 575, "y": 390, "w": 22, "h": 22},
    {"type": "gem", "x": 790, "y": 310, "w": 22, "h": 22},
    {"type": "hazard", "x": 635, "y": 470, "w": 42, "h": 32},
    {"type": "door", "x": 915, "y": 455, "w": 36, "h": 65},
]

# ---------- PLAYER ----------
hero = pygame.Rect(55, 450, 34, 48)
spawn_position = (55, 450)
player_x = float(hero.x)
player_y = float(hero.y)
velocity_y = 0.0
on_ground = False

lives = 3
score = 0
collected_gems = set()
mode = "menu"

selected_type = "platform"
message = "Welcome! Explore, collect gems and reach the magic portal."
message_time = 0

# AI command editor
ai_input = ""
ai_busy = False
ai_result = ""
ai_lock = threading.Lock()

# Moving hazards keep their original positions.
hazard_phases = {}


def say(text):
    global message, message_time
    message = str(text)[:150]
    message_time = pygame.time.get_ticks() + 5000


def get_rect(obj):
    return pygame.Rect(obj["x"], obj["y"], obj["w"], obj["h"])


def draw_text(text, x, y, color=WHITE, f=font):
    surface = f.render(str(text), True, color)
    screen.blit(surface, (x, y))


def draw_button(text, rect, active=False):
    color = (90, 59, 145) if active else PANEL
    pygame.draw.rect(screen, color, rect, border_radius=9)
    pygame.draw.rect(
        screen, PURPLE if active else (91, 74, 126),
        rect, 2, border_radius=9
    )
    surface = small.render(text, True, WHITE)
    screen.blit(surface, surface.get_rect(center=rect.center))


def draw_background():
    top, bottom = THEMES.get(theme_name, THEMES["Dreamy Purple"])

    for y in range(HEIGHT):
        t = y / HEIGHT
        color = tuple(
            int(top[i] * (1 - t) + bottom[i] * t)
            for i in range(3)
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

    # Stable stars
    for i in range(75):
        x = (i * 157 + 31) % WIDTH
        y = WORLD_TOP + (i * 83 + 15) % (WORLD_BOTTOM - WORLD_TOP)
        radius = 1 + (i % 3 == 0)
        pygame.draw.circle(screen, (140, 124, 202), (x, y), radius)

    # Floating glowing circles
    t = pygame.time.get_ticks() / 900
    for i in range(5):
        x = 100 + i * 200
        y = 150 + int(math.sin(t + i) * 12)
        pygame.draw.circle(screen, (95, 65, 150), (x, y), 24, 1)
        pygame.draw.circle(screen, PURPLE, (x, y), 5)


def draw_object(obj, index):
    rect = get_rect(obj)
    kind = obj["type"]

    if kind == "platform":
        pygame.draw.rect(screen, (91, 67, 145), rect, border_radius=6)
        pygame.draw.rect(screen, LAVENDER, rect, 2, border_radius=6)
        pygame.draw.line(
            screen, CYAN,
            (rect.x + 7, rect.y + 3),
            (rect.right - 7, rect.y + 3), 2
        )

    elif kind == "spike":
        points = [
            (rect.x, rect.bottom),
            (rect.centerx, rect.y),
            (rect.right, rect.bottom)
        ]
        pygame.draw.polygon(screen, RED, points)
        pygame.draw.polygon(screen, WHITE, points, 2)

    elif kind == "gem":
        if index in collected_gems and mode == "play":
            return

        pulse = int(math.sin(pygame.time.get_ticks() / 160 + index) * 3)
        x, y = rect.center
        points = [
            (x, y - 13 - pulse),
            (x + 10, y),
            (x, y + 13 + pulse),
            (x - 10, y)
        ]
        pygame.draw.polygon(screen, CYAN, points)
        pygame.draw.polygon(screen, WHITE, points, 2)

    elif kind == "hazard":
        t = pygame.time.get_ticks() / 300
        shift = int(math.sin(t + index) * 45)
        rect.x += shift
        pygame.draw.rect(screen, RED, rect, border_radius=9)
        pygame.draw.circle(screen, GOLD, (rect.centerx, rect.centery), 6)

    elif kind == "door":
        pygame.draw.rect(screen, (83, 48, 137), rect, border_radius=12)
        pygame.draw.rect(screen, GOLD, rect, 3, border_radius=12)
        pygame.draw.circle(screen, CYAN, (rect.centerx, rect.y + 22), 8)


def draw_hero():
    if hero_image:
        screen.blit(hero_image, (hero.x - 7, hero.y - 6))
    else:
        pygame.draw.ellipse(
            screen, PINK,
            (hero.x + 3, hero.y + 19, 28, 28)
        )
        pygame.draw.circle(
            screen, (255, 220, 196),
            (hero.centerx, hero.y + 13), 14
        )
        pygame.draw.circle(
            screen, PURPLE,
            (hero.centerx, hero.y + 6), 14
        )
        pygame.draw.circle(
            screen, (255, 220, 196),
            (hero.centerx, hero.y + 15), 10
        )


def draw_hud():
    pygame.draw.rect(screen, (27, 20, 52), (0, 0, WIDTH, 60))
    draw_text("DREAMQUEST AI", 15, 10, LAVENDER, font)
    draw_text(f"Gems: {score}", 230, 17, CYAN)
    draw_text(f"Lives: {lives}", 340, 17, PINK)
    draw_text(f"Theme: {theme_name}", 445, 18, GOLD, small)

    draw_button("PLAY", pygame.Rect(730, 12, 65, 35), mode == "play")
    draw_button("EDIT", pygame.Rect(805, 12, 65, 35), mode == "edit")
    draw_button("SAVE", pygame.Rect(880, 12, 55, 35))
    draw_button("LOAD", pygame.Rect(940, 12, 55, 35))


def draw_editor():
    pygame.draw.rect(screen, (24, 17, 48), (0, 555, WIDTH, 145))
    draw_text("LEVEL EDITOR  |  Select an item, then click in the world to place it",
              14, 560, LAVENDER, small)

    palette = [
        ("platform", "Platform"),
        ("spike", "Spikes"),
        ("gem", "Gem"),
        ("hazard", "Moving Hazard"),
        ("door", "Portal"),
        ("erase", "Erase")
    ]

    x = 14
    for kind, label in palette:
        width = 125 if kind == "hazard" else 100
        rect = pygame.Rect(x, 584, width, 33)
        draw_button(label, rect, selected_type == kind)
        x += width + 7

    draw_text("AI level command:", 15, 631, CYAN, small)
    input_rect = pygame.Rect(155, 625, 655, 35)
    pygame.draw.rect(screen, (43, 31, 72), input_rect, border_radius=8)
    pygame.draw.rect(screen, PURPLE, input_rect, 1, border_radius=8)

    visible_input = ai_input[-72:]
    draw_text(visible_input or "Example: Add five gems near the portal",
              165, 633, WHITE if ai_input else (165, 150, 190), small)

    draw_button("APPLY AI", pygame.Rect(820, 625, 90, 35))
    draw_button("CLEAR", pygame.Rect(915, 625, 70, 35))

    draw_text(
        "Left-click: Place | Right-click: Remove | Save before closing",
        15, 670, WHITE, small
    )


def save_level():
    data = {
        "objects": objects,
        "theme": theme_name
    }

    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
        say("Your fantasy level has been saved!")
    except OSError as exc:
        say(f"Could not save level: {exc}")


def load_level():
    global objects, theme_name, collected_gems

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        valid_types = {"platform", "spike", "gem", "hazard", "door"}
        loaded = []

        for obj in data.get("objects", []):
            if obj.get("type") not in valid_types:
                continue

            x = max(0, min(WIDTH - 20, int(obj.get("x", 0))))
            y = max(WORLD_TOP, min(WORLD_BOTTOM - 10, int(obj.get("y", 100))))
            w = max(15, min(400, int(obj.get("w", 30))))
            h = max(15, min(150, int(obj.get("h", 25))))

            loaded.append({
                "type": obj["type"],
                "x": x, "y": y, "w": w, "h": h
            })

        if loaded:
            objects = loaded

        if data.get("theme") in THEMES:
            theme_name = data["theme"]

        collected_gems = set()
        say("Level loaded successfully!")

    except (OSError, ValueError, json.JSONDecodeError):
        say("No saved level found. Create a level and save it first.")


def add_object(kind, x, y):
    sizes = {
        "platform": (120, 18),
        "spike": (34, 28),
        "gem": (22, 22),
        "hazard": (42, 32),
        "door": (36, 65)
    }

    w, h = sizes[kind]
    x = max(0, min(WIDTH - w, x - w // 2))
    y = max(WORLD_TOP, min(WORLD_BOTTOM - h, y - h // 2))

    # Keep the ground platform in place
    if kind == "platform" and y > 500 and x < 10 and w > 900:
        return

    objects.append({
        "type": kind,
        "x": x, "y": y, "w": w, "h": h
    })


def remove_nearest(x, y):
    candidates = [
        (i, obj) for i, obj in enumerate(objects)
        if not (
            obj["type"] == "platform"
            and obj["x"] == 0
            and obj["w"] >= 900
            and obj["y"] >= 500
        )
    ]

    if not candidates:
        return

    index, obj = min(
        candidates,
        key=lambda pair: math.hypot(
            get_rect(pair[1]).centerx - x,
            get_rect(pair[1]).centery - y
        )
    )

    if get_rect(obj).inflate(30, 30).collidepoint(x, y):
        objects.pop(index)
        say("Object removed.")


def apply_local_command(command):
    """Simple fallback commands if Ollama is unavailable."""
    global theme_name, objects, collected_gems

    text = command.lower()
    count_match = re.search(r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b", text)

    words = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }

    count = 1
    if count_match:
        raw = count_match.group(1)
        count = int(raw) if raw.isdigit() else words.get(raw, 1)

    if "clear" in text or "remove all" in text or "delete all" in text:
        objects = [
            obj for obj in objects
            if obj["type"] == "platform"
            and obj["x"] == 0 and obj["w"] >= 900
        ]
        collected_gems = set()
        say("Cleared the level objects. Your ground remains.")
        return

    if "forest" in text:
        theme_name = "Enchanted Forest"
        say("Theme changed to Enchanted Forest!")
        return
    if "ice" in text or "snow" in text:
        theme_name = "Ice Palace"
        say("Theme changed to Ice Palace!")
        return
    if "candy" in text:
        theme_name = "Candy Kingdom"
        say("Theme changed to Candy Kingdom!")
        return
    if "purple" in text or "dream" in text:
        theme_name = "Dreamy Purple"
        say("Theme changed to Dreamy Purple!")
        return

    if "remove" in text or "delete" in text:
        kind = next(
            (k for k in ["spike", "gem", "hazard", "platform", "door"]
             if k in text or (k == "hazard" and "obstacle" in text)),
            None
        )
        if kind:
            removable = [
                obj for obj in objects
                if obj["type"] == kind and not (
                    kind == "platform" and obj["x"] == 0 and obj["w"] >= 900
                )
            ]
            for obj in removable[:count]:
                objects.remove(obj)
            collected_gems = set()
            say(f"Removed {min(count, len(removable))} {kind}(s).")
        else:
            say("Try: Remove all spikes, remove gems, or remove hazards.")
        return

    kind = None
    if "platform" in text or "bridge" in text:
        kind = "platform"
    elif "spike" in text or "trap" in text:
        kind = "spike"
    elif "gem" in text or "crystal" in text:
        kind = "gem"
    elif "hazard" in text or "enemy" in text or "obstacle" in text:
        kind = "hazard"
    elif "door" in text or "portal" in text or "exit" in text:
        kind = "door"

    if kind:
        for _ in range(max(1, min(count, 20))):
            add_object(
                kind,
                random.randint(80, WIDTH - 80),
                random.randint(160, 485)
            )
        collected_gems = set()
        say(f"Added {count} {kind}(s) to your world!")
        return

    say("Try: Add five gems, add platforms, remove all spikes, or change theme to forest.")


def ask_ai(command):
    """
    Ask Ollama to convert natural language into safe edit actions.
    If AI is offline, use local command handling.
    """
    global ai_busy, ai_result

    prompt = f"""
You are the level-editing assistant for a 2D fantasy platform game.
Read the player's command and return ONLY a JSON object.
Supported action values: add, remove, clear, theme.
Supported object types: platform, spike, gem, hazard, door.
Supported themes: Dreamy Purple, Enchanted Forest, Candy Kingdom, Ice Palace.
Count must be an integer from 1 to 20.
Examples:
"Add five gems" -> {{"action":"add","type":"gem","count":5}}
"Add a bridge" -> {{"action":"add","type":"platform","count":1}}
"Remove all spikes" -> {{"action":"remove","type":"spike","count":20}}
"Clear everything" -> {{"action":"clear"}}
"Make the world an icy palace" -> {{"action":"theme","theme":"Ice Palace"}}
"Add three moving obstacles" -> {{"action":"add","type":"hazard","count":3}}
Player command: {command}
Return JSON only. No Markdown.
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False
            },
            timeout=18
        )
        response.raise_for_status()

        answer = response.json().get("response", "").strip()
        match = re.search(r"\{.*\}", answer, re.DOTALL)
        if not match:
            raise ValueError("AI did not return JSON")

        action = json.loads(match.group(0))

        with ai_lock:
            ai_result = action

    except Exception:
        with ai_lock:
            ai_result = {"fallback": command}

    finally:
        with ai_lock:
            ai_busy = False


def start_ai_command():
    global ai_busy, ai_result

    command = ai_input.strip()
    if not command:
        say("Type a level-editing command first.")
        return

    if ai_busy:
        say("The AI is still working. Please wait.")
        return

    with ai_lock:
        ai_result = None
        ai_busy = True

    threading.Thread(
        target=ask_ai, args=(command,), daemon=True
    ).start()


def apply_ai_result():
    global ai_result, objects, theme_name, collected_gems

    with ai_lock:
        result = ai_result
        ai_result = None

    if not result:
        return

    if "fallback" in result:
        apply_local_command(result["fallback"])
        return

    action = result.get("action", "")
    kind = result.get("type", "")
    count = max(1, min(20, int(result.get("count", 1))))

    if action == "theme":
        chosen = result.get("theme", "")
        if chosen in THEMES:
            theme_name = chosen
            say(f"Theme changed to {theme_name}!")
        else:
            say("Unknown theme. Try forest, candy, ice or purple.")
        return

    if action == "clear":
        objects = [
            obj for obj in objects
            if obj["type"] == "platform"
            and obj["x"] == 0 and obj["w"] >= 900
        ]
        collected_gems = set()
        say("Level cleared. The ground remains.")
        return

    if kind not in {"platform", "spike", "gem", "hazard", "door"}:
        say("The AI did not understand that object. Try gems, spikes or platforms.")
        return

    if action == "remove":
        removable = [
            obj for obj in objects
            if obj["type"] == kind and not (
                kind == "platform" and obj["x"] == 0 and obj["w"] >= 900
            )
        ]
        for obj in removable[:count]:
            objects.remove(obj)
        collected_gems = set()
        say(f"Removed {min(count, len(removable))} {kind}(s).")
        return

    if action == "add":
        for _ in range(count):
            add_object(
                kind,
                random.randint(70, WIDTH - 70),
                random.randint(150, 485)
            )
        collected_gems = set()
        say(f"AI added {count} {kind}(s) to your level!")
        return

    say("Try a command such as: Add five gems.")


def start_playing():
    global mode, hero, player_x, player_y
    global velocity_y, lives, score, collected_gems

    mode = "play"
    hero.x, hero.y = spawn_position
    player_x = float(hero.x)
    player_y = float(hero.y)
    velocity_y = 0.0
    lives = 3
    score = 0
    collected_gems = set()
    say("Reach the glowing portal! Collect gems and avoid red traps.")


# ---------- MAIN LOOP ----------
running = True

while running:
    clock.tick(60)
    now = pygame.time.get_ticks()

    draw_background()

    # Draw game objects
    for i, obj in enumerate(objects):
        draw_object(obj, i)

    if mode in ("play", "edit"):
        draw_hero()

    draw_hud()

    if mode == "menu":
        title = large.render("CREATE YOUR MAGIC WORLD", True, LAVENDER)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 205)))

        draw_text(
            "Explore a fantasy world, overcome obstacles and collect gems.",
            155, 265, WHITE, small
        )
        draw_text(
            "Build your own levels and ask AI to change them in English.",
            145, 295, CYAN, small
        )
        draw_button("START ADVENTURE", pygame.Rect(350, 350, 180, 48))
        draw_button("OPEN LEVEL EDITOR", pygame.Rect(545, 350, 190, 48))

        # Dark menu overlay behind the content
        # Keep the actual level visible as a preview.

    if mode == "edit":
        draw_editor()

    if mode == "play":
        keys = pygame.key.get_pressed()

        dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(
            keys[pygame.K_LEFT] or keys[pygame.K_a]
        )

        player_x += dx * 4
        hero.x = int(player_x)

        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and on_ground:
            velocity_y = -12
            on_ground = False

        velocity_y += 0.48
        velocity_y = min(velocity_y, 12)
        player_y += velocity_y
        hero.y = int(player_y)

        # Horizontal boundaries
        hero.left = max(0, hero.left)
        hero.right = min(WIDTH, hero.right)
        player_x = float(hero.x)

        # Platform collision only while falling
        on_ground = False

        if velocity_y >= 0:
            for obj in objects:
                if obj["type"] != "platform":
                    continue

                rect = get_rect(obj)

                if (
                    hero.right > rect.left
                    and hero.left < rect.right
                    and hero.bottom >= rect.top
                    and hero.bottom - velocity_y <= rect.top + 5
                ):
                    hero.bottom = rect.top
                    player_y = float(hero.y)
                    velocity_y = 0
                    on_ground = True

        # Falling off the level
        if hero.top > HEIGHT:
            lives -= 1
            hero.x, hero.y = spawn_position
            player_x, player_y = float(hero.x), float(hero.y)
            velocity_y = 0
            say("You fell! Try the jump again.")

        # Collect gems
        for i, obj in enumerate(objects):
            if obj["type"] == "gem" and i not in collected_gems:
                if hero.colliderect(get_rect(obj)):
                    collected_gems.add(i)
                    score += 1
                    say("Gem collected! Keep going!")

        # Hazard collision
        for i, obj in enumerate(objects):
            if obj["type"] in ("spike", "hazard"):
                rect = get_rect(obj)

                if obj["type"] == "hazard":
                    rect.x += int(
                        math.sin(now / 300 + i) * 45
                    )

                if hero.colliderect(rect):
                    lives -= 1
                    hero.x, hero.y = spawn_position
                    player_x, player_y = float(hero.x), float(hero.y)
                    velocity_y = 0
                    say("Ouch! Avoid the red obstacles.")
                    break

        # Portal collision
        for obj in objects:
            if obj["type"] == "door" and hero.colliderect(get_rect(obj)):
                mode = "victory"
                break

        if lives <= 0:
            mode = "gameover"

        draw_text("Move: A/D or arrows   Jump: SPACE / W / UP", 15, 62, WHITE, small)
        draw_text("Avoid red traps and reach the glowing portal!", 15, 82, CYAN, small)

    if mode in ("victory", "gameover"):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 5, 30, 205))
        screen.blit(overlay, (0, 0))

        title = "LEVEL COMPLETE!" if mode == "victory" else "TRY AGAIN!"
        color = GOLD if mode == "victory" else PINK
        label = large.render(title, True, color)
        screen.blit(label, label.get_rect(center=(WIDTH // 2, 270)))

        draw_text(f"Gems collected: {score}", WIDTH // 2 - 85, 325, CYAN)
        draw_button("PLAY AGAIN", pygame.Rect(400, 375, 180, 45))

    # Toast message
    if now < message_time:
        pygame.draw.rect(
            screen, (31, 23, 60),
            (15, HEIGHT - 38, 700, 28),
            border_radius=7
        )
        draw_text(message, 25, HEIGHT - 34, CYAN, small)

    # ---------- EVENTS ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if mode == "edit":
                if event.key == pygame.K_RETURN:
                    start_ai_command()
                    ai_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    ai_input = ai_input[:-1]
                elif event.key == pygame.K_ESCAPE:
                    mode = "menu"
                elif event.unicode and event.unicode.isprintable():
                    if len(ai_input) < 180:
                        ai_input += event.unicode

            elif event.key == pygame.K_ESCAPE:
                mode = "menu"

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Top navigation
            if my < 55:
                if 730 <= mx <= 795:
                    start_playing()
                elif 805 <= mx <= 870:
                    mode = "edit"
                    say("Select an object below, then click where you want to place it.")
                elif 880 <= mx <= 935:
                    save_level()
                elif 940 <= mx <= 995:
                    load_level()

            elif mode == "menu":
                if 350 <= mx <= 530 and 350 <= my <= 398:
                    start_playing()
                elif 545 <= mx <= 735 and 350 <= my <= 398:
                    mode = "edit"

            elif mode in ("gameover", "victory"):
                if 400 <= mx <= 580 and 375 <= my <= 420:
                    start_playing()

            elif mode == "edit":
                if event.button == 3 and WORLD_TOP < my < 550:
                    remove_nearest(mx, my)

                elif event.button == 1:
                    if my >= 584 and my <= 617:
                        if mx < 114:
                            selected_type = "platform"
                        elif mx < 221:
                            selected_type = "spike"
                        elif mx < 328:
                            selected_type = "gem"
                        elif mx < 460:
                            selected_type = "hazard"
                        elif mx < 567:
                            selected_type = "door"
                        elif mx < 674:
                            selected_type = "erase"

                    elif 625 <= my <= 660:
                        if 820 <= mx <= 910:
                            start_ai_command()
                        elif 915 <= mx <= 985:
                            objects = [
                                obj for obj in objects
                                if obj["type"] == "platform"
                                and obj["x"] == 0 and obj["w"] >= 900
                            ]
                            collected_gems = set()
                            say("Cleared the level objects.")

                    elif WORLD_TOP < my < 545:
                        if selected_type == "erase":
                            remove_nearest(mx, my)
                        else:
                            add_object(selected_type, mx, my)
                            say(f"Placed {selected_type}.")

    # Apply AI results without modifying the game from the worker thread.
    apply_ai_result()

    pygame.display.flip()

pygame.quit()
