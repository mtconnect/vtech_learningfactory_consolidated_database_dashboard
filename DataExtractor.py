from io import BytesIO

import requests
import xml.etree.ElementTree as ET


class DataExtractor:
    def __init__(self, urls):
        self.urls = urls

    def get_namespaces(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            # Find the namespace URI (assumes the default namespace is used for the document)
            namespaces = dict([node for _, node in ET.iterparse(BytesIO(response.content), events=['start-ns'])])
            return namespaces  # This returns a dictionary of namespaces

    def get_root(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            # Directly parse the XML content
            root = ET.fromstring(response.content)
            return root
        return None

    def get_devices(self, url):
        namespace = self.get_namespaces(url)
        root = self.get_root(url)
        devices = []
        if root is not None:
            # Adjust XPath to use namespace correctly
            for device_stream in root.findall('.//m:DeviceStream', namespace):
                devices.append({
                    'uuid': device_stream.attrib['uuid'],
                    'name': device_stream.attrib['name']
                })
        return devices

    def get_first_timestamp(self, url):
        namespace = self.get_namespaces(url)
        root = self.get_root(url)
        if root:
            for device_stream in root.findall('.//m:DeviceStream', namespace):
                for timestamp in device_stream.findall('.//*[@timestamp]', namespace):
                    return timestamp.attrib['timestamp']
        return None

    def get_all_latest_samples(self, url):
        namespace = self.get_namespaces(url)
        root = self.get_root(url)
        latest_samples = {}
        if root is not None:
            # Ensure namespace is correctly used in XPath
            ns = namespace  # Use the namespace dictionary obtained from get_namespaces
            for sample in root.findall('.//m:Samples/*', ns):
                dataItemId = sample.attrib['dataItemId']
                timestamp = sample.attrib['timestamp']
                value = sample.text
                # Using dataItemId as the key, store a tuple of (timestamp, value)
                latest_samples[dataItemId] = (timestamp, value)
        return latest_samples

    def get_component_streams(self, url, device_uuid):
        namespace = self.get_namespaces(url)
        root = self.get_root(url)
        if root is not None:
            ns = namespace  # {'m': namespace[1:-1]}  # adjust based on actual namespace URI
            device_stream = root.find(f'.//m:DeviceStream[@uuid="{device_uuid}"]', ns)
            if device_stream is not None:
                component_streams = device_stream.findall('.//m:ComponentStream', ns)
                return [comp.attrib for comp in component_streams]
        return []

    def get_events_and_samples(self, url, device_uuid, component_id):
        """
            Extracts detailed information about all events and samples for a specific device and component stream.

            :param url: The URL of the MTConnect data source.
            :param device_uuid: The UUID of the device.
            :param component_id: The ID of the component stream.
            :return: A dictionary with two keys, 'events' and 'samples', each containing a list of detailed dictionaries for each event and sample.
            """
        namespace = self.get_namespaces(url)['m']
        root = self.get_root(url)
        if root is None:
            return {'events': [], 'samples': []}

        events_and_samples = {'events': [], 'samples': []}
        xpath_base = f".//m:DeviceStream[@uuid='{device_uuid}']/m:ComponentStream[@componentId='{component_id}']"
        events_xpath = f"{xpath_base}/m:Events/*"
        samples_xpath = f"{xpath_base}/m:Samples/*"

        # Extract Events
        for event in root.findall(events_xpath, namespaces={'m': namespace}):
            event_details = {
                'name': event.tag.split('}')[-1],  # Get the tag name without namespace
                'dataItemId': event.get('dataItemId'),
                'sequence': event.get('sequence'),
                'timestamp': event.get('timestamp'),
                'value': event.text
            }
            events_and_samples['events'].append(event_details)

        # Extract Samples
        for sample in root.findall(samples_xpath, namespaces={'m': namespace}):
            sample_details = {
                'name': sample.tag.split('}')[-1],  # Get the tag name without namespace
                'dataItemId': sample.get('dataItemId'),
                'sequence': sample.get('sequence'),
                'timestamp': sample.get('timestamp'),
                'value': sample.text
            }
            events_and_samples['samples'].append(sample_details)

        return events_and_samples

    def get_component_id(self, url, device_uuid, component_name):
        """
        Retrieves the componentId for a specified component of a device.

        :param url: The URL of the MTConnect data source.
        :param device_uuid: The UUID of the device.
        :param component_name: The name of the component to find the ID for.
        :return: The componentId as a string or None if not found.
        """
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
