import cv2
import tkinter as tk
from tkinter import simpledialog, filedialog

coordinates = []
drag = False
point1 = ()
point2 = ()
areas = []

def click_event(event, x, y, flags, param):
    global drag, point1, point2, areas
    if event == cv2.EVENT_LBUTTONDOWN:
        point1 = (x, y)
        drag = True

    elif event == cv2.EVENT_LBUTTONUP:
        point2 = (x, y)
        drag = False
        cv2.rectangle(img, point1, point2, (0, 255, 0), 2)
        cv2.imshow("image", img)
        
        root = tk.Tk()
        root.withdraw()
        area_name = simpledialog.askstring("Input", "Enter the name for this area:")
        
        if area_name:
            areas.append({
                'name': area_name,
                'coordinates': [point1, point2]
            })
            print(f"Area added: {area_name} with coordinates {point1} and {point2}")

def import_image():
    global img, areas
    areas = []  # Reset areas
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("JPG files", "*.jpg"), ("All files", "*.*")])

    if not file_path:
        return

    img = cv2.imread(file_path)
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_event)

    while True:
        cv2.imshow("image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

    with open("coordinates.txt", "w") as f:
        for area in areas:
            f.write(f"{area['name']}: {area['coordinates']}\n")

    print("Coordinates have been saved to 'coordinates.txt'.")

# Import button
while True:
    print("Press 'i' to import an image, 'q' to quit.")
    key = input()
    if key == 'i':
        import_image()
    elif key == 'q':
        break
