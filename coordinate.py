import cv2
import os
import tkinter as tk
from tkinter import simpledialog, filedialog, Text, Button, Scrollbar, Frame

drag = False
point1 = ()
point2 = ()
areas = []
img = None
img_temp = None
reopen_window = True

def click_event(event, x, y, flags, param):
    global drag, point1, point2, areas, img, img_temp
    img_changed = False

    if event == cv2.EVENT_LBUTTONDOWN:
        point1 = (x, y)
        drag = True
        img_temp = img.copy()

    elif event == cv2.EVENT_LBUTTONUP:
        point2 = (x, y)
        drag = False
        cv2.rectangle(img, point1, point2, (0, 255, 0), 2)
        img_changed = True
        
        root = tk.Tk()
        root.withdraw()
        area_name = simpledialog.askstring("Input", "Enter the name for this area:")
        
        if area_name:
            areas.append({
                'name': area_name,
                'coordinates': [point1, point2]
            })
            text_box.insert(tk.END, f"{area_name}: {point1} - {point2}\n")
            img_temp = img.copy()
        else:
            img = img_temp.copy()

    elif event == cv2.EVENT_MOUSEMOVE:
        if drag:
            img_temp_drag = img_temp.copy()
            cv2.rectangle(img_temp_drag, point1, (x, y), (0, 255, 0), 2)
            img = img_temp_drag
            img_changed = True

    if img_changed:
        cv2.imshow("image", img)

def import_image():
    global img, areas, file_path, img_temp, reopen_window
    areas = [] 
    file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("JPG files", "*.jpg"), ("All files", "*.*")])

    if not file_path:
        return

    original_dir = os.getcwd()
    os.chdir(os.path.dirname(file_path))
    img = cv2.imread(os.path.basename(file_path))
    os.chdir(original_dir) 

    img_temp = img.copy()
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

# GUI setup
root = tk.Tk()
root.title("Image Coordinate Finder")

frame = Frame(root)
frame.pack(pady=5)

scrollbar = Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_box = Text(frame, height=10, width=50, yscrollcommand=scrollbar.set)
text_box.pack(side=tk.LEFT, fill=tk.BOTH)

scrollbar.config(command=text_box.yview)

import_button = Button(root, text="Import Image", command=import_image)
import_button.pack(pady=5)

save_button = Button(root, text="Save Coordinates", command=save_coordinates)
save_button.pack(pady=5)

root.mainloop()
