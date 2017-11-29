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
        'name': 'ㅎㅇㅎㅇ',
    }
    return render(request, 'all/index.html', data)

def login(request):
    login_fail = None
    login_fail_message = None

    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        username = request.POST['user_id']
        password = request.POST['user_pw']

        user = authenticate(username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return HttpResponseRedirect('/')
        else:
            login_fail = True
            login_fail_message = '아이디나 비밀번호가 올바르지 않습니다.'

    data = {
        'login_fail': login_fail,
        'login_fail_message': login_fail_message,
    }

    return render(request, 'all/login.html', data)

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')

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
        'spot': ret,
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

def my(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    userinfo = Manager.objects.filter(user=request.user)
    if userinfo.count() != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    pw_fail = None
    pw_fail_message = None
    pw_success = None
    pw_success_message = None
    if request.method == 'POST':
        if request.POST['form-type'] == 'edit-pw':
            pw = request.POST['user-pw']
            pw1 = request.POST['user-pw1']
            pw2 = request.POST['user-pw2']
            user = authenticate(username=userinfo.user.username, password=pw)
            if user:
                if pw1 == pw2:
                    user.set_password(pw1)
                    user.save()
                    auth_login(request, user)
                    pw_success = True
                    pw_success_message = '비밀번호를 변경하였습니다.'
                else:
                    pw_fail = True
                    pw_fail_message = '재입력한 비밀번호가 새 비밀번호와 다릅니다.'
            else:
                pw_fail = True
                pw_fail_message = '현재 비밀번호가 올바르지 않습니다.'
        elif request.POST['form-type'] == 'edit-info':
            name = request.POST['user-name']
            cell = request.POST['user-cell']
            userinfo = Manager.objects.get(user=request.user)
            userinfo.name = name
            userinfo.cell = cell
            userinfo.save()
    data = {
        'userinfo': userinfo,
        'pw_fail': pw_fail,
        'pw_fail_message': pw_fail_message,
        'pw_success': pw_success,
        'pw_success_message': pw_success_message,
    }
    return render(request, 'all/my.html', data)

def manage(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    userinfo = Manager.objects.filter(user=request.user)
    if userinfo.count() != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    if not userinfo.charge:
        return HttpResponseRedirect('/')
    users = Manager.objects.all()
    data = {
        'userinfo': userinfo,
        'users': users,
    }
    return render(request, 'all/manage.html', data)

def manage_edit(request, user_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    userinfo = Manager.objects.filter(user=request.user)
    if userinfo.count() != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    if not userinfo.charge:
        return HttpResponseRedirect('/')
    userinfo = Manager.objects.filter(pk=user_id)
    if userinfo.count() != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    cctvs =  Cctv.objects.filter(manager=userinfo)
    data = {
        'userinfo': userinfo,
        'cctvs': cctvs,
    }
    return render(request, 'all/manage_edit.html', data)