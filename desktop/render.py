import math
import os
import sys
from PIL import Image, ImageTk

if getattr(sys, 'frozen', False):
    ASSETS = sys._MEIPASS
else:
    ASSETS = os.path.dirname(os.path.abspath(__file__))


class Character:
    W = 180
    H = 200

    def __init__(self, canvas):
        self.canvas = canvas
        self._img_cache = {}
        self._tk_img = {}
        self._load()

    def _load(self):
        for name in ('idle', 'crawl', 'jump', 'land'):
            path = os.path.join(ASSETS, f'pose_{name}.png')
            img = Image.open(path).convert('RGBA')
            self._img_cache[name] = img
            self._tk_img[name] = ImageTk.PhotoImage(img)
        # 为 crawl 准备左右摇摆变体
        base = self._img_cache['crawl']
        self._img_cache['crawl_l'] = base.rotate(6, expand=True,
                                                  fillcolor=(0, 0, 0, 0))
        self._img_cache['crawl_r'] = base.rotate(-6, expand=True,
                                                  fillcolor=(0, 0, 0, 0))
        self._tk_img['crawl_l'] = ImageTk.PhotoImage(self._img_cache['crawl_l'])
        self._tk_img['crawl_r'] = ImageTk.PhotoImage(self._img_cache['crawl_r'])

    def clear(self):
        self.canvas.delete('pet')

    def draw(self, pose, phase, facing):
        c = self.canvas
        self.clear()

        if pose == 'idle':
            key = 'idle'
            bob = math.sin(phase * 0.8) * 2
            rot = 0
        elif pose == 'crawl':
            # 交替左右摇摆模拟四足爬行
            t = (math.sin(phase) + 1) / 2  # 0..1
            key = 'crawl_l' if t > 0.5 else 'crawl_r'
            bob = math.sin(phase * 1.5) * 3
            rot = 0
        elif pose == 'jump':
            key = 'jump'
            bob = 0
            rot = 0
        else:
            key = 'land'
            bob = 0
            rot = 0

        tk_img = self._tk_img[key]
        iw = tk_img.width()
        ih = tk_img.height()
        x = (Character.W - iw) // 2
        y = int((Character.H - ih) - 10 + bob)

        # 面朝方向：镜像
        if facing < 0:
            pil_img = self._img_cache[key].transpose(Image.FLIP_LEFT_RIGHT)
            tk_img = ImageTk.PhotoImage(pil_img)
            self._tk_img['_flip'] = tk_img  # prevent GC

        c.create_image(x + iw // 2, y + ih // 2, image=tk_img, anchor='center',
                       tags='pet')
