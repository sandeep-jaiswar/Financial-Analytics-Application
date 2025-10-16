import logging
from datetime import datetime
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json

from api_service.services import YahooFinanceService, YahooFinanceException, RateLimitExceededException


logger = logging.getLogger('api_service')
yahoo_finance_service = YahooFinanceService()


@api_view(['GET'])
def get_quote(request, symbol):
    """
    GET /api/stocks/{symbol}/quote - Get real-time quote for a symbol
    """
    try:
        quote = yahoo_finance_service.get_stock_quote(symbol.upper())
        return Response(quote.to_dict(), status=status.HTTP_200_OK)
    except YahooFinanceException as e:
        logger.error(f"Error fetching quote: {str(e)}")
        return Response(
            {'error': 'Internal server error', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except RateLimitExceededException as e:
        logger.warning(f"Rate limit exceeded: {str(e)}")
        return Response(
            {'error': 'Rate limit exceeded', 'message': str(e)},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )


@api_view(['GET'])
def get_history(request, symbol):
    """
    GET /api/stocks/{symbol}/history - Get historical quotes
    Query params: from (date), to (date), interval (1d/1wk/1mo)
    """
    try:
        from_date_str = request.GET.get('from')
        to_date_str = request.GET.get('to')
        interval = request.GET.get('interval', '1d').lower()
        
        if not from_date_str or not to_date_str:
            return Response(
                {'error': 'Missing required parameters', 'message': 'from and to dates are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Convert interval from Spring format to yfinance format
        interval_map = {
            'daily': '1d',
            '1d': '1d',
            'weekly': '1wk',
            '1wk': '1wk',
            'monthly': '1mo',
            '1mo': '1mo'
        }
        interval = interval_map.get(interval, '1d')
        
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d')
        
        quotes = yahoo_finance_service.get_historical_quotes(
            symbol.upper(), from_date, to_date, interval
        )
        
        return Response([q.to_dict() for q in quotes], status=status.HTTP_200_OK)
    except ValueError as e:
        logger.error(f"Invalid date format: {str(e)}")
        return Response(
            {'error': 'Invalid date format', 'message': 'Use YYYY-MM-DD format'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except YahooFinanceException as e:
        logger.error(f"Error fetching history: {str(e)}")
        return Response(
            {'error': 'Internal server error', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except RateLimitExceededException as e:
        logger.warning(f"Rate limit exceeded: {str(e)}")
        return Response(
            {'error': 'Rate limit exceeded', 'message': str(e)},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )


@api_view(['POST'])
def get_multiple_quotes(request):
    """
    POST /api/stocks/quotes - Get quotes for multiple symbols
    Request body: { "symbols": ["AAPL", "GOOGL", "MSFT"] }
    """
    try:
        data = request.data
        symbols = data.get('symbols', [])
        
        if not symbols or not isinstance(symbols, list):
            return Response(
                {'error': 'Invalid request', 'message': 'symbols array is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        symbols = [s.upper() for s in symbols]
        quotes = yahoo_finance_service.get_multiple_quotes(symbols)
        
        return Response([q.to_dict() for q in quotes], status=status.HTTP_200_OK)
    except YahooFinanceException as e:
        logger.error(f"Error fetching multiple quotes: {str(e)}")
        return Response(
            {'error': 'Internal server error', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except RateLimitExceededException as e:
        logger.warning(f"Rate limit exceeded: {str(e)}")
        return Response(
            {'error': 'Rate limit exceeded', 'message': str(e)},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

