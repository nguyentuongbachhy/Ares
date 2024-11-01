import tkinter as tk, os, time
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
from Sokoban import Warehouse
from SokobanSolver import solve_weight_sokoban_bfs, solve_weight_sokoban_dfs, solve_weight_sokoban_ucs, solve_weight_sokoban_as


__author__ = "Quatermelon"
__version__ = "1.0"

class Home:
    def __init__(self, root, app_root_folder):
        self.root = root
        self.app_root_folder = app_root_folder
        self.canvas = tk.Canvas(self.root, width=1000, height=600)
        self.canvas.pack()

        self.image_dict = {
            'background': self.load_image('background', resize=(1000, 600)),
            'moon': self.load_image('moon', resize=(100, 100)),
            'title': self.load_image('title', resize=(600, 180)),
            'clouds': [self.load_image(f'cloud/{i}') for i in range(3)]
        }

        self.draw_elements()

        self.clouds = []

        self.clouds_position = [0, 750, 1000]
        self.cloud_speed = 2

        self.draw_clouds()
        self.animate_clouds()

    def load_image(self, name, resize:tuple = None):
        path = os.path.join(self.app_root_folder, 'images', 'background', 'home', f'{name}.png')
        image = Image.open(path)

        if resize:
            image = image.resize(resize, Image.LANCZOS)

        return ImageTk.PhotoImage(image)


    def draw_elements(self):
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_dict['background'])
        self.canvas.create_image(400, 80, anchor=tk.CENTER, image=self.image_dict['moon'])
        self.canvas.create_image(500, 250, anchor=tk.CENTER, image=self.image_dict['title'])


    def draw_clouds(self):
        for i in range(3):
            cloud = self.canvas.create_image(self.clouds_position[i], 100, anchor=tk.CENTER, image = self.image_dict['clouds'][i])
            self.clouds.append(cloud)

    def animate_clouds(self):
        for i in range(3):
            self.canvas.move(self.clouds[i], self.cloud_speed, 0)
            pos = self.canvas.coords(self.clouds[i])[0]

            if pos > 1920:
                self.canvas.move(self.clouds[i], -1920 - 100, 0)

        self.root.after(50, self.animate_clouds)


direction_offset = {
    'Left': (-1, 0),
    'Right': (1, 0),
    'Up': (0, -1),
    'Down': (0, 1)
}

# image_dict = {
#     'ares': {
#         'go_ahead': [tk.PhotoImage(file=os.path.join(app_root_folder, 'images', 'ares', 'go_ahead', f"{i}.png")) for i in range(4)],
#         'go_back': [tk.PhotoImage(file=os.path.join(app_root_folder, 'images', 'ares', 'go_back', f"{i}.png")) for i in range(4)],
#         'go_left': [tk.PhotoImage(file=os.path.join(app_root_folder, 'images', 'ares', 'go_left', f"{i}.png")) for i in range(4)],
#         'go_right': [tk.PhotoImage(file=os.path.join(app_root_folder, 'images', 'ares', 'go_right', f"{i}.png")) for i in range(4)],
#         'stand': tk.PhotoImage(file=os.path.join(app_root_folder, 'images', 'ares', 'stand', "0.png"))
#     },
#     'background': {
#         'home': {
#             'background': tk.PhotoImage(file=os.path.join(app_root_folder, 'images', 'background', 'home', 'background.png')),
#             'moon': tk.PhotoImage(file=os.path.join(app_root_folder, 'images', 'background', 'home', 'moon.png')),
#             'title': tk.PhotoImage(file=os.path.join(app_root_folder, 'images', 'background', 'home', 'title.png')),
#             'cloud': [tk.PhotoImage(file=os.path.join(app_root_folder, 'images', 'background', 'home', 'cloud', f'{i}.png')) for i in range(3)],
#         }
#     }
# }


if __name__ == '__main__':
    root  = tk.Tk()
    root.geometry('1000x600')
    app_root_folder = os.getcwd()

    home_page = Home(root, app_root_folder)

    root.mainloop()
