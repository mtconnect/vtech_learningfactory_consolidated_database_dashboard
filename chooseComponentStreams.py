import tkinter as tk
from tkinter import ttk

class ComponentStreamsWindow:
    def __init__(self, devices, extractor):
        self.devices = devices
        self.extractor = extractor
        self.selected_streams = []  # To store selections

        # Initialize the window
        self.root = tk.Tk()
        self.root.title("Component Streams")
        self.root.geometry("600x600")  # Make the window a perfect square
        self.root.configure(bg='#0C5686')  # Set background color to dark blue

    def show_window(self):
        container = ttk.Frame(self.root)
        container.pack(fill='both', expand=True)
        canvas = tk.Canvas(container, bg='#0C5686')
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#0C5686')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        checkboxes_vars = {}

        for device_tuple in self.devices:
            device_uuid, url = device_tuple[0], device_tuple[1]
            component_streams = self.extractor.get_component_streams(url, device_uuid)

            device_label = tk.Label(scrollable_frame, text=f"Device {device_uuid} - Component Streams:", fg="white",
                                    bg='#0C5686', font=("Trebuchet MS", 18))
            device_label.pack(anchor='w', pady=5)

            for stream in component_streams:
                stream_name = f"{device_uuid}_{stream['name']}"
                var = tk.BooleanVar()

                text = stream['component'] + ' ' + stream['name'] if stream['name'].lower() != stream[
                    'component'].lower() else stream['component']

                chk = tk.Checkbutton(scrollable_frame, text=text, variable=var, fg="white", bg='#0C5686',
                                     selectcolor="grey", activebackground="#0C5686", activeforeground="white",
                                     font=("Trebuchet MS", 18))
                chk.pack(anchor='w')
                checkboxes_vars[stream_name] = (var, url, device_uuid, stream['name'])

        submit_btn = ttk.Button(self.root, text="Submit", command=lambda: self.on_submit(checkboxes_vars), style='My.TButton')
        submit_btn.pack(pady=10)

        style = ttk.Style()
        style.configure('My.TButton', font=('Trebuchet MS', 18), background='#0C5686')

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.root.mainloop()

    def on_submit(self, checkboxes_vars):
        for stream_id, (var, url, device_uuid, stream_id) in checkboxes_vars.items():
            if var.get():  # If the checkbox is selected
                self.selected_streams.append((url, device_uuid, stream_id))
        self.root.destroy()

    def get_selected_streams(self):
        return self.selected_streams
