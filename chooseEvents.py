import tkinter as tk
from tkinter import ttk
import sqlite3
from sqlite3 import Error
import sched
import time
import mysql.connector
from mysql.connector import Error


def get_component_id(self, url, device_uuid, component_name):
    namespace = self.get_namespaces(url)
    root = self.get_root(url)
    if root is not None:
        # Find the ComponentStream element with the matching name attribute
        ns = namespace  # Use the namespace dictionary obtained from get_namespaces
        xpath = f".//m:DeviceStream[@uuid='{device_uuid}']/m:ComponentStream[@name='{component_name}']"
        component_stream = root.find(xpath, ns)
        if component_stream is not None:
            return component_stream.attrib.get('componentId')
    return None


class EventWindow:
    def __init__(self, selected_streams, extractor):
        self.end_time = None
        self.s = None
        self.duration = None
        self.frequency = None
        self.duration_entry = None
        self.freq_entry = None
        self.freq_label = None
        self.add_to_db_checkbox = None
        self.add_to_db_var = None
        self.duration_label = None
        self.selected_streams = selected_streams
        self.extractor = extractor
        self.selected_events = []
        self.checkboxes_vars = {}

        self.root = tk.Tk()
        self.root.title("Select Events")
        self.root.configure(bg='#0C5686')

    def show_window(self):
        container = ttk.Frame(self.root)
        container.pack(fill='both', expand=True)
        canvas = tk.Canvas(container, bg='#0C5686')
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#0C5686')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for url, device_uuid, stream in self.selected_streams:
            events = self.extractor.get_events_and_samples(url, device_uuid,
                                                           self.extractor.get_component_id(url, device_uuid, stream))
            stream_label = tk.Label(scrollable_frame, text=f"{stream} - Data Points:", fg="white", bg='#0C5686',
                                    font=("Trebuchet MS", 20))
            stream_label.pack(anchor='w', pady=5)

            for event_dict in events['events'] + events['samples']:
                var = tk.BooleanVar()
                chk = tk.Checkbutton(scrollable_frame, text=event_dict['dataItemId'] + ": " + event_dict['name'],
                                     variable=var, fg="white", bg='#0C5686',
                                     selectcolor="grey", activebackground='#0C5686', font=("Trebuchet MS", 20))
                chk.pack(anchor='w')
                self.checkboxes_vars[
                    (url, device_uuid, stream, event_dict['name'], event_dict['value'], event_dict['timestamp'])] = var

        self.add_to_db_var = tk.BooleanVar()
        self.add_to_db_checkbox = tk.Checkbutton(
            self.root,
            text="Add selected events and samples to a database?",
            variable=self.add_to_db_var,
            fg="white",
            bg='#0C5686',
            selectcolor="grey",
            activebackground='#0C5686',
            font=("Trebuchet MS", 20)
        )
        self.add_to_db_checkbox.pack(anchor='w')

        self.freq_label = tk.Label(self.root, text="Data collection frequency (sec):", fg="white", bg='#0C5686',
                                   font=("Trebuchet MS", 20))
        self.freq_label.pack(anchor='w')
        self.freq_entry = tk.Entry(self.root, font=("Trebuchet MS", 20))
        self.freq_entry.pack(anchor='w')

        self.duration_label = tk.Label(self.root, text="Data collection duration (sec):", fg="white", bg='#0C5686',
                                       font=("Trebuchet MS", 20))
        self.duration_label.pack(anchor='w')
        self.duration_entry = tk.Entry(self.root, font=("Trebuchet MS", 20))
        self.duration_entry.pack(anchor='w')

        style = ttk.Style()
        style.configure('SubmitButton.TButton', font=('Trebuchet MS', 20), background='#0C5686')

        submit_btn = ttk.Button(self.root, text="Submit", command=self.on_submit, style='SubmitButton.TButton')
        submit_btn.pack(pady=10)

        self.root.mainloop()

    def on_submit(self):
        # Fetch the frequency and duration input from the user
        try:
            self.frequency = int(self.freq_entry.get())
            self.duration = int(self.duration_entry.get())  # Fetching duration
        except ValueError:
            print("Please enter valid integers for the frequency and duration.")
            return

        # Get selected events and add them to the list
        for (url, device_uuid, stream, event_name, event_value, timestamp), var in self.checkboxes_vars.items():
            if var.get():
                self.selected_events.append((device_uuid, stream, event_name, event_value, timestamp))

        # Check if the 'Add to database' option is selected
        if self.add_to_db_var.get():
            self.add_events_to_database(self.selected_events)

        # Schedule data fetching if a valid frequency and duration are provided
        if self.frequency > 0 and self.duration > 0:
            self.s = sched.scheduler(time.time, time.sleep)
            self.s.enter(self.frequency, 1, self.fetch_data, (self.s,))
            self.end_time = time.time() + self.duration  # Calculate end time
            self.s.run()  # This starts the scheduling loop

        self.root.destroy()

    def get_selected_events(self):
        return self.selected_events

    def add_events_to_database(self, events):
        db_file = 'example.db'  # Name of the SQLite database file
        try:
            connection = sqlite3.connect(db_file)
            cursor = connection.cursor()

            # Loop through each event to ensure the table exists and insert the data
            for event in events:
                table_name = event[1] + '' + event[2]  # Assuming event[2] is the event name from your tuple

                # Create table if it does not exist
                create_table_query = f"""
                        CREATE TABLE IF NOT EXISTS `{table_name}` (
                            id INTEGER PRIMARY KEY,
                            data_item_id TEXT,
                            timestamp TEXT,
                            value TEXT
                        );
                        """
                cursor.execute(create_table_query)

                # Insert the data
                insert_query = f"""
                        INSERT INTO `{table_name}` (data_item_id, timestamp, value)
                        VALUES (?, ?, ?);
                        """
                # Assuming event structure matches the required values
                print(event)
                print("Inserting to table " + str(event[0]) + ', ' + str(event[4]) + ', ' + str(event[3]))
                cursor.execute(insert_query, (event[0], event[4], event[3]))  # Modify as needed

            connection.commit()
        except Error as e:
            print("Error while connecting to SQLite", e)
        finally:
            if connection:
                connection.close()

    def fetch_data(self, sc):
        current_time = time.time()
        if current_time < self.end_time:
            # Code to fetch data goes here. After fetching, push it into the database.
            print("Fetching data...")
            self.add_events_to_database(
                self.selected_events)  # Assuming fetched data is formatted similarly to self.selected_events
            # self.add_events_to_my_sql_database
            # Reschedule the event
            sc.enter(self.frequency, 1, self.fetch_data, (sc,))
        else:
            print("Data collection duration has ended.")

    '''
    Alternate function for MySQL database
    '''
    def add_events_to_mysql_database(self, events):
        db_config = {
            # enter info here
        }
        try:
            connection = mysql.connector.connect(**db_config)
            if connection.is_connected():
                cursor = connection.cursor()

                for event in events:
                    table_name = f"{event[1]}_{event[2]}"  # Adjusted for MySQL table naming conventions

                    # MySQL requires backticks for table names that might conflict with reserved keywords
                    create_table_query = f"""
                            CREATE TABLE IF NOT EXISTS `{table_name}` (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                data_item_id VARCHAR(255),
                                timestamp VARCHAR(255),
                                value VARCHAR(255)
                            ) ENGINE=InnoDB;
                            """
                    cursor.execute(create_table_query)

                    insert_query = f"""
                            INSERT INTO `{table_name}` (data_item_id, timestamp, value)
                            VALUES (%s, %s, %s);
                            """
                    cursor.execute(insert_query, (event[0], event[4], event[3]))

                connection.commit()
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

    '''
    Alternate function to create the Learning Factory database. 
    The LF database will need to collect historical data because 
    the machines are not constantly running live. Also, to be compatible
    with work of other teammates. The tables need to be organized by machine 
    and include all selected events. In my opinion, this setup is not as extensible
    as the other approach (one table for each datapoint and its timestamp) because
    the data desired may vary by machine.
    '''
    def add_events_to_mysql_LF_database(self, events):
        pass