"""
This simple animation example shows how to bounce a rectangle
on the screen.

It assumes a programmer knows how to create functions already.

It does not assume a programmer knows how to create classes. If you do know
how to create classes, see the starting template for a better example:

http://arcade.academy/examples/starting_template.html

Or look through the examples showing how to use Sprites.

A video walk-through of this example is available at:
https://vimeo.com/168063840

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.bouncing_rectangle

"""
import numpy as np
import arcade
import random
import networkx as nx
from localization import localize, generate_problem
from sensor_selection import activate_sensors

random.seed(27)

# --- Set up states
STATE_INITIAL = True
STATE_RUNNING = False

# --- Set up the constants

# Size of the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
SCREEN_TITLE = "QCVehicleNetwork"

NUM_BIT = 62
DX = SCREEN_WIDTH / NUM_BIT
DY = SCREEN_HEIGHT / NUM_BIT
DD = (DX ** 2 + DY ** 2) ** 0.5

MAX_UNIT = 63

# Size of the rectangle
CIRCLE_WIDTH = 50
CIRCLE_HEIGHT = 50
VEHICLE_WIDTH = 100
VEHICLE_WIDTH = 100
BACKGROUND = arcade.load_texture("bg.png")


# Buttons
PLAY_BUTTON = arcade.Sprite("play.png", 0.5)
STOP_BUTTON = arcade.Sprite("pause.png", 0.5)
RESET_BUTTON = arcade.Sprite("reset.png", 0.5)

button_sprites = arcade.SpriteList()
button_sprites.append(PLAY_BUTTON)
button_sprites.append(STOP_BUTTON)
button_sprites.append(RESET_BUTTON)

btnx = range(50, 400, 50)
btny = 50
for i in range(len(button_sprites)):
    button_sprites[i].center_x = btnx[i]
    button_sprites[i].center_y = btny


# valid distance
RADIUS = 200
mouse_x = -100
mouse_y = -100

# colors
ACTIVE_SENSOR_COLOR = arcade.color.AQUAMARINE
ACTIVE_SENSOR_EDGE_COLOR = arcade.color.AQUAMARINE
NON_ACTIVE_SENSOR_COLOR = arcade.color.ARTICHOKE
NON_ACTIVE_SENSOR_EDGE_COLOR = arcade.color.ARTICHOKE
VEHICLE_COLOR = arcade.color.AUREOLIN
VEHICLE_EDGE_COLOR = arcade.color.AUREOLIN
ESTIMATION_COLOR = arcade.color.CORAL_RED

class Node:
    def __init__(self, x, y, w, c=arcade.color.CARIBBEAN_GREEN, shape='circle'):
        self.x = x  #32 23 22 23
        self.y = y
        self.w = w
        self.c = c
        self.shape = shape
        self.dx = 100 * random.choice([-1, 1])
        self.dy = 100 * random.choice([-1, 1])

    def move(self, dt):

        # Figure out if we hit the edge and need to reverse.
        if self.x < CIRCLE_WIDTH // 2:
            self.dx = abs(self.dx)
        if self.x > SCREEN_WIDTH - CIRCLE_WIDTH // 2:
            self.dx = -abs(self.dx)
        if self.y < CIRCLE_HEIGHT // 2:
            self.dy = abs(self.dy)
        if self.y > SCREEN_HEIGHT - CIRCLE_HEIGHT // 2:
            self.dy = -abs(self.dy)

        dx = (mouse_x - self.x)
        dy = (mouse_y - self.y)

        if (dx ** 2 + dy ** 2) ** 0.5 < 20:
            return

        ratio = 100 / (dx**2 + dy**2)**0.5
        self.x += dx * ratio * dt
        self.y += dy * ratio * dt


    def render(self):
        if self.shape == 'circle':
            arcade.draw_circle_filled(self.x, self.y,
                                         self.w, color=self.c)
        elif self.shape == 'rect':
            arcade.draw_rectangle_filled(self.x, self.y,
                                         self.w, self.w, self.c)

class Edge:
    def __init__(self, node1, node2, w=1, c=arcade.color.CARIBBEAN_GREEN):
        self.node1 = node1
        self.node2 = node2
        self.w = w
        self.c = c
    def render(self):
        arcade.draw_line(self.node1.x, self.node1.y,
                self.node2.x, self.node2.y,
                self.c, 2)

def random_pos():
    return random.randint(CIRCLE_WIDTH // 2, SCREEN_WIDTH - CIRCLE_WIDTH // 2), random.randint(CIRCLE_HEIGHT // 2, SCREEN_HEIGHT - CIRCLE_HEIGHT // 2)

def create_random_nodes(n, **argv):
    ret = []
    for i in range(n):
        x, y = random_pos()
        ret.append(Node(x=x, y=y, w=10, **argv))
    return ret


def distance(node1, node2):
    return ((node1.x - node2.x) ** 2 + (node1.y - node2.y) ** 2) ** 0.5

def create_edge(nodes1, nodes2, radius, **argv):
    edges = []
    for i in range(len(nodes1)):
        for j in range(len(nodes2)):
            if i <= j:
                continue
            if distance(nodes1[i], nodes2[j]) < radius:
                edges.append(Edge(nodes1[i], nodes2[j], **argv))
    return edges

def render(eles):
    for e in eles:
        e.render()

def move(nodes, dt):
    for i in range(len(nodes)):
        nodes[i].move(dt)

sensors = create_random_nodes(15, c=NON_ACTIVE_SENSOR_COLOR)
vehicles = create_random_nodes(1, c=VEHICLE_COLOR)
active_sensor_ids = []
problem_string = ""
problems = []

counter = 0
ex = -100
ey = -100

def on_draw(delta_time):
    global vehicles
    global sensors
    global active_sensor_ids
    global DX
    global DY
    global DD
    global counter
    global ex
    global ey
    global mouse_x
    global mouse_y
    global problem_string
    global problems

    """
    Use this function to draw everything to the screen.
    """

    # Start the render. This must happen before any drawing
    # commands. We do NOT need a stop render command.
    arcade.start_render()

    arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND)
    button_sprites.draw()

    arcade.draw_circle_filled(mouse_x, mouse_y,
            10, color=arcade.color.WHITE)
    #
    # plot all sensor  (include non-active and active sensor)
    #

    # all edges
    edges = create_edge(sensors, sensors, 200, c=NON_ACTIVE_SENSOR_EDGE_COLOR)
    render(edges)

    # all sensors
    render(sensors)

    #
    # initial state
    #
    global STATE_INITIAL

    if STATE_INITIAL:
        sensors = create_random_nodes(15, c=NON_ACTIVE_SENSOR_COLOR)
        vehicles = create_random_nodes(1, c=VEHICLE_COLOR)
        arcade.draw_text("Applay sensor placement algorithm...", SCREEN_WIDTH//2, SCREEN_HEIGHT//2, arcade.color.BLACK, 12)
        is_activate = activate_sensors(sensors, RADIUS)

        # set sensor colors
        for i in range(len(is_activate)):
            sensors[i].c = ACTIVE_SENSOR_COLOR if is_activate[i] else NON_ACTIVE_SENSOR_COLOR
            if is_activate[i]:
                active_sensor_ids.append(i)

        render(sensors)
        STATE_INITIAL = False
        return

    #
    # plot active sensors
    #
    active_sensors = [sensors[i] for i in range(len(sensors)) if i in active_sensor_ids]
    render(active_sensors)

    # plot active sensor edge
    active_edges = create_edge(active_sensors, active_sensors, RADIUS)
    render(active_edges)

    if STATE_RUNNING:
        #
        # plot vehicle
        #
        move(vehicles, delta_time)
    # plot vehicle moving
    edges = create_edge(active_sensors, vehicles, RADIUS, c=VEHICLE_EDGE_COLOR)
    render(edges)

    # perform estimation
    arcade.draw_text(problem_string, vehicles[0].x, vehicles[0].y, arcade.color.WHITE, 8)
    if counter >= 20:
        problems = generate_problem(vehicles[0], active_sensors, RADIUS)
        problem_string = "\n".join(["dis %d loc %d loc %d"%p for p in problems][:len(edges)])
        ex, ey = localize(problems, DX, DY)
        counter = 0
    arcade.draw_rectangle_outline(ex+DX/2, ey+DY/2,
                             DX*4, DY*8, color=ESTIMATION_COLOR)


    # plot
    render(vehicles)


    counter += 1

    # Modify rectangles position based on the delta
    # vector. (Delta means change. You can also think
    # of this as our speed and direction.)
    # on_draw.center_x += on_draw.delta_x * delta_time
    # on_draw.center_y += on_draw.delta_y * delta_time

    # Figure out if we hit the edge and need to reverse.
    # if on_draw.center_x < CIRCLE_WIDTH // 2 \
    #         or on_draw.center_x > SCREEN_WIDTH - CIRCLE_WIDTH // 2:
    #     on_draw.delta_x *= -1
    # if on_draw.center_y < CIRCLE_HEIGHT // 2 \
    #         or on_draw.center_y > SCREEN_HEIGHT - CIRCLE_HEIGHT // 2:
    #     on_draw.delta_y *= -1


# Below are function-specific variables. Before we use them
# in our function, we need to give them initial values. Then
# the values will persist between function calls.
#
# In other languages, we'd declare the variables as 'static' inside the
# function to get that same functionality.
#
# Later on, we'll use 'classes' to track position and velocity for multiple
# objects.
# on_draw.center_x = 100  # type: ignore # dynamic attribute on function obj  # Initial x position
# on_draw.center_y = 50   # type: ignore # dynamic attribute on function obj  # Initial y position
# on_draw.delta_x = 115   # type: ignore # dynamic attribute on function obj  # Initial change in x
# on_draw.delta_y = 130   # type: ignore # dynamic attribute on function obj  # Initial change in y

class Simulator(arcade.Window):

    def __init__(self, width, height, title):

        # Call the parent class's init function
        super().__init__(width, height, title)

        # Make the mouse disappear when it is over the window.
        # So we just see our object, not the pointer.
        arcade.set_background_color(arcade.color.ASH_GREY)

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called when the user presses a mouse button.
        """
        global STATE_RUNNING
        global STATE_INITIAL
        global mouse_x
        global mouse_y
        mouse_x = x
        mouse_y = y
        for i in range(len(button_sprites)):
            # calculate distance
            distance = ((button_sprites[i].center_x - x) ** 2 + (button_sprites[i].center_y - y) ** 2) ** 0.5
            if distance < 30:
                if i == 0:
                    STATE_RUNNING = True
                if i == 1:
                    STATE_RUNNING = False
                if i == 2:
                    STATE_INITIAL = True
                    STATE_RUNNING = False

    def on_mouse_motion(self, x, y, dx, dy):
        global mouse_x
        global mouse_y
        mouse_x = x
        mouse_y = y

def main():
    # Open up our window
    Simulator(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    # Tell the computer to call the draw command at the specified interval.
    arcade.schedule(on_draw, 1 / 60)

    # Run the program
    arcade.run()


if __name__ == "__main__":
    main()
