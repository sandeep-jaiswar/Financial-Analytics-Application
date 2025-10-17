import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import clickhouse_connect
from django.conf import settings


logger = logging.getLogger('api_service')


def get_clickhouse_client():
    """
    Get ClickHouse client using clickhouse_connect (modern library)
    """
    return clickhouse_connect.get_client(
        host=getattr(settings, 'CLICKHOUSE_HOST', 'localhost'),
        port=getattr(settings, 'CLICKHOUSE_PORT', 8123),
        username=getattr(settings, 'CLICKHOUSE_USER', 'default'),
        password=getattr(settings, 'CLICKHOUSE_PASSWORD', ''),
        database=getattr(settings, 'CLICKHOUSE_DATABASE', 'default'),
    )


@api_view(['GET'])
def get_symbols(request):
    """
    GET /api/marketdata/symbols - Get list of all available symbols from eq_masters
    Query params: 
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 50, max: 100)
    """
    try:
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 50)), 100)
        
        if page < 1:
            return Response(
                {'error': 'Invalid page number', 'message': 'Page must be >= 1'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        offset = (page - 1) * per_page
        
        client = get_clickhouse_client()
        
        # Get symbols from eq_masters with OHLCV data statistics
        query = """
            SELECT 
                em.ticker,
                em.trading_symbol,
                em.description,
                COUNT(eo.datetime) as record_count,
                MIN(eo.datetime) as first_date,
                MAX(eo.datetime) as last_date
            FROM eq_masters em
            LEFT JOIN eq_ohlcv eo ON em.ticker = eo.ticker
            GROUP BY em.ticker, em.trading_symbol, em.description
            ORDER BY em.ticker
            LIMIT {limit} OFFSET {offset}
        """
        
        results = client.query(query.format(limit=per_page, offset=offset))
        
        # Get total count
        total_count_result = client.query("SELECT COUNT(DISTINCT ticker) FROM eq_masters")
        total_count = total_count_result.result_rows[0][0] if total_count_result.result_rows else 0
        
        symbols = []
        for row in results.result_rows:
            symbols.append({
                'ticker': row[0],
                'tradingSymbol': row[1],
                'description': row[2],
                'recordCount': row[3],
                'firstDate': row[4].isoformat() if row[4] else None,
                'lastDate': row[5].isoformat() if row[5] else None,
            })
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return Response({
            'symbols': symbols,
            'pagination': {
                'page': page,
                'perPage': per_page,
                'totalItems': total_count,
                'totalPages': total_pages,
                'hasNext': page < total_pages,
                'hasPrev': page > 1
            }
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        logger.error(f"Invalid parameter: {str(e)}")
        return Response(
            {'error': 'Invalid parameter', 'message': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error fetching symbols: {str(e)}")
        return Response(
            {'error': 'Internal server error', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_marketdata_by_symbol(request, symbol):
    """
    GET /api/marketdata/:symbol - Get market data for a specific symbol from eq_ohlcv
    Query params:
        - from (date): Start date (YYYY-MM-DD)
        - to (date): End date (YYYY-MM-DD)
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 100, max: 1000)
    """
    try:
        # Get query parameters
        from_date_str = request.GET.get('from')
        to_date_str = request.GET.get('to')
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 100)), 1000)
        
        if page < 1:
            return Response(
                {'error': 'Invalid page number', 'message': 'Page must be >= 1'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set default date range if not provided (last 30 days)
        if not to_date_str:
            to_date = datetime.now().date()
        else:
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        
        if not from_date_str:
            from_date = to_date - timedelta(days=30)
        else:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
        
        if from_date > to_date:
            return Response(
                {'error': 'Invalid date range', 'message': 'from date must be before to date'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        offset = (page - 1) * per_page
        
        client = get_clickhouse_client()
        
        # Get market data with pagination
        query = """
            SELECT ticker, datetime, open, high, low, close, volume
            FROM eq_ohlcv
            WHERE ticker = '{ticker}' 
              AND toDate(datetime) BETWEEN toDate('{from_date}') AND toDate('{to_date}')
            ORDER BY datetime DESC
            LIMIT {limit} OFFSET {offset}
        """
        
        results = client.query(query.format(
            ticker=symbol.upper(),
            from_date=from_date,
            to_date=to_date,
            limit=per_page,
            offset=offset
        ))
        
        # Get total count
        count_query = """
            SELECT COUNT(*)
            FROM eq_ohlcv
            WHERE ticker = '{ticker}'
              AND toDate(datetime) BETWEEN toDate('{from_date}') AND toDate('{to_date}')
        """
        
        count_result = client.query(count_query.format(
            ticker=symbol.upper(),
            from_date=from_date,
            to_date=to_date
        ))
        total_count = count_result.result_rows[0][0] if count_result.result_rows else 0
        
        market_data = []
        for row in results.result_rows:
            market_data.append({
                'ticker': row[0],
                'datetime': row[1].isoformat() if row[1] else None,
                'open': float(row[2]) if row[2] is not None else None,
                'high': float(row[3]) if row[3] is not None else None,
                'low': float(row[4]) if row[4] is not None else None,
                'close': float(row[5]) if row[5] is not None else None,
                'volume': int(row[6]) if row[6] is not None else None,
            })
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return Response({
            'ticker': symbol.upper(),
            'data': market_data,
            'dateRange': {
                'from': from_date.isoformat(),
                'to': to_date.isoformat()
            },
            'pagination': {
                'page': page,
                'perPage': per_page,
                'totalItems': total_count,
                'totalPages': total_pages,
                'hasNext': page < total_pages,
                'hasPrev': page > 1
            }
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        logger.error(f"Invalid parameter: {str(e)}")
        return Response(
            {'error': 'Invalid parameter', 'message': 'Use YYYY-MM-DD format for dates'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error fetching market data for {symbol}: {str(e)}")
        return Response(
            {'error': 'Internal server error', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def fetch_latest_for_ticker(client, ticker):
    """
    Helper function to fetch latest data for a single ticker (used in parallel processing)
    """
    try:
        query = """
            SELECT ticker, datetime, open, high, low, close, volume
            FROM eq_ohlcv
            WHERE ticker = '{ticker}'
            ORDER BY datetime DESC
            LIMIT 1
        """
        result = client.query(query.format(ticker=ticker))
        
        if result.result_rows:
            row = result.result_rows[0]
            return {
                'ticker': row[0],
                'datetime': row[1].isoformat() if row[1] else None,
                'open': float(row[2]) if row[2] is not None else None,
                'high': float(row[3]) if row[3] is not None else None,
                'low': float(row[4]) if row[4] is not None else None,
                'close': float(row[5]) if row[5] is not None else None,
                'volume': int(row[6]) if row[6] is not None else None,
            }
        return None
    except Exception as e:
        logger.warning(f"Error fetching latest data for {ticker}: {str(e)}")
        return None


@api_view(['GET'])
def get_latest_marketdata(request):
    """
    GET /api/marketdata/latest - Get latest market data across symbols using parallel processing
    Query params:
        - symbols (string): Comma-separated list of symbols (optional)
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 50, max: 100)
        - parallel (bool): Use parallel processing (default: true)
    """
    try:
        # Get query parameters
        symbols_param = request.GET.get('symbols')
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 50)), 100)
        use_parallel = request.GET.get('parallel', 'true').lower() != 'false'
        
        if page < 1:
            return Response(
                {'error': 'Invalid page number', 'message': 'Page must be >= 1'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        offset = (page - 1) * per_page
        
        client = get_clickhouse_client()
        
        # Build query based on whether symbols are specified
        if symbols_param:
            symbols_list = [s.strip().upper() for s in symbols_param.split(',')]
            
            # If parallel processing is enabled and we have multiple symbols
            if use_parallel and len(symbols_list) > 1:
                # Use ThreadPoolExecutor for parallel fetching
                market_data = []
                with ThreadPoolExecutor(max_workers=min(10, len(symbols_list))) as executor:
                    # Submit all tasks
                    future_to_ticker = {
                        executor.submit(fetch_latest_for_ticker, client, ticker): ticker 
                        for ticker in symbols_list[offset:offset + per_page]
                    }
                    
                    # Collect results as they complete
                    for future in as_completed(future_to_ticker):
                        result = future.result()
                        if result:
                            market_data.append(result)
                
                # Sort by ticker for consistent output
                market_data.sort(key=lambda x: x['ticker'])
                total_count = len(symbols_list)
                
            else:
                # Sequential processing for single symbol or when parallel is disabled
                query = """
                    SELECT ticker, datetime, open, high, low, close, volume
                    FROM (
                        SELECT ticker, datetime, open, high, low, close, volume,
                               ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY datetime DESC) as rn
                        FROM eq_ohlcv
                        WHERE ticker IN {tickers}
                    ) t
                    WHERE rn = 1
                    ORDER BY ticker
                    LIMIT {limit} OFFSET {offset}
                """
                
                tickers_str = "('" + "','".join(symbols_list) + "')"
                results = client.query(query.format(
                    tickers=tickers_str,
                    limit=per_page,
                    offset=offset
                ))
                
                market_data = []
                for row in results.result_rows:
                    market_data.append({
                        'ticker': row[0],
                        'datetime': row[1].isoformat() if row[1] else None,
                        'open': float(row[2]) if row[2] is not None else None,
                        'high': float(row[3]) if row[3] is not None else None,
                        'low': float(row[4]) if row[4] is not None else None,
                        'close': float(row[5]) if row[5] is not None else None,
                        'volume': int(row[6]) if row[6] is not None else None,
                    })
                
                total_count = len(symbols_list)
        else:
            # Get latest data for all symbols
            query = """
                SELECT ticker, datetime, open, high, low, close, volume
                FROM (
                    SELECT ticker, datetime, open, high, low, close, volume,
                           ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY datetime DESC) as rn
                    FROM eq_ohlcv
                ) t
                WHERE rn = 1
                ORDER BY ticker
                LIMIT {limit} OFFSET {offset}
            """
            
            results = client.query(query.format(
                limit=per_page,
                offset=offset
            ))
            
            market_data = []
            for row in results.result_rows:
                market_data.append({
                    'ticker': row[0],
                    'datetime': row[1].isoformat() if row[1] else None,
                    'open': float(row[2]) if row[2] is not None else None,
                    'high': float(row[3]) if row[3] is not None else None,
                    'low': float(row[4]) if row[4] is not None else None,
                    'close': float(row[5]) if row[5] is not None else None,
                    'volume': int(row[6]) if row[6] is not None else None,
                })
            
            # Get total count
            count_result = client.query("SELECT COUNT(DISTINCT ticker) FROM eq_ohlcv")
            total_count = count_result.result_rows[0][0] if count_result.result_rows else 0
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return Response({
            'data': market_data,
            'pagination': {
                'page': page,
                'perPage': per_page,
                'totalItems': total_count,
                'totalPages': total_pages,
                'hasNext': page < total_pages,
                'hasPrev': page > 1
            }
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        logger.error(f"Invalid parameter: {str(e)}")
        return Response(
            {'error': 'Invalid parameter', 'message': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error fetching latest market data: {str(e)}")
        return Response(
            {'error': 'Internal server error', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
