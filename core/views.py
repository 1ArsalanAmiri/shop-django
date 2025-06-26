from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Product, Invoice, InvoiceItem, Payment
from .forms import InvoiceForm
import requests
from django.contrib.auth.decorators import login_required



# تنظیمات زرین پال
ZP_API_REQUEST = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
ZP_API_STARTPAY = "https://sandbox.zarinpal.com/pg/StartPay/"
ZP_API_VERIFY = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
CALLBACK_URL = "http://127.0.0.1:8000/payment/verify/"  # آدرس بازگشتی پرداخت



def get_cart(request):
    cart = request.session.get("cart", {})
    # تضمین اینکه کلیدها رشته هستند
    return {str(k): v for k, v in cart.items()} if isinstance(cart, dict) else {}

def get_cart_total_price(cart):
    total = 0
    for pid, count in cart.items():
        try:
            product = Product.objects.get(id=int(pid))
            price = (product.price - product.price * product.discount) * count
            total += price
        except Product.DoesNotExist:
            continue
    return total

def add_to_cart(cart, obj):
    if obj.count > 0 and obj.enabled:
        cart[str(obj.id)] = cart.get(str(obj.id), 0) + 1

def remove_from_cart(cart, id):
    id = str(id)
    if id in cart:
        del cart[id]


class CheckOutView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'  # یا بهتر: reverse_lazy('login')
    def get(self, request):
        cart = get_cart(request)
        products = Product.objects.filter(id__in=cart.keys())
        form = InvoiceForm()
        return render(request, "core/checkout.html", {
            "form": form,
            "cart": cart,
            "products": products,
            "total": get_cart_total_price(cart),
        })

    def post(self, request):
        cart = get_cart(request)
        if not cart:
            return render(request, "core/checkout_error.html", {"error": "سبد خرید شما خالی است."})

        form = InvoiceForm(request.POST)
        if not form.is_valid():
            return render(request, "core/checkout.html", {"form": form})

        invoice = form.save(commit=False)
        invoice.user = request.user
        invoice.total = get_cart_total_price(cart)
        invoice.save()

        products = Product.objects.filter(id__in=cart.keys())
        items_to_create = []
        for pid, quantity in cart.items():
            product = products.get(id=int(pid))
            item = InvoiceItem(
                invoice=invoice,
                product=product,
                quantity=quantity,
                price=product.price,
                discount=product.discount,
                name=product.name,
            )
            item.total = (item.price * item.quantity) * (1 - item.discount)
            items_to_create.append(item)
        InvoiceItem.objects.bulk_create(items_to_create)

        payment = Payment.objects.create(
            invoice=invoice,
            total=invoice.total,
            description="پرداخت از سایت ما",
            user_ip=request.META.get("REMOTE_ADDR"),
            authority="",  # بعد از گرفتن Authority ذخیره می‌کنیم
            status=Payment.STATUS_PENDING,
        )

        data = {
            "merchant_id": settings.MERCHANT,
            "amount": int(invoice.total),
            "description": "پرداخت از سایت",
            "callback_url": CALLBACK_URL,
        }

        try:
            response = requests.post(ZP_API_REQUEST, json=data, headers={"content-type": "application/json"}, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            return render(request, "core/checkout_error.html", {"error_code": f"خطا در ارتباط با درگاه: {e}"})

        res_data = response.json()
        if res_data.get('data', {}).get('code') == 100:
            authority = res_data['data']['authority']
            payment.authority = authority
            payment.save()
            return HttpResponseRedirect(ZP_API_STARTPAY + authority)
        else:
            error_code = res_data.get('errors', {}).get('code', 'نامشخص')
            return render(request, "core/checkout_error.html", {"error_code": error_code})


class VerifyView(View):
    def get(self, request):
        status = request.GET.get('Status')
        authority = request.GET.get('Authority')

        if status == "OK" and authority:
            try:
                payment = Payment.objects.get(authority=authority, status=Payment.STATUS_PENDING)
            except Payment.DoesNotExist:
                return render(request, 'core/payment_failed.html')

            verify_data = {
                "merchant_id": settings.MERCHANT,
                "authority": authority,
                "amount": int(payment.total),
            }
            try:
                response = requests.post(ZP_API_VERIFY, json=verify_data, headers={"content-type": "application/json"}, timeout=10)
                response.raise_for_status()
            except requests.RequestException:
                payment.status = Payment.STATUS_ERROR
                payment.save()
                return render(request, 'core/payment_failed.html')

            res_data = response.json()
            if res_data.get("data", {}).get("code") == 100:
                payment.status = Payment.STATUS_DONE
                payment.RefID = str(res_data["data"]["ref_id"])
                payment.save()
                return render(request, 'core/payment_done.html', {'refid': payment.RefID})
            else:
                payment.status = Payment.STATUS_ERROR
                payment.save()
                return render(request, 'core/payment_failed.html')

        return render(request, 'core/payment_failed.html')


# Cart Views

class AddToCartView(View):
    def get(self, request, id):
        obj = get_object_or_404(Product, id=id)
        cart = get_cart(request)
        add_to_cart(cart, obj)
        request.session["cart"] = cart
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(cart)
        return HttpResponseRedirect(reverse("core:product_list"))

class RemoveFromCartView(View):
    def get(self, request, id):
        cart = get_cart(request)
        remove_from_cart(cart, id)
        request.session["cart"] = cart
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"total": get_cart_total_price(cart), "cart": cart})
        return HttpResponseRedirect(reverse("core:product_list"))

class EmptyCartView(View):
    def get(self, request):
        request.session["cart"] = {}
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"total": 0, "cart": {}})
        return HttpResponseRedirect(reverse("core:product_list"))

class ShowCartView(View):
    def get(self, request):
        cart = get_cart(request)
        products = Product.objects.filter(id__in=list(cart.keys()))
        cart_objects = {}
        for pid, count in cart.items():
            product = next((p for p in products if p.id == int(pid)), None)
            if product:
                price = (product.price - product.price * product.discount) * count
                cart_objects[str(pid)] = {
                    "obj": product,
                    "price": price,
                    "count": count,
                }
        return render(request, 'core/cart.html', {'cart': cart_objects, 'total': get_cart_total_price(cart)})


class ListProducts(View):
    def get(self, request):
        products = Product.objects.all()
        return render(request, "core/product_list.html", {"products": products})




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Product
from . import serializers


class ProductListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = serializers.ProductListSerializer(products, many=True)
        return Response(serializer.data)

def home_view(request):
    return render(request, 'bits/home.html')

