import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from django.core.management.base import BaseCommand
from pms_integration.exceptions import PMSIntegrationError
from pms_integration.models.hotel import Hotel
from pms_integration.services.ingestor import BookingIngestor
from pms_integration.services.mapper import GenericJsonMapper
from pms_integration.services.pms_client import PMSClient


class Command(BaseCommand):
    help = "Sync booking data for all hotels using their PMS configuration"

    def handle(self, *args, **options):
        hotels = Hotel.objects.select_related("pms_config").all()

        if not hotels:
            self.stdout.write(self.style.WARNING("No hotels configured"))
            return

        self.stdout.write(
            self.style.SUCCESS(f"Starting sync for {hotels.count()} hotels\n")
        )

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.sync_hotel, hotel): hotel for hotel in hotels
            }

            for future in as_completed(futures):
                hotel = futures[future]
                try:
                    future.result()
                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(f"[Hotel {hotel.id}] Sync failed: {e}")
                    )

        self.stdout.write(self.style.SUCCESS("\nAll sync tasks completed."))

    def sync_hotel(self, hotel):
        mock_data_path = Path("mock_data/mock_pms_bookings.json")  # hardcoded for now
        config_path = Path(hotel.pms_config.config_file_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        try:
            # Load PMS config
            with config_path.open("r", encoding="utf-8") as f:
                config = json.load(f)

            # Load raw data from mock file
            client = PMSClient(str(mock_data_path))
            raw_bookings = client.fetch_bookings()

            mapper = GenericJsonMapper(config)
            ingestor = BookingIngestor(hotel.id)

            success, failed = 0, 0
            for raw in raw_bookings:
                try:
                    dto = mapper.map(raw)
                    ingestor.save_booking(dto)
                    success += 1
                except PMSIntegrationError as e:
                    failed += 1
                    logging.critical(f"[Hotel {hotel.id}] Skipped booking due to: {e}")

            logging.info(f"[Hotel {hotel.id}] Synced: {success}, Failed: {failed}")

        except Exception as e:
            raise RuntimeError(f"Error during sync for hotel {hotel.id}: {e}")
