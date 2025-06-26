from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

app_name = 'account'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('activate/<uid>/<hash>/', views.ActivateView.as_view(), name='activate'),
    path('login/', LoginView.as_view(template_name='account/login.html'), name='login'),
]
