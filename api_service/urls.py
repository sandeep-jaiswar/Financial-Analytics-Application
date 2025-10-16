from django.urls import path
from api_service import views

urlpatterns = [
    path('<str:symbol>/quote/', views.get_quote, name='get_quote'),
    path('<str:symbol>/history/', views.get_history, name='get_history'),
    path('quotes/', views.get_multiple_quotes, name='get_multiple_quotes'),
]
