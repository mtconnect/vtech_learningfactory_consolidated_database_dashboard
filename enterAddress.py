import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class AddressBook:
    def __init__(self):
        self.addresses = []

    def add_address(self, address):
        if address and address not in self.addresses:
            self.addresses.append(address)

    def get_addresses(self):
        return self.addresses


class AddressEntryWindow:
    def __init__(self, address_book):
        self.address_book = address_book

    def show(self):
        def add_ip():
            ip_address = ip_entry.get()
            if ip_address:
                ip_list.insert(tk.END, ip_address)
                self.address_book.add_address(ip_address)
                ip_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Warning", "Please enter a valid IP address or website.")

        def done():
            root.destroy()

        root = tk.Tk()
        root.title("IP and Website Input")
        root.configure(bg='#0C5686')
        root.geometry("600x600")

        style = ttk.Style()
        style.configure('My.TButton', font=('Trebuchet MS', 18))

        label = tk.Label(root, text="Welcome! Please enter a web address", font=("Trebuchet MS", 18), fg='white',
                         bg='#0C5686')
        label.pack(pady=(10, 5))

        frame = tk.Frame(root, bg='#0C5686')
        frame.pack(padx=10, pady=10)

        ip_entry = tk.Entry(frame, width=30, font=("Trebuchet MS", 18), bg="white", fg="black")
        ip_entry.pack(side=tk.LEFT, padx=(0, 10))

        add_button = tk.Button(frame, text="+", font=("Trebuchet MS", 18), command=add_ip, bg="#0C5686", fg="white")
        add_button.pack(side=tk.LEFT)

        ip_list = tk.Listbox(root, width=80, height=10, font=("Trebuchet MS", 18), bg="#0C5686", fg="white")
        ip_list.pack(padx=10, pady=(0, 10))

        done_button = ttk.Button(root, text="Submit", command=done, style='My.TButton')
        done_button.pack(pady=(10, 0))

        root.mainloop()
