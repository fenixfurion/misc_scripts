#!/usr/bin/env python3
import tkinter as tk
from tkinter.colorchooser import askcolor
import math
import functools
import random

@functools.total_ordering
class Hexagon:
    def __init__(self, array, row, column, color=None, isLocked=False):
        self.array = int(array)
        self.row = int(row)
        self.column = int(column)
        self.isLocked = isLocked
        self.isInitialized = False
        if not color:
            # randomcolor = f'#{random.randrange(0, 2**24):06x}'
            # self.color = randomcolor
            self.color = '#ffffff'
        else:
            self.color = color
        print(f"Initing Hexagon at {(self.array, self.row, self.column)}.")

    def lock(self):
        self.isLocked = True

    def unlock(self):
        self.isLocked = False

    def set_color(self, color):
        self.color = color

    def convert_from_arc(self):
        array = float(self.array)
        row = float(self.row)
        column = float(self.column)
        
        x = (array / 2.0) + column
        y = (math.sqrt(3.0) * ((array / 2.0) + row))

        # print(f"Input: array={array}, row={row}, column={column}")
        # print(f"Output: x={x}, y={y}")
        return x, y

    def get_neighbor_coords(self):
        a = self.array
        r = self.row
        c = self.column
        neighbors = [
            (1-a, r-(1-a), c-(1-a)),
            (1-a, r-(1-a), c+a),
            (a, r, c-1),
            (a, r, c+1),
            (1-a, r+a, c-(1-a)),
            (1-a, r+a, c+a)
        ]
        return neighbors

    def get_valid_neighbors(self, hexmap):
        valid_neighbors = []
        for neighbor in self.get_neighbor_coords():
            if neighbor in hexmap.keys():
                valid_neighbors.append(neighbor)
        return valid_neighbors

    def get_initialized_neighbors(self, hexmap):
        initialized_neighbors = []
        for neighbor in self.get_neighbor_coords():
            if neighbor in hexmap.keys() and hexmap[neighbor].isInitialized:
                initialized_neighbors.append(neighbor)
        return initialized_neighbors

    def __eq__(self, other):
        return (self.array, self.row, self.column) == (other.array, other.row, other.column)

    def __lt__(self, other):
        return (self.array, self.row, self.column) < (other.array, other.row, other.column)

    def __str__(self):
        return f"Hexagon({self.array}, {self.row}, {self.column}, color={self.color}, isLocked={self.isLocked}, isInitialized={self.isInitialized})"
    
    def __repr__(self):
        return f"Hexagon({self.array}, {self.row}, {self.column}, color={self.color}, isLocked={self.isLocked}, isInitialized={self.isInitialized})"

def draw_regular_hexagon(canvas, hexagon):
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    # Calculate the radius as 5% of the smallest dimension of the window
    r = min(canvas_width, canvas_height) * 0.025
    canvas_mid_x = canvas_width / 2
    canvas_mid_y = canvas_height / 2

    x, y = hexagon.convert_from_arc()
    x *= r * math.sqrt(3.0)
    y *= r * math.sqrt(3.0)
    x += canvas_mid_x
    y += canvas_mid_y
    angle = 360 / 6
    points = []

    for i in range(6):
        x_i = x + r * math.cos(math.radians(30 + angle * i))
        y_i = y + r * math.sin(math.radians(30 + angle * i))
        points.extend([x_i, y_i])

    # print(f"Hexagon {(hexagon.array, hexagon.row, hexagon.column)} - Cartesian Coordinates: {x}, {y}")
    if hexagon.isLocked:
        outline = "#000000"
    else:
        outline = "#AAAAAA"
    object_id = canvas.create_polygon(points, outline=outline, fill=hexagon.color, width=3)
    return object_id

def resize_window(event=None):
    print(f"Window size is now {canvas.winfo_width()}x{canvas.winfo_height()}")
    redraw_hexagons()

def redraw_hexagons(event=None):
    canvas.delete("all")
    hex_canvas_objects = {}

    hexagon_key_list = list(hexagons.keys())
    hexagon_key_list.sort()

    print(f"Redrawing {len(hexagon_key_list)} hexagons...")
    tooltips = {}
    locked_list = []
    for key in hexagon_key_list:
        object_id = draw_regular_hexagon(canvas, hexagons[key])
        if hexagons[key].isLocked:
            locked_list.append(object_id)
        # print(f"Drew hexagon {key}, got id {object_id}")
        hex_canvas_objects[object_id] = key
        canvas.tag_bind(object_id, '<Enter>', functools.partial(item_hovered, id_mapping=hex_canvas_objects))
        canvas.tag_bind(object_id, '<Button-3>', functools.partial(hex_toggle_lock, id_mapping=hex_canvas_objects))
        canvas.tag_bind(object_id, '<Button-1>', functools.partial(hex_choose_color, id_mapping=hex_canvas_objects))

    for elem in locked_list:
        canvas.tag_raise(elem)


def item_hovered(event, id_mapping):
    canvas_item_id = event.widget.find_withtag('current')[0]
    coordinates = id_mapping[canvas_item_id]
    hexagon = hexagons[coordinates]
    #print(f"Hovered over {canvas_item_id} - coords are {coordinates} - color: {hexagon.color}")
    canvas.winfo_toplevel().title(f"Hexagons - {coordinates} - color: {hex_to_rgb(hexagon.color)}")

def hex_toggle_lock(event, id_mapping):
    canvas_item_id = event.widget.find_withtag('current')[0]
    coordinates = id_mapping[canvas_item_id]
    hexagon = hexagons[coordinates]
    print(f"Right clicked {canvas_item_id} - coords are {coordinates}")
    new_status = not hexagon.isLocked
    hexagon.isLocked = new_status
    print(f"Hexagon is now {'un' if not new_status else ''}locked")
    redraw_hexagons()

def hex_choose_color(event, id_mapping):
    canvas_item_id = event.widget.find_withtag('current')[0]
    coordinates = id_mapping[canvas_item_id]
    print(f"Left clicked {canvas_item_id} - coords are {coordinates}")
    hexagon = hexagons[coordinates]
    chosen_color = askcolor(hexagon.color, title=f"Choose color for {coordinates}")
    if chosen_color[1]:
        hexagon.color = chosen_color[1]
        # auto initialize and lock these
        hexagon.isInitialized = True
        hexagon.isLocked = True
        print(f"Hexagon color is now {hexagon.color}")
    else:
        print(f"Canceled color dialog - color is {hexagon.color}")
    redraw_hexagons()

def reflow_click_callback():
    print("Executing color reflow...")
    reflow_colors(-1)

def step_click_callback():
    print("Executing color reflow...")
    reflow_colors(1)

def hex_to_rgb(hexstring):
    assert hexstring[0] == '#'
    assert len(hexstring) == 7
    rgb = tuple(int(hexstring[1+i:1+i+2], 16) for i in (0, 2, 4))
    return rgb

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def get_neighbor_blend(hexmap, neighbors, coordinates):
    num_neighbors = len(neighbors)
    # print(f"Hexagon {coordinates} has {num_neighbors} neighbors.")
    total_r = 0
    total_g = 0
    total_b = 0
    for neighbor in neighbors:
        r, g, b = hex_to_rgb(hexmap[neighbor].color)
        # print(f"Neighbor {neighbor} has color {(r,g,b)}")
        total_r += r
        total_g += g
        total_b += b
        # print(f"Total colors: {(total_r, total_g, total_b)}")
    out_r = total_r//num_neighbors
    out_g = total_g//num_neighbors
    out_b = total_b//num_neighbors
    # print(f"Output colors: {(out_r, out_g, out_b)}")
    return rgb_to_hex((out_r, out_g, out_b))


def reflow_colors(steps, depth=0):
    depth += 1
    print(f"Iteration: {depth}")
    num_locked = len([1 for elem in hexagons.values() if elem.isLocked])
    num_initialized = len([1 for elem in hexagons.values() if elem.isInitialized])
    print(f"Number of locked hexagons: {num_locked} Number of initialzed hexagons: {num_initialized}")
    # iterate through each hexagon.
    # for each one that's not locked, check to see if there are any neighbors that are initialized.
    # if there are, make it the blend of all of its neighbors.
    # once we're done, apply changes and intialize the hexagons.
    changes_to_apply = {}
    hex_key_list = list(hexagons.keys())
    # sort first so we get a deterministic order for hexagons
    hex_key_list.sort()
    for key in hex_key_list:
        current_hex = hexagons[key]
        if current_hex.isLocked:
            continue
        # assume neighbors are valid and initialized
        neighbors = current_hex.get_initialized_neighbors(hexagons)
        num_neighbors = len(neighbors)
        if len(neighbors) == 0:
            # no neighbors
            continue
        # print(f"Hex {key}: Found {num_neighbors} neighbors: {neighbors})")
        blended_color = get_neighbor_blend(hexagons, neighbors, key)
        changes_to_apply[key] = blended_color

    changes_keys = list(changes_to_apply.keys())
    changes_keys.sort()
    newly_initialized = 0
    total_color_changes = 0
    for key in changes_keys:
        if not hexagons[key].color == changes_to_apply[key]:
            hexagons[key].set_color(changes_to_apply[key])
            # print(f"Changing {key} to {changes_to_apply[key]}")
            total_color_changes += 1
        if not hexagons[key].isInitialized:
            newly_initialized += 1
            hexagons[key].isInitialized = True
    print(f"{total_color_changes} hexagons updated. {newly_initialized} hexagons initialized.")
    redraw_hexagons()

    # need to add another case that breaks out of the infinite loop
    if (newly_initialized == 0 and total_color_changes == 0):
        print(f"Nothing else to reflow. Total iterations: {depth}")
        return
    if (num_locked == 0 or num_initialized == 0) and steps == -1:
        print(f"Don't reflow with nothing locked or initialized...")
        return
    # where no hexagons changed
    if depth == steps:
        # base case
        return
    else:
        reflow_colors(steps, depth=depth)

def create_neighbor_hexagons(hexagon):
    a = hexagon.array
    r = hexagon.row
    c = hexagon.column
    neighbors = hexagon.get_neighbor_coords()
    created_hexagons = []
    for candidate in neighbors:
        if not (candidate in hexagons.keys()):
            # *candidate expands the candidate tuple
            created_hexagons.append(Hexagon(*candidate))
        else:
            print(f"Not generating {candidate} as this already exists.")
    return created_hexagons

def main():
    global hexagons, canvas, hex_canvas_objects
    root = tk.Tk()
    root.resizable(True, True)
    root.title("Pointy-Top Hexagons")
    root.geometry("1000x1200")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    frame = tk.Frame(root)
    frame.pack(expand=1, fill=tk.BOTH)
    frame.grid(row=0, sticky="nsew")

    canvas = tk.Canvas(frame, bg="#aaa")
    canvas.grid(sticky=tk.N+tk.S+tk.E+tk.W)
    canvas.pack(fill=tk.BOTH, expand=True)  # Make the canvas resizable

    botframe = tk.Frame(root, height=200)
    botframe.grid(row=1, sticky="sew")

    reflow_button = tk.Button(botframe, text="Reflow", command=reflow_click_callback)
    reflow_button.place(x=50, y=50)

    reflow_step_button = tk.Button(botframe, text="Step Reflow", command=step_click_callback)
    reflow_step_button.place(x=50, y=100)

    root.update()

    hexagons = dict({(0,0,0): Hexagon(0,0,0)})
    print(hexagons)
    depth = 10
    new_hexagons = [hexagons[key] for key in hexagons.keys()]
    new_hexagons.sort()
    print(new_hexagons)
    for i in range(depth):
        current_hexagons = new_hexagons
        new_hexagons = []
        for current_hex in current_hexagons:
            print(current_hex)
            created_hexagons = create_neighbor_hexagons(current_hex)
            new_hexagons += list(created_hexagons)
            print(f"Created {len(created_hexagons)} hexagons.")
            print(new_hexagons)
            for hexagon in new_hexagons:
                hexagons[(hexagon.array, hexagon.row, hexagon.column)] = hexagon
            print(f"Total hexagons: {len(hexagons)}")
    hexagon_list = [hexagons[key] for key in hexagons.keys()]
    hexagon_list.sort()
    for hexagon in hexagon_list:
        print(hexagon)

    canvas.bind("<Configure>", resize_window)
    redraw_hexagons()

    root.mainloop()

if __name__ == "__main__":
    main()

