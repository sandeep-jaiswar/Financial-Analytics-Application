from django.shortcuts import render
from django.views import View


class HomeView(View):
    """Home page view"""
    def get(self, request):
        return render(request, 'ui_app/home.html', {
            'title': 'Financial Analytics Dashboard',
        })


class StocksView(View):
    """Stocks list view"""
    def get(self, request):
        from django.conf import settings
        symbols = getattr(settings, 'INGESTION_SYMBOLS', [])
        return render(request, 'ui_app/stocks.html', {
            'title': 'Stock Quotes',
            'symbols': symbols,
        })

