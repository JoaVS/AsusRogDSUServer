import socket
import struct
import binascii
import asyncio
from winsdk.windows.devices.sensors import Gyrometer, Accelerometer

# Configuración del servidor DSU (Cemuhook)
UDP_IP = "127.0.0.1"
UDP_PORT = 26760

class DsuServer:
    def __init__(self):
        self.gyro = Gyrometer.get_default()
        self.accel = Accelerometer.get_default()
        if not self.gyro or not self.accel:
            print("[-] Error: No se detectaron los sensores físicos de la ROG Ally.")
            exit(1)
        
        # Configurar tasa de refresco de los sensores (en milisegundos)
        self.gyro.report_interval = max(self.gyro.minimum_report_interval, 16)
        self.accel.report_interval = max(self.accel.minimum_report_interval, 16)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"[+] Servidor DSU iniciado en {UDP_IP}:{UDP_PORT}")
        print("[+] Sensores de movimiento vinculados correctamente. Dejá esta ventana abierta.")

    def _create_packet(self, msg_type, payload):
        # Cabecera estándar del protocolo Cemuhook DSU
        magic = b'DSUS'
        protocol_version = 1001
        packet_len = len(payload) + 4
        # El espacio del checksum (4 bytes) inicialmente se llena con ceros
        header_without_crc = struct.pack('<4sHHI', magic, protocol_version, packet_len, 0)
        server_id = struct.pack('<I', 12345) # ID aleatorio del servidor
        
        full_packet = header_without_crc + server_id + msg_type + payload
        # Calcular CRC32 sobre todo el paquete y sustituir los bytes del espacio vacío
        crc = binascii.crc32(full_packet) & 0xffffffff
        return full_packet[:8] + struct.pack('<I', crc) + full_packet[12:]

    def get_motion_data(self):
        # Leer datos de los sensores de Windows
        g_reading = self.gyro.get_current_reading()
        a_reading = self.accel.get_current_reading()

        # En caso de lecturas nulas temporales, enviar ceros
        gx, gy, gz = (g_reading.angular_velocity_x, g_reading.angular_velocity_y, g_reading.angular_velocity_z) if g_reading else (0,0,0)
        ax, ay, az = (a_reading.acceleration_x, a_reading.acceleration_y, a_reading.acceleration_z) if a_reading else (0,0,0)

        # Conversión de unidades estándar a las esperadas por Cemuhook (Deg/s y Gs)
        # Nota: Ajustar los signos (-/+) si notas el eje invertido en el emulador
        gyro_data = struct.pack('<fff', gx, -gz, gy) 
        accel_data = struct.pack('<fff', ax, -az, ay)
        return accel_data + gyro_data

    def handle_request(self, data, addr):
        if len(data) < 20: return
        
        # Leer tipo de mensaje (Bytes 16-19)
        msg_type = data[16:20]

        if msg_type == b'\x00\x00\x10\x00': # Protocol Ports Request
            # Responder que tenemos un control en el Slot 0
            payload = struct.pack('<B BBBBB 4s I', 0, 2, 1, 1, 0, b'\x00\x00\x00\x00', 0)
            response = self._create_packet(b'\x00\x00\x10\x00', payload)
            self.sock.sendto(response, addr)

        elif msg_type == b'\x01\x00\x10\x00': # Data Request
            # Responder con la estructura completa de datos de movimiento
            # Slot 0, conectado, modelo regular
            slot_info = struct.pack('<BBBBBB', 0, 2, 1, 1, 0, 0)
            mac_address = b'\x00\x00\x00\x00\x00\x01'
            battery_status = b'\x05' # Completamente cargado
            
            # Datos de botones/sticks simulados en cero (Citra solo leerá la IMU de acá)
            controls_mock = bytes(12) 
            
            # Timestamp en microsegundos
            timestamp = struct.pack('<Q', 0) 
            motion = self.get_motion_data()

            payload = slot_info + mac_address + battery_status + controls_mock + timestamp + motion
            response = self._create_packet(b'\x01\x00\x10\x00', payload)
            self.sock.sendto(response, addr)

    async def start(self):
        self.sock.setblocking(False)
        loop = asyncio.get_running_loop()
        while True:
            try:
                data, addr = await loop.sock_recvfrom(self.sock, 1024)
                self.handle_request(data, addr)
            except Exception as e:
                pass
            await asyncio.sleep(0.008) # Mantiene la tasa cercana a los ~120Hz

if __name__ == "__main__":
    server = DsuServer()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\n[-] Servidor apagado.")
