
from django.shortcuts import render
from django import views
from . import forms , models
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes , force_str
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.urls import reverse
from account.tokens import activation_token_generator


# Create your views here.
class SignUpView(views.View):


    def get(self,request):
        #show the signup form
        form = forms.SignUpForm()
        return render(request, 'account/signup.html', {'form':form})


    def post(self , request):
        #create new user and send email
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False) #create obj and saves it into Database
            obj.is_active = False
            obj.save()

            subject = 'Thank you for signing up , Please activate your account'

            uid = urlsafe_base64_encode(force_bytes(obj.pk))

            token = activation_token_generator.make_token(obj)

            activation_link = request.build_absolute_uri(
                reverse('account:activate' , kwargs={'uid':uid , 'hash':token})
            )

            send_mail(
                subject,
                f'Hi {obj.username}, click the link to activate your account:\n{activation_link}',
                'prodarsalan808@gmail.com',
                [obj.email],
                fail_silently=False,
            )
            return render(request, 'account/signup_done.html', {'obj':obj})
        return render(request, 'account/signup.html', {'form':form})



class ActivateView(views.View):
    def get(self , request , uid , hash ):

        # NOTE: ALL VIEWS MUST ALWAYS RETURN HTTPResponse
        id = force_str(urlsafe_base64_decode(uid))

        user = get_object_or_404(models.User , id = id)

        if user.is_active:
            return render(request , 'account/activate_error.html')

        if activation_token_generator.check_token(user , hash):
            user.is_active = True
            user.save()
            return render(request , 'account/activate_done.html')
        return render(request, 'account/activate_error.html')