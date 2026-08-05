import math
import random

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse, Triangle
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage


class PetApp(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._resize, pos=self._resize)

        self.tex = {}
        self.ar = {}
        for n in ('idle', 'crawl', 'jump', 'land'):
            self.tex[n] = CoreImage('assets/pose_%s.png' % n).texture
            self.ar[n] = self.tex[n].width / self.tex[n].height
        self.tex_f = {}
        for n in ('idle', 'crawl', 'jump', 'land'):
            self.tex_f[n] = CoreImage('assets/pose_%s_f.png' % n).texture

        self.pet_h = 200.0
        self.pet_w = self.pet_h * self.ar['idle']
        self.floor_y = 60.0

        self.px = 100.0
        self.py = self.floor_y
        self.dir = 1
        self.state = 'idle'
        self.state_t = 1.5
        self.phase = random.random() * math.tau
        self.jump_t = 0.0
        self.jump_h = 130.0
        self.jump_dur = 0.85
        self.jump_cd = 0.0
        self.speed = 4.0

        self.breads = []
        self.bread_timer = random.uniform(5, 10)
        self.hearts = []
        self.pat_timer = random.uniform(35, 60)
        self.following = False
        self.target = None
        self.touched = False

        Clock.schedule_interval(self._update, 1 / 60.0)

    def _resize(self, *a):
        w, h = self.size
        if h <= 0:
            return
        self.floor_y = max(30.0, h * 0.06)
        self.pet_h = max(150.0, min(300.0, h * 0.2))
        self.pet_w = self.pet_h * self.ar['idle']
        if self.py < self.floor_y:
            self.py = self.floor_y

    def spawn_bread(self):
        w, h = self.size
        if w <= 0:
            return
        self.breads.append({'x': random.uniform(20, max(30, w - 70)),
                            'ph': random.random() * math.tau,
                            'bob': 0})

    def spawn_hearts(self, x, y, n):
        for _ in range(n):
            self.hearts.append({
                'x': x + random.uniform(-40, 40),
                'y': y + random.uniform(-10, 10),
                'age': 0,
                'life': random.uniform(0.9, 1.6),
                'size': random.uniform(5, 9),
                'vx': random.uniform(-30, 30),
                'vy': random.uniform(-90, -50),
            })

    def _start_jump(self):
        self.state = 'jump'
        self.jump_t = 0.0
        self.jump_cd = 1.2

    def _start_petted(self):
        self.following = False
        self.state = 'petted'
        self.state_t = 2.0
        self.spawn_hearts(self.px + self.pet_w / 2,
                          self.py + self.pet_h + 30, 8)

    def _update(self, dt):
        w, h = self.size
        if w <= 0 or h <= 0:
            return
        self.phase += dt * 6
        self.jump_cd -= dt

        for ht in self.hearts[:]:
            ht['age'] += dt
            if ht['age'] >= ht['life']:
                self.hearts.remove(ht)
                continue
            ht['x'] += ht['vx'] * dt
            ht['y'] += ht['vy'] * dt
            ht['vy'] -= 80 * dt

        for b in self.breads:
            b['bob'] = math.sin(self.phase + b['ph']) * 2

        self.bread_timer -= dt
        if self.bread_timer <= 0:
            self.bread_timer = random.uniform(8, 16)
            self.spawn_bread()

        self.pat_timer -= dt
        if self.pat_timer <= 0 and not self.following \
                and self.state != 'petted' and not self.touched:
            self.following = True
            self.state = 'follow'
            self.state_t = 15

        if self.state == 'idle':
            self.state_t -= dt
            if self.state_t <= 0:
                self.state = 'crawl'
                self.state_t = random.uniform(3, 7)
        elif self.state == 'crawl':
            self._crawl(dt)
        elif self.state == 'jump':
            self._jump(dt)
        elif self.state == 'land':
            self.state_t -= dt
            if self.state_t <= 0:
                self.state = 'follow' if self.following else 'crawl'
                self.state_t = random.uniform(2, 5)
        elif self.state == 'eat':
            self.state_t -= dt
            if self.state_t <= 0:
                self.state = 'crawl'
        elif self.state == 'follow':
            self._follow(dt)
        elif self.state == 'petted':
            self.py = self.floor_y + math.sin(self.phase * 2) * 4
            self.state_t -= dt
            if self.state_t <= 0:
                self.py = self.floor_y
                self.state = 'idle'
                self.pat_timer = random.uniform(35, 60)

        for b in self.breads[:]:
            bx = b['x'] + 30
            if (self.state not in ('jump', 'follow', 'petted')
                    and abs(bx - (self.px + self.pet_w / 2)) < self.pet_w * 0.7
                    and abs(self.py - self.floor_y) < 10):
                self.breads.remove(b)
                self.state = 'eat'
                self.state_t = 1.2
                self.spawn_hearts(self.px + self.pet_w / 2,
                                  self.py + self.pet_h + 20, 4)
                break

        if self.px < 0:
            self.px = 0
            if self.state == 'crawl' and not self.following:
                self.dir = 1
        if self.px > w - self.pet_w:
            self.px = w - self.pet_w
            if self.state == 'crawl' and not self.following:
                self.dir = -1

        self._draw(w, h)

    def _crawl(self, dt):
        if self.breads:
            b = min(self.breads, key=lambda bb: abs(bb['x'] - self.px))
            target = b['x'] + 30 - self.pet_w / 2
            if abs(target - self.px) > 6:
                self.dir = 1 if target > self.px else -1
        self.px += self.dir * self.speed
        if self.jump_cd <= 0 and random.random() < 0.004:
            self._start_jump()

    def _jump(self, dt):
        self.jump_t += dt / self.jump_dur
        self.px += self.dir * self.speed * 1.3
        if self.jump_t >= 1:
            self.py = self.floor_y
            self.state = 'land'
            self.state_t = 0.15
            return
        t = self.jump_t
        self.py = self.floor_y - self.jump_h * 4 * t * (1 - t)

    def _follow(self, dt):
        self.state_t -= dt
        if self.state_t <= 0:
            self.following = False
            self.state = 'idle'
            self.pat_timer = random.uniform(35, 60)
            return
        tx, ty = self.target if self.target else \
            (self.width / 2, self.floor_y + self.pet_h / 2)
        cx = self.px + self.pet_w / 2
        cy = self.py + self.pet_h / 2
        dx = tx - cx
        dy = ty - cy
        if abs(dx) < 50 and abs(dy) < 90:
            self._start_petted()
            return
        if dx > 8:
            self.dir = 1
        elif dx < -8:
            self.dir = -1
        self.px += self.dir * self.speed * 1.6
        if self.jump_cd <= 0 and ty < self.py + self.pet_h * 0.55:
            self._start_jump()

    def on_touch_down(self, touch):
        self.target = touch.pos
        self.touched = True
        if (self.px <= touch.x <= self.px + self.pet_w
                and self.py <= touch.y <= self.py + self.pet_h):
            self._start_petted()
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        self.target = touch.pos
        if self.state in ('idle', 'crawl', 'land', 'eat'):
            self.following = True
            self.state = 'follow'
            self.state_t = 15
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self.touched = False
        return super().on_touch_up(touch)

    def _draw(self, w, h):
        self.canvas.clear()
        with self.canvas:
            Color(0.87, 0.94, 1.0, 1)
            Rectangle(pos=(0, 0), size=(w, h))
            Color(0.85, 0.68, 0.45, 1)
            Rectangle(pos=(0, 0), size=(w, self.floor_y))
            Color(0.5, 0.75, 0.45, 1)
            Rectangle(pos=(0, 0), size=(w, 8))

            for b in self.breads:
                bx = b['x']
                by = self.floor_y + 10 + b['bob']
                Color(0.9, 0.66, 0.1, 1)
                Ellipse(pos=(bx, by), size=(30, 20))
                Color(0.55, 0.36, 0.05, 1)
                Ellipse(pos=(bx + 11, by + 3), size=(8, 8))

            pose = 'idle'
            if self.state in ('crawl', 'follow'):
                pose = 'crawl'
            elif self.state == 'jump':
                pose = 'jump'
            elif self.state == 'land':
                pose = 'land'
            tex = self.tex_f[pose] if self.dir < 0 else self.tex[pose]
            Color(1, 1, 1, 1)
            Rectangle(texture=tex, pos=(self.px, self.py),
                      size=(self.pet_w, self.pet_h))

            for ht in self.hearts:
                x, y, s = ht['x'], ht['y'], ht['size']
                a = 1 - ht['age'] / ht['life']
                Color(1, 0.4, 0.6, a)
                Ellipse(pos=(x - s, y - s * 0.4), size=(s * 1.4, s * 1.4))
                Ellipse(pos=(x + s * 0.4, y - s * 0.4), size=(s * 1.4, s * 1.4))
                Triangle(points=[x - s * 0.9, y - s * 0.3,
                                 x + s * 0.9, y - s * 0.3,
                                 x, y + s * 1.4])


class MonkeyPetApp(App):
    def build(self):
        return PetApp()


if __name__ == '__main__':
    MonkeyPetApp().run()
