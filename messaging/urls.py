from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('messages/', views.MessageList.as_view()),
    path('messages/csv/', views.MessageListCsv.as_view()),
    path('messages/create/', views.MessageCreate.as_view()),
    path('messages/<int:pk>/', views.MessageDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
