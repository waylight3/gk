from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.db.models import Q
from datetime import datetime, date, timezone
from ipware.ip import get_ip
import html, difflib, json
from django.core.mail import send_mail
from django.http import JsonResponse
from all.models import *

def index(request):
    data = {
        'name':'ㅎㅇㅎㅇ',
    }
    return render(request, 'all/index.html', data)

def spot(request):
    ret = Spot.objects.all()
    if request.method == 'POST':
        o = request.POST.get('option', False)
        q = request.POST['spot_query']
        c = Cctv.objects.filter(name=q)
        print(c)
        if c.count()>0: 
            ret = Spot.objects.filter(cctv=c)
        else:
            ret = None
    data = {
        'spot' : ret,
    }
    return render(request, 'all/spot.html', data)

def cctv(request):
    ret = Cctv.objects.all()
    if request.method == 'POST':
        o = request.POST['option']
        q = request.POST['cctv_query']
        print(o)
        if o == 'name':
            ret = Cctv.objects.filter(name=q)
        elif o == 'start_date':
            ret = Cctv.objects.filter(start_date=q)
        elif o == 'manager':
            if Manager.objects.filter(name=q).count() > 0:
                m = Manager.objects.get(name=q)
                ret = Cctv.objects.filter(manager=m)
            else:
                ret = None
    data = {
        'cctv': ret,
    }
    return render(request, 'all/cctv.html', data)
