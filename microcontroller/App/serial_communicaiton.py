import serial
import serial.tools.list_ports
import time

def auto_detect_arduino(test_message="ping\n", timeout=1, baudrate=9600):
    ports = serial.tools.list_ports.comports()

    print("🔍 Scansione delle porte seriali in corso...\n")

    for port in ports:
        try:
            print(f"Provo la porta: {port.device}")
            ser = serial.Serial(port.device, baudrate, timeout=timeout)
            time.sleep(2)  # attesa reset Arduino

            ser.write(test_message.encode())   # invio messaggio
            time.sleep(0.2)
            response = ser.readline().decode(errors='ignore').strip()

            if response:
                print(f"\n✅ Arduino trovato sulla porta: {port.device}")
                print(f"📩 Risposta ricevuta: {response}\n")
                return ser  # ritorna l'oggetto deja aperto (pronto all'uso)

            ser.close()

        except Exception:
            pass

    print("\n❌ Nessuna risposta dalle porte seriali.")
    return None


# Esempio di utilizzo
if __name__ == "__main__":
    ser = auto_detect_arduino("ping\n")
    if ser:
        ser.write(b"hello arduino!\n")
