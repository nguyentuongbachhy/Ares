import tkinter as tk, os, time
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk, ImageDraw
from tkinter import font as tkFont
from Sokoban import Warehouse
from SokobanSolver import solve_weight_sokoban_bfs, solve_weight_sokoban_dfs, solve_weight_sokoban_ucs, solve_weight_sokoban_as


__author__ = "Quatermelon"
__version__ = "1.0"

class AboutPage:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(self.root, bg="white")
        self.frame.place(relwidth=1, relheight=1)
        
        label = tk.Label(self.frame, text="About the Sokoban Game", font=("Arial", 24), bg="white")
        label.pack(pady=20)
        
        text = "This is a simple Sokoban game where you move boxes to storage locations. Enjoy playing!"
        text_label = tk.Label(self.frame, text=text, font=("Arial", 14), bg="white", wraplength=800)
        text_label.pack(pady=20)
        
        back_button = tk.Button(self.frame, text="Back", command=self.back_to_home)
        back_button.pack(pady=20)
    
    def back_to_home(self):
        self.frame.destroy()
        Home(self.root, app_root_folder)

class OptionsPage:
    def __init__(self, root, app_root_folder):
        self.root = root
        self.app_root_folder = app_root_folder
        self.maps = self.load_maps()
        self.current_page = 0

        self.image_dict = {
            'background': self.load_image('images/background/options/background.png', resize=(1000, 600)),
            'title': self.load_image('images/background/options/title.png', resize=(300, 25)),
            'next': self.load_image('images/background/util/next.png', resize=(30, 50)),
            'prev': self.load_image('images/background/util/prev.png', resize=(30, 50)),
            'back': self.load_image('images/background/util/back.png', resize=(75, 50))
        }

        self.canvas = tk.Canvas(self.root, width=1000, height=600)
        self.canvas.pack()

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_dict['background'])
        self.canvas.create_image(300, 75, anchor=tk.CENTER, image=self.image_dict['title'])
        
        self.back_button = self.canvas.create_image(50, 550, anchor=tk.CENTER, image=self.image_dict['back'])
        self.canvas.tag_bind(self.back_button, "<Button-1>", lambda event: self.go_back())
        self.canvas.tag_bind(self.back_button, "<Enter>", lambda event: self.canvas.config(cursor='hand2'))
        self.canvas.tag_bind(self.back_button, "<Leave>", lambda event: self.canvas.config(cursor=''))

        self.show_map_options()
    
    def load_image(self, filepath:str, resize:tuple = None, rounded_corners = False, radius = 20):
        path = os.path.join(self.app_root_folder, filepath)
        image = Image.open(path).convert('RGBA')

        if resize:
            image = image.resize(resize, Image.LANCZOS)

        if rounded_corners:
            image = self.round_corners(image, radius)

        return ImageTk.PhotoImage(image)
    
    def load_maps(self):
        map_folder = os.path.join(self.app_root_folder, 'images/background/map')
        return [os.path.join(map_folder, file) for file in os.listdir(map_folder) if file.endswith('.png')]

    def show_map_options(self):
        self.canvas.delete('map')

        start = self.current_page * 2
        end = start + 2
        displayed_maps = self.maps[start: end]

        for index, map_file in enumerate(displayed_maps):
            x_position = 400 * index + 75
            map_image = self.load_image(map_file, resize=(420, 252), rounded_corners=True, radius=20)
            border_width = 5
            border_color = "white"
            self.canvas.create_rectangle(
                x_position - border_width, 175 - border_width,
                x_position + 420 + border_width, 175 + 252 + border_width,
                fill=border_color, outline=""
            )
            
            map_image_id = self.canvas.create_image(x_position, 175, anchor=tk.NW, image=map_image)
            self.canvas.image = map_image

            self.canvas.tag_bind(map_image_id, "<Button-1>", lambda e, m=map_file: self.start_game(m))
            self.canvas.tag_bind(map_image_id, "<Enter>", lambda event: self.canvas.config(cursor='hand2'))
            self.canvas.tag_bind(map_image_id, "<Leave>", lambda event: self.canvas.config(cursor=''))

        if len(self.maps) > 2:
            if start > 0:  # Show "prev" button if not on the first page
                self.prev_button = self.canvas.create_image(50, 500, anchor=tk.CENTER, image=self.image_dict['prev'])
                self.canvas.tag_bind(self.prev_button, "<Button-1>", lambda event: self.show_prev())
                self.canvas.tag_bind(self.prev_button, "<Enter>", lambda event: self.canvas.config(cursor='hand2'))
                self.canvas.tag_bind(self.prev_button, "<Leave>", lambda event: self.canvas.config(cursor=''))
            if end < len(self.maps):  # Show "next" button if not on the last page
                self.next_button = self.canvas.create_image(950, 500, anchor=tk.CENTER, image=self.image_dict['next'])
                self.canvas.tag_bind(self.next_button, "<Button-1>", lambda event: self.show_next())
                self.canvas.tag_bind(self.next_button, "<Enter>", lambda event: self.canvas.config(cursor='hand2'))
                self.canvas.tag_bind(self.next_button, "<Leave>", lambda event: self.canvas.config(cursor=''))

    def round_corners(self, image, radius):
    # Convert image to RGBA (to support transparency)
        image = image.convert("RGBA")
        
        # Create a mask with rounded corners
        rounded_mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(rounded_mask)
        draw.rounded_rectangle(
            (0, 0, image.size[0], image.size[1]),
            radius=radius,
            fill=255
        )
        
        # Apply the rounded mask to the image
        rounded_image = Image.new("RGBA", image.size)
        rounded_image.paste(image, (0, 0), rounded_mask)
        return rounded_image

    def show_next(self):
        self.current_page = min(self.current_page + 1, len(self.maps) // 2)
        self.show_map_options()

    def show_prev(self):
        self.current_page = max(0, self.current_page - 1)
        self.show_map_options()

    def go_back(self):
        self.canvas.destroy()
        Home(self.root, self.app_root_folder)

    def start_game(self, map_file):
        self.canvas.destroy()
        GamePage(self.root, self.app_root_folder, map_file)


class MainGame:
    def __init__(self, frame: tk.Frame, cells: dict, root, app_root_folder: str, warehouse: Warehouse):
        self.frame = frame
        self.warehouse = warehouse
        self.cells = cells
        self.root = root
        self.app_root_folder = app_root_folder
        self.solution = None
        font_path = os.path.join(self.app_root_folder, 'font/ArcadeGamer.TTF')
        self.font = tkFont.Font(family="ArcadeGamer", size=15)
        self.image_dict = {
            'ares': {
                'go_ahead': [self.load_image(f'images/ares/go_ahead/{i}.png', (40, 40)) for i in range(4)],
                'go_back': [self.load_image(f'images/ares/go_back/{i}.png', (40, 40)) for i in range(4)],
                'go_left': [self.load_image(f'images/ares/go_left/{i}.png', (40, 40)) for i in range(4)],
                'go_right': [self.load_image(f'images/ares/go_right/{i}.png', (40, 40)) for i in range(4)],
                'stand': self.load_image('images/ares/stand/0.png'),
            },
            'wall': self.load_image('images/cell/wall.png', (40, 40)),
            'box': self.load_image('images/cell/box.png', (40, 40)),
            'box_on_target': self.load_image('images/cell/right_box.png', (40, 40)),
            'target': self.load_image('images/cell/dock.png', (40, 40)),
            'in_space': self.load_image('images/cell/in_space.png', (40, 40)),
            'out_space': self.load_image('images/cell/out_space.png', (40, 40))
        }

    def get_box_weight(self, x, y):
        try:
            w = self.warehouse.weights[self.warehouse.boxes.index((x, y))]
        except:
            w = 0
        return w
    
    def make_cell(self, cell_image, box_weight=None):
        canvas = tk.Canvas(self.frame,
                           width=30,
                           height=30)
        canvas.create_image(0, 0, anchor=tk.NW, image=cell_image)
        if box_weight != None:
            canvas.create_text(15, 15, text=str(box_weight), fill='black', font=self.font)

        return canvas

    def clear_level(self):
        if self.frame:
            self.frame.destroy()
        self.frame = tk.Frame(self.root)
        self.warehouse = Warehouse()
        self.cells = dict()
        

    def start_level(self):
        self.root.title(f"Ares's Adventure v{__version__}")
        self.root.geometry('1000x600')
        self.fresh_display()

    def clean_cell(self, x, y):
        if (x, y) in self.cells:
            self.cells[(x, y)].destroy()
            del self.cells[(x, y)]

    def fresh_display(self):
        for x, y in self.warehouse.walls:
            self.cells[(x, y)] = self.make_cell(self.image_dict['wall'])
            self.cells[(x, y)].grid(row=y,column=x)
        
        for x, y in self.warehouse.targets:
            self.cells[(x, y)] = self.make_cell(self.image_dict['target'])
            self.cells[(x, y)].grid(row=y,column=x)

        for x, y in self.warehouse.boxes:
            if (x, y) in self.warehouse.targets:
                self.clean_cell(x, y)
                self.cells[(x, y)] = self.make_cell(self.image_dict['box_on_target'], self.get_box_weight(x, y))
                self.cells[(x, y)].grid(row=y,column=x)
            else:
                self.cells[(x, y)] = self.make_cell(self.image_dict['box'], self.get_box_weight(x, y))
                self.cells[(x, y)].grid(row=y,column=x)

        x, y = self.warehouse.worker
        if (x, y) in self.warehouse.targets:
            self.cells[(x, y)].destroy()
        self.cells[(x, y)] = self.make_cell(self.image_dict['ares']['stand'])
        self.cells[(x, y)].grid(row=y,column=x)

        self.frame.pack(fill=tk.BOTH, expand=True)




    def load_image(self, filepath:str, resize:tuple = None):
        path = os.path.join(self.app_root_folder, filepath)
        image = Image.open(path)

        if resize != None:
            image = image.resize(resize, Image.LANCZOS)

        return ImageTk.PhotoImage(image)

class GamePage:
    def __init__(self, root, app_root_folder, map_file):
        self.root = root
        self.app_root_folder = app_root_folder
        self.image = self.load_image(map_file, resize=(1000, 600))

        self.frame = tk.Frame(self.root, width=1000, height=600)
        self.frame.pack()

        self.background_label = tk.Label(self.frame, image=self.image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.method = None

        self.draw_game_controls()
        self.draw_map()

    def load_image(self, filepath:str, resize:tuple = None):
        path = os.path.join(self.app_root_folder, filepath)
        image = Image.open(path)

        if resize:
            image = image.resize(resize, Image.LANCZOS)

        return ImageTk.PhotoImage(image)


    def draw_game_controls(self):
        game_control = tk.Menu(self.root)
        self.root.config(menu=game_control)

        # Menu Options
        option_control = tk.Menu(game_control, tearoff=0)
        game_control.add_cascade(label='Options', menu=option_control)
        option_control.add_command(label='Restart', command=self.restart_game)
        option_control.add_separator()
        option_control.add_command(label='Quit', command=self.quit_game)

        # Menu Solve
        solve_control = tk.Menu(game_control, tearoff=0)
        game_control.add_cascade(label='Solve', menu=solve_control)

        # Submenu Methods
        methods_menu = tk.Menu(solve_control, tearoff=0)
        methods_menu.add_command(label="BFS", command=lambda: self.set_method("BFS"))
        methods_menu.add_command(label="DFS", command=lambda: self.set_method("DFS"))
        methods_menu.add_command(label="UCS", command=lambda: self.set_method("UCS"))
        methods_menu.add_command(label="A*", command=lambda: self.set_method("A*"))

        solve_control.add_cascade(label="Methods", menu=methods_menu)

        solve_control.add_command(label="Plan Action Sequence", command=self.plan_action_sequence, state='disabled')
        solve_control.add_command(label="Play Action Sequence", command=self.play_action_sequence, state='disabled')
        
        self.solve_control = solve_control
        self.plan_action_index = self.solve_control.index("Plan Action Sequence")
        self.play_action_index = self.solve_control.index("Play Action Sequence")


    def set_method(self, method):
        self.method = method
        self.solve_control.entryconfig(self.plan_action_index, state="normal")
        self.solve_control.entryconfig(self.play_action_index, state="normal")

    def plan_action_sequence(self):
        if self.method:
            print("Planning action sequence with", self.method)

    def play_action_sequence(self):
        if self.method:
            print("Playing action sequence with", self.method)

    def quit_game(self):
        self.method = None
        self.canvas.destroy()

        print("Quit game")


    def draw_map(self):
        warehouse = Warehouse()
        warehouse.load_warehouse(r"./warehouses/input_10_10_2_4.txt")

        self.main_game = MainGame(self.frame, {}, self.root, self.app_root_folder, warehouse)
        
        self.main_game.start_level()

    def restart_game(self):
        # Code to restart the game
        pass

    def start_game(self):
        self.method = None

        self.root.nametowidget(self.plan_action).config(state="disabled")
        self.root.nametowidget(self.play_action).config(state="disabled")
        # Code to start the game
        pass

    def solve(self, algorithm):
        # Code to solve with the chosen algorithm
        print(f"Solving with {algorithm}")

class Home:
    def __init__(self, root, app_root_folder):
        self.root = root
        self.app_root_folder = app_root_folder

        self.clouds = []
        
        self.clouds_position = [0, 750, 1000]
        self.cloud_speed = 2
        self.animation_running = True


        self.canvas = tk.Canvas(self.root, width=1000, height=600)
        self.canvas.pack()

        self.image_dict = {
            'background': self.load_image('images/background/home/background.png', resize=(1000, 600)),
            'moon': self.load_image('images/background/home/moon.png', resize=(100, 100)),
            'title': self.load_image('images/background/home/title.png', resize=(500, 150)),
            'clouds': [self.load_image(f'images/background/util/cloud/{i}.png') for i in range(3)],
            'play': self.load_image('images/background/home/play.png', resize=(200, 70)),
            'about': self.load_image('images/background/home/about.png',resize=(300, 70))
        }

        self.draw_elements()

        play_button = tk.Button(self.root, image=self.image_dict['play'], command=self.go_to_options, cursor='hand2')
        about_button = tk.Button(self.root, image=self.image_dict['about'], command=self.go_to_about, cursor='hand2')

        play_button.place(x=500, y=360, anchor=tk.CENTER)
        about_button.place(x=500, y=460, anchor=tk.CENTER)
        self.add_press_effect(play_button)
        self.add_press_effect(about_button)

        self.draw_clouds()
        self.animate_clouds()

    def load_image(self, filepath:str, resize:tuple = None):
        path = os.path.join(self.app_root_folder, filepath)
        image = Image.open(path)

        if resize:
            image = image.resize(resize, Image.LANCZOS)

        return ImageTk.PhotoImage(image)

    def go_to_options(self):
        self.stop_animation()
        self.canvas.destroy()
        OptionsPage(self.root, self.app_root_folder)


    def go_to_about(self):
        self.stop_animation()
        self.canvas.destroy()
        AboutPage(self.root)

    def add_press_effect(self, button):
        def on_press(event):
            button.config(relief="sunken", padx=3, pady=3)

        def on_release(event):
            button.config(relief="raised", padx=5, pady=5)

        button.bind("<ButtonPress-1>", on_press)
        button.bind("<ButtonRelease-1>", on_release)

    def draw_elements(self):
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_dict['background'])
        self.canvas.create_image(400, 80, anchor=tk.CENTER, image=self.image_dict['moon'])
        self.canvas.create_image(500, 220, anchor=tk.CENTER, image=self.image_dict['title'])


    def draw_clouds(self):
        for i in range(3):
            cloud = self.canvas.create_image(self.clouds_position[i], 100, anchor=tk.CENTER, image = self.image_dict['clouds'][i])
            self.clouds.append(cloud)

    def animate_clouds(self):
        if not self.animation_running or not self.canvas:
            return
        for i in range(3):
            self.canvas.move(self.clouds[i], self.cloud_speed, 0)
            pos = self.canvas.coords(self.clouds[i])[0]

            if pos > 1920:
                self.canvas.move(self.clouds[i], -1920 - 100, 0)

        self.root.after(50, self.animate_clouds)

    def stop_animation(self):
        self.animation_running = False

direction_offset = {
    'Left': (-1, 0),
    'Right': (1, 0),
    'Up': (0, -1),
    'Down': (0, 1)
}

if __name__ == '__main__':
    root  = tk.Tk()
    app_root_folder = os.getcwd()
    root.geometry('1000x600')
    root.title("Ares's adventure")
    root.iconphoto(
        False,
        tk.PhotoImage(file=os.path.join(app_root_folder, 'images/ares/stand/0.png'))
    )

    home_page = Home(root, app_root_folder)

    root.mainloop()
