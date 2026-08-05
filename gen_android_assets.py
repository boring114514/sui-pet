from PIL import Image, ImageFilter
import numpy as np
import os

src = r'C:\Users\boyun\Downloads\抠出纯净人像.png'
out_dir = r'C:\Users\boyun\Documents\Default Project\AndroidPet\assets'
os.makedirs(out_dir, exist_ok=True)

img = Image.open(src).convert('RGBA')
bbox = img.getbbox()
if bbox:
    img = img.crop(bbox)

# 白色背景 → 透明
arr = np.array(img)
r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]
white = (r > 230) & (g > 230) & (b > 230) & (a > 200)
arr[:,:,3] = np.where(white, 0, arr[:,:,3])
alpha = Image.fromarray(arr[:,:,3], 'L').filter(ImageFilter.GaussianBlur(radius=2))
arr[:,:,3] = np.array(alpha)
img = Image.fromarray(arr, 'RGBA')
bbox = img.getbbox()
if bbox:
    img = img.crop(bbox)

target_h = 240
scale = target_h / img.height
target_w = max(int(img.width * scale), 1)
img = img.resize((target_w, target_h), Image.LANCZOS)
print('base', img.size)

poses = {'idle': 0, 'crawl': 10, 'jump': -15, 'land': 5}
for name, ang in poses.items():
    if ang == 0:
        base = img
    else:
        base = img.rotate(ang, expand=True, resample=Image.BICUBIC,
                          fillcolor=(0, 0, 0, 0))
    base.save(os.path.join(out_dir, f'pose_{name}.png'))
    base.transpose(Image.FLIP_LEFT_RIGHT).save(
        os.path.join(out_dir, f'pose_{name}_f.png'))
    print(name, base.size)

# 图标 512x512
icon = Image.new('RGBA', (512, 512), (255, 255, 255, 0))
bg = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
rad = 64
big = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
big.paste(img, (256 - img.width // 2, 256 - img.height // 2), img)
icon.alpha_composite(big)
icon.save(os.path.join(out_dir, 'icon.png'))
print('icon saved')
