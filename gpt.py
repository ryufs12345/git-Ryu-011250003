"""
Top-Down Shooter — Single-file Python game using tkinter
Created for: You (best effort single-file game)
How to run: save this file as `py_topdown_shooter.py` and run `python py_topdown_shooter.py`
Requires: Python 3.7+ (tkinter included)

Features:
- Player movement with arrow keys or WASD
- Shoot with Space or mouse click
- Multiple enemy types with simple AI
- Power-ups (health, rapid fire, shield)
- Score, levels, and wave system
- Pause, Start menu, Game Over screen
- High score saved to `highscore.txt`
- Clean, readable code with comments so you can extend it

Enjoy! If you'd like a different genre (platformer, puzzle, RPG) or
want assets (images/sound) added, tell me and I'll adapt it.
"""

import tkinter as tk
import random
import time
import math
import json
import os

# ----------------------------- Configuration -----------------------------
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 28
PLAYER_SPEED = 6
BULLET_SPEED = 14
ENEMY_BASE_SPEED = 2.0
SPAWN_INTERVAL = 1200  # milliseconds
POWERUP_CHANCE = 0.12
FIRE_COOLDOWN = 220  # milliseconds

HIGH_SCORE_FILE = "highscore.txt"

# ----------------------------- Utility Functions -----------------------------
# ... keep all your existing imports and classes ...

class Kamehameha(GameObject):
    def __init__(self, x, y, direction=(0, -1)):
        super().__init__(x, y)
        self.duration = 30  # frames
        self.dir = direction
        self.width = 40
        self.color = 'cyan'

    def update(self, dt):
        self.duration -= 1
        if self.duration <= 0:
            self.dead = True

    def draw(self, canvas):
        # Draw vertical beam
        if self.dir[1] < 0:  # upwards
            canvas.create_rectangle(self.x - self.width//2, 0,
                                    self.x + self.width//2, self.y,
                                    fill=self.color, stipple="gray25")
        else:  # downwards if needed
            canvas.create_rectangle(self.x - self.width//2, self.y,
                                    self.x + self.width//2, HEIGHT,
                                    fill=self.color, stipple="gray25")

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.size = PLAYER_SIZE
        self.color = "#2ECC71"
        self.speed = PLAYER_SPEED
        self.vx = 0
        self.vy = 0
        self.health = 100
        self.max_health = 100
        self.last_shot = 0
        self.fire_rate = FIRE_COOLDOWN
        self.shield_time = 0
        self.rapid_time = 0
        self.score = 0
        self.kamehameha_cd = 0  # <<< NEW

    def move(self, dx, dy):
        self.vx = dx * self.speed
        self.vy = dy * self.speed

    def shoot(self, target_x, target_y, now):
        if now - self.last_shot < self.fire_rate:
            return None
        self.last_shot = now
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy) or 1
        nx = dx / dist
        ny = dy / dist
        speed = BULLET_SPEED * (1.6 if self.rapid_time > 0 else 1.0)
        return Bullet(self.x, self.y, nx * speed, ny * speed, owner='player')

    def take_damage(self, amt):
        if self.shield_time > 0:
            return
        self.health -= amt
        if self.health <= 0:
            self.dead = True

    def update(self, dt):
        if self.shield_time > 0:
            self.shield_time -= dt
        if self.rapid_time > 0:
            self.rapid_time -= dt
        if self.kamehameha_cd > 0:           # <<< NEW
            self.kamehameha_cd -= dt
        self.x += self.vx
        self.y += self.vy
        self.x = clamp(self.x, 20, WIDTH - 20)
        self.y = clamp(self.y, 20, HEIGHT - 20)

    def draw(self, canvas):
        s = self.size
        points = [self.x, self.y - s // 2, self.x - s // 2, self.y + s // 2, self.x + s // 2, self.y + s // 2]
        canvas.create_polygon(points, fill=self.color, outline='black', width=1)
        bar_w = 80
        hx = self.x - bar_w / 2
        hy = self.y + s
        canvas.create_rectangle(hx, hy, hx + bar_w, hy + 8, fill='#333')
        hp_w = (self.health / self.max_health) * bar_w
        canvas.create_rectangle(hx + 1, hy + 1, hx + 1 + hp_w - 2, hy + 7, fill='#E74C3C')
        if self.shield_time > 0:
            canvas.create_oval(self.x - s, self.y - s, self.x + s, self.y + s, outline='cyan', width=3)


class Game:
    # ... keep existing __init__ ...

    def setup_bindings(self):
        self.root.bind('<KeyPress>', self.on_key)
        self.root.bind('<KeyRelease>', self.on_key_release)
        self.root.bind('<Button-1>', self.on_click)
        self.root.bind('<Motion>', self.on_mouse_move)
        self.root.bind('<space>', lambda e: None)

    def on_key(self, event):
        self.keys.add(event.keysym)
        if event.keysym == 'Escape':
            if self.game_state == 'playing':
                self.toggle_pause()
        if self.game_state == 'menu' and event.keysym == 'Return':
            self.start_game()
        if self.game_state == 'gameover' and event.keysym == 'Return':
            self.start_game()

        # <<< NEW: Press E for Kamehameha
        if event.keysym.lower() == 'e' and self.game_state == 'playing':
            if self.player.kamehameha_cd <= 0:
                beam = Kamehameha(self.player.x, self.player.y, (0, -1))
                self.bullets.append(beam)
                self.player.kamehameha_cd = 8000  # 8 seconds cooldown

    # ... keep rest unchanged ...

    def update(self, dt_ms):
        dt = dt_ms / 1000.0
        # (player movement & shooting unchanged)

        self.player.update(dt_ms)

        for b in self.bullets:
            b.update(dt)
        self.bullets = [b for b in self.bullets if not b.dead]

        # damage from Kamehameha <<< NEW
        for b in [bb for bb in self.bullets if isinstance(bb, Kamehameha)]:
            for e in list(self.enemies):
                if abs(e.x - b.x) < b.width and e.y < b.y:
                    e.health -= 50
                    if e.health <= 0:
                        e.dead = True
                        self.player.score += int(20 * (1 + e.level/2))

        # (rest of collision/update code unchanged)

def clamp(v, a, b):
    return max(a, min(b, v))


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# ----------------------------- Game Objects -----------------------------
class GameObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dead = False

    def update(self, dt):
        pass

    def draw(self, canvas):
        pass


class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.size = PLAYER_SIZE
        self.color = "#2ECC71"
        self.speed = PLAYER_SPEED
        self.vx = 0
        self.vy = 0
        self.health = 100
        self.max_health = 100
        self.last_shot = 0
        self.fire_rate = FIRE_COOLDOWN
        self.shield_time = 0
        self.rapid_time = 0
        self.score = 0

    def move(self, dx, dy):
        self.vx = dx * self.speed
        self.vy = dy * self.speed

    def shoot(self, target_x, target_y, now):
        if now - self.last_shot < self.fire_rate:
            return None
        self.last_shot = now
        # Direction vector
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy) or 1
        nx = dx / dist
        ny = dy / dist
        speed = BULLET_SPEED * (1.6 if self.rapid_time > 0 else 1.0)
        return Bullet(self.x, self.y, nx * speed, ny * speed, owner='player')

    def take_damage(self, amt):
        if self.shield_time > 0:
            return
        self.health -= amt
        if self.health <= 0:
            self.dead = True

    def update(self, dt):
        # decays
        if self.shield_time > 0:
            self.shield_time -= dt
        if self.rapid_time > 0:
            self.rapid_time -= dt
        self.x += self.vx
        self.y += self.vy
        # clamp to screen
        self.x = clamp(self.x, 20, WIDTH - 20)
        self.y = clamp(self.y, 20, HEIGHT - 20)

    def draw(self, canvas):
        s = self.size
        points = [self.x, self.y - s // 2, self.x - s // 2, self.y + s // 2, self.x + s // 2, self.y + s // 2]
        canvas.create_polygon(points, fill=self.color, outline='black', width=1)
        # health bar
        bar_w = 80
        hx = self.x - bar_w / 2
        hy = self.y + s
        canvas.create_rectangle(hx, hy, hx + bar_w, hy + 8, fill='#333')
        hp_w = (self.health / self.max_health) * bar_w
        canvas.create_rectangle(hx + 1, hy + 1, hx + 1 + hp_w - 2, hy + 7, fill='#E74C3C')
        # shield overlay
        if self.shield_time > 0:
            canvas.create_oval(self.x - s, self.y - s, self.x + s, self.y + s, outline='cyan', width=3)


class Bullet(GameObject):
    def __init__(self, x, y, vx, vy, owner='enemy'):
        super().__init__(x, y)
        self.vx = vx
        self.vy = vy
        self.radius = 4 if owner == 'player' else 6
        self.owner = owner
        self.color = '#3498DB' if owner == 'player' else '#E67E22'

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        if self.x < -50 or self.x > WIDTH + 50 or self.y < -50 or self.y > HEIGHT + 50:
            self.dead = True

    def draw(self, canvas):
        r = self.radius
        canvas.create_oval(self.x - r, self.y - r, self.x + r, self.y + r, fill=self.color)


class Enemy(GameObject):
    def __init__(self, x, y, type_id=0, level=1):
        super().__init__(x, y)
        self.type_id = type_id
        self.level = level
        self.angle = 0
        # type variations
        if type_id == 0:
            self.color = '#E74C3C'
            self.health = 10 + level * 3
            self.speed = ENEMY_BASE_SPEED + level * 0.12
            self.radius = 18
            self.shoot_prob = 0.02
        elif type_id == 1:
            self.color = '#9B59B6'
            self.health = 18 + level * 5
            self.speed = (ENEMY_BASE_SPEED - 0.6) + level * 0.08
            self.radius = 26
            self.shoot_prob = 0.045
        else:
            self.color = '#F1C40F'
            self.health = 30 + level * 8
            self.speed = (ENEMY_BASE_SPEED + 0.6) + level * 0.15
            self.radius = 36
            self.shoot_prob = 0.06

    def update(self, dt, player=None):
        # simple homing towards player with some wobble
        if player:
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.hypot(dx, dy) or 1
            nx = dx / dist
            ny = dy / dist
            wobble = math.sin(time.time() * 3 + self.level) * 0.4
            self.x += (nx + wobble * 0.2) * self.speed
            self.y += (ny + wobble * 0.2) * self.speed
        else:
            self.y += self.speed

        # die off-screen
        if self.x < -100 or self.x > WIDTH + 100 or self.y > HEIGHT + 120:
            self.dead = True

    def draw(self, canvas):
        r = self.radius
        canvas.create_oval(self.x - r, self.y - r, self.x + r, self.y + r, fill=self.color, outline='black')
        # simple health nib
        hp_w = max(0, (self.health / (10 + self.level * 8)) * (r * 1.6))
        canvas.create_rectangle(self.x - r, self.y - r - 10, self.x - r + hp_w, self.y - r - 6, fill='red')


class Powerup(GameObject):
    TYPES = ['health', 'rapid', 'shield', 'score']

    def __init__(self, x, y, ptype=None):
        super().__init__(x, y)
        self.ptype = ptype if ptype else random.choice(Powerup.TYPES)
        self.radius = 12

    def update(self, dt):
        self.y += 1.2
        if self.y > HEIGHT + 40:
            self.dead = True

    def draw(self, canvas):
        r = self.radius
        if self.ptype == 'health':
            c = '#E74C3C'
            canvas.create_rectangle(self.x - r, self.y - r, self.x + r, self.y + r, fill=c)
            canvas.create_text(self.x, self.y, text='+', fill='white')
        elif self.ptype == 'rapid':
            c = '#3498DB'
            canvas.create_oval(self.x - r, self.y - r, self.x + r, self.y + r, fill=c)
            canvas.create_text(self.x, self.y, text='⚡', font=('Arial', 10))
        elif self.ptype == 'shield':
            c = '#1ABC9C'
            canvas.create_polygon(self.x, self.y - r, self.x - r, self.y + r, self.x + r, self.y + r, fill=c)
            canvas.create_text(self.x, self.y, text='S', fill='white')
        else:
            c = '#F39C12'
            canvas.create_rectangle(self.x - r, self.y - r, self.x + r, self.y + r, fill=c)
            canvas.create_text(self.x, self.y, text='★', fill='white')


# ----------------------------- Game Controller -----------------------------
class Game:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='#0B132B')
        self.canvas.pack()
        self.running = False
        self.paused = False
        self.last_time = time.time()
        self.player = Player(WIDTH // 2, HEIGHT - 80)
        self.objects = []  # all bullets, enemies, powerups
        self.enemies = []
        self.bullets = []
        self.powerups = []
        self.keys = set()
        self.level = 1
        self.wave = 1
        self.spawn_job = None
        self.game_state = 'menu'  # menu, playing, gameover
        self.high_score = self.load_high_score()
        self.setup_bindings()
        self.draw_menu()

    def setup_bindings(self):
        self.root.bind('<KeyPress>', self.on_key)
        self.root.bind('<KeyRelease>', self.on_key_release)
        self.root.bind('<Button-1>', self.on_click)
        self.root.bind('<Motion>', self.on_mouse_move)
        # for mac keyboards etc
        self.root.bind('<space>', lambda e: None)

    def on_key(self, event):
        self.keys.add(event.keysym)
        if event.keysym == 'Escape':
            if self.game_state == 'playing':
                self.toggle_pause()
        if self.game_state == 'menu' and event.keysym == 'Return':
            self.start_game()
        if self.game_state == 'gameover' and event.keysym == 'Return':
            self.start_game()

    def on_key_release(self, event):
        if event.keysym in self.keys:
            self.keys.remove(event.keysym)

    def on_click(self, event):
        if self.game_state == 'menu':
            self.start_game()
        elif self.game_state == 'playing':
            bullet = self.player.shoot(event.x, event.y, int(time.time() * 1000))
            if bullet:
                self.bullets.append(bullet)
        elif self.game_state == 'gameover':
            self.start_game()

    def on_mouse_move(self, event):
        # optional: aim with mouse; not used for movement
        pass

    def draw_menu(self):
        self.canvas.delete('all')
        self.canvas.create_text(WIDTH/2, HEIGHT/2 - 40, text='PY TOP-DOWN SHOOTER', font=('Helvetica', 28, 'bold'), fill='white')
        self.canvas.create_text(WIDTH/2, HEIGHT/2 + 10, text='Arrow keys / WASD to move · Space or Click to shoot', font=('Arial', 14), fill='white')
        self.canvas.create_text(WIDTH/2, HEIGHT/2 + 50, text='Press ENTER or Click to Start', font=('Arial', 12), fill='#AAAAAA')
        self.canvas.create_text(100, 20, text=f'High Score: {self.high_score}', fill='yellow', anchor='w')

    def start_game(self):
        self.canvas.delete('all')
        self.player = Player(WIDTH // 2, HEIGHT - 80)
        self.objects = []
        self.enemies = []
        self.bullets = []
        self.powerups = []
        self.level = 1
        self.wave = 1
        self.game_state = 'playing'
        self.last_time = time.time()
        self.schedule_spawn()
        self.game_loop()

    def schedule_spawn(self):
        if self.spawn_job:
            self.root.after_cancel(self.spawn_job)
        self.spawn_job = self.root.after(SPAWN_INTERVAL, self.spawn_wave)

    def spawn_wave(self):
        # spawn a handful of enemies with increasing difficulty
        count = min(12, 4 + self.level + random.randint(0, self.level))
        for _ in range(count):
            side = random.choice(['left', 'right', 'top'])
            if side == 'left':
                x = random.randint(-20, 60)
                y = random.randint(20, HEIGHT // 2)
            elif side == 'right':
                x = random.randint(WIDTH - 60, WIDTH + 20)
                y = random.randint(20, HEIGHT // 2)
            else:
                x = random.randint(60, WIDTH - 60)
                y = random.randint(-80, -20)
            t = random.choices([0,1,2], weights=[60,30,10])[0]
            enemy = Enemy(x, y, type_id=t, level=self.level)
            self.enemies.append(enemy)
        # maybe drop powerups
        if random.random() < POWERUP_CHANCE:
            px = random.randint(60, WIDTH - 60)
            py = random.randint(-40, 20)
            self.powerups.append(Powerup(px, py))
        # next wave slightly later
        self.level += 0.5
        self.schedule_spawn()

    def toggle_pause(self):
        if self.game_state != 'playing':
            return
        self.paused = not self.paused
        if not self.paused:
            self.last_time = time.time()
            self.game_loop()
        else:
            self.canvas.create_text(WIDTH/2, HEIGHT/2, text='PAUSED', font=('Helvetica', 36), fill='white', tag='pause')

    def game_loop(self):
        if self.game_state != 'playing':
            return
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        if not self.paused:
            self.update(int(dt * 1000))
            self.render()
        # continue
        self.root.after(16, self.game_loop)

    def update(self, dt_ms):
        dt = dt_ms / 1000.0
        # handle input
        dx = 0
        dy = 0
        if 'Left' in self.keys or 'a' in self.keys or 'A' in self.keys:
            dx -= 1
        if 'Right' in self.keys or 'd' in self.keys or 'D' in self.keys:
            dx += 1
        if 'Up' in self.keys or 'w' in self.keys or 'W' in self.keys:
            dy -= 1
        if 'Down' in self.keys or 's' in self.keys or 'S' in self.keys:
            dy += 1
        self.player.move(dx, dy)

        # auto-fire with space
        if 'space' in self.keys or 'spacebar' in self.keys or 'space' in self.keys:
            mouse_x, mouse_y = self.root.winfo_pointerx() - self.root.winfo_rootx(), self.root.winfo_pointery() - self.root.winfo_rooty()
            bullet = self.player.shoot(mouse_x, mouse_y, int(time.time() * 1000))
            if bullet:
                self.bullets.append(bullet)

        # update player
        self.player.update(dt_ms)

        # update bullets
        for b in self.bullets:
            b.update(dt)
        self.bullets = [b for b in self.bullets if not b.dead]

        # update enemies
        for e in self.enemies:
            e.update(dt, player=self.player)
            # enemy can shoot occasionally
            if random.random() < e.shoot_prob:
                dx = self.player.x - e.x
                dy = self.player.y - e.y
                d = math.hypot(dx, dy) or 1
                nx, ny = dx/d, dy/d
                speed = 6 + e.level * 0.1
                self.bullets.append(Bullet(e.x, e.y, nx * speed, ny * speed, owner='enemy'))
        self.enemies = [e for e in self.enemies if not e.dead]

        # update powerups
        for p in self.powerups:
            p.update(dt)
        self.powerups = [p for p in self.powerups if not p.dead]

        # collisions: bullets vs enemies
        for b in list(self.bullets):
            if b.owner == 'player':
                for e in list(self.enemies):
                    if distance((b.x, b.y), (e.x, e.y)) < e.radius + b.radius:
                        e.health -= 8
                        b.dead = True
                        if e.health <= 0:
                            e.dead = True
                            self.player.score += int(10 * (1 + e.level/2))
                            # spawn small powerup sometimes
                            if random.random() < 0.18:
                                self.powerups.append(Powerup(e.x, e.y))
            else:
                # enemy bullet vs player
                if distance((b.x, b.y), (self.player.x, self.player.y)) < b.radius + (self.player.size/2):
                    self.player.take_damage(10)
                    b.dead = True

        # enemies vs player
        for e in list(self.enemies):
            if distance((e.x, e.y), (self.player.x, self.player.y)) < e.radius + (self.player.size / 2):
                self.player.take_damage(16)
                e.dead = True

        # player pickups
        for p in list(self.powerups):
            if distance((p.x, p.y), (self.player.x, self.player.y)) < p.radius + (self.player.size / 2):
                self.apply_powerup(p)
                p.dead = True

        # level progression and difficulty
        # every 200 points increase wave
        if self.player.score > self.wave * 200:
            self.wave += 1
            # bump enemy speed and slightly increase spawn frequency
            global SPAWN_INTERVAL
            SPAWN_INTERVAL = max(400, SPAWN_INTERVAL - 40)

        # check game over
        if self.player.dead:
            self.end_game()

    def apply_powerup(self, p):
        if p.ptype == 'health':
            self.player.health = clamp(self.player.health + 28, 0, self.player.max_health)
        elif p.ptype == 'rapid':
            self.player.rapid_time += 6.0
        elif p.ptype == 'shield':
            self.player.shield_time += 6.0
        elif p.ptype == 'score':
            self.player.score += 80

    def render(self):
        self.canvas.delete('all')
        # background grid
        for gx in range(0, WIDTH, 80):
            self.canvas.create_line(gx, 0, gx, HEIGHT, fill='#071019')
        for gy in range(0, HEIGHT, 80):
            self.canvas.create_line(0, gy, WIDTH, gy, fill='#071019')

        # draw powerups
        for p in self.powerups:
            p.draw(self.canvas)
        # draw enemies
        for e in self.enemies:
            e.draw(self.canvas)
        # draw bullets
        for b in self.bullets:
            b.draw(self.canvas)
        # draw player
        self.player.draw(self.canvas)

        # HUD
        self.canvas.create_text(12, 12, anchor='nw', text=f'Score: {self.player.score}', fill='white', font=('Arial', 12))
        self.canvas.create_text(WIDTH - 12, 12, anchor='ne', text=f'Wave: {self.wave}', fill='white', font=('Arial', 12))
        self.canvas.create_text(12, 34, anchor='nw', text=f'Health: {int(self.player.health)}', fill='white', font=('Arial', 12))
        self.canvas.create_text(WIDTH - 12, 34, anchor='ne', text=f'High: {self.high_score}', fill='yellow', font=('Arial', 12))

        # show status effects
        sx = WIDTH/2
        sy = 18
        statuses = []
        if self.player.rapid_time > 0:
            statuses.append(f'RAPID({int(self.player.rapid_time)})')
        if self.player.shield_time > 0:
            statuses.append(f'SHIELD({int(self.player.shield_time)})')
        if statuses:
            self.canvas.create_text(sx, sy, text=' | '.join(statuses), fill='white')

    def end_game(self):
        self.game_state = 'gameover'
        self.save_high_score(self.player.score)
        self.canvas.delete('all')
        self.canvas.create_text(WIDTH/2, HEIGHT/2 - 40, text='GAME OVER', font=('Helvetica', 36, 'bold'), fill='white')
        self.canvas.create_text(WIDTH/2, HEIGHT/2, text=f'Score: {self.player.score}', font=('Helvetica', 18), fill='#FFDD57')
        self.canvas.create_text(WIDTH/2, HEIGHT/2 + 30, text=f'High Score: {self.high_score}', font=('Helvetica', 14), fill='yellow')
        self.canvas.create_text(WIDTH/2, HEIGHT/2 + 70, text='Press ENTER or Click to play again', font=('Helvetica', 12), fill='#AAAAAA')
        if self.spawn_job:
            self.root.after_cancel(self.spawn_job)

    # ----------------------------- High score persistence -----------------------------
    def load_high_score(self):
        try:
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    return int(f.read().strip() or 0)
        except Exception:
            return 0
        return 0

    def save_high_score(self, score):
        if score > self.high_score:
            self.high_score = score
            try:
                with open(HIGH_SCORE_FILE, 'w') as f:
                    f.write(str(score))
            except Exception:
                pass


# ----------------------------- Run the game -----------------------------

def main():
    root = tk.Tk()
    root.title('Py Top-Down Shooter')
    # center on screen
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - WIDTH) // 2
    y = (screen_h - HEIGHT) // 2
    root.geometry(f'{WIDTH}x{HEIGHT}+{x}+{y}')
    root.resizable(False, False)
    game = Game(root)
    root.mainloop()


if __name__ == '__main__':
    main()
