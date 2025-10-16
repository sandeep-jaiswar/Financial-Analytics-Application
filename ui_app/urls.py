from django.urls import path
from ui_app import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('stocks/', views.StocksView.as_view(), name='stocks'),
]
