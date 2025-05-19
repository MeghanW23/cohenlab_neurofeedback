import tkinter as tk
from PIL import Image, ImageTk, ImageGrab, ImageDraw
from AppKit import NSScreen
import pyautogui

def get_second_monitor_coords():
    # Get all screens using NSScreen
    screens = NSScreen.screens()
    
    if len(screens) < 2:
        print("No second monitor detected.")
        return None
    
    # Get the frame of the second monitor
    second_monitor = screens[1].frame()
    
    # Convert frame coordinates (AppKit uses a flipped Y-axis)
    primary_screen_height = screens[0].frame().size.height
    x = int(second_monitor.origin.x)
    y = int(primary_screen_height - second_monitor.origin.y - second_monitor.size.height)
    width = int(second_monitor.size.width)
    height = int(second_monitor.size.height)
    
    return (x, y, x + width, y + height)

def capture_second_monitor():
    # Get second monitor coordinates
    monitor_coords = get_second_monitor_coords()
    if monitor_coords is None:
        return None

    # Capture the screen area of the second monitor
    screenshot = ImageGrab.grab(bbox=monitor_coords)
    
    # Get the current mouse position
    mouse_x, mouse_y = pyautogui.position()
    
    # Check if the mouse is within the second monitor bounds
    if monitor_coords[0] <= mouse_x < monitor_coords[2] and monitor_coords[1] <= mouse_y < monitor_coords[3]:
        # Translate mouse coordinates relative to the second monitor
        relative_x = mouse_x - monitor_coords[0]
        relative_y = mouse_y - monitor_coords[1]
        
        # Draw the cursor on the screenshot
        draw = ImageDraw.Draw(screenshot)
        cursor_size = 20 
        draw.ellipse(
            (relative_x - cursor_size, relative_y - cursor_size,
             relative_x + cursor_size, relative_y + cursor_size),
            fill="red",  # Cursor color
            outline="black",
        )
    
    return screenshot

def update_canvas():
    # Capture the content of the second monitor
    screenshot = capture_second_monitor()
    if screenshot is None:
        return
    
    # Resize the screenshot to fit the canvas
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    resized_screenshot = screenshot.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
    
    # Convert the screenshot to a Tkinter image
    tk_image = ImageTk.PhotoImage(resized_screenshot)
    
    # Display the image on the canvas
    canvas.itemconfig(image_container, image=tk_image)
    canvas.image = tk_image  # Prevent garbage collection
    
    # Schedule the next update
    root.after(100, update_canvas)

# Create the main Tkinter window
root = tk.Tk()
root.title("Second Monitor Viewer")

# Get the second monitor's dimensions
monitor_coords = get_second_monitor_coords()
if monitor_coords is None:
    print("No second monitor detected. Exiting.")
    exit()

monitor_width = monitor_coords[2] - monitor_coords[0]
monitor_height = monitor_coords[3] - monitor_coords[1]
canvas_width = monitor_width // 4
canvas_height = monitor_height // 4

# Create a canvas to display the second monitor content
canvas = tk.Canvas(root, bg="black", width=canvas_width, height=canvas_height)
canvas.pack(fill=tk.BOTH, expand=True)

# Add an image container to the canvas
image_container = canvas.create_image(0, 0, anchor=tk.NW)

# Start updating the canvas
update_canvas()

# Start the Tkinter event loop
root.mainloop()
