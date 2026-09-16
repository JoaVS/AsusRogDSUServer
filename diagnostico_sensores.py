import asyncio
import subprocess
import importlib.metadata
from winsdk.windows.devices.sensors import Gyrometer, Accelerometer


def powershell(command):
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True, text=True
    )
    return (out.stdout + out.stderr).strip()


async def main():
    print(f"winsdk '{importlib.metadata.version('winsdk')}'")

    gyro = Gyrometer.get_default()
    accel = Accelerometer.get_default()
    print("Gyrometer.get_default():", gyro)
    print("Accelerometer.get_default():", accel)

    if gyro:
        g = gyro.get_current_reading()
        print("  lectura gyro:", None if not g else (g.angular_velocity_x, g.angular_velocity_y, g.angular_velocity_z))
    if accel:
        a = accel.get_current_reading()
        print("  lectura accel:", None if not a else (a.acceleration_x, a.acceleration_y, a.acceleration_z))

    print()
    print("--- Servicio de sensores de Windows ---")
    print(powershell("Get-Service SensorService | Format-List Name, Status, StartType"))

    print("--- Dispositivos clase 'Sensors' (Administrador de dispositivos) ---")
    print(powershell("Get-PnpDevice -Class Sensors -ErrorAction SilentlyContinue | Format-List FriendlyName, Status, InstanceId"))

    print("--- Posibles sensores HID (InvenSense/Bosch/IMU/Accel/Gyro) ---")
    print(powershell(
        "Get-PnpDevice -ErrorAction SilentlyContinue | Where-Object { "
        "$_.InstanceId -match 'HID' -and $_.FriendlyName -match 'Sensor|InvenSense|Bosch|IMU|Accel|Gyro' } "
        "| Format-List FriendlyName, Status, InstanceId"
    ))

asyncio.run(main())