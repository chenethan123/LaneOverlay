# python3
import tkinter as tk
from tkinter.ttk import *
from tkinter import *
import requests
from login import extrauser
import numpy as np
import cv2 as cv
from PIL import Image, ImageTk
path = 'My+Movie+4.mov'
video = cv.VideoCapture(path)


video.set(cv.CAP_PROP_FRAME_WIDTH, 300)
video.set(cv.CAP_PROP_FRAME_HEIGHT, 300)

from datetime import datetime


fen = tk.Tk()

def update_log_text():
    with open(f"{extrauser}.txt", "r") as file:
        log_content = file.read()
        log_text.config(state=tk.NORMAL)
        log_text.delete("1.0", tk.END)
        log_text.insert(tk.END, log_content)
        log_text.config(state=tk.DISABLED)
        log_text.yview(tk.END)  # scroll down to end!


def movement(direction):
    time = datetime.now()
    current_hour = time.strftime("%H")
    hourint = int(current_hour) - 5
    if hourint < 0:
        hourint = 24 + hourint
    current_time = time.strftime(f"%Y-%m-%d {hourint}:%M:%S %Z%z")

    with open(f'{extrauser}.txt', 'at') as f:
        f.write(f"{extrauser} pressed {direction} at " + current_time + "\n")

    url = "http://192.168.1.36:5000"
    requests.post(url, json={'command': direction})
    
    update_log_text()


def logout():
    fen.destroy()
    time = datetime.now()
    current_hour = time.strftime("%H")
    hourint = int(current_hour) - 5
    if hourint < 0:
        hourint = 24 + hourint
    current_time = time.strftime(f"%Y-%m-%d {hourint}:%M:%S %Z%z")

    with open(f'{extrauser}.txt', 'at') as f:
        f.write(f"{extrauser} has logged out at " + current_time + "\n")

    update_log_text()




# Create a label widget to display the video feed
label_widget = tk.Label(fen)
label_widget.grid(row=1)

# Create a frame for the video feed
left = tk.Frame(fen, bg="grey", width=300, height=300)
left.pack_propagate(False)
tk.Label(left, text="Line Detection", fg="white", bg="black", anchor="center", justify="center").pack()
left.grid(column=0, row=0, pady=5, padx=10, sticky="n")

# Create a label widget to display the video feed inside the left frame
video_label = tk.Label(left)
video_label.pack()

# masked line detection stuff ----------------------------------------------------
region_top_left = (0, 250)  # Example values for top-left coordinate
region_bottom_right = (640, 360)  # Example values for bottom-right coordinate
# masked line detection stuff ----------------------------------------------------

video_path = 'My+Movie+4.mov'
cap = cv.VideoCapture(video_path)


def update_video_feed():
    ret, frame = cap.read()
    if ret:
        frame = cv.resize(frame, (640, 360))
        region_of_interest = frame[region_top_left[1]:region_bottom_right[1], region_top_left[0]:region_bottom_right[0]]
        gray_roi = cv.cvtColor(region_of_interest, cv.COLOR_BGR2GRAY)
        roi_edges = cv.Canny(gray_roi, 50, 150)
        lines = cv.HoughLinesP(roi_edges, 1, np.pi / 180, 50, minLineLength=30, maxLineGap=30)

        if lines is not None:
            left_points = []
            right_points = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                x1 += region_top_left[0]
                y1 += region_top_left[1]
                x2 += region_top_left[0]
                y2 += region_top_left[1]

                cv.line(frame, (x1, y1), (x2, y2), (0, 255, 0), thickness=2)

                slope = (y2 - y1) / (x2 - x1) if (x2 - x1) != 0 else float('inf')
                if slope < 0:  # Left line
                    left_points.append((x1, y1))
                    left_points.append((x2, y2))
                elif slope > 0:  # Right line
                    right_points.append((x1, y1))
                    right_points.append((x2, y2))

            left_x1 = left_x2 = 0
            right_x1 = right_x2 = 0

            if left_points:
                left_line = cv.fitLine(np.array(left_points), cv.DIST_L2, 0, 0.01, 0.01)
                vx, vy, x, y = left_line[0], left_line[1], left_line[2], left_line[3]
                left_intercept = y - vy / vx * x
                left_x1 = int((region_top_left[1] - left_intercept) / (vy / vx))
                left_x2 = int((region_bottom_right[1] - left_intercept) / (vy / vx))
                cv.line(frame, (left_x1, region_top_left[1]), (left_x2, region_bottom_right[1]), (0, 0, 255),
                        thickness=2)

            if right_points:
                right_line = cv.fitLine(np.array(right_points), cv.DIST_L2, 0, 0.01, 0.01)
                vx, vy, x, y = right_line[0], right_line[1], right_line[2], right_line[3]
                right_intercept = y - vy / vx * x
                right_x1 = int((region_top_left[1] - right_intercept) / (vy / vx))
                right_x2 = int((region_bottom_right[1] - right_intercept) / (vy / vx))
                cv.line(frame, (right_x1, region_top_left[1]), (right_x2, region_bottom_right[1]), (0, 0, 255),
                        thickness=2)

        opencv_image = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
        pil_image = Image.fromarray(opencv_image)
        photo_image = ImageTk.PhotoImage(image=pil_image)

        video_label.photo_image = photo_image
        video_label.configure(image=photo_image)
    else:
        print("Failed to retrieve frame from the video source.")

    fen.after(10, update_video_feed)

update_video_feed()
sty = Style(fen)
sty.configure("TSeparator", background="black")

# TOP RIGHT

right = tk.Frame(fen, width=200, height=200, bg="grey")
right.pack_propagate(False)
tk.Label(right, text="Movement Controls", fg="white", bg="black").pack()
right.grid(column=2, row=0, pady=5, padx=10, sticky="n")

forwardbutton = Button(right, text="↑", width=7, command=lambda: movement("forward"))
forwardbutton.grid(row=0, column=2, pady=(30, 3), padx=10, columnspan=2)

leftbutton = Button(right, text="←", width=3, command=lambda: movement("left"))
leftbutton.grid(row=1, column=1, pady=3)

stopbutton = Button(right, text="◉", width=3, command=lambda: movement("stop"))
stopbutton.grid(row=1, column=2, pady=3)

demobutton = Button(right, text="▶", width=3, command=lambda: movement("demo"))
demobutton.grid(row=1, column=3, pady=3)

rightbutton = Button(right, text="→", width=3, command=lambda: movement("right"))
rightbutton.grid(row=1, column=4, pady=3)

backbutton = Button(right, text="↓", width=7, command=lambda: movement("backward"))
backbutton.grid(row=2, column=2, pady=3, columnspan=2)

logoutbutton = Button(right, text="Logout", width=5, command=lambda: logout())
logoutbutton.grid(row=3, column=2, pady=(20, 16), columnspan=2)

# Bottom Left

bleft = tk.Frame(fen, bg="grey", width=200, height=200)

bleft.pack_propagate(False)
tk.Label(bleft, text="Raw Video", fg="white", bg="black", anchor="center", justify="center").pack()
bleft.grid(column=0, row=1, pady=5, padx=10, sticky="n")
sep = Separator(fen, orient="vertical")
sep.grid(column=1, row=1, sticky="ns")

label_widget = Label(bleft)
label_widget.pack()

def open_cam():
    _, frame = video.read()
    opencv_image = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
    captured_image = Image.fromarray(opencv_image)
    photo_image = ImageTk.PhotoImage(image=captured_image)
    label_widget.photo_image = photo_image
    label_widget.configure(image=photo_image)
    label_widget.after(10, open_cam)

open_cam()

# BOTTOM RIGHT
bright = tk.Frame(fen, bg="grey", width=200, height=200)
bright.pack_propagate(False)
tk.Label(bright, text="Log", fg="white", bg="black").pack()
log_text = tk.Text(bright, fg="white", bg="black", height=10, width=30, wrap=tk.WORD, state=tk.DISABLED)
log_text.grid(column=0, row=2, pady=22, padx=10, sticky="n", rowspan=2)

scrollbar = tk.Scrollbar(bright, command=log_text.yview)

log_text.config(yscrollcommand=scrollbar.set)

bright.grid(column=2, row=1, pady=5, padx=10, sticky="n")

update_log_text()

fen.mainloop()
