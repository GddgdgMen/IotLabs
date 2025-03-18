from csv import DictReader
from datetime import datetime
from domain.aggregated_data import AggregatedData
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.parking import Parking

class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str, parking_filename: str, batch_size=5):
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.parking_filename = parking_filename
        self.batch_size = batch_size
        self.accelerometer_data = []
        self.gps_data = []
        self.parking_data = []
        self.current_index = 0  # Для циклічного читання

    def _load_csv(self, filename):
        try:
            with open(filename, "r") as file:
                reader = DictReader(file)
                return list(reader)
        except FileNotFoundError:
            print(f"❌ Error: File {filename} not found!")
            return []

    def startReading(self):
        """Завантажує дані з файлів у пам'ять"""
        self.accelerometer_data = self._load_csv(self.accelerometer_filename)
        self.gps_data = self._load_csv(self.gps_filename)
        self.parking_data = self._load_csv(self.parking_filename)
        self.current_index = 0  # Скидаємо індекс читання

    def stopReading(self):
        """Очистка зчитаних даних"""
        self.accelerometer_data.clear()
        self.gps_data.clear()
        self.parking_data.clear()

    def read(self):
        """Зчитує batch_size записів і повертає список AggregatedData"""
        batch = []
        for _ in range(self.batch_size):
            if not self.accelerometer_data or not self.gps_data or not self.parking_data:
                return []

            acc = self.accelerometer_data[self.current_index % len(self.accelerometer_data)]
            gps = self.gps_data[self.current_index % len(self.gps_data)]
            park = self.parking_data[self.current_index % len(self.parking_data)]

            accelerometer = Accelerometer(int(acc["x"]), int(acc["y"]), int(acc["z"]))
            gps = Gps(float(gps["longitude"]), float(gps["latitude"]))
            parking = Parking(int(park["empty_count"]), gps)  # GPS додаємо до паркінгу

            aggregated_data = AggregatedData(
                accelerometer=accelerometer,
                gps=gps,
                parking=parking,
                time=datetime.fromisoformat(park["timestamp"]),
            )

            batch.append(aggregated_data)
            self.current_index += 1  # Рухаємось вперед, циклічно

        return batch
