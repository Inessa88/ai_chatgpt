from django.urls import path

from . import views

urlpatterns = [
    path('stores/', views.store_list, name='store-list'),
    path('stores/<int:pk>/', views.store_detail, name='store-detail'),
]
