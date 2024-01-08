
from django.urls import path

from antibot.views import index

urlpatterns = [
    path('', index, name='index'),

]
