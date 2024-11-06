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

class MapView:
    def __init__(self, map_file):
        self.map_file = map_file

        

class OptionsPage:
    def __init__(self, root, app_root_folder):
        self.root = root
        self.app_root_folder = app_root_folder
        self.maps = self.load_maps()
        self.current_page = 0
        self.clouds = []
        self.clouds_position = [0, 750, 1000]
        self.cloud_speed = 2
        self.animation_running = True


        self.image_dict = {
            'background': self.load_image('images/background/options/background.png', resize=(1000, 600)),
            'title': self.load_image('images/background/options/title.png', resize=(300, 25)),
            'next': self.load_image('images/background/util/next.png', resize=(30, 50)),
            'prev': self.load_image('images/background/util/prev.png', resize=(30, 50)),
            'back': self.load_image('images/background/util/back.png', resize=(75, 50)),
            'clouds': [self.load_image(f'images/background/util/cloud/{i}.png') for i in range(3)],
        }

        self.canvas = tk.Canvas(self.root, width=1000, height=600)
        self.canvas.pack()

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_dict['background'])
        self.canvas.create_image(300, 75, anchor=tk.CENTER, image=self.image_dict['title'])
        
        self.back_button = self.canvas.create_image(50, 550, anchor=tk.CENTER, image=self.image_dict['back'])
        self.canvas.tag_bind(self.back_button, "<Button-1>", lambda event: self.go_back())
        self.canvas.tag_bind(self.back_button, "<Enter>", lambda event: self.canvas.config(cursor='hand2'))
        self.canvas.tag_bind(self.back_button, "<Leave>", lambda event: self.canvas.config(cursor=''))

        self.draw_clouds()
        self.animate_clouds()

        self.show_map_options()
    
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
        self.stop_animation()
        self.canvas.destroy()
        Home(self.root, self.app_root_folder)

    def start_game(self, map_file):
        self.stop_animation()
        self.canvas.destroy()
        GamePage(self.root, self.app_root_folder, map_file)

class MainGame:
    def __init__(self, frame: tk.Frame, cells: dict, root, app_root_folder: str, warehouse_path: str):
        self.parent_frame = frame
        self.warehouse_path = warehouse_path
        self.warehouse = self.load_warehouse(self.warehouse_path)
        self.cells = cells
        self.root = root
        self.app_root_folder = app_root_folder
        self.solution = None
        self.font = tkFont.Font(family="ArcadeGamer", size=15)
        
        self.cell_size = 50
        grid_width = self.warehouse.ncols * self.cell_size
        grid_height = self.warehouse.nrows * self.cell_size

        self.grid_frame = tk.Frame(self.parent_frame, width=grid_width, height=grid_height)
        self.grid_frame.place(x = 900 - grid_width, y=10, width=grid_width, height=grid_height)


        self.image_dict = {
            'ares': {
                'go_ahead': [self.load_image(f'images/ares/go_ahead/{i}.png', (50, 50)) for i in range(4)],
                'go_back': [self.load_image(f'images/ares/go_back/{i}.png', (50, 50)) for i in range(4)],
                'go_left': [self.load_image(f'images/ares/go_left/{i}.png', (50, 50)) for i in range(4)],
                'go_right': [self.load_image(f'images/ares/go_right/{i}.png', (50, 50)) for i in range(4)],
                'stand': self.load_image('images/ares/stand/0.png', (50, 50)),
            },
            'wall': self.load_image('images/cell/wall.png', (50, 50)),
            'box': self.load_image('images/cell/box.png', (50, 50)),
            'box_on_target': self.load_image('images/cell/right_box.png', (50, 50)),
            'target': self.load_image('images/cell/dock.png', (50, 50)),
            'in_space': self.load_image('images/cell/in_space.png', (50, 50)),
            'out_space': self.load_image('images/cell/out_space.png', (50, 50)),
            'victory_title': self.load_image('images/background/util/victory.png', (740, 100))
        }
        
        self.direction_offset = {
            'Left': (-1, 0),
            'Right': (1, 0),
            'Up': (0, -1),
            'Down': (0, 1)
        }


    def load_warehouse(self, warehouse_path: str):
        try:
            warehouse = Warehouse()
            warehouse.load_warehouse(warehouse_path)
            return warehouse
        except:
            return None

    def get_box_weight(self, x, y):
        try:
            w = self.warehouse.weights[self.warehouse.boxes.index((x, y))]
        except:
            w = 0
        return w

    def make_cell(self, cell_image, row, col, box_weight=None):
        canvas = tk.Canvas(self.grid_frame,
                           width=50,
                           height=50,
                           highlightthickness=0,
                           bd=0)
        canvas.create_image(0, 0, anchor=tk.NW, image=cell_image)
        if box_weight is not None:
            canvas.create_text(25, 25, text=str(box_weight), fill='red', font=(self.font, 15, 'bold'))
        canvas.grid(row=row, column=col)
        return canvas

    def clear_level(self):
        for cell in self.cells.values():
            cell.destroy()
        self.cells.clear()
        self.warehouse = self.load_warehouse(self.warehouse_path)

    def start_level(self):
        self.root.title(f"Ares's Adventure - {self.warehouse_path.split('/')[-1].split('.')[0]}")
        self.fresh_display()

    def clean_cell(self, x, y):
        if (x, y) in self.cells:
            self.cells[(x, y)].destroy()
            del self.cells[(x, y)]

    def fresh_display(self):
        for row in range(self.warehouse.nrows):
            for col in range(self.warehouse.ncols):
                position = (col, row)

                if position in self.warehouse.walls:
                    self.cells[position] = self.make_cell(self.image_dict['wall'], row, col)
                elif position in self.warehouse.targets:
                    self.cells[position] = self.make_cell(self.image_dict['target'], row, col)
                elif position in self.warehouse.boxes:
                    if position in self.warehouse.targets:
                        self.cells[position] = self.make_cell(self.image_dict['box_on_target'], row, col, self.get_box_weight(col, row))
                    else:
                        self.cells[position] = self.make_cell(self.image_dict['box'], row, col, self.get_box_weight(col, row))
                elif position == self.warehouse.worker:
                    self.cells[position] = self.make_cell(self.image_dict['ares']['stand'], row, col)
                else:
                    self.cells[position] = self.make_cell(self.image_dict['in_space'], row, col)


    def move_player(self, direction: str):
        map_direction = {
            'l': 'Left',
            'r': 'Right',
            'u': 'Up',
            'd': 'Down'
        }
        if direction in map_direction.keys():
            direction = map_direction[direction]
        x, y = self.warehouse.worker
        xy_offset = self.direction_offset[direction]
        next_x, next_y = x + xy_offset[0], y + xy_offset[1]

        if (next_x, next_y) in self.warehouse.walls:
            return
        if (next_x, next_y) in self.warehouse.boxes:
            if not self.try_move_box((next_x, next_y), (next_x + xy_offset[0], next_y + xy_offset[1])):
                return

        self.clean_cell(x, y)
        self.clean_cell(next_x, next_y)

        self.cells[(next_x, next_y)] = self.make_cell(self.image_dict['ares']['stand'], next_y, next_x)
        self.warehouse.worker = (next_x, next_y)

        if (x, y) in self.warehouse.targets:
            self.cells[(x, y)] = self.make_cell(self.image_dict['target'], y, x)
        else:
            self.cells[(x, y)] = self.make_cell(self.image_dict['in_space'], y, x)

        if all(z in self.warehouse.targets for z in self.warehouse.boxes):
            self.show_victory_screen()
        


    def show_victory_screen(self):
        self.canvas = tk.Canvas(self.parent_frame, width=1000, height=600, highlightthickness=0, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.create_image(130, 200, anchor=tk.NW, image=self.image_dict['victory_title'])
        back_button = tk.Button(self.parent_frame, text="Back", command=self.destroy_canvas, cursor='hand2', width=20, pady=5, font=(self.font, 20, 'bold'))
        self.canvas.create_window(490, 400, window=back_button)

    def destroy_canvas(self):
        self.canvas.destroy()
        self.grid_frame.destroy()
        self.parent_frame.destroy()
        Home(self.root, self.app_root_folder)


    def try_move_box(self, location: tuple, next_location: tuple):
        x, y = location
        next_x, next_y = next_location

        if (next_x, next_y) not in self.warehouse.walls and (next_x, next_y) not in self.warehouse.boxes:
            if (next_x, next_y) in self.cells:
                self.clean_cell(next_x, next_y)

            if (next_x, next_y) in self.warehouse.targets:
                self.cells[(next_x, next_y)] = self.make_cell(self.image_dict['box_on_target'], next_y, next_x, self.get_box_weight(x, y))
            else:
                self.cells[(next_x, next_y)] = self.make_cell(self.image_dict['box'], next_y, next_x, self.get_box_weight(x, y))
            
            self.clean_cell(x, y)
            if (x, y) in self.warehouse.targets:
                self.cells[(x, y)] = self.make_cell(self.image_dict['target'], y, x)
            else:
                self.cells[(x, y)] = self.make_cell(self.image_dict['in_space'], y, x)

            bi = self.warehouse.boxes.index((x, y))
            self.warehouse.boxes[bi] = (next_x, next_y)

            return True
        return False

    def key_handler(self, event):
        if event.keysym in ('Left', 'Right', 'Up', 'Down'):
            self.move_player(event.keysym)
        if event.keysym in ('r', 'R'):
            self.clear_level()
            self.start_level()
    
    def solve_puzzle(self, method: str):
        if self.warehouse is None:
            print("Load a warehouse!!")
            return
        print("Starting to analyze to find solution...")
        t0 = time.time()
        if method == "BFS":
            solution, total_cost = solve_weight_sokoban_bfs(self.warehouse)
        elif method == "DFS":
            solution, total_cost = solve_weight_sokoban_dfs(self.warehouse)
        elif method == "UCS":
            solution, total_cost = solve_weight_sokoban_ucs(self.warehouse)
        else:
            solution, total_cost = solve_weight_sokoban_as(self.warehouse)
        t1 = time.time()

        print(f"Analysis took {t1 - t0:.6f} seconds")
        if solution == "Impossible":
            self.solution = None
            print("No solution found!")
        else:
            self.solution = solution
            print(f"Solution found with a cost of {total_cost}\n", solution, '\n')

    def play_solution(self):
        if self.solution and len(self.solution) > 0:
            self.move_player(self.solution.pop(0))
            self.parent_frame.after(300, self.play_solution)



    def load_image(self, filepath:str, resize:tuple = None):
        path = os.path.join(self.app_root_folder, filepath)
        image = Image.open(path)
        if resize:
            image = image.resize(resize, Image.LANCZOS)
        return ImageTk.PhotoImage(image)

class GamePage:
    def __init__(self, root, app_root_folder, map_file):
        self.root = root
        self.app_root_folder = app_root_folder
        self.image = self.load_image(map_file, resize=(1000, 600))
        self.font = tkFont.Font(family="ArcadeGamer", size=15)
        

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.background_label = tk.Label(self.frame, image=self.image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.dominant_color = self.get_dominant_color(map_file)

        self.small_frame = tk.Frame(self.frame, width=250, height=250, bg=self.dominant_color)
        self.small_frame.place(x=50, y=0, anchor="nw", width=250, height=250)
        
        self.draw_game_controls()
        self.draw_map()

    def get_dominant_color(self, image_path):
        image = Image.open(image_path)

        image = image.convert("RGB")
        
        width, height = image.size

        top_half = image.crop((0, 0, width, height // 2))

        pixels = top_half.getdata()
        
        r, g, b = 0, 0, 0
        for pixel in pixels:
            r += pixel[0]
            g += pixel[1]
            b += pixel[2]
        
        total_pixels = len(pixels)
        if total_pixels > 0:
            r //= total_pixels
            g //= total_pixels
            b //= total_pixels

        return f'#{r:02x}{g:02x}{b:02x}'

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        return (r, g, b)

    def get_text_color(self, dominant_color):
        r, g, b = self.hex_to_rgb(dominant_color)
        brightness = 0.299 * r + 0.587 * g + 0.114 * b
        return 'black' if brightness > 128 else 'white'

    def load_image(self, filepath:str, resize:tuple = None):
        path = os.path.join(self.app_root_folder, filepath)
        image = Image.open(path)

        if resize:
            image = image.resize(resize, Image.LANCZOS)

        return ImageTk.PhotoImage(image)

    def draw_game_controls(self):
        text_color = self.get_text_color(self.dominant_color)
        control_label = tk.Label(self.small_frame, text="GAME CONTROLS", bg=self.dominant_color, font=(self.font, 20, 'bold'), fg=text_color)
        control_label.pack(pady=5)
        
        self.algorithm_label = tk.Label(self.small_frame, text="ALGORITHMS: UNKNOWN", bg=self.dominant_color, font=(self.font, 14, 'bold'), fg=text_color)
        self.algorithm_label.pack(pady=5)


        button_frame = tk.Frame(self.small_frame, bg=self.dominant_color)
        button_frame.pack(pady=5)

        restart_button = tk.Button(button_frame, text="Restart", command=self.restart_game, font=(self.font, 10), cursor="hand2")
        restart_button.pack(side=tk.LEFT, padx=5)

        quit_button = tk.Button(button_frame, text="Quit", command=self.quit_game, font=(self.font, 10), cursor="hand2")
        quit_button.pack(side=tk.LEFT, padx=5)

        solve_button = tk.Button(self.small_frame, text="Solve", font=(self.font, 10), cursor="hand2")
        solve_button.pack(pady=5)

        self.solve_menu = tk.Menu(solve_button, tearoff=0)
        methods_menu = tk.Menu(self.solve_menu, tearoff=0)
        methods_menu.add_command(label="BFS", command=lambda: self.set_method("BFS"))
        methods_menu.add_command(label="DFS", command=lambda: self.set_method("DFS"))
        methods_menu.add_command(label="UCS", command=lambda: self.set_method("UCS"))
        methods_menu.add_command(label="A*", command=lambda: self.set_method("A*"))

        self.solve_menu.add_cascade(label="Methods", menu=methods_menu)
        self.solve_menu.add_command(label="Plan Action Sequence", command=self.plan_action_sequence, state='disabled')
        self.solve_menu.add_command(label="Play Action Sequence", command=self.play_action_sequence, state='disabled')

        solve_button.config(command=lambda: self.solve_menu.post(solve_button.winfo_rootx(), solve_button.winfo_rooty() + solve_button.winfo_height()))

        for button in (restart_button, solve_button, quit_button):
            button.config(width=7)

    def draw_map(self):
        warehouse_path = r"./warehouses/input_10_10_2_8.txt"
        self.main_game = MainGame(self.frame, {}, self.root, self.app_root_folder, warehouse_path)
        self.root.bind_all("<Key>", self.main_game.key_handler)
        self.main_game.start_level()


    def set_method(self, method):
        self.method = method
        self.algorithm_label.config(text=f"ALGORITHM: {self.method}")
        self.solve_menu.entryconfig("Plan Action Sequence", state="normal")
        self.solve_menu.entryconfig("Play Action Sequence", state="normal")

    def plan_action_sequence(self):
        if self.method:
            print("Planning action sequence with", self.method)
            self.main_game.solve_puzzle(self.method)

    def play_action_sequence(self):
        if self.method:
            print("Playing action sequence with", self.method)
            self.main_game.play_solution()

    def restart_game(self):
        print("Game Restarted")
        self.main_game.clear_level()
        self.main_game.start_level()

    def solve(self):
        print(f"Solving with {self.method}")


    def quit_game(self):
        self.frame.destroy()
        Home(self.root, self.app_root_folder)

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

if __name__ == '__main__':
    root  = tk.Tk()
    app_root_folder = os.getcwd()
    root.geometry('1000x600')
    root.title("Ares's adventure")
    root.iconphoto(
        False,
        tk.PhotoImage(file=os.path.join(app_root_folder, 'images/ares/stand/0.png'))
    )
    root.wm_attributes('-transparentcolor', 'gray')
    home_page = Home(root, app_root_folder)

    root.mainloop()