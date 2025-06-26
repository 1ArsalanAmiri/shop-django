from django.urls import include, path , re_path , include
from . import views

from .views import CheckOutView


app_name = 'core'
urlpatterns = [
    # path('', views.ListProducts.as_view(), name='product_list'),
    path('', views.ListProducts.as_view(), name='product_list'),
    path('', views.home_view, name='home'),
    path('cart/', views.ShowCartView.as_view(), name='cart_detail'),
    path('cart/add/<int:id>', views.AddToCartView.as_view(), name='cart_add'),
    path('cart/remove/<int:id>', views.RemoveFromCartView.as_view(), name='cart_remove'),
    path('cart/empty', views.EmptyCartView.as_view(), name='cart_empty'),
    path('cart', views.ShowCartView.as_view(), name='cart_show'),
    path('checkout/', CheckOutView.as_view(), name='checkout'),
    path('payment/verify/', views.VerifyView.as_view(), name='verify'),

    path('api/product', views.ProductListAPIView.as_view(), name='api_product'),


    # path('ajaxtestpage', views.AjaxTestPage.as_view()),
    # path('testjson', views.Test.as_view())
]

