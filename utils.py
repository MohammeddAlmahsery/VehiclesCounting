import cv2 as cv
from dotenv import load_dotenv
import os

load_dotenv(".env")
INPUT_PATH = os.getenv("INPUT_PATH")
OUTPUT_PATH = os.getenv("OUTPUT_PATH")

in_line = ((320, 266), (640, 266))
out_line = ((0, 200), (320, 200))

GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
RED = (0, 0, 255)
NAVY_BLUE = (120, 30, 30)

def info_string(cars_inside, cars_entered, cars_left):
    return [
        f"Cars Inside: {cars_inside}",
        f"Cars Entered: {cars_entered}",
        f"Cars Left: {cars_left}"
    ]


def draw_info(img, cars_inside, cars_entered, cars_left):
    lines = info_string(cars_inside, cars_entered, cars_left)

    x, y0 = 15, 30   # starting position
    dy = 30          # line spacing
    font = cv.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    thickness = 2

    for i, line in enumerate(lines):
        y = y0 + i * dy

        # Draw white shadow for visibility
        cv.putText(img, line, (x+2, y+2), font, font_scale, (255, 255, 255), thickness+1, cv.LINE_AA)
        # Draw main text
        cv.putText(img, line, (x, y), font, font_scale, NAVY_BLUE, thickness, cv.LINE_AA)

    # Draw extra lines (borders)
    img_out = cv.line(img, (320, 200), (320, 266), BLUE, 2)   # Split inside/outside
    img_out = cv.line(img_out, in_line[0], in_line[1], GREEN, 2)  # In border
    img_out = cv.line(img_out, out_line[0], out_line[1], RED, 2)  # Out border
    
    return img_out


def is_touching_line(box, line):

    pt1, pt2 = line
    rect = tuple(map(int, box))

    inside, new_pt1, new_pt2 = cv.clipLine(rect, pt1, pt2)

    return inside


def is_vehicle_entering(vehicle):

    if is_touching_line(vehicle.box, in_line):
        return 1
    
    return 0


def is_vehicle_leaving(vehicle):

    if is_touching_line(vehicle.box, out_line):
        return 1
    
    return 0