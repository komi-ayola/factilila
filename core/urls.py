# core/urls.py
from django.urls import path
from .views import home, whoami

app_name = 'core'

urlpatterns = [
    path('', home, name='home'),
    path('whoami/', whoami, name='whoami')

]
