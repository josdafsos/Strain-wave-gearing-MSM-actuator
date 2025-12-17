# serial_controller_simple.py
import re
import serial
import time
from serial.tools import list_ports
from logic.parameters import input_sync


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
        self.start_message = ["hello world", "control"]  # Expected device startup messages
        self.app = app

        self.last_message = ""  # Last complete message received from device
        self.values = {}        # Dictionary to store parsed parameter values

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
            ports = [p for p in ports if "usb" in p.subsystem.lower()]
        elif self.app.system == "Windows":
            ports = [p for p in ports if "com" in p.name.lower()]
        else:
            self.app.show_message("System not known, all ports scanned.")

        if not ports:
            self.app.show_message("No board identifier found. Scanning all ports.")

        # Move preferred port to the top of the list
        if tentative_port:
            for i, p in enumerate(ports):
                if p.device == tentative_port:
                    ports.insert(0, ports.pop(i))
                    break

        # Attempt to connect to each port
        for port in ports:
            try:
                self.app.show_message("⏳ Trying to connect to " + port.device)
                self.serial_connection = serial.Serial(port.device, self.baud_rate, timeout=1)
                time.sleep(0.5)
                self.write("Dummy_Text", False) # Send dummy message
                response = self.read(20)  # Read device response (Wait for 10s)
                for tentative_start_message in self.start_message:
                    if tentative_start_message in response.lower(): # Check if the expected answer is in the answer message
                        self.app.show_message(f"✅ Device found on: {port.device}")
                        self.write("Dummy_Text", False)  # Send dummy command to get the current controller values
                        self.read(10)  # Read device response and update last_message
                        self.sync_values()
                        return 
                self.serial_connection.close()
            except Exception:
                self.serial_connection = None
                continue

        self.app.show_message("❌ No device found!")
        return None

    # -------------------- Writing --------------------
    def write(self, message, auto_split: bool =True, commands_per_group=6):
        """
        Sends commands to the device in groups and reads responses after each group.

        Args:
            auto_split: Automatically split the messages into groups.
            message: Semi-colon-separated command string to send.
            commands_per_group: Number of commands sent in one batch.
        """

        if auto_split:
            commands = [cmd.strip() for cmd in message.split(";") if cmd.strip()]
            if not commands:
                self.app.show_message("No commands found!")
                return

            for i in range(0, len(commands), commands_per_group):
                group = ";".join(commands[i:i + commands_per_group]) + ";"
                # Send batch of commands
                self.serial_connection.write(group.encode())

                # Show sent commands in serial monitor if exists
                if getattr(self.app, "serial_monitor", None):
                    self.app.serial_monitor.add_text(f">>> {group}", True)

                self.read() # Read the controller answer after each send

        else:
            self.serial_connection.write(message.encode())


    # -------------------- Reading --------------------
    def read(self, timeout=60):
        """
        Reads from the serial buffer until a complete message arrives or the timeout expires.

        Args:
            timeout: Maximum time in seconds to wait for a complete message.

        Returns:
            str: The last complete message received.
        """
        buffer = b""
        final_message_key = b""
        start_time = time.time()

        # This loop will loop will keep reading the buffer until the end of the message is detected (final_message_key) or the timeout expires.
        while time.time() - start_time < timeout:

            buffer += self.serial_connection.read_all()

            if b"\n\n" in buffer: # Real board
                final_message_key = b"\n\n"
            # The emulator conditions will be delated when no longer needed
            elif b"\r\n\r\n" in buffer: # Board emulator
                final_message_key = b"\r\n\r\n"
            elif b'Hello world\r\n' in buffer: # Board emulator - starting message
                self.last_message = "Hello world"
                return self.last_message

            # Check if a complete message is in the buffer
            if final_message_key:
                msg, buffer = buffer.split(final_message_key, 1)
                msg_decoded = msg.decode().strip()
                if msg_decoded:
                    self.last_message = msg_decoded
                    self.sync_values()  # Parse and update internal values

                    # Display message in the serial monitor if it exists
                    if getattr(self.app, "serial_monitor", None):
                        self.app.serial_monitor.add_text(msg_decoded)

                    return self.last_message
            time.sleep(0.01)  # Avoid blocking CPU too much

        if not buffer:
            self.app.show_message("⚠️ No message received!")
        else:
            self.app.show_message("⚠️ Timeout: incomplete message from device")
        return self.last_message

    # -------------------- Update values --------------------
    def sync_values(self, print_flag=False):
        """
        Parses the last message from the device and updates the internal values dictionary.

        Args:
            print_flag: If True, prints the parsed response.
        """
        response = self.last_message
        if print_flag:
            self.app.show_message("Parsing response:\n", response)

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
                    # str_to_write = f"{val_to_write:.3f}".replace(".", ",") # For float commands
                    str_to_write = str(int(val_to_write)) # For integer commands
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
