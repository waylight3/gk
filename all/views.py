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

def spot_specific(request, spot_id):
    cctv = None
    spot = None
    if Spot.objects.filter(pk=spot_id).count() > 0:
        spot = Spot.objects.get(pk=spot_id)
    cctv = Cctv.objects.all()
    if request.method == 'POST':
        if request.POST['form-type'] == 'edit-info':
            pw = request.POST['user-pw']
            name = request.POST['user-name']
            manager_id = request.POST['manager-id']
            spot.manager = Manager.objects.get(pk=manager_id)
            cctv.save()
        elif request.POST['form-type'] == 'add-cctv':
            cctv_id = request.POST['cctv-id']
            cctv = Cctv.objects.get(pk=cctv_id)
            exist_flag = False
            for c in spot.cctvs.all():
                if c == cctv:
                    exist_flag = True
                    #print("already exist")
                    break
            if exist_flag == False:
                spot.cctvs.add(cctv)
                cctv.save()
    data = {
        'cctv': cctv,
        'spot': spot,
    }

    return render(request, 'all/spot_specific.html', data)

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

def cctv_specific(request, cctv_id):
    cctv = None
    meta = None
    row = []
    if Cctv.objects.filter(pk=cctv_id).count() > 0:
        cctv = Cctv.objects.get(pk=cctv_id)
        if Meta.objects.filter(cctv=cctv).count() > 0:
            meta = Meta.objects.filter(cctv=cctv)
            for m in meta:
                if Row.objects.filter(meta=m.pk).count() > 0:
                    row.append(Row.objects.filter(meta=m.pk)[0])
    spot = Spot.objects.all()
    if request.method == 'POST':
        if request.POST['form-type'] == 'edit-info':
            pw = request.POST['user-pw']
            name = request.POST['user-name']
            manager_id = request.POST['manager-id']
            #cctv.name = name
            #cctv.cell = cell
            cctv.manager = Manager.objects.get(pk=manager_id)
            cctv.save()
        elif request.POST['form-type'] == 'add-spot':
            spot_id = request.POST['spot-id']
            spot = Spot.objects.get(pk=spot_id)
            exist_flag = False
            for s in cctv.spots.all():
                if s == spot:
                    exist_flag = True
                    #print("already exist")
                    break
            if exist_flag == False:
                cctv.spots.add(spot)
                cctv.save()
    data = {
        'cctv': cctv,
        'spot': spot,
        'meta': meta,
        'row': row,
    }

    return render(request, 'all/cctv_specific.html', data)

def cctv_remove_spot(request, cctv_id, spot_id):
    cctv = Cctv.objects.filter(pk=cctv_id)
    if cctv.count() != 1:
        return HttpResponseRedirect('/')
    cctv = cctv[0]
    #cctv.spots.through.objects.filter(pk=spot_id).delete()
    spot = Spot.objects.filter(pk=spot_id)
    if spot.count() != 1:
        return HttpResponseRedirect('/')
    for s in cctv.spots.all():
        if s == spot[0]:
            cctv.spots.remove(s)
    cctv.save()
    return HttpResponseRedirect('/cctv_specific/%s' % cctv_id)

def cctv_remove_row(request, cctv_id, row_id):
    cctv = Cctv.objects.filter(pk=cctv_id)
    print("HI")
    if cctv.count() != 1:
        return HttpResponseRedirect('/')
    cctv = cctv[0]
    #cctv.spots.through.objects.filter(pk=spot_id).delete()
    row = Row.objects.filter(pk=row_id)
    if row.count() != 1:
        return HttpResponseRedirect('/')
    row.delete()

    return HttpResponseRedirect('/cctv_specific/%s' % cctv_id)

def neighbor(request):
    ret = Neighbor.objects.all()
    if request.method == 'POST':
        o = request.POST.get('option', False)
        q = request.POST['neighbor_query']
        n = Neighbor.objects.filter(name=q)
        print(n)
        if o == 'name':
            if n.count()>0: 
                ret = n
            else:
                ret = None
        elif o == 'spot':
            ret = []
            for s in Spot.objects.filter(indoor_loc=q):
                for n in Neighbor.objects.filter(spot1=s):
                    if not n in ret:
                        ret.append(n)
                for n in Neighbor.objects.filter(spot2=s):
                    if not n in ret:
                        ret.append(n)
    data = {
        'neighbor': ret,
    }
    return render(request, 'all/neighbor.html', data)

def neighbor_specific(request, neighbor_id):
    if Neighbor.objects.filter(pk=neighbor_id).count() > 0:
        neighbor = Neighbor.objects.get(pk=neighbor_id)
    spot = Spot.objects.all()
    if request.method == 'POST':
        if request.POST['form-type'] == 'edit-info':
            name = request.POST['neighbor-name']
            neighbor.name = name
            neighbor.save()
    data = {
        'neighbor': neighbor
    }

    return render(request, 'all/neighbor_specific.html', data)


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
    users = Manager.objects.filter(charge=False)
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
    user = User.objects.filter(pk=user_id)
    if user.count() != 1:
        return HttpResponseRedirect('/')
    user = user[0]
    userinfo = Manager.objects.get(user=user)
    if request.method == 'POST':
        if request.POST['form-type'] == 'edit-info':
            pw = request.POST['user-pw']
            name = request.POST['user-name']
            cell = request.POST['user-cell']
            user.name = name
            user.cell = cell
            user.set_password(pw)
            user.save()
        elif request.POST['form-type'] == 'add-cctv':
            cctv_id = request.POST['cctv-id']
            cctv = Cctv.objects.get(pk=cctv_id)
            cctv.manager = userinfo
            cctv.save()
    cctvs =  Cctv.objects.filter(manager=userinfo)
    data = {
        'userinfo': userinfo,
        'cctvs': cctvs,
    }
    return render(request, 'all/manage_edit.html', data)

def manage_remove_user(request, user_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    userinfo = Manager.objects.filter(user=request.user)
    if userinfo.count() != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    if not userinfo.charge:
        return HttpResponseRedirect('/')
    user = User.objects.filter(pk=user_id)
    if user.count() != 1:
        return HttpResponseRedirect('/')
    user = user[0]
    user.delete()
    return HttpResponseRedirect('/manage')

def manage_remove_cctv(request, user_id, cctv_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    userinfo = Manager.objects.filter(user=request.user)
    if userinfo.count() != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    if not userinfo.charge:
        return HttpResponseRedirect('/')
    user = User.objects.filter(pk=user_id)
    if user.count() != 1:
        return HttpResponseRedirect('/')
    user = user[0]
    cctv = Cctv.objects.filter(pk=cctv_id)
    if cctv.count() != 1:
        return HttpResponseRedirect('/')
    cctv = cctv[0]
    cctv.manager = None
    cctv.save()
    return HttpResponseRedirect('/manage/edit/%s' % user_id)

def api(request, query):
    q = query.split('/')
    print(q)
    if q[0] == 'cctv_list':
        if request.GET['user_id'] != '-1':
            user = User.objects.get(pk=request.GET['user_id'])
            manager = Manager.objects.get(user=user)
            cctvs = Cctv.objects.filter(manager=manager)
        else:
            cctvs = Cctv.objects.all()
        names = [{'id':c.pk, 'name':c.name, 'start_date':str(c.start_date), 'spots':' '.join([s.address for s in c.spots.all()]) } for c in cctvs]
        jsondata = json.dumps(names)
        return HttpResponse(jsondata, content_type='application/json')
    elif q[0] == 'spot_list':
        spot = Spot.objects.all()
        names = [{'id':s.pk, 'indoor_loc':s.indoor_loc, 'floor_no':s.floor_no, 'dep_name':s.dep_name, 'address':s.address} for s in spot]
        jsondata = json.dumps(names)
        return HttpResponse(jsondata, content_type='application/json')
