import asyncio
import importlib.metadata
import winsdk
from winsdk.windows.devices.sensors import Gyrometer, Accelerometer
from winsdk.windows.devices.enumeration import DeviceInformation


async def main():
    print(f"winsdk '{importlib.metadata.version('winsdk')}'")

    print("--- Dispositivos de la clase Sensor (Windows) ---")
    selector = 'System.Devices.InterfaceClassGuid:="{' + "c0183a8f-fd21-4e8a-8955-ac126a29cccb" + '}"'
    try:
        devices = await DeviceInformation.find_all_async(selector)
        if not devices:
            print("  Ningun sensor registrado en Windows.")
        for d in devices:
            print(f"  [{d.name}] id={d.id}")
    except Exception as e:
        print(f"  Error enumerando: {e}")
    print()

    gyro = Gyrometer.get_default()
    accel = Accelerometer.get_default()
    print("Gyrometer.get_default():", gyro)
    print("Accelerometer.get_default():", accel)

    if gyro:
        g = gyro.get_current_reading()
        if g:
            print("  lectura gyro:", g.angular_velocity_x, g.angular_velocity_y, g.angular_velocity_z)
        else:
            print("  lectura gyro: None")
    if accel:
        a = accel.get_current_reading()
        if a:
            print("  lectura accel:", a.acceleration_x, a.acceleration_y, a.acceleration_z)
        else:
            print("  lectura accel: None")

asyncio.run(main())