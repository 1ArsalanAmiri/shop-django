from django.shortcuts import render , get_object_or_404
from django.views import View
from . import models
# Create your views here.
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect

from django.http import JsonResponse

from . import forms
from zeep import Client

zarinpal = Client('https://zarinpal.com/pg/services/WebGate/wsdl')
mid = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'


def get_cart_total_price(cart):
    total = 0

    objects = models.Product.objects.filter(id__in=[int(k) for k in cart.keys()])

    for id , count in cart.items():
        obj = objects.get(id=int(id))
        total +=  (obj.price - obj.price * obj.discount) * count
    return total



def normalize_cart_keys(cart):
    return {str(k): v for k, v in cart.items()}



def get_cart(request):
    cart = request.session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}
    return normalize_cart_keys(cart)




def remove_from_cart(cart , id):
    id = str(id)
    if id in cart:
        del cart[id]



def add_to_cart(cart , obj):
    if obj.count > 0 and obj.enabled:
        cart[str(obj.id)] = cart.get(str(obj.id), 0) + 1



class ListProducts(View):
    def get(self, request):
        obj =  models.Product.objects.all()
        return render(request, 'core/product_list.html', {'products': obj})


class Button(View):
    def get (self, request):
        obj = models.Button.objects.all()


class AddToCartView(View):
    def get(self, request , id):

            obj = get_object_or_404(models.Product, id=id)
            cart = get_cart(request)
            add_to_cart(cart, obj)
            request.session['cart'] = cart

            if request.headers.get("x-requested-with") == 'XMLHttpRequest':
                #Serialization
                return JsonResponse(cart)
            return HttpResponseRedirect(reverse('core:product_list'))


class RemoveFromCartView(View):
    def get(self , request , id):
        cart =  get_cart(request)
        remove_from_cart(cart , id)
        request.session['cart'] = cart
        if request.headers.get("x-requested-with") == 'XMLHttpRequest':
            # Serialization
            return JsonResponse({'total': get_cart_total_price(cart),
                                 'cart':cart})
        return HttpResponseRedirect(reverse('core:product_list'))


class EmptyCartView(View):
    def get(self , request):
        request.session['cart'] = {}
        if request.headers.get("x-requested-with") == 'XMLHttpRequest':
            # Serialization
            return JsonResponse({'total':0 , 'cart':{} })
        return HttpResponseRedirect(reverse('core:product_list'))


class ShowCartView(View):
    def get(self, request):
        cart = get_cart(request)
        objects = models.Product.objects.filter(id__in = list(cart.keys()))
        cart_objects = {}
        for id , count in cart.items():
            obj = objects.get(id = id)
            cart_objects[id] = {
                'obj' : obj ,
                'price' : (obj.price - obj.price * obj.discount) * count ,
                'count' : count,
            }
        return render(request , 'core/cart.html' , {'cart': cart_objects ,
                                                                 'total':get_cart_total_price(cart)})

class VerifyView(View):
    pass



class CheckOutView(View):
    def get(self , request ):
        form = forms.InvoiceForm()
        cart = get_cart(request)
        objects = models.Product.objects.filter(id__in = list(cart.keys()))
        cart_objects = {}
        for id , count in cart.items():
            obj = objects.get(id = id)
            cart_objects[id] = {
                'obj' : obj ,
                'price' : (obj.price - obj.price * obj.discount) * count ,
                'count' : count,
            }
        return render(request , 'core/checkout.html' , {'form': form ,'total': get_cart_total_price(cart),
                                                        'cart': cart_objects,})

    def post(self , request ):
        form = forms.InvoiceForm(request.POST)
        if form.is_valid():
            #Create Payment
            invoice = form.save(commit=False)
            invoice.user = request.user
            cart = get_cart(request)
            invoice.total = get_cart_total_price(cart)
            invoice.save()
            items = models.Product.objects.filter(id__in = cart.keys())
            item_objects = []
            for item_id , item_count in cart.items():
                obj = items.get(id=item_id)
                invoice_item_obj = models.InvoiceItem()
                invoice_item_obj.product = obj
                invoice_item_obj.count = item_count
                invoice_item_obj.discount = obj.discount
                invoice_item_obj.price = obj.price
                invoice_item_obj.name = obj.name
                invoice_item_obj.total = invoice_item_obj.total * item_count
                invoice_item_obj.total -= invoice_item_obj.total * invoice_item_obj.discount
                # invoice_item_obj.save()
                item_objects.append(invoice_item_obj)
            models.InvoiceItem.objects.bulk_create(item_objects)
            payment = models.Payment()
            payment.total = invoice.total - invoice.total * invoice.discount
            payment.total += payment.total * invoice.vat
            payment.description = 'kharid az site ma'
            payment.user_ip = get_user_ip(request)


            callback_url = 'http://'+get_current_site(request)+reverse('core:verify')

            res = zarinpal.service.PaymentRequest(mid , payment.total,
                                                  payment.description,
                                                  invoice.user.email ,
                                                  invoice.user.phone,
                                                  callback_url)
            if res.status_code == 100:
                payment.authority = res.Authority
                payment.save()
                return redirect(f'https://sandbox.zarinpal.com/pg/StartPay/{payment.authority}')
            else:
                return render(request , 'core/checkout_error.html' , {'payment': payment})

        return render(request , 'core/checkout.html' , {'form': form })


def get_user_ip(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if not ip:
        ip = request.META.get('REMOTE_ADDR')
    return ip




class Test(View):
    def get(self , request):
        if request.headers.get("x-requested-with") == 'XMLHttpRequest':
            a = [
                {'name': 'ali',
                'age' : 20 ,
                }
            ]
        return JsonResponse(a , safe = False)


class AjaxTestPage(View):
    def get(self, request):
        return render(request , 'core/ajaxtest.html')
