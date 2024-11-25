from django.http import HttpResponse
from django.shortcuts import render, redirect
# Remove the request import from context_processors as it's not needed
# from django.template.context_processors import request

from .forms import AppointmentForm  # Use relative import
from .models import Appointment, Member, Contact  # Group model imports
import requests  # For making HTTP requests
import json  # For JSON handling

# Remove unused imports:
# from enum import member

from .credentials import MpesaAccessToken, LipanaMpesaPpassword
from .forms import ImageUploadForm
from .models import ImageModel


# Create your views here.
def index(request):
    if request.method == 'POST':
        if Member.objects.filter(
            username=request.POST['username'],
            password=request.POST['password'],
        ).exists():
            return render(request, 'index.html')
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


def services(request):
    return render(request, 'service-details.html')
def starter(request):
    return render(request, 'starter-page.html')
def about(request):
    return render(request, 'about.html')
def doctors(request):
    return render(request, 'doctors/index.html')
def myservice(request):
    return render(request, 'services.html')
def appointment(request):
   if request.method == 'POST':
       myappointment= Appointment(
           name=request.POST['name'],
           email=request.POST['email'],
           phone=request.POST['phone'],
           date=request.POST['date'],
           department=request.POST['department'],
           doctor=request.POST['doctor'],
           message=request.POST['message']
       )
       myappointment.save()
       return redirect('/show')
   else:
       return render(request, 'appointment.html')

def contact(request):
    if request.method =='POST':
        contactus=Contact(
            name=request.POST['name'],
            email=request.POST['email'],
            subject=request.POST['subject'],
            message=request.POST['message']

        )
        contactus.save()
        return redirect('/contact')
    else:
        return render(request, 'contact.html')


def show(request):
    allappointments=Appointment.objects.all()
    return render(request, 'show.html', {'appointment':allappointments})
def delete(request, id):
    appoint=Appointment.objects.get(id=id)
    appoint.delete()
    return redirect('/show')

def contactshow(request):
    contactus=Contact.objects.all()
    return render(request, 'contactshow.html', {'contact':contactus})

def delete(request, id):
    contact=Contact.objects.get(id=id)
    contact.delete()
    return redirect('/contactshow')

def edit(request, id):
    editappointment=Appointment.objects.get(id=id)
    return render(request, 'edit.html',{'appointment':editappointment})

def update(request, id):
   updateinfo=Appointment.objects.get(id=id)
   form=AppointmentForm(request.POST, instance=updateinfo)
   if form.is_valid():
       form.save()
       return redirect('/show')
   else:
       return render(request, 'edit.html')

def register(request):
    if request.method == 'POST':
        members =Member(
            name = request.POST['name'],
            username=request.POST['username'],
            password=request.POST['password']
        )
        members.save()
        return redirect('/login')
    else:
        return render(request, 'register.html')


def login(request):
    return render(request, 'login.html')

def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/showimage')
    else:
        form = ImageUploadForm()
    return render(request, 'upload_image.html', {'form': form})

def show_image(request):
    images = ImageModel.objects.all()
    return render(request, 'show_image.html', {'images': images})

def imagedelete(request, id):
    image = ImageModel.objects.get(id=id)
    image.delete()
    return redirect('/showimage')


class HTTPBasicAuth:
    pass


def token(request):
    consumer_key = 'HOhhHUPcYJVolZ5cDMfyrLihi2q0TPmpJv0rhWqCoLX9UBWW'
    consumer_secret = 'tvYAVaekVPPcVpgWByLUY1AGBAKTCaprt4Gz1n44rvGitUcDEx9K5RCreAOT9ps6'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'token.html', {"token":validated_mpesa_access_token})

def pay(request):
   return render(request, 'pay.html')



def stk(request):
    if request.method =="POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        request = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
            "AccountReference": "eMobilis",
            "TransactionDesc": "Web Development Charges"
        }
        response = requests.post(api_url, json=request, headers=headers)
        return HttpResponse("Success")