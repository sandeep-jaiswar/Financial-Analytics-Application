import requests
from clickhouse_driver import Client
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def load_eq_masters(request):
    """
    Fetch EQ Masters data from NSE and insert into ClickHouse
    """
    try:
        # Fetch data from NSE API with proper headers
        nse_url = "https://charting.nseindia.com/Charts/GetEQMasters"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/plain, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.nseindia.com/',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        session = requests.Session()
        response = session.get(nse_url, headers=headers, timeout=60)
        response.raise_for_status()
        
        # Parse the pipe-delimited response
        lines = response.text.strip().split('\n')
        
        # Skip header line
        data_lines = lines[1:]
        
        records = []
        for line in data_lines:
            if line.strip():
                parts = line.split('|')
                if len(parts) >= 4:
                    records.append({
                        'scrip_code': int(parts[0]),
                        'trading_symbol': parts[1],
                        'description': parts[2],
                        'instrument_type': int(parts[3])
                    })
        
        # Insert into ClickHouse with proper error handling
        try:
            client_config = {
                'host': settings.CLICKHOUSE_HOST,
                'port': settings.CLICKHOUSE_PORT,
                'user': settings.CLICKHOUSE_USER,
                'database': settings.CLICKHOUSE_DATABASE
            }
            
            # Only add password if it's not empty
            if settings.CLICKHOUSE_PASSWORD:
                client_config['password'] = settings.CLICKHOUSE_PASSWORD
                
            client = Client(**client_config)
            
            # Test connection first
            client.execute("SELECT 1")
            
            # Create database if it doesn't exist
            client.execute(f"CREATE DATABASE IF NOT EXISTS {settings.CLICKHOUSE_DATABASE}")
            
            # Create table if it doesn't exist
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS eq_masters (
                scrip_code UInt32,
                trading_symbol String,
                description String,
                instrument_type UInt8,
                created_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (scrip_code, trading_symbol)
            PARTITION BY toYYYYMM(created_at)
            """
            client.execute(create_table_sql)
            
            # Clear existing data (optional - remove if you want to keep historical data)
            client.execute("TRUNCATE TABLE eq_masters")
            
            # Insert new data
            if records:
                client.execute(
                    "INSERT INTO eq_masters (scrip_code, trading_symbol, description, instrument_type) VALUES",
                    records
                )
                
        except Exception as db_error:
            logger.error(f"ClickHouse error: {db_error}")
            return JsonResponse({
                'status': 'error',
                'message': 'Database connection failed. Please check ClickHouse configuration.',
                'error': str(db_error)
            }, status=500)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Successfully loaded {len(records)} EQ Masters records',
            'records_count': len(records)
        })
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch data from NSE: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to fetch data from NSE API',
            'error': str(e)
        }, status=500)
        
    except Exception as e:
        logger.error(f"Failed to load EQ Masters: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to load EQ Masters data',
            'error': str(e)
        }, status=500)