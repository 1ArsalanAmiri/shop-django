from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

app_name = 'account'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('activate/<uid>/<hash>/', views.ActivateView.as_view(), name='activate'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('contact/', views.contact_us, name='product_contact'),
    path('about/', views.about_us, name='product_about'),
    path('privacy/', views.privacy, name='product_privacy'),
]
