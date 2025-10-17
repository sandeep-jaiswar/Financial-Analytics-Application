from django.urls import path
from api_service import marketdata_views

urlpatterns = [
    path('symbols/', marketdata_views.get_symbols, name='marketdata_symbols'),
    path('latest/', marketdata_views.get_latest_marketdata, name='marketdata_latest'),
    path('<str:symbol>/', marketdata_views.get_marketdata_by_symbol, name='marketdata_by_symbol'),
]
