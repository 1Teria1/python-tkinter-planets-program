import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from math import sin, cos, radians
import random as rnd

G = 6
root = tk.Tk()
root.attributes("-fullscreen", True)
root['bg'] = "#525154"
screen_width = root.winfo_screenwidth()
screen_height =root.winfo_screenheight() - 200
root.title('')
unselected_color = '#40d0ff'
canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="#10033f")
planets = []
spacecrafts = []
is_stopped = True
selected = None
traj_img = tk.PhotoImage(width=screen_width, height=screen_height)
iteration_counter = 0
iterations_between_traj = 3000
extra_window = None
delay = 15


def centroid(points):
    x = points[::2]
    y = points[1::2]
    return [sum(x) / len(x), sum(y) / len(y)]


def remove_letters(string, letters):
    s1 = string
    for letter in letters:
        s1 = s1.replace(letter, '')
    return s1


def count_all_letters(string, letters):
    answer = 0
    for letter in letters:
        answer += string.count(letter)
    return answer


def convert_color(r, g, b):
    return f'#{hex(r)[2:].ljust(2, "0")}{hex(g)[2:].ljust(2, "0")}{hex(b)[2:].ljust(2, "0")}'


def calc_central(planets):
    a, b = 0, 0
    for planet in planets:
        a += planet.mass * planet.coords[0]
        b += planet.mass
    x = a / b
    a, b = 0, 0
    for planet in planets:
        a += planet.mass * planet.coords[1]
        b += planet.mass
    y = a / b
    return [x, y]


def vectorsum(*args):
    x = 0
    y = 0
    for i in args:
        x += i[0]
        y += i[1]
    return [x, y]


def perpendicular_vector(vector):
    return [-vector[1], vector[0]]


def valid_float(string):
    return remove_letters(string, ['.', '-']).replace(',', '.').isdigit() and string not in ['.', '-']


class Planet():
 
    def __init__(self, mass=10, coords=[0, 0], speed=[0, 0], is_fixed=False, color = 'red', name='planet', radius=0):
        global planets
        if radius == 0:
            radius = mass
        self.name = name
        self.is_fixed = is_fixed
        self.mass = mass
        self.coords = coords
        self.speed = speed
        self.color = color
        
        self.ball = canvas.create_oval(coords[0] - radius, coords[1] - radius,
                                       coords[0] + radius, coords[1] + radius, fill=color, outline=unselected_color, width=1)
        planets.append(self)

    
    def calculate_acceleration(self, *args):
        q = []
        for planet in args:
            if planet == self:
                continue
            V = [planet.coords[0] - self.coords[0], planet.coords[1] - self.coords[1]]
            distance = (V[0] ** 2 + V[1] ** 2) ** 0.5
            if distance == 0:
                continue
            F = (planet.mass * G) / (distance ** 3)
            Fx, Fy = V[0] * F, V[1] * F
            q.append((Fx, Fy))
        return vectorsum(*q)


class DialogWindow():
    
    window = None
    
    def __init__(self, x, y):
        global selected
        if selected is None:
            return
        
        def change_fixed_value():
            self.fixed_value = not self.fixed_value
        
        fixed_checkbox = tk.IntVar()
        extra_window = tk.Tk()
        extra_window.geometry(f'+{x}+{y}')
        extra_window['bg'] = 'blue'
        coords_label = tk.Label(text=f'Coords: {round(selected.coords[0], 2)} : {round(selected.coords[1], 2)}',
                                master=extra_window)
        speed_label = tk.Label(text=f'Speed: {round(selected.speed[0], 2)} : {round(selected.speed[1], 2)}',
                               master=extra_window)
        entry_speedx = tk.Entry(extra_window, width=8, bd=3, justify='center')
        entry_speedy = tk.Entry(extra_window, width=8, bd=3, justify='center')
        entry_coordsx = tk.Entry(extra_window, width=8, bd=3, justify='center')
        entry_coordsy = tk.Entry(extra_window, width=8, bd=3, justify='center')
        
        fixed_button = tk.Button(extra_window, command=change_fixed_value)
        fixed_value = False
        
        
        update_button = tk.Button(extra_window, command=update_values, bg="green", fg="black", text='OK')
        
        self.window = extra_window
        self.speedx = entry_speedx
        self.speedy = entry_speedy
        self.coordsx = entry_coordsx
        self.coordsy = entry_coordsy
        self.coords_label = coords_label
        self.speed_label = speed_label
        self.fixed_value = fixed_value
        
        coords_label.grid(row=0, column=0)
        speed_label.grid(row=1, column=0)
        entry_speedx.grid(row=1, column=1)
        entry_speedy.grid(row=1, column=2)
        entry_coordsx.grid(row=0, column=1)
        entry_coordsy.grid(row=0, column=2)
        update_button.grid(row=2, column=1)
        fixed_button.grid(row=2, column=0)
        
        extra_window.overrideredirect(True)


class ListOfPlanets():

    def __init__(self, x, y):

        global selected
        list_window = tk.Tk()
        list_window.title('List of planets')
        list_canvas = tk.Canvas(list_window)

        
        blocks = []
        for i, planet in enumerate(planets):
            block = tk.Frame(list_window, relief='ridge', padx=5, pady=5, bd=3)
            coords = tk.Label(block, text=f'{round(planet.coords[0], 2)} : {round(planet.coords[1], 2)}')
            speeds = tk.Label(block, text=f'{round(planet.speed[0], 2)} : {round(planet.speed[1], 2)}')
            select_button = tk.Button(block, command=(lambda: (selected := planet) and print(planet.color, selected)))
            
            select_button.grid(row=1, column=0)
            coords.grid(row=0, column=0)
            speeds.grid(row=0, column=1)
            block.pack()


class LabelEntryButton(tk.Frame):

    def __init__(self, master, func, label_text):
        super().__init__(master, relief='ridge', bd=3)

        def call_func():
            func(entry.get(), label)
        
        label = tk.Label(self, text=label_text)
        entry = tk.Entry(self, width=10, justify='center')
        b = tk.Button(self, text='OK', command=call_func)
        
        label.pack(side='left', fill='x')
        entry.pack(side='left', padx=5)
        b.pack(side='right')


class Panel(tk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        def change_G(x, label):
            global G
            if valid_float(x):
                G = float(x)
                label.config(text=f'G: {G}')
        
        def change_iterations_between_traj(x, label):
            global iterations_between_traj
            if valid_float(x) and float(x) > 0:
                iterations_between_traj = float(x)
                label.config(text=f'Traj. dens: {iterations_between_traj}')
        
        def change_delay(x, label):
            global delay
            if x.isdigit() and int(x) > 0:
                delay = int(x)
                label.config(text=f'Delay ms: {delay}')
        
        
        
        traj_UI = LabelEntryButton(self, change_iterations_between_traj, f'Traj. dens: {iterations_between_traj}')
        G_UI = LabelEntryButton(self, change_G, f'G: {G}')
        delay_UI = LabelEntryButton(self, change_delay, f'Delay ms: {delay}')
        save_button = tk.Button(self, command=save_simulation, text='Save')
        load_button = tk.Button(self, command=save_simulation, text='Load')

        delay_UI.place(x=0, y=0, width=200)
        G_UI.place(x=0, y=35, width=200)
        traj_UI.place(x=0, y=70, width=200)
        save_button.place(x=1810, y=0, width=100)
        load_button.place(x=1810, y=30, width=100)


def update():
    global iteration_counter
    iteration_counter += 1
    
    speeds = []
    for planet in planets:
        if planet.is_fixed:
            speeds.append(planet.speed)
            continue
        planet.speed = vectorsum(planet.speed, planet.calculate_acceleration(*planets))
    
    for spacecraft in spacecrafts:
        spacecraft.speed = vectorsum(spacecraft.speed, spacecraft.calculate_acceleration(*planets))
        canvas.move(spacecraft.craft, *spacecraft.speed)
        spacecraft.coords = centroid(canvas.coords(spacecraft.craft))
    
    if iteration_counter % iterations_between_traj == 0:
        display_traj()
    
    for i, planet in enumerate(planets):
        canvas.move(planet.ball, *planet.speed)
        planet.coords = [(canvas.coords(planet.ball)[0] + canvas.coords(planet.ball)[2]) / 2,
                    (canvas.coords(planet.ball)[1] + canvas.coords(planet.ball)[3]) / 2]
    
    canvas.move(central, -canvas.coords(central)[0] + calc_central(planets)[0],
                -canvas.coords(central)[1] + calc_central(planets)[1]) 
    if not is_stopped:
        root.after(delay, update)


class SpaceCraft():
    
    def __init__(self, speed=[0, 0], coords=[0, 0], rotation=0):
        spacecrafts.append(self)
        self.speed = speed
        self.coords = coords
        self.craft = canvas.create_polygon([coords[0], coords[1], coords[0] - 7, coords[1] + 14, coords[0] + 7, coords[1] + 14], outline='#f11', fill='#1f1', width=1)
        self.force_vector = [sin(radians(rotation)), cos(radians(rotation))]


    def calculate_acceleration(self, *args):
        q = []
        for planet in args:
            if planet == self:
                continue
            V = [planet.coords[0] - self.coords[0], planet.coords[1] - self.coords[1]]
            ln = (V[0] ** 2 + V[1] ** 2) ** 0.5
            if ln == 0:
                continue
            F = (planet.mass * G) / (ln ** 3)
            Fx, Fy = V[0] * F, V[1] * F
            q.append((Fx, Fy))
        return vectorsum(*q)

    
    def align_rotation(self, angle):
        centroid = centroid(...)

    def engine_force(self, force):
        self.speed = vectorsum(self.speed, [self.force_vector[0] * force, self.force_vector[1] * force])


'''a = SpaceCraft(coords=[100, 100], speed=[3, 0])
a.engine_force(-0.6)'''

def stop_start(event):
    global is_stopped
    if is_stopped:
        if selected is not None:
            canvas.itemconfig(selected.ball, outline=unselected_color)
        is_stopped = False
        update()
    else:
        is_stopped = True


def left_click(event):
    lengths = []
    
    for planet in planets:
        V = [planet.coords[0] - event.x, planet.coords[1] - event.y]
        lengths.append((V[0] ** 2 + V[1] ** 2) ** 0.5)
    
    if min(lengths) <= 30 and is_stopped:
        select_planet(planets[lengths.index(min(lengths))])
        canvas.itemconfig(selected.ball, outline='yellow')
    else:
        select_planet(None)


def select_planet(planet):
    global selected
    
    if planet is None:
        canvas.itemconfig(selected.ball, outline=unselected_color)
        selected = None
        return
    
    selected = planet
    canvas.itemconfig(selected.ball, outline='yellow')


def save_simulation():
    save_adress = filedialog.asksaveasfilename(defaultextension='txt')
    if save_adress == '':
        return
    
    with open(save_adress, 'w') as save_file:
        save_file.write()
         

        
def display_traj():
    global traj_img
    for planet in planets:
        if not screen_width >= planet.coords[0] >= 0 or not screen_height >= planet.coords[1] >= 0:
            continue
        traj_img.put(planet.color, list(map(int, planet.coords)))
    canvas.create_image((screen_width // 2, screen_height // 2), image=traj_img, state="normal")


def motion(event):
    global selected
    '''if selected is not None and is_stopped:
        x, y = event.x, event.y
        canvas.move(selected.ball, x - canvas.coords(selected.ball)[0] - abs(selected.mass) ** 0.5 / 2,
                    y - canvas.coords(selected.ball)[1] - abs(selected.mass) ** 0.5 / 2)
        selected.coords = [(canvas.coords(selected.ball)[0] + canvas.coords(selected.ball)[2]) / 2,
                    (canvas.coords(selected.ball)[1] + canvas.coords(selected.ball)[3]) / 2]
    else:
        selected = None'''
        
 
def update_values():
    global selected

    x_cord = extra_window.coordsx.get()
    y_cord = extra_window.coordsy.get()
    x_speed = extra_window.speedx.get()
    y_speed = extra_window.speedy.get()
    
    
    if valid_float(x_speed):
        selected.speed[0] = float(extra_window.speedx.get().replace(',', '.'))
    if valid_float(y_speed):
        selected.speed[1] = float(extra_window.speedy.get().replace(',', '.'))
        
    if valid_float(x_cord):
        canvas.move(selected.ball, float(x_cord) - selected.coords[0], 0)
        selected.coords[0] = float(extra_window.coordsx.get().replace(',', '.'))
    if valid_float(y_cord):
        canvas.move(selected.ball, 0, float(y_cord) - selected.coords[1])
        selected.coords[1] = float(extra_window.coordsy.get().replace(',', '.'))
    
    extra_window.coords_label.config(text=f'Coords: {round(selected.coords[0], 2)} : {round(selected.coords[1], 2)}')
    extra_window.speed_label.config(text=f'Speed: {round(selected.speed[0], 2)} : {round(selected.speed[1], 2)}')

 
def right_click(event):
    global extra_window
    if selected is None:
        return
    if extra_window is not None:
        extra_window.window.destroy()
    extra_window = DialogWindow(event.x_root, event.y_root)


a = Planet(mass=597.26, coords=[700, 384], speed=[0, 0], is_fixed=True, color='green', radius=63.78)
b = Planet(mass=7.3477, coords=[700 - 363, 384], speed=[0, 10.23 / 3.4], color='#8888ff', radius=17.38)
Planet(mass=0.01, coords=[264, 387], speed=[0, 2.75], color='red', radius=6)
#Planet(mass=55, coords=[250, 400], speed=[0, 0])
#Planet(mass=10, coords=[100, 400], speed=[0, -1.5], color='blue')
'''for i in range(150):
    Planet(coords=[rnd.randint(0, 1920), rnd.randint(0, 1080)])'''
#Planet(mass=30, coords=[200, 384], speed=[0, 3], color='')

_ = calc_central(planets)
central = canvas.create_oval(_[0] - 4, _[1] - 4, _[0] + 4, _[1] + 4, fill='#ffaf00')
    

panel = Panel(width=1000)

root.bind('<Tab>', lambda event: ListOfPlanets(event.x, event.y))
root.bind('<space>', stop_start)
canvas.bind('<Motion>', motion)
canvas.bind('<Button-1>', left_click)
canvas.bind('<Button-3>', right_click)
root.bind('<Delete>', lambda event: print(event.x)) # TODO: удаление планеты по нажатию Delete


canvas.pack()
panel.pack(side='left', fill='both', expand=True)
root.mainloop()
