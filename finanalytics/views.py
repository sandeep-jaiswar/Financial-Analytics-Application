import requests
import clickhouse_connect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_clickhouse_client():
    """
    Centralized ClickHouse client using settings.CLICKHOUSE
    """
    conf = settings.CLICKHOUSE
    return clickhouse_connect.get_client(
        host=conf['HOST'],
        port=conf['PORT'],
        username=conf['USER'],
        password=conf['PASSWORD'],
        database=conf['DATABASE']
    )

@require_http_methods(["GET"])
def load_eq_masters(request):
    """
    Fetch EQ Masters data from NSE and insert into ClickHouse
    """
    try:
        nse_url = "https://charting.nseindia.com/Charts/GetEQMasters"
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            ),
            'Accept': 'text/plain, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.nseindia.com/',
            'X-Requested-With': 'XMLHttpRequest'
        }

        session = requests.Session()
        try:
            # Pre-flight request (some environments require it)
            session.get("https://www.nseindia.com", headers=headers, timeout=10)
        except requests.RequestException:
            logger.debug("NSE homepage preflight failed or skipped")

        response = session.get(nse_url, headers=headers, timeout=60)
        response.raise_for_status()

        text = response.text.strip()
        if not text:
            return JsonResponse({
                'status': 'success',
                'message': 'No data returned from NSE',
                'records_count': 0,
                'data': []
            })

        lines = text.splitlines()
        data_lines = lines[1:] if len(lines) > 1 and '|' in lines[0] else lines

        records = []
        for line in data_lines:
            if not line.strip():
                continue
            parts = line.split('|')
            if len(parts) < 4:
                continue
            try:
                scrip_code = int(parts[0])
            except (ValueError, TypeError):
                continue

            trading_symbol = parts[1].strip()
            description = parts[2].strip()
            ticker = trading_symbol.split('-')[0] + ".BO"
            try:
                instrument_type = int(parts[3])
            except (ValueError, TypeError):
                instrument_type = 0

            records.append((scrip_code, trading_symbol, ticker, description, instrument_type))

        # ----------------------------------------------------------
        # Insert into ClickHouse
        # ----------------------------------------------------------
        try:
            client = get_clickhouse_client()

            # quick connectivity test
            client.query("SELECT 1")

            print(f"Inserting {len(records)} EQ Masters records into ClickHouse")
            print(client)


            tables = client.query("SHOW TABLES").result_rows
            print("Existing tables:", tables)
            print(records[:5])  # Print first 5 records for verification

            if records:
                client.insert(
                    'eq_masters',
                    records,
                    column_names=['scrip_code', 'trading_symbol', 'ticker', 'description', 'instrument_type']
                )

        except Exception as db_error:
            logger.error("ClickHouse error: %s", db_error)
            return JsonResponse({
                'status': 'error',
                'message': 'Database operation failed',
                'error': str(db_error)
            }, status=500)

        return JsonResponse({
            'status': 'success',
            'message': f'Successfully loaded {len(records)} EQ Masters records',
            'records_count': len(records)
        })

    except requests.RequestException as e:
        logger.error("Failed to fetch data from NSE: %s", e)
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to fetch data from NSE API',
            'error': str(e)
        }, status=500)

    except Exception as e:
        logger.exception("Unexpected failure in load_eq_masters")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to load EQ Masters data',
            'error': str(e)
        }, status=500)
