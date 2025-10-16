import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from data_ingestion.repository import ClickHouseRepository


logger = logging.getLogger('api_service')


@api_view(['GET'])
def get_symbols(request):
    """
    GET /api/marketdata/symbols - Get list of all available symbols
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
        
        repository = ClickHouseRepository()
        client = repository.get_client()
        
        # Get distinct symbols with count
        results = client.execute(
            """
            SELECT symbol, COUNT(*) as record_count, MIN(date) as first_date, MAX(date) as last_date
            FROM market_data
            GROUP BY symbol
            ORDER BY symbol
            LIMIT %(limit)s OFFSET %(offset)s
            """,
            {'limit': per_page, 'offset': offset}
        )
        
        # Get total count
        total_count_result = client.execute(
            "SELECT COUNT(DISTINCT symbol) FROM market_data"
        )
        total_count = total_count_result[0][0] if total_count_result else 0
        
        symbols = []
        for row in results:
            symbols.append({
                'symbol': row[0],
                'recordCount': row[1],
                'firstDate': row[2].isoformat() if row[2] else None,
                'lastDate': row[3].isoformat() if row[3] else None,
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
    GET /api/marketdata/:symbol - Get market data for a specific symbol
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
        
        repository = ClickHouseRepository()
        client = repository.get_client()
        
        # Get market data with pagination
        results = client.execute(
            """
            SELECT symbol, timestamp, date, open, high, low, close, volume, adjusted_close
            FROM market_data
            WHERE symbol = %(symbol)s AND date BETWEEN %(from_date)s AND %(to_date)s
            ORDER BY date DESC, timestamp DESC
            LIMIT %(limit)s OFFSET %(offset)s
            """,
            {
                'symbol': symbol.upper(),
                'from_date': from_date,
                'to_date': to_date,
                'limit': per_page,
                'offset': offset
            }
        )
        
        # Get total count
        count_result = client.execute(
            """
            SELECT COUNT(*)
            FROM market_data
            WHERE symbol = %(symbol)s AND date BETWEEN %(from_date)s AND %(to_date)s
            """,
            {
                'symbol': symbol.upper(),
                'from_date': from_date,
                'to_date': to_date
            }
        )
        total_count = count_result[0][0] if count_result else 0
        
        market_data = []
        for row in results:
            market_data.append({
                'symbol': row[0],
                'timestamp': row[1].isoformat() if row[1] else None,
                'date': row[2].isoformat() if row[2] else None,
                'open': float(row[3]) if row[3] else None,
                'high': float(row[4]) if row[4] else None,
                'low': float(row[5]) if row[5] else None,
                'close': float(row[6]) if row[6] else None,
                'volume': int(row[7]) if row[7] else None,
                'adjustedClose': float(row[8]) if row[8] else None,
            })
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return Response({
            'symbol': symbol.upper(),
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


@api_view(['GET'])
def get_latest_marketdata(request):
    """
    GET /api/marketdata/latest - Get latest market data across all symbols
    Query params:
        - symbols (string): Comma-separated list of symbols (optional)
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 50, max: 100)
    """
    try:
        # Get query parameters
        symbols_param = request.GET.get('symbols')
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 50)), 100)
        
        if page < 1:
            return Response(
                {'error': 'Invalid page number', 'message': 'Page must be >= 1'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        offset = (page - 1) * per_page
        
        repository = ClickHouseRepository()
        client = repository.get_client()
        
        # Build query based on whether symbols are specified
        if symbols_param:
            symbols_list = [s.strip().upper() for s in symbols_param.split(',')]
            
            # Get latest data for each specified symbol
            results = client.execute(
                """
                SELECT symbol, timestamp, date, open, high, low, close, volume, adjusted_close
                FROM (
                    SELECT symbol, timestamp, date, open, high, low, close, volume, adjusted_close,
                           ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY date DESC, timestamp DESC) as rn
                    FROM market_data
                    WHERE symbol IN %(symbols)s
                ) t
                WHERE rn = 1
                ORDER BY symbol
                LIMIT %(limit)s OFFSET %(offset)s
                """,
                {
                    'symbols': symbols_list,
                    'limit': per_page,
                    'offset': offset
                }
            )
            
            # Get total count
            count_result = client.execute(
                "SELECT COUNT(DISTINCT symbol) FROM market_data WHERE symbol IN %(symbols)s",
                {'symbols': symbols_list}
            )
        else:
            # Get latest data for all symbols
            results = client.execute(
                """
                SELECT symbol, timestamp, date, open, high, low, close, volume, adjusted_close
                FROM (
                    SELECT symbol, timestamp, date, open, high, low, close, volume, adjusted_close,
                           ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY date DESC, timestamp DESC) as rn
                    FROM market_data
                ) t
                WHERE rn = 1
                ORDER BY symbol
                LIMIT %(limit)s OFFSET %(offset)s
                """,
                {
                    'limit': per_page,
                    'offset': offset
                }
            )
            
            # Get total count
            count_result = client.execute(
                "SELECT COUNT(DISTINCT symbol) FROM market_data"
            )
        
        total_count = count_result[0][0] if count_result else 0
        
        market_data = []
        for row in results:
            market_data.append({
                'symbol': row[0],
                'timestamp': row[1].isoformat() if row[1] else None,
                'date': row[2].isoformat() if row[2] else None,
                'open': float(row[3]) if row[3] else None,
                'high': float(row[4]) if row[4] else None,
                'low': float(row[5]) if row[5] else None,
                'close': float(row[6]) if row[6] else None,
                'volume': int(row[7]) if row[7] else None,
                'adjustedClose': float(row[8]) if row[8] else None,
            })
        
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
