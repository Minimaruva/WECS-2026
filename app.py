"""
Anti-Doomscroll - Application Entry Point
"""

import tkinter as tk

from ui.main_menu import MainMenu


if __name__ == "__main__":
    root = tk.Tk()
    menu = MainMenu(root)
    root.mainloop()
