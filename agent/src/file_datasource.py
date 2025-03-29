from csv import DictReader, reader
from datetime import datetime
import logging
from domain.aggregated_data import AggregatedData
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.parking import Parking
import config

class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str, parking_filename: str, batch_size=5):
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.parking_filename = parking_filename

        self.accelerometer_file = None
        self.gps_file = None
        self.parking_file = None

        self.accelerometer_reader = None
        self.gps_reader = None
        self.parking_reader = None

        self.batch_size = batch_size
        self.accelerometer_data = []
        self.gps_data = []
        self.parking_data = []
        self.current_batch = []  # Для циклічного читання

    def startReading(self):
        """Завантажує дані з файлів у пам'ять"""
        self.accelerometer_file = open(self.accelerometer_filename, 'r')
        self.gps_file = open(self.gps_filename, 'r')
        self.parking_file = open(self.parking_filename, 'r')

        self.accelerometer_reader = reader(self.accelerometer_file)
        self.gps_reader = reader(self.gps_file)
        self.parking_reader = reader(self.parking_file)
        next(self.accelerometer_file, None)
        next(self.gps_file, None)
        next(self.parking_file, None)
        self.current_batch = []  # Скидаємо індекс читання

    def stopReading(self):
        """Очистка зчитаних даних"""
        self.accelerometer_file.close()
        self.gps_file.close()
        self.parking_file.close()

        self.accelerometer_data = []
        self.gps_data = []
        self.parking_data = []

        self.current_batch = []

    def _reset_readers(self) -> None:
        """Resets accelerometer, GPS and air quality file pointers"""
        self.accelerometer_file.seek(0)
        self.gps_file.seek(0)
        self.parking_file.seek(0)
        
        next(self.accelerometer_reader, None)
        next(self.gps_reader, None)
        next(self.parking_reader, None)

    def _reset_accelerometer_reader(self) -> None:
        self.accelerometer_file.seek(0)
        next(self.accelerometer_reader, None)

    def _reset_parking_reader(self) -> None:
        self.parking_file.seek(0)
        next(self.parking_reader, None)

    def _reset_gps_reader(self) -> None:
        self.gps_file.seek(0)
        next(self.gps_reader, None)


    def read(self):
        
        if not self.current_batch:
            for _ in range(self.batch_size):
                try:
                    acc_data = next(self.accelerometer_reader)
                except StopIteration:
                    self._reset_accelerometer_reader()
                try:
                    gps_data = next(self.gps_reader)
                except StopIteration:
                    self._reset_gps_reader()
                try:
                    parking_data =  next(self.parking_reader)
                except StopIteration:
                    self._reset_parking_reader()
                    continue
                accelerometer = Accelerometer(
                    x=int(acc_data[0]),
                    y=int(acc_data[1]),
                    z=int(acc_data[2])
                )

                gps = Gps(
                    latitude=float(gps_data[0]),
                    longitude=float(gps_data[1])
                )

                parking_gps = Gps(
                    latitude=float(parking_data[1]),
                    longitude=float(parking_data[2])
                )

                parking = Parking(
                    empty_count=int(parking_data[0]),
                    gps=parking_gps
                )

                aggregated_data = AggregatedData(
                    accelerometer=accelerometer,
                    gps=gps,
                    timestamp=datetime.now(),
                    user_id=config.USER_ID,
                    parking_slots=parking.empty_count
                )

                self.current_batch.append([aggregated_data, parking])
                
        return self.current_batch.pop(0) if self.current_batch else None
        