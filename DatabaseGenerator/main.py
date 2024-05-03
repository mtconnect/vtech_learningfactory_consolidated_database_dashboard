from enterAddress import AddressBook
from enterAddress import AddressEntryWindow
class DataExtractorApp:
    def __init__(self):
        self.address_book = AddressBook()
        self.urls = []
        self.extractor = None
        self.devices_with_urls = []
        self.selected_devices_with_urls = []
        self.selected_component_streams = []
        self.selected_events = []

    def fetch_addresses(self):
        address_entry_window = AddressEntryWindow(self.address_book)
        address_entry_window.show()
        self.urls = self.address_book.get_addresses()

    def create_data_extractor(self):
        from DataExtractor import DataExtractor
        self.extractor = DataExtractor(self.urls)

    def accumulate_devices(self):
        for url in self.urls:
            devices = self.extractor.get_devices(url)
            for device in devices:
                self.devices_with_urls.append((device, url))

    def show_device_selection_window(self):
        from chooseDevices import DeviceSelectionWindow
        device_selection_window = DeviceSelectionWindow(self.devices_with_urls)
        device_selection_window.show_window()
        self.selected_devices_with_urls = device_selection_window.get_selected_devices()

    def show_component_streams_window(self):
        from chooseComponentStreams import ComponentStreamsWindow
        if self.selected_devices_with_urls:
            component_streams_window = ComponentStreamsWindow(self.selected_devices_with_urls, self.extractor)
            component_streams_window.show_window()
            self.selected_component_streams = component_streams_window.get_selected_streams()

    def show_event_window(self):
        from chooseEvents import EventWindow
        if self.selected_component_streams:
            event_window = EventWindow(self.selected_component_streams, self.extractor)
            event_window.show_window()
            self.selected_events = event_window.get_selected_events()

    def run(self):
        self.fetch_addresses()
        self.create_data_extractor()
        self.accumulate_devices()
        self.show_device_selection_window()
        self.show_component_streams_window()
        self.show_event_window()

# Example usage
if __name__ == "__main__":
    app = DataExtractorApp()
    app.run()
