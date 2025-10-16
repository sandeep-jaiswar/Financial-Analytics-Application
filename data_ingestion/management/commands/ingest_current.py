from django.core.management.base import BaseCommand
from data_ingestion.service import DataIngestionService


class Command(BaseCommand):
    help = 'Ingest current market quotes for configured symbols'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbols',
            type=str,
            help='Comma-separated list of stock symbols (e.g., AAPL,GOOGL,MSFT)',
        )

    def handle(self, *args, **options):
        service = DataIngestionService()
        
        symbols = None
        if options['symbols']:
            symbols = [s.strip() for s in options['symbols'].split(',')]
        
        self.stdout.write(self.style.SUCCESS('Starting current quote ingestion...'))
        
        success_count = service.ingest_current_quotes_batch(symbols)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully ingested {success_count} quotes')
        )
