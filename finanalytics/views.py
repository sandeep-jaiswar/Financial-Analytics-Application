# python
import logging
from typing import List, Tuple, Any

import requests
import clickhouse_connect
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.conf import settings
from nsemine import nse, live, historical, fno
from .utils import NseMineWrapper

logger = logging.getLogger(__name__)
client = NseMineWrapper()
client.preflight()

def get_clickhouse_client():
    """
    Centralized ClickHouse client using settings.CLICKHOUSE
    """
    conf = getattr(settings, "CLICKHOUSE", None)
    if not conf:
        raise RuntimeError("CLICKHOUSE configuration missing in Django settings")

    return clickhouse_connect.get_client(
        host=conf["HOST"],
        port=conf["PORT"],
        username=conf["USER"],
        password=conf["PASSWORD"],
        database=conf["DATABASE"],
    )


@require_http_methods(["GET"])
def load_eq_masters(request: HttpRequest) -> JsonResponse:
    """
    Fetch EQ Masters data from NSE and insert into ClickHouse
    """
    try:
        nse_url = "https://charting.nseindia.com/Charts/GetEQMasters"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            ),
            "Accept": "text/plain, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.nseindia.com/",
            "X-Requested-With": "XMLHttpRequest",
        }

        session = requests.Session()
        try:
            # Pre-flight request (some environments require it)
            session.get("https://www.nseindia.com", headers=headers, timeout=10)
        except requests.RequestException:
            logger.debug("NSE homepage preflight failed or skipped")

        response = session.get(nse_url, headers=headers, timeout=60)
        response.raise_for_status()

        text = (response.text or "").strip()
        if not text:
            return JsonResponse(
                {"status": "success", "message": "No data returned from NSE", "records_count": 0, "data": []}
            )

        lines = text.splitlines()
        data_lines = lines[1:] if len(lines) > 1 and "|" in lines[0] else lines

        records: List[Tuple[Any, ...]] = []
        for line in data_lines:
            if not line.strip():
                continue
            parts = line.split("|")
            if len(parts) < 4:
                continue
            try:
                scrip_code = int(parts[0])
            except (ValueError, TypeError):
                continue

            trading_symbol = parts[1].strip()
            description = parts[2].strip()
            ticker = trading_symbol.split("-")[0]
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

            logger.info("Inserting %d EQ Masters records into ClickHouse", len(records))
            tables = getattr(client.query("SHOW TABLES"), "result_rows", None)
            logger.debug("Existing tables: %s", tables)
            logger.debug("First 5 records preview: %s", records[:5])

            if records:
                client.insert(
                    "eq_masters",
                    records,
                    column_names=["scrip_code", "trading_symbol", "ticker", "description", "instrument_type"],
                )

        except Exception as db_error:
            logger.error("ClickHouse error: %s", db_error)
            return JsonResponse(
                {"status": "error", "message": "Database operation failed", "error": str(db_error)}, status=500
            )

        return JsonResponse(
            {"status": "success", "message": f"Successfully loaded {len(records)} EQ Masters records", "records_count": len(records)}
        )

    except requests.RequestException as e:
        logger.error("Failed to fetch data from NSE: %s", e)
        return JsonResponse(
            {"status": "error", "message": "Failed to fetch data from NSE API", "error": str(e)}, status=500
        )

    except Exception as e:
        logger.exception("Unexpected failure in load_eq_masters")
        return JsonResponse({"status": "error", "message": "Failed to load EQ Masters data", "error": str(e)}, status=500)


@require_http_methods(["GET"])
def load_eq_ohlcv(request: HttpRequest) -> JsonResponse:
    """
    API to fetch last 1 year OHLCV data for all tickers in eq_masters
    """
    try:
        client = get_clickhouse_client()

        # Ensure table exists
        client.command(
            """
        CREATE TABLE IF NOT EXISTS eq_ohlcv (
            trading_symbol String,
            symbol_bo String,
            date Date,
            open Float32,
            high Float32,
            low Float32,
            close Float32,
            volume UInt64,
            created_at DateTime DEFAULT now()
        )
        ENGINE = MergeTree()
        ORDER BY (trading_symbol, date)
        PARTITION BY toYYYYMM(date)
        """
        )

        # Fetch tickers from eq_masters
        result = getattr(client.query("SELECT trading_symbol, ticker FROM eq_masters"), "result_rows", None)
        if not result:
            return JsonResponse({"status": "success", "message": "No tickers found in eq_masters", "records_count": 0})

        # Define last 1 year range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)

        all_ohlcv: List[Tuple[Any, ...]] = []
        for trading_symbol, ticker in result:
            base_ticker = ticker.split(".")[0]
            logger.info("Fetching OHLCV for %s", base_ticker)
            try:
                ohlcv_records = historical.get_stock_historical_data(base_ticker, start_date, end_date) or []
            except Exception as e:
                logger.warning("Failed to fetch historical data for %s: %s", base_ticker, e)
                ohlcv_records = []

            # If API returned dicts or objects, ensure tuples/lists for ClickHouse insert
            if ohlcv_records and isinstance(ohlcv_records[0], dict):
                for r in ohlcv_records:
                    all_ohlcv.append(
                        (
                            r.get("trading_symbol"),
                            r.get("symbol_bo"),
                            r.get("date"),
                            r.get("open"),
                            r.get("high"),
                            r.get("low"),
                            r.get("close"),
                            r.get("volume"),
                        )
                    )
            else:
                all_ohlcv.extend(ohlcv_records)

        if not all_ohlcv:
            return JsonResponse({"status": "success", "message": "No OHLCV data fetched", "records_count": 0})

        # Insert into ClickHouse
        client.insert(
            "eq_ohlcv",
            all_ohlcv,
            column_names=["trading_symbol", "symbol_bo", "date", "open", "high", "low", "close", "volume"],
        )

        return JsonResponse(
            {
                "status": "success",
                "message": f"Successfully loaded OHLCV for {len(result)} tickers",
                "records_count": len(all_ohlcv),
            }
        )

    except Exception as e:
        logger.exception("Failed to load OHLCV data")
        return JsonResponse({"status": "error", "message": "Database operation failed", "error": str(e)}, status=500)

@require_http_methods(["GET"])
def load_nse_eq_ohlcv(request: HttpRequest) -> JsonResponse:
    """
    Fetch historical OHLCV per ticker and insert records into ClickHouse,
    ensuring proper normalization to tuple format before insertion.
    """
    try:
        ch_client = get_clickhouse_client()
        nse_wrapper = client  # NseMineWrapper (initialized globally)
        rows = getattr(ch_client.query("SELECT ticker FROM eq_masters"), "result_rows", None) or []

        if not rows:
            return JsonResponse({"status": "success", "message": "No tickers found in eq_masters", "records_count": 0})

        inserted_total = 0
        failed_tickers = []
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)

        for row in rows:
            ticker = row[0] if isinstance(row, (list, tuple)) else row
            if not ticker:
                continue

            try:
                data = nse_wrapper.get_stock_historical_data(ticker, start_date, end_date)
            except Exception as e:
                logger.warning("Failed to fetch historical for %s: %s", ticker, e)
                continue

            # Normalize output into list-of-dicts
            if data is None:
                logger.debug("No data returned for %s", ticker)
                continue

            if hasattr(data, "to_dict"):  # pandas DataFrame
                try:
                    records = data.to_dict(orient="records")
                except Exception:
                    logger.debug("Unable to convert DataFrame to records for %s", ticker)
                    records = []
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                records = data
            else:
                records = []

            if not records:
                logger.debug("Empty records for %s", ticker)
                continue

            # Ensure consistent keys
            valid_records = []
            for rec in records:
                try:
                    valid_records.append((
                        rec.get("ticker", ticker),
                        rec.get("date") or rec.get("datetime"),
                        float(rec.get("open", 0)),
                        float(rec.get("high", 0)),
                        float(rec.get("low", 0)),
                        float(rec.get("close", 0)),
                        int(rec.get("volume", 0)),
                    ))
                except Exception as parse_err:
                    logger.debug("Skipping malformed record for %s: %s", ticker, parse_err)

            if not valid_records:
                continue

            try:
                # Ensure table exists
                ch_client.command(
                    """
                    CREATE TABLE IF NOT EXISTS eq_ohlcv (
                        ticker String,
                        datetime DateTime,
                        open Float32,
                        high Float32,
                        low Float32,
                        close Float32,
                        volume UInt64,
                        created_at DateTime DEFAULT now()
                    )
                    ENGINE = MergeTree()
                    ORDER BY (ticker, datetime)
                    PARTITION BY toYYYYMM(datetime)
                    """
                )

                ch_client.insert(
                    "eq_ohlcv",
                    valid_records,
                    column_names=["ticker", "datetime", "open", "high", "low", "close", "volume"],
                )
                inserted_total += len(valid_records)
                logger.info("Inserted %d records for %s", len(valid_records), ticker)

            except Exception as e:
                failed_tickers.append(ticker)
                logger.exception("ClickHouse insert failed for %s: %s", ticker, e)

        return JsonResponse({
            "status": "success",
            "message": f"Inserted {inserted_total} records across {len(rows)} tickers",
            "failed_tickers": failed_tickers,
            "records_count": inserted_total,
        })

    except Exception as e:
        logger.exception("Failed to load NSE OHLCV data")
        return JsonResponse({
            "status": "error",
            "message": "Unexpected failure",
            "error": str(e),
        }, status=500)
