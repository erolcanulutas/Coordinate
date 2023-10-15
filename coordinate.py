import cv2
import os
import tkinter as tk
from tkinter import simpledialog, filedialog, Text, Button, Scrollbar, Frame, Checkbutton, IntVar
from PIL import Image, ImageDraw, ImageTk
import numpy as np

# Initialize variables
drag = False
point1 = ()
point2 = ()
areas = []
img = None
img_temp = None
reopen_window = True
img_original = None


def click_event(event, x, y, flags, param):
    global drag, point1, point2, areas, img, img_temp, frame_count, center_size
    img_changed = False

    if event == cv2.EVENT_LBUTTONDOWN:
        if center_click.get():
            if center_size:
                w, h = center_size
                point1 = (x - w // 2, y - h // 2)
                point2 = (x + w // 2, y + h // 2)

                area_name = f"Frame_{frame_count}" if auto_name.get() else simpledialog.askstring("Input", "Enter the name for this area:")
                
                if area_name is not None:
                    cv2.rectangle(img, point1, point2, (0, 255, 0), 2)
                    # Draw diagonal lines
                    cv2.line(img, point1, point2, (0, 255, 0), 1)
                    cv2.line(img, (point1[0], point2[1]), (point2[0], point1[1]), (0, 255, 0), 1)
                    img_changed = True
                
                    frame_count += 1
                    
                    areas.append({
                        'name': area_name,
                        'coordinates': [point1, point2]
                    })
                    text_box.insert(tk.END, f"{area_name}: {point1} - {point2}\n")
                    img_temp = img.copy()
            else:
                point1 = (x, y)
                drag = True
                img_temp = img.copy()
        else:
            point1 = (x, y)
            drag = True
            img_temp = img.copy()

    elif event == cv2.EVENT_LBUTTONUP:
        if not center_click.get() or not center_size:
            point2 = (x, y)
            drag = False
            cv2.rectangle(img, point1, point2, (0, 255, 0), 2)
            # Draw diagonal lines
            cv2.line(img, point1, point2, (0, 255, 0), 1)
            cv2.line(img, (point1[0], point2[1]), (point2[0], point1[1]), (0, 255, 0), 1)
            img_changed = True
            
            frame_count += 1
            area_name = f"Frame_{frame_count}" if auto_name.get() else simpledialog.askstring("Input", "Enter the name for this area:")
            
            if area_name:
                areas.append({
                    'name': area_name,
                    'coordinates': [point1, point2]
                })
                text_box.insert(tk.END, f"{area_name}: {point1} - {point2}\n")
                img_temp = img.copy()
                if center_click.get():
                    center_size = (point2[0] - point1[0], point2[1] - point1[1])
            else:
                img = img_temp.copy()

    elif event == cv2.EVENT_MOUSEMOVE and drag:
        img_temp_drag = img_temp.copy()
        cv2.rectangle(img_temp_drag, point1, (x, y), (0, 255, 0), 2)
        # Draw diagonal lines while drawing the rectangle
        cv2.line(img_temp_drag, point1, (x, y), (0, 255, 0), 1)
        cv2.line(img_temp_drag, (point1[0], y), (x, point1[1]), (0, 255, 0), 1)
        img = img_temp_drag
        img_changed = True

    if img_changed:
        cv2.imshow("image", img)
        


def import_image():
    global img, areas, file_path, img_temp, reopen_window, img_original
    areas = []  # Reset areas
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")])



    if not file_path:
        return

    # Use PIL to read the image
    try:
        pil_image = Image.open(file_path)
        img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Failed to load image: {e}")
        return
    
    img_temp = img.copy()
    img_original = img.copy()
    height, width, _ = img.shape
    text_box.insert(tk.END, f"Image: {os.path.basename(file_path)}, Resolution: {width}x{height}\n")

    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_event)
    reopen_window = True

    while reopen_window:
        cv2.imshow("image", img)
        if cv2.waitKey(1) == 27:  # 27 is the ESC key
            break
        if cv2.getWindowProperty('image', cv2.WND_PROP_VISIBLE) < 1: 
            break

    cv2.destroyAllWindows()
    reopen_window = False


def save_coordinates():
    save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if not save_path:
        return
    with open(save_path, "w") as f:
        for area in areas:
            f.write(f"{area['name']}: {area['coordinates']}\n")
    print(f"Coordinates have been saved to '{save_path}'.")
    
def save_as_gif():
    global areas, img_temp, img_original 

    if not areas or img_original is None:
        print("No areas to save or image is not loaded.")
        return

    # Ask for the preferred FPS
    fps = simpledialog.askinteger("Input", "Enter the preferred FPS:")
    if fps is None:
        return
    duration = int(1000 / fps)  # Duration for each frame in milliseconds

    # Convert the OpenCV image to PIL format for easy slicing and GIF creation
    img_rgb = cv2.cvtColor(img_original, cv2.COLOR_BGR2RGB)  # Use img_original here
    pil_img = Image.fromarray(img_rgb)

    frames = []
    for area in areas:
        x1, y1 = area['coordinates'][0]
        x2, y2 = area['coordinates'][1]
        frame = pil_img.crop((x1, y1, x2, y2))  # Crop the image to create the frame
        frames.append(frame)

    # Open save dialog to select GIF location
    save_path = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF files", "*.gif"), ("All files", "*.*")])
    if not save_path:
        return

    # Save frames as a GIF
    frames[0].save(save_path, save_all=True, append_images=frames[1:], loop=0, duration=duration)
    print(f"Saved GIF to {save_path}.")
    

def reset_application():
    global areas, img, img_temp, text_box, frame_count, center_size
    areas = []
    if img_temp is not None:
        img = img_temp.copy()
    text_box.delete(1.0, tk.END)
    frame_count = 0
    center_size = ()
    print("Application state has been reset.")


# GUI setup
root = tk.Tk()
root.title("Image Coordinate Finder")

# Initialize Tkinter variables here
auto_name = IntVar()
center_click = IntVar()
center_size = ()
frame_count = 0

frame = Frame(root)
frame.grid(row=0, column=0, columnspan=4, pady=5)

scrollbar = Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_box = Text(frame, height=10, width=50, yscrollcommand=scrollbar.set)
text_box.pack(side=tk.LEFT, fill=tk.BOTH)

scrollbar.config(command=text_box.yview)

import_button = Button(root, text="Import Image", command=import_image)
import_button.grid(row=1, column=0, pady=5)

auto_name_check = Checkbutton(root, text="Auto-name", variable=auto_name)
auto_name_check.grid(row=1, column=1, pady=5)

center_click_check = Checkbutton(root, text="Center Click", variable=center_click)
center_click_check.grid(row=1, column=2, pady=5)

save_button = Button(root, text="Save Coordinates", command=save_coordinates)
save_button.grid(row=2, column=0, pady=5)

save_gif_button = Button(root, text="Save as GIF", command=save_as_gif)
save_gif_button.grid(row=2, column=1, pady=5)

reset_button = Button(root, text="Reset", command=reset_application)
reset_button.grid(row=2, column=2, pady=5)

root.mainloop()
