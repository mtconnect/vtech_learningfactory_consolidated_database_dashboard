import tkinter as tk
from tkinter import ttk

class DeviceSelectionWindow:
    def __init__(self, devices_with_urls):
        self.selected_devices = None
        self.devices_with_urls = devices_with_urls
        self.checkboxes_vars = {}  # Maps (device_uuid, url) tuples to BooleanVars
        self.root = tk.Tk()
        self.root.title("Device Selection")
        self.setup_ui()

    def setup_ui(self):
        self.root.geometry("600x600")  # Set the window to a perfect square
        self.root.configure(bg='#0C5686')  # Set background color to dark blue

        # Add a title label with updated font and size
        title_label = tk.Label(self.root, text="Please select device(s).", fg="white", bg="#0C5686",
                               font=("Trebuchet MS", 18))
        title_label.pack(pady=(10, 18))

        # Frame for checkboxes to ensure they align nicely
        checkbox_frame = tk.Frame(self.root, bg='#0C5686')
        checkbox_frame.pack(padx=10, pady=10)

        # Generate checkboxes for each device with updated font, size, and color
        for (device, url) in self.devices_with_urls:
            var = tk.BooleanVar()
            device_uuid = device['uuid']  # Assuming 'uuid' is a key in each device dict
            device_name = device['name']  # Assuming 'name' is a key in each device dict

            # Use a (device_uuid, url) tuple as the key
            self.checkboxes_vars[(device_uuid, url)] = var

            # Checkbox with device name and UUID with updated font and size
            chk = tk.Checkbutton(checkbox_frame, text=f"{device_name}: {device_uuid}", variable=var,
                                 fg="white", bg="#0C5686", selectcolor="grey",
                                 activebackground="#0C5686", activeforeground="white",
                                 font=("Trebuchet MS", 18))
            chk.pack(anchor='w')

        # Submit button with updated font and size
        submit_btn = ttk.Button(self.root, text="Submit", command=self.on_submit, style='my.TButton')
        submit_btn.pack(pady=10)

        # Configuring the button style for consistency
        style = ttk.Style()
        style.configure('my.TButton', font=('Trebuchet MS', 18), background='#0C5686')

    def on_submit(self):
        self.selected_devices = [device_with_url for device_with_url, var in self.checkboxes_vars.items() if var.get()]
        self.root.destroy()

    def get_selected_devices(self):
        return self.selected_devices

    def show_window(self):
        self.root.mainloop()
