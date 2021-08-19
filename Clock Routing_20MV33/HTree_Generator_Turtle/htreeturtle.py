import turtle
SPEED = 8
BG_COLOR = "red"
PEN_COLOR = "lightgreen"
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
DRAWING_WIDTH = 500
DRAWING_HEIGHT = 500
PEN_WIDTH = 5
TITLE = "H-Tree Fractal"
FRACTAL_DEPTH = 3
def draw_line(tur, pos1, pos2):
    tur.penup()
    tur.goto(pos1[0], pos1[1])
    tur.pendown()
    tur.goto(pos2[0], pos2[1])

def recursive_draw(tur, x, y, width, height, count):
    draw_line(
        tur,
        [x + width * 0.25, height // 2 + y],
        [x + width * 0.75, height // 2 + y],
    )
    draw_line(
        tur,
        [x + width * 0.25, (height * 0.5) // 2 + y],
        [x + width * 0.25, (height * 1.5) // 2 + y],
    )
    draw_line(
        tur,
        [x + width * 0.75, (height * 0.5) // 2 + y],
        [x + width * 0.75, (height * 1.5) // 2 + y],
    )
    if count <= 0:
        return
    else:
        count -= 1

        recursive_draw(tur, x, y, width // 2, height // 2, count)
        recursive_draw(tur, x + width // 2, y, width // 2, height // 2, count)
        recursive_draw(tur, x, y + width // 2, width // 2, height // 2, count)
        recursive_draw(tur, x + width // 2, y + width // 2, width // 2,
height // 2, count)

if __name__ == "__main__":
    # Screen setup
    screen = turtle.Screen()
    screen.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
    screen.title(TITLE)
    screen.bgcolor(BG_COLOR)
    # Turtle artist (pen) setup
    artist = turtle.Turtle()
    artist.hideturtle()
    artist.pensize(PEN_WIDTH)
    artist.color(PEN_COLOR)
    artist.speed(SPEED)

    recursive_draw(artist, - DRAWING_WIDTH / 2, - DRAWING_HEIGHT / 2,
DRAWING_WIDTH, DRAWING_HEIGHT, FRACTAL_DEPTH)

    turtle.done()
