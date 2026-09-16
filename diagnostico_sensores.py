import asyncio
import importlib.metadata
import winsdk
from winsdk.windows.devices.sensors import Gyrometer, Accelerometer
from winsdk.windows.devices.enumeration import DeviceInformation


async def list_class_devices(selector, label):
    print(f"--- {label} ---")
    try:
        devices = await DeviceInformation.find_all_async(selector)
        if not devices:
            print("  Ningun dispositivo encontrado en esta clase.")
        for d in devices:
            print(f"  [{d.name}] id={d.id}")
    except Exception as e:
        print(f"  Error enumerando: {e}")
    print()


async def main():
    print(f"winsdk '{importlib.metadata.version('winsdk')}'")

    for sensor_class, selector in (
        (Gyrometer, Gyrometer.get_device_selector()),
        (Accelerometer, Accelerometer.get_device_selector()),
    ):
        await list_class_devices(selector, sensor_class.__name__)

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