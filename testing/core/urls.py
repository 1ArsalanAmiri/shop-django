from django.urls import include, path , re_path , include
from . import views


app_name = 'core'
urlpatterns = [
    # path('', views.ListProducts.as_view(), name='product_list'),
    path('', views.ListProducts.as_view(), name='product_list'),
    path('cart/add/<int:id>', views.AddToCartView.as_view(), name='cart_add'),
    path('cart/remove/<int:id>', views.RemoveFromCartView.as_view(), name='cart_remove'),
    path('cart/empty', views.EmptyCartView.as_view(), name='cart_empty'),
    path('cart', views.ShowCartView.as_view(), name='cart_show'),
    path('checkout', views.CheckOutView.as_view(), name='checkout'),
    path('checkout', views.CheckOutView.as_view(), name='checkout'),
    path('verify' , views.VerifyView.as_view(), name='verify'),

    # path('ajaxtestpage', views.AjaxTestPage.as_view()),
    # path('testjson', views.Test.as_view())


]
