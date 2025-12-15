# serial_controller_simple.py
import re
import serial
import time
from serial.tools import list_ports
from logic.parameters import input_sync
from ui.serial_monitor import SerialMonitor


class SerialController:
    def __init__(self, app, tentative_port=None):
        """
        Initializes the serial controller for communication with the device.

        Args:
            app: Reference to the main app containing values, parameters, and serial monitor.
            tentative_port: Optional preferred port to try first.
        """
        self.serial_connection = None  # Serial connection object
        self.baud_rate = 115200        # Standard baud rate for communication
        self.start_message = ["hello world", "= 0"]  # Expected device startup messages
        self.app = app

        self.last_message = ""  # Last complete message received from device
        self.values = {}        # Dictionary to store parsed parameter values

    # -------------------- Reading --------------------
    def read(self, timeout=2):
        """
        Reads from the serial buffer until a complete message arrives or the timeout expires.

        Args:
            timeout: Maximum time in seconds to wait for a complete message.

        Returns:
            str: The last complete message received.
        """
        buffer = b""
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.serial_connection.in_waiting:
                buffer += self.serial_connection.read(self.serial_connection.in_waiting)

            # Check if a complete message is in the buffer
            if b"\r\n\r\n" in buffer:
                msg, buffer = buffer.split(b"\r\n\r\n", 1)
                msg_decoded = msg.decode().strip()
                if msg_decoded:
                    self.last_message = msg_decoded
                    self.sync_values()  # Parse and update internal values

                    # Display message in the serial monitor if it exists
                    if getattr(self.app, "serial_monitor", None):
                        self.app.serial_monitor.add_text(msg_decoded)

                    return self.last_message
            time.sleep(0.01)  # Avoid blocking CPU too much

        print("⚠️ Timeout: incomplete message from device")
        return self.last_message

    # -------------------- Writing --------------------
    def write(self, message, commands_per_group=4):
        """
        Sends commands to the device in groups and reads responses after each group.

        Args:
            message: Semi-colon-separated command string to send.
            commands_per_group: Number of commands sent in one batch.
        """
        commands = [cmd.strip() for cmd in message.split(";") if cmd.strip()]
        if not commands:
            print("No commands found!")
            return

        for i in range(0, len(commands), commands_per_group):
            group = ";".join(commands[i:i + commands_per_group]) + ";"
            # Send batch of commands
            self.serial_connection.write(group.encode())

            # Show sent commands in serial monitor if exists
            if getattr(self.app, "serial_monitor", None):
                self.app.serial_monitor.add_text(f">>> {group}")

            self.read()  # Read device response and update last_message

    # -------------------- Connection --------------------
    def connect_to_device(self, tentative_port=None):
        """
        Attempts to detect and connect to the serial device automatically.

        Args:
            tentative_port: Preferred port to try first.

        Returns:
            Serial object if connected, else None.
        """
        ports = list_ports.comports()

        # Filter ports based on OS
        if self.app.system == "Linux":
            key = "usb"
        elif self.app.system == "Windows":
            key = "com"
        else:
            print("System not known")
            key = ""

        if key:
            ports = [p for p in ports if key in p.description.lower()]

        # Move preferred port to the top of the list
        if tentative_port:
            for i, p in enumerate(ports):
                if p.device == tentative_port:
                    ports.insert(0, ports.pop(i))
                    break

        # Attempt to connect to each port
        for port in ports:
            try:
                serial_conn = serial.Serial(port.device, self.baud_rate, timeout=1)
                time.sleep(1)
                serial_conn.write(b"ping\n")

                start_time = time.time()
                while time.time() - start_time < 3:  # 3-second timeout
                    response = serial_conn.read_all().decode().strip().lower()
                    for tentative_start_message in self.start_message:
                        if tentative_start_message in response:
                            self.app.show_message(f"✅ Device found on: {port.device}")
                            self.serial_connection = serial_conn
                            self.write("Dummy_Text")  # Send dummy command to sync
                            self.sync_values()
                            return serial_conn
                serial_conn.close()
            except Exception:
                continue

        self.app.show_message("❌ No device found!")
        return None

    # -------------------- Update values --------------------
    def sync_values(self, print_flag=False):
        """
        Parses the last message from the device and updates the internal values dictionary.

        Args:
            print_flag: If True, prints the parsed response.
        """
        response = self.last_message
        if print_flag:
            print("Parsing response:\n", response)

        # Loop through all coils and parameters to extract values
        for coil_id in range(self.app.in_columns):
            for parameter_id in range(len(self.app.parameters_acr)):
                str_to_find = f"({self.app.parameters_acr[parameter_id]}{coil_id+1}) = "
                pattern = re.escape(str_to_find) + r"([-+]?\d+(?:,\d+)?)"
                match = re.search(pattern, response)
                if match:
                    tmp_string = match.group(1)
                    # Save value as integer (replace comma with dot if needed)
                    self.values[(coil_id, parameter_id)] = int(tmp_string.replace(",", "."))
                    self.app.values[(coil_id, parameter_id)] = self.values[(coil_id, parameter_id)]

        # Sync app UI entries and sliders
        input_sync(self.app)

    # -------------------- Write app values to device --------------------
    def app_to_controller(self):
        """
        Sends all app values that differ from the controller's current values to the device.
        """
        parts = []
        for coil_id in range(self.app.in_columns):
            for parameter_id in range(len(self.app.parameters_acr)):
                param = self.app.parameters_acr[parameter_id]
                val_to_write = self.app.values.get((coil_id, parameter_id), None)
                current_value = self.values.get((coil_id, parameter_id), None)
                if val_to_write != current_value:
                    str_to_write = f"{val_to_write:.3f}".replace(".", ",")
                    # Format command based on control method
                    if self.app.control_method == "Coil-based":
                        parts.append(f"{param}{coil_id + 1}={str_to_write}")
                    else:
                        parts.append(f"{param}={str_to_write}")

        if not parts:
            self.app.show_message("All values are already up to date!")
            return

        # Send all changed parameters to the device
        self.write(";".join(parts) + ";")
        input_sync(self.app)
        self.app.show_message("✅ Parameters sent and synchronized!")
