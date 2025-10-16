from django.core.management.base import BaseCommand
from data_ingestion.service import DataIngestionService


class Command(BaseCommand):
    help = 'Ingest historical market data for configured symbols'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbols',
            type=str,
            help='Comma-separated list of stock symbols (e.g., AAPL,GOOGL,MSFT)',
        )
        parser.add_argument(
            '--days',
            type=int,
            help='Number of days of historical data to fetch',
        )

    def handle(self, *args, **options):
        service = DataIngestionService()
        
        symbols = None
        if options['symbols']:
            symbols = [s.strip() for s in options['symbols'].split(',')]
        
        days = options.get('days')
        
        self.stdout.write(self.style.SUCCESS('Starting historical data ingestion...'))
        
        total_saved = service.ingest_historical_data_batch(symbols, days)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully ingested {total_saved} records')
        )
