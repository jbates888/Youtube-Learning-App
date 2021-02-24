from django.urls import path
from . import views

urlpatterns = [
    path('<str:name>', views.home, name='app-home'),
    #path('', views.home, name = 'app-home'),

    #  path('account/', views.account, name='app-account'),
]
