import math
import random
import tkinter as tk

from render import Character
from obstacles import get_obstacles, get_cursor_pos
from bread import Bread, BREAD_W, BREAD_H, spawn_random


class Pet:
    def __init__(self, root, canvas, wa):
        self.root = root
        self.canvas = canvas
        self.wa = wa
        self.char = Character(canvas)
        self.fps = 30
        self.speed = 2.4
        self.jump_h = 120
        self.jump_dur = 0.9
        self.rects = []
        self._refresh = 0
        self.breads = []
        self.eat_cd = 0
        self.hearts = []
        self.following = False
        self.mouse_timer = random.uniform(60, 180)

        self.wx = random.uniform(wa[0], wa[2] - Character.W)
        self.ground_y = wa[3] - Character.H
        self.wy = self.ground_y
        self.dir = 1 if random.random() < 0.5 else -1
        self.state = 'idle'
        self.state_t = random.uniform(1.0, 2.5)
        self.phase = random.random() * math.pi * 2
        self.jump_t = 0
        self.turn_cd = 0
        self.jump_cd = 0
        self.held = False
        self._bind_menu()

    def start(self):
        self._place()
        self._loop()

    def _loop(self):
        self._tick()
        self.root.after(1000 // self.fps, self._loop)

    def _tick(self):
        dt = 1.0 / self.fps
        self.phase += 0.22
        self.turn_cd -= 1
        self.jump_cd -= 1
        self.eat_cd -= 1
        self._refresh += 1
        if self._refresh % 15 == 0:
            self.rects = get_obstacles()

        for b in self.breads:
            b.update(dt)
        self.breads = [b for b in self.breads if b.alive]

        for h in self.hearts[:]:
            h['age'] += dt
            if h['age'] >= h['life']:
                self.hearts.remove(h)
                continue
            h['x'] += h['vx'] * dt
            h['y'] += h['vy'] * dt
            h['vy'] -= 40 * dt

        self.mouse_timer -= dt
        if (self.mouse_timer <= 0 and not self.held
                and not self.following and self.state not in ('eat',)):
            self.following = True
            self.state = 'follow'
            self.state_t = 12

        if self.state == 'idle':
            self.state_t -= dt
            if self.state_t <= 0:
                self.state = 'crawl'
                self.state_t = random.uniform(3.5, 8.0)
        elif self.state == 'crawl':
            self._move_crawl()
        elif self.state == 'jump':
            self._move_jump()
        elif self.state == 'land':
            self.state_t -= dt
            if self.state_t <= 0:
                self.state = 'follow' if self.following else 'crawl'
                self.state_t = random.uniform(2.0, 5.0)
        elif self.state == 'eat':
            self._move_eat()
        elif self.state == 'follow':
            self._move_follow()
        elif self.state == 'petted':
            self._move_petted()

        for b in self.breads:
            if b.hit(self.wx, self.wy, Character.W, Character.H):
                b.alive = False
                self.state = 'idle'
                self.state_t = 0.8
                self.eat_cd = 15

        wa = self.wa
        if self.wx <= wa[0] + 1:
            self.wx = wa[0] + 1
            self._turn()
        if self.wx >= wa[2] - Character.W - 1:
            self.wx = wa[2] - Character.W - 1
            self._turn()

        pose = 'idle'
        if self.state == 'crawl' or self.state == 'follow':
            pose = 'crawl'
        elif self.state == 'jump':
            pose = 'jump'
        elif self.state == 'land':
            pose = 'land'
        self.char.draw(pose, self.phase, self.dir)
        self._draw_breads()
        self._draw_hearts()
        self._place()

    def _draw_breads(self):
        c = self.canvas
        c.delete('bread')
        for b in self.breads:
            if not b.alive:
                continue
            x, y = b.x, b.y + b.bob
            # 简笔面包
            c.create_oval(x, y, x + BREAD_W, y + BREAD_H,
                          fill='#e6a817', outline='#8b5e00', width=2, tags='bread')
            c.create_line(x + 5, y + 6, x + BREAD_W - 5, y + 6,
                          fill='#8b5e00', width=1, tags='bread')
            c.create_line(x + 6, y + 3, x + BREAD_W - 6, y + 3,
                          fill='#d4930a', width=1, tags='bread')

    def _move_crawl(self):
        target = self._nearest_bread()
        if target is not None and self.eat_cd <= 0:
            tx, ty = target
            dx = tx - (self.wx + Character.W / 2)
            if dx > 8:
                self.dir = 1
            elif dx < -8:
                self.dir = -1
            else:
                self.state = 'eat'
                self.state_t = 1.2
                return
        self.wx += self.dir * self.speed
        if self._overlapped() and self.jump_cd <= 0:
            self._start_jump()
            return
        if self._blocked_ahead() and self.turn_cd <= 0:
            if self._jumpable() and self.jump_cd <= 0 and random.random() < 0.5:
                self._start_jump()
            else:
                self._turn()

    def _move_eat(self):
        self.state_t -= 1.0 / self.fps
        if self.state_t <= 0:
            self.state = 'crawl'
            self.state_t = random.uniform(2.0, 5.0)

    def _move_follow(self):
        self.state_t -= 1.0 / self.fps
        if self.state_t <= 0:
            self.following = False
            self.state = 'idle'
            self.state_t = random.uniform(2.0, 4.0)
            self.mouse_timer = random.uniform(60, 180)
            return
        mx, my = get_cursor_pos()
        cx = self.wx + Character.W / 2
        cy = self.wy + Character.H / 2
        dx = mx - cx
        dy = my - cy
        if abs(dx) < 55 and abs(dy) < 90:
            self._start_petted()
            return
        if dx > 8:
            self.dir = 1
        elif dx < -8:
            self.dir = -1
        self.wx += self.dir * self.speed * 1.4
        if self._blocked_ahead() and self.jump_cd <= 0:
            if self._jumpable():
                self._start_jump()
                return
        if my < self.wy + Character.H * 0.55 and self.jump_cd <= 0:
            self._start_jump()

    def _start_petted(self):
        self.following = False
        self.state = 'petted'
        self.state_t = 2.5
        self._spawn_hearts()

    def _move_petted(self):
        self.state_t -= 1.0 / self.fps
        if self.state_t <= 0:
            self.state = 'idle'
            self.state_t = random.uniform(2.0, 4.0)
            self.mouse_timer = random.uniform(60, 180)

    def _spawn_hearts(self):
        cx = self.wx + Character.W / 2
        cy = self.wy + 35
        for _ in range(6):
            self.hearts.append({
                'x': cx + random.uniform(-30, 30),
                'y': cy + random.uniform(-10, 10),
                'age': 0,
                'life': random.uniform(1.0, 1.8),
                'size': random.uniform(4, 8),
                'vx': random.uniform(-10, 10),
                'vy': random.uniform(-28, -14),
            })

    def _draw_hearts(self):
        c = self.canvas
        c.delete('heart')
        for h in self.hearts:
            x = h['x'] - self.wx
            y = h['y'] - self.wy
            s = h['size']
            color = '#ff6b9d'
            c.create_oval(x - s, y - s * 0.6, x, y + s * 0.4,
                          fill=color, outline='', tags='heart')
            c.create_oval(x, y - s * 0.6, x + s, y + s * 0.4,
                          fill=color, outline='', tags='heart')
            c.create_polygon(x - s * 0.95, y - s * 0.1, x + s * 0.95,
                             y - s * 0.1, x, y + s * 1.1,
                             fill=color, outline='', tags='heart')

    def _nearest_bread(self):
        if not self.breads:
            return None
        cx = self.wx + Character.W / 2
        cy = self.wy + Character.H / 2
        best = None
        best_d = float('inf')
        for b in self.breads:
            if not b.alive:
                continue
            bx = b.x + BREAD_W / 2
            by = b.y + BREAD_H / 2
            d = (bx - cx) ** 2 + (by - cy) ** 2
            if d < best_d:
                best_d = d
                best = (bx, by)
        return best

    def spawn_bread(self, x=None, y=None):
        if x is None:
            b = spawn_random(self.wa)
        else:
            b = Bread(x, y)
        self.breads.append(b)

    def _start_jump(self):
        self.state = 'jump'
        self.jump_t = 0
        self.jump_cd = 18

    def _move_jump(self):
        dt = 1.0 / self.fps
        self.jump_t += dt / self.jump_dur
        self.wx += self.dir * self.speed * 1.15
        if self.jump_t >= 1:
            self.wy = self.ground_y
            self.state = 'land'
            self.state_t = 0.18
            return
        t = self.jump_t
        self.wy = self.ground_y - self.jump_h * 4 * t * (1 - t)

    def _turn(self):
        self.dir = -self.dir
        self.turn_cd = 20

    def _blocked_ahead(self):
        W = Character.W
        H = Character.H
        nleft = min(self.wx, self.wx + self.dir * W)
        nright = max(self.wx, self.wx + self.dir * W)
        top = self.wy
        bot = self.wy + H
        margin = 8
        for (l, t, r, b) in self.rects:
            if r <= nleft + margin or l >= nright - margin:
                continue
            if b <= top + 2 or t >= bot - 2:
                continue
            return True
        return False

    def _jumpable(self):
        W = Character.W
        H = Character.H
        nleft = self.wx - W
        nright = self.wx + W
        top = self.wy
        bot = self.wy + H
        margin = 8
        for (l, t, r, b) in self.rects:
            if r <= nleft or l >= nright:
                continue
            if b <= top + 2 or t >= bot - 2:
                continue
            if (b - top) < self.jump_h * 0.9:
                return True
        return False

    def _overlapped(self):
        W = Character.W
        H = Character.H
        for (l, t, r, b) in self.rects:
            if r <= self.wx or l >= self.wx + W:
                continue
            if b <= self.wy or t >= self.wy + H:
                continue
            return True
        return False

    def _place(self):
        self.root.geometry('%dx%d+%d+%d' % (Character.W, Character.H,
                                            int(self.wx), int(self.wy)))

    def _bind_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label='喂面包', command=lambda: self.spawn_bread())
        self.menu.add_command(label='求抚摸', command=self._ask_pet)
        self.menu.add_command(label='休息一下', command=self._to_idle)
        self.menu.add_command(label='跳一下', command=self._force_jump)
        self.menu.add_command(label='转个方向', command=self._turn)
        self.menu.add_separator()
        self.menu.add_command(label='退出', command=self.root.destroy)
        self.canvas.bind('<Button-3>', self._popup)
        self.canvas.bind('<Button-1>', self._grab)
        self.canvas.bind('<B1-Motion>', self._drag)
        self.canvas.bind('<ButtonRelease-1>', self._release)

    def _popup(self, e):
        try:
            self.menu.tk_popup(e.x_root, e.y_root)
        finally:
            self.menu.grab_release()

    def _grab(self, e):
        self.held = True
        self._dx = e.x_root - int(self.wx)
        self._dy = e.y_root - int(self.wy)
        self._was_state = self.state

    def _drag(self, e):
        self.wx = e.x_root - self._dx
        self.wy = e.y_root - self._dy
        self._place()

    def _release(self, e):
        self.held = False
        wa = self.wa
        if self.wx < wa[0]:
            self.wx = wa[0]
        if self.wx > wa[2] - Character.W:
            self.wx = wa[2] - Character.W
        self.ground_y = wa[3] - Character.H
        self.state = self._was_state if self._was_state in ('idle', 'crawl') else 'idle'
        self.state_t = random.uniform(1.0, 3.0)

    def _to_idle(self):
        self.state = 'idle'
        self.state_t = random.uniform(2.0, 4.0)

    def _force_jump(self):
        if self.state in ('idle', 'crawl'):
            self._start_jump()

    def _ask_pet(self):
        if self.state not in ('follow', 'petted'):
            self.following = True
            self.state = 'follow'
            self.state_t = 12
