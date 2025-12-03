# serial_controller_simple.py
import re
import serial
import time
from serial.tools import list_ports
from logic.parameters import input_sync
from ui.serial_monitor import SerialMonitor


class SerialController:
    def __init__(self, app, tentative_port=None):
        self.serial_connection = None
        self.baud_rate = 115200
        self.start_message = "hello world"
        self.app = app

        # Last complete message received
        self.last_message = ""
        self.values = {}

    # -------------------- Reading --------------------
    def read(self, timeout=2):
        """Reads from the serial buffer until a complete message arrives or the timeout expires"""
        buffer = b""
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.serial_connection.in_waiting:
                buffer += self.serial_connection.read(self.serial_connection.in_waiting)

            if b"\r\n\r\n" in buffer:
                msg, buffer = buffer.split(b"\r\n\r\n", 1)
                msg_decoded = msg.decode().strip()
                if msg_decoded:
                    self.last_message = msg_decoded
                    self.sync_values()
                    if getattr(self.app, "serial_monitor", None):
                        self.app.serial_monitor.add_text(msg_decoded)

                    return self.last_message
            time.sleep(0.01)  # small delay to avoid blocking CPU

        print("⚠️ Timeout: incomplete message from device")
        return self.last_message

    # -------------------- Writing --------------------
    def write(self, message, commands_per_group=4):
        """Sends commands in groups, reads device response after each group"""
        commands = [cmd.strip() for cmd in message.split(";") if cmd.strip()]
        if not commands:
            print("No commands found!")
            return

        for i in range(0, len(commands), commands_per_group):
            group = ";".join(commands[i:i + commands_per_group]) + ";"
            # print("Sending:", group)
            self.serial_connection.write(group.encode())

            if getattr(self.app, "serial_monitor", None):
                self.app.serial_monitor.add_text(f">>> {group}")

            self.read()  # reads and updates last_message

    # -------------------- Connection --------------------
    def connect_to_device(self, tentative_port=None):
        ports = list_ports.comports()

        if self.app.system == "Linux":
            key = "usb"
        elif self.app.system == "Windows":
            key = "com"
        else:
            print("System not known")
            key = ""

        if key:
            ports = [p for p in ports if key in p.description.lower()]

        # Preferred port moved to the top
        if tentative_port:
            for i, p in enumerate(ports):
                if p.device == tentative_port:
                    ports.insert(0, ports.pop(i))
                    break

        for port in ports:
            try:
                serial_conn = serial.Serial(port.device, self.baud_rate, timeout=1)
                time.sleep(1)
                serial_conn.write(b"ping\n")

                start_time = time.time()
                while time.time() - start_time < 3:  # 3-second timeout
                    response = serial_conn.read_all().decode().strip().lower()
                    if self.start_message in response:
                        self.app.show_message(f"✅ Device found on: {port.device}")
                        self.serial_connection = serial_conn
                        self.write("Dummy_Text")
                        self.sync_values()
                        return serial_conn
                serial_conn.close()
            except Exception:
                continue

        self.app.show_message("❌ No device found!")
        return None

    # -------------------- Update values --------------------
    def sync_values(self, print_flag=False):
        response = self.last_message
        if print_flag:
            print("Parsing response:\n", response)

        for coil_id in range(self.app.in_columns):
            for parameter_id in range(len(self.app.parameters_acr)):
                str_to_find = f"({self.app.parameters_acr[parameter_id]}{coil_id+1}) = "
                pattern = re.escape(str_to_find) + r"([-+]?\d+(?:,\d+)?)"
                match = re.search(pattern, response)
                if match:
                    tmp_string = match.group(1)
                    # Save as float
                    self.values[(coil_id, parameter_id)] = int(tmp_string.replace(",", "."))
                    self.app.values[(coil_id, parameter_id)] = self.values[(coil_id, parameter_id)]

        input_sync(self.app)

    # -------------------- Write app values to device --------------------
    def app_to_controller(self):
        parts = []
        for coil_id in range(self.app.in_columns):
            for parameter_id in range(len(self.app.parameters_acr)):
                param = self.app.parameters_acr[parameter_id]
                val_to_write = self.app.values.get((coil_id, parameter_id), None)
                current_value = self.values.get((coil_id, parameter_id), None)
                if val_to_write != current_value:
                    str_to_write = f"{val_to_write:.3f}".replace(".", ",")
                    if self.app.control_method == "Coil-based":
                        parts.append(f"{param}{coil_id + 1}={str_to_write}")
                    else:
                        parts.append(f"{param}={str_to_write}")
        if not parts:
            self.app.show_message("All values are already up to date!")
            return
        self.write(";".join(parts) + ";")
        input_sync(self.app)
        self.app.show_message("✅ Parameters sent and synchronized!")
