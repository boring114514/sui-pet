import ctypes
import tkinter as tk

from render import Character
from obstacles import get_work_area
from pet import Pet

TRANSPARENT = '#ff00ff'


def main():
    ctypes.windll.user32.SetProcessDPIAware()
    wa = get_work_area()
    root = tk.Tk()
    root.title('Desktop Pet')
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    root.attributes('-transparentcolor', TRANSPARENT)
    canvas = tk.Canvas(root, width=Character.W, height=Character.H,
                       bg=TRANSPARENT, highlightthickness=0)
    canvas.pack()
    Pet(root, canvas, wa).start()
    root.mainloop()


if __name__ == '__main__':
    main()
