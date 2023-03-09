import glob
import threading
import time


# Note that we're inheriting from threading.Thread here;
# see https://docs.python.org/3/library/threading.html
# for more information.
class DS18B20(threading.Thread):
    default_base_dir = "/sys/bus/w1/devices/"

    def __init__(self, base_dir=None):
        super().__init__()
        self._base_dir = base_dir if base_dir else self.default_base_dir
        self.daemon = True
        self.discover()

    def discover(self):
        device_folder = glob.glob(self._base_dir + "28*")
        self._num_devices = len(device_folder)
        self._device_file: list[str] = []
        for i in range(self._num_devices):
            self._device_file.append(device_folder[i] + "/w1_slave")

        self._values: list[float | None] = [None] * self._num_devices
        self._times: list[float] = [0.0] * self._num_devices

    def run(self):
        """Thread entrypoint: read sensors in a loop.

        Calling DS18B20.start() will cause this method to run in
        a separate thread.
        """

        while True:
            for dev in range(self._num_devices):
                self._read_temp(dev)

            # Adjust this value as you see fit, noting that you will never
            # read actual sensor values more often than 750ms * self._num_devices.
            time.sleep(1)

    def _read_temp(self, index):
        for i in range(3):
            with open(self._device_file[index], "r") as f:
                data = f.read()

            if "YES" not in data:
                time.sleep(0.1)
                continue

            disacard, sep, reading = data.partition(" t=")
            temp = float(reading) / 1000.0
            self._values[index] = temp
            self._times[index] = time.time()
            break
        else:
            print(f"failed to read device {index}")

    def tempC(self, index=0):
        return self._values[index]

    def device_count(self):
        """Return the number of discovered devices"""
        return self._num_devices