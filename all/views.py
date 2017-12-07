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
import datetime, csv, os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import mimetypes
from django.db import connection

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
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    #userinfo1 = Manager.objects.filter(user=request.user)
    userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '"+str(request.user.pk)+"'")
    #print(list(userinfo.query))
    #print("I'm alive")
    #print(userinfo)
    if len(list(userinfo.query)) != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    ret = []
    if userinfo.charge:
        #ret = Spot.objects.all()
        ret = Spot.objects.raw("SELECT `all_spot`.`id`, `all_spot`.`indoor_loc`, `all_spot`.`floor_no`, `all_spot`.`dep_name`, `all_spot`.`address` FROM `all_spot`")
        #print(ret.query)
        #cc = Cctv.objects.all()
        cc = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv`")
        #print(cc.query)
    else:
        #cc = Cctv.objects.filter(manager=userinfo)
        cc = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`manager_id` = '%s'"% userinfo.pk)
        for i in range(len(list(cc.query))):
            #spot = Spot.objects.filter(spot_cctvs=(cc[i]))
            spot = Spot.objects.raw("SELECT `all_spot`.`id`, `all_spot`.`indoor_loc`, `all_spot`.`floor_no`, `all_spot`.`dep_name`, `all_spot`.`address` FROM `all_spot` INNER JOIN `all_cctv_spots` ON (`all_spot`.`id` = `all_cctv_spots`.`spot_id`) WHERE `all_cctv_spots`.`cctv_id` = '%s'" % cc[i].pk)
            #print(cc[i].pk)
            #print(spot.query)
            for j in range(len(list(spot))):
                if not spot[j] in ret:
                    ret = ret + [spot[j]]
                #print(spot[0])
    if request.method == 'POST':
        o = request.POST['option']
        q = request.POST['spot_query']
        #c = Cctv.objects.filter(name=q)
        c = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`name` = '%s'" % q)
        #print(c.query) 
        #ret = Spot.objects.filter(spot_cctvs=c)
        ret = Spot.objects.raw("SELECT `all_spot`.`id`, `all_spot`.`indoor_loc`, `all_spot`.`floor_no`, `all_spot`.`dep_name`, `all_spot`.`address` FROM `all_spot` INNER JOIN `all_cctv_spots` ON (`all_spot`.`id` = `all_cctv_spots`.`spot_id`) WHERE `all_cctv_spots`.`cctv_id` = (SELECT U0.`id` AS Col1 FROM `all_cctv` U0 WHERE U0.`name` = '%s')" %q)
        #print(ret.query)
    data = {
        'spot': ret,
        'cctv': cc,
    }
    return render(request, 'all/spot.html', data)

def spot_specific(request, spot_id):
    cc = None
    #temp = Spot.objects.filter(pk=spot_id)
    spot = Spot.objects.raw("SELECT `all_spot`.`id`, `all_spot`.`indoor_loc`, `all_spot`.`floor_no`, `all_spot`.`dep_name`, `all_spot`.`address` FROM `all_spot` WHERE `all_spot`.`id` = '%s'" % spot_id)
    #print(spot.query)
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    #userinfo1 = Manager.objects.filter(user=request.user)
    userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '"+str(request.user.pk)+"'")
    if len(list(userinfo.query)) != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    ret = []
    #print(userinfo.charge)
    if userinfo.charge:
        #ret = Spot.objects.all()
        ret = Spot.objects.raw("SELECT `all_spot`.`id`, `all_spot`.`indoor_loc`, `all_spot`.`floor_no`, `all_spot`.`dep_name`, `all_spot`.`address` FROM `all_spot`")
        #print(ret.query)
        #cc = Cctv.objects.all()
        cc = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv`")
        #print(cc.query)
    else:
        cc = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`manager_id` = '%s'"% userinfo.pk)
        #print(cc)
    if len(list(spot)) > 0:
        spot = Spot.objects.raw("SELECT `all_spot`.`id`, `all_spot`.`indoor_loc`, `all_spot`.`floor_no`, `all_spot`.`dep_name`, `all_spot`.`address` FROM `all_spot` WHERE `all_spot`.`id` = '%s'" % spot_id)
        #temp = Spot.objects.filter(pk=spot_id)
        #spot = Spot.objects.get(pk=spot_id)
        spot = spot[0]
        #print(temp[0])
        #print(spot)
    # if request.method == 'POST':
    #     if request.POST['form-type'] == 'edit-info':
    #         pw = request.POST['user-pw']
    #         name = request.POST['user-name']
    #         manager_id = request.POST['manager-id']
    #         temp = Manager.objects.filter(pk=manager_id)
    #         print(temp.query)
    #         spot.manager = Manager.objects.get(pk=manager_id)
    #         cctv.save()
    #     elif request.POST['form-type'] == 'add-cctv':
    #         cctv_id = request.POST['cctv-id']
    #         cctv = Cctv.objects.get(pk=cctv_id)
    #         exist_flag = False
    #         for c in spot.cctvs.all():
    #             if c == cctv:
    #                 exist_flag = True
    #                 #print("already exist")
    #                 break
    #         if exist_flag == False:
    #             spot.cctvs.add(cctv)
    #             cctv.save()
    # ctrl + /
    data = {
        'cctv': cc,
        'spot': spot,
    }

    return render(request, 'all/spot_specific.html', data)

def cctv(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    #userinfo = Manager.objects.filter(user=request.user)
    userinfo = Manager.objects.raw("SELECT * FROM `all_manager` WHERE `all_manager`. `user_id` = " + str(request.user.pk))
    #print(userinfo_raw[0].charge)
    #if userinfo.count() != 1:
    if len(list(userinfo)) != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    auth = None
    ret = None
    if userinfo.charge:
        auth = "charged"
        #ret = Cctv.objects.all()
        ret = Cctv.objects.raw("SELECT * FROM `all_cctv`")
    else:
        auth = "un-charged"
        #ret = Cctv.objects.filter(manager=userinfo.pk)
        ret = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`manager_id` = "+str(userinfo.pk))
        #print(str(ret.query))
    if request.method == 'POST':
        if request.POST.get('form-type', False) == 'file-upload':
            file_meta = request.FILES['new-cctvs']
            rows = file_meta.read().decode().split('\n')
            for r in rows:
                rs = r.split(',')
                if len(rs) != 3: break
                name = rs[0]
                date = rs[1]
                #manager = Manager.objects.filter(pk=rs[2])
                manager = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`id` = "+str(rs[2]))
                #print(str(manager.query))
                if len(list(manager)) != 1:
                    return HttpResponseRedirect('/cctv')
                manager = manager[0]
                ts = datetime.datetime(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2].split('T')[0]), int(date.split('T')[1].split(':')[0]), int(date.split('T')[1].split(':')[1]), 0, 0)
                #Cctv.objects.create(name=name, start_date=ts, manager=manager)
                with connection.cursor() as c:
                    c.execute(
                        "INSERT INTO `all_cctv` (`name`, `start_date`, `manager_id`) VALUES ('%s', '%s', '%s')" % (
                        name, ts, str(manager.pk)))
            return HttpResponseRedirect('/cctv')
        elif request.POST.get('option', False) == False:
            date = request.POST['cctv-date']
            #Cctv.objects.create(name=request.POST['cctv-name'], start_date=datetime.datetime(int(date.split('-')[0]), int(date.split('-')[1]),
            #                  int(date.split('-')[2].split('T')[0]), int(date.split('T')[1].split(':')[0]),
            #                  int(date.split('T')[1].split(':')[1]), 0, 0), manager=Manager.objects.get(pk=request.POST['manager-id']))
            with connection.cursor() as c:
                c.execute(
                    "INSERT INTO `all_cctv` (`name`, `start_date`, `manager_id`) VALUES ('%s', '%s', '%s')" % (
                    request.POST['cctv-name'],
                    datetime.datetime(int(date.split('-')[0]), int(date.split('-')[1]),
                                          int(date.split('-')[2].split('T')[0]), int(date.split('T')[1].split(':')[0])),
                    request.POST['manager-id']))

        else:
            o = request.POST['option']
            q = request.POST['cctv_query']
            if userinfo.charge:
                if o == 'name':
                    #ret = Cctv.objects.filter(name=q)
                    ret = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`name` = '"+str(q)+"'")
                elif o == 'start_date':
                    date = q
                    d = datetime.datetime(int(date.split('-')[0]), int(date.split('-')[1]),
                                      int(date.split('-')[2].split('T')[0]), int(date.split('T')[1].split(':')[0]),
                                      int(date.split('T')[1].split(':')[1]), 0, 0)
                    #ret = Cctv.objects.filter(start_date=d)
                    ret = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`start_date` = '"+str(d)+"'")
                elif o == 'manager':
                    m = Manager.objects.raw(
                        "SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`name` = '" + str(
                            q) + "'")
                    if len(list(m)) > 0:
                        #m = Manager.objects.filter(name=q)
                        #print(m.query)
                        #ret = Cctv.objects.filter(manager=m[0])
                        ret = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`manager_id` = '"+str(m[0].pk)+"'")
                    else:
                        ret = None
            else:
                ret = None
    data = {
        'cctv': ret,
        'auth': auth,
    }
    return render(request, 'all/cctv.html', data)

def cctv_specific(request, cctv_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    userinfo = Manager.objects.raw("SELECT * FROM `all_manager` WHERE `all_manager`. `user_id` = '%s'" % request.user.pk)
    if len(list(userinfo)) != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    auth = "un-charged"
    if userinfo.charge:
        auth = "charged"
    #cctv = Cctv.objects.filter(pk=cctv_id)
    cctv = Cctv.objects.raw("SELECT * FROM `all_cctv` WHERE `all_cctv`.`id` = '%s'" % cctv_id)
    if len(list(cctv)) != 1:
        return HttpResponseRedirect('/cctv')
    cctv = cctv[0]
    if cctv.manager.pk != userinfo.pk and userinfo.charge == False:
        return HttpResponseRedirect('/cctv')
    meta_list = []
    #metamon = Meta.objects.filter(cctv=cctv)
    for m in Meta.objects.raw("SELECT * FROM `all_meta` WHERE `all_meta`.`cctv_id` = '%s'" % cctv.pk):
        avg_size, avg_xpos, avg_ypos, avg_speed = 0, 0, 0, 0
        objs = set()
        time_min = None
        time_max = None
        #metamon = Row.objects.filter(meta=m)
        meta_row = Row.objects.raw("SELECT * FROM `all_row` WHERE `all_row`.`meta_id` = '%s'" % m.pk)
        for r in meta_row:
            avg_size += r.size
            avg_xpos += r.xpos
            avg_ypos += r.ypos
            avg_speed += r.speed
            objs.add(r.obj_id)
            if time_min == None or time_min > r.time_stamp:
                time_min = r.time_stamp
            if time_max == None or time_max < r.time_stamp:
                time_max = r.time_stamp
        cnt = len(list(meta_row))
        if cnt != 0:
            avg_size /= cnt
            avg_xpos /= cnt
            avg_ypos /= cnt
            avg_speed /= cnt
            dtime = time_max - time_min
            meta_list.append({'pk': m.pk, 'name': m.name, 'cctv': m.cctv, 'video': m.video, 'avg_size': avg_size,
                              'avg_xpos': avg_xpos, 'avg_ypos': avg_ypos, 'avg_speed': avg_speed, 'rec_no': cnt,
                              'obj_no': len(objs), 'time_len': '%s:%s:%s' % (
                dtime.seconds // 3600, dtime.seconds % 3600 // 60, dtime.seconds % 60)})
    #spot = Spot.objects.all()
    spot = Spot.objects.raw("SELECT * FROM `all_spot`")
    if request.method == 'POST':
        if request.POST['form-type'] == 'edit-info':
            name = request.POST['cctv-name']
            date = request.POST['cctv-date']
            manager_id = request.POST['manager-id']
            cctv.name = name
            cctv.start_date = datetime.datetime(int(date.split('-')[0]), int(date.split('-')[1]),
                                                int(date.split('-')[2].split('T')[0]), int(date.split('T')[1].split(':')[0]),
                                                int(date.split('T')[1].split(':')[1]), 0, 0)
            #manager_list = Manager.objects.filter(pk=manager_id)
            manager_list = Manager.objects.raw("SELECT * FROM `all_manager` WHERE `all_manager`.`id` = '%s'" % manager_id)
            if len(list(manager_list)) == 1:
                cctv.manager = manager_list[0]
            cctv.save()
        elif request.POST['form-type'] == 'add-spot':
            spot_id = request.POST['spot-id']
            #spot = Spot.objects.filter(pk=spot_id)
            spot = Spot.objects.raw("SELECT * FROM `all_spot` WHERE `all_spot`.`id` = '%s'" % spot_id)
            exist_flag = False
            for s in cctv.spots.all():
                if s == spot[0]:
                    exist_flag = True
                    break
            if exist_flag == False:
                cctv.spots.add(spot[0])
                cctv.save()
        elif request.POST['form-type'] == 'file-upload':
            file_video = request.FILES['new-video']
            file_meta = request.FILES['new-meta']
            default_storage.save('%s' % file_video.name, ContentFile(file_video.read()))
            #video = Video.objects.create(name=''.join(file_video.name.split('.')[:-1]), ext=file_video.name.split('.')[-1], cctv=cctv)
            with connection.cursor() as c:
                c.execute(
                    "INSERT INTO `all_video` (`name`, `ext`, `cctv_id`) VALUES ('%s', '%s', '%s')" % (
                        ''.join(file_video.name.split('.')[:-1]),
                        file_video.name.split('.')[-1],
                        str(cctv.pk)))
            videos = Video.objects.raw("SELECT `all_video`.`id`, `all_video`.`name`, `all_video`.`ext`, `all_video`.`cctv_id` FROM `all_video`")
            video = None
            for v in videos:
                if video == None:
                    video = v
                elif video.pk < v.pk:
                    video = v
            #mmeta = Meta.objects.create(name=file_meta.name, cctv=cctv, video=video)
            with connection.cursor() as c:
                c.execute(
                    "INSERT INTO `all_meta` (`name`, `cctv_id`, `video_id`) VALUES ('%s', '%s', '%s')" % (
                        file_meta.name,
                        str(cctv.pk),
                        str(video.pk)))
            mmetas = Meta.objects.raw("SELECT * FROM `all_meta`")
            mmeta = None
            for mm in mmetas:
                if mmeta == None:
                    mmeta = mm
                elif mmeta.pk < mm.pk:
                    mmeta = mm
            rows = file_meta.read().decode().split('\n')
            for r in rows:
                rs = r.split(',')
                if len(rs) != 7: break
                date = rs[1]
                ts = datetime.datetime(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2].split('T')[0]), int(date.split('T')[1].split(':')[0]), int(date.split('T')[1].split(':')[1]), 0, 0)
                #Row.objects.create(meta=mmeta, obj_id=rs[0], time_stamp=ts, size=float(rs[2]), xpos=float(rs[3]), ypos=float(rs[4]), speed=float(rs[5]), color=rs[6])
                with connection.cursor() as c:
                    c.execute(
                        "INSERT INTO `all_row` (`meta_id`, `obj_id`, `time_stamp`, `size`, `xpos`, `ypos`, `speed`, `color`)"
                        " VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                            str(mmeta.pk),
                            rs[0],
                            ts,
                            str(float(rs[2])),
                            str(float(rs[3])),
                            str(float(rs[4])),
                            str(float(rs[5])),
                            str(rs[6])
                        ))
            return HttpResponseRedirect('/cctv_specific/%s' % cctv.pk)
    data = {
        'cctv': cctv,
        'spot': spot,
        'meta': meta_list,
        'auth': auth,
    }

    return render(request, 'all/cctv_specific.html', data)

def cctv_remove_spot(request, cctv_id, spot_id):
    #cctv = Cctv.objects.filter(pk=cctv_id)
    cctv = Cctv.objects.raw("SELECT * FROM `all_cctv` WHERE `all_cctv`.`id` = '%s'" % cctv_id)
    if len(list(cctv)) != 1:
        return HttpResponseRedirect('/')
    cctv = cctv[0]
    #spot = Spot.objects.filter(pk=spot_id)
    spot = Spot.objects.raw("SELECT * FROM `all_spot` WHERE `all_spot`.`id` = '%s'" % spot_id)
    #print(spot.query)
    if len(list(spot)) != 1:
        return HttpResponseRedirect('/')
    for s in cctv.spots.all():
        if s == spot[0]:
            cctv.spots.remove(s)
    cctv.save()
    return HttpResponseRedirect('/cctv_specific/%s' % cctv_id)

def cctv_remove_meta(request, cctv_id, meta_id):
    #cctv = Cctv.objects.filter(pk=cctv_id)
    cctv = Cctv.objects.raw("SELECT * FROM `all_cctv` WHERE `all_cctv`.`id` = '%s'" % cctv_id)
    if len(list(cctv)) != 1:
        return HttpResponseRedirect('/')
    cctv = cctv[0]
    #meta = Meta.objects.filter(pk=meta_id)
    meta = Meta.objects.raw("SELECT `all_meta`.`id`, `all_meta`.`name`, `all_meta`.`cctv_id`, `all_meta`.`video_id` FROM `all_meta` WHERE `all_meta`.`id` = '%s'" % meta_id)
    if len(list(meta)) != 1:
        return HttpResponseRedirect('/')
    meta[0].delete()

    return HttpResponseRedirect('/cctv_specific/%s' % cctv_id)

def meta(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    #userinfo = Manager.objects.filter(user=request.user)
    userinfo = Manager.objects.raw("SELECT * FROM `all_manager` WHERE `all_manager`. `user_id` = '%s'" % request.user.pk)
    if len(list(userinfo)) != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    metas = []
    #cctvs = Cctv.objects.filter(manager=userinfo)
    cctvs = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`manager_id` = '%s'" % userinfo.pk)
    #print(cctvs.query)
    if userinfo.charge:
        #cctvs = Cctv.objects.all()
        cctvs = Cctv.objects.raw("SELECT * FROM `all_cctv`")
    if request.method == 'POST':
        o = request.POST['option']
        q = request.POST['meta-query']
        if o == 'cctv-name':
            #cctvs = cctvs.filter(name=q)
            cctvs = Cctv.objects.raw("SELECT * FROM `all_cctv` WHERE `all_cctv`.`name` = '%s'" % q)
        elif o == 'spot':
            temp = []
            for c in cctvs:
                for s in c.spots.all():
                    if s.indoor_loc == q:
                        temp.append(c)
                        break
            cctvs = temp
        elif o == 'sequence':
            cctvs = []
            q = ''.join(q.split(","))
            tmp = []
            for ss in Sequence.objects.raw("SELECT * FROM `all_sequence`"):
                temp1 = list(ss.neighbors.all())
                temp2 = [temp1[0]]
                num = len(temp1)-1
                while num > 0:
                    for n1 in temp1:
                        if temp2[0].spot1 == n1.spot2:
                            temp2 = [n1] + temp2
                            num-=1
                            break
                    for n1 in temp1:
                        if temp2[-1].spot2 == n1.spot1:
                            temp2 = temp2 + [n1]
                            num-=1
                            break
                temp = ''.join('<%s-%s>' % (n.spot1.indoor_loc, n.spot2.indoor_loc) for n in temp2)
                if temp != q:
                    continue
                total_good = True
                for n in ss.neighbors.all():
                    good = False
                    for c in n.spot1.spot_cctvs.all():
                        if c.manager == userinfo:
                            good = True
                            break
                    if userinfo.charge == False and not good:
                        total_good = False
                        break
                    good = False
                    for c in n.spot2.spot_cctvs.all():
                        if c.manager == userinfo:
                            good = True
                            break
                    if userinfo.charge == False and not good:
                        total_good = False
                        break
                if not total_good:
                    break
                for n in ss.neighbors.all():
                    for c in n.spot1.spot_cctvs.all():
                        if c in cctvs: continue
                        cctvs.append(c)
                    for c in n.spot2.spot_cctvs.all():
                        if c in cctvs: continue
                        cctvs.append(c)
        elif o == 'time':
            t1 = None
            t2 = None
            metas = []
            if q[0] == '~':
                date = q[1:]
                t1 = datetime.datetime(1, 1, 1, 0, 0)
                t2 = datetime.datetime(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2].split('T')[0]), int(date.split('T')[1].split(':')[0]), int(date.split('T')[1].split(':')[1]), 0, 0)
            elif q[-1] == '~':
                date = q[:-1]
                t1 = datetime.datetime(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2].split('T')[0]), int(date.split('T')[1].split(':')[0]), int(date.split('T')[1].split(':')[1]), 0, 0)
                t2 = datetime.datetime(9999, 12, 31, 0, 0)
            else:
                date = q.split('~')[0]
                t1 = datetime.datetime(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2].split('T')[0]), int(date.split('T')[1].split(':')[0]), int(date.split('T')[1].split(':')[1]), 0, 0)
                date = q.split('~')[-1]
                t2 = datetime.datetime(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2].split('T')[0]), int(date.split('T')[1].split(':')[0]), int(date.split('T')[1].split(':')[1]), 0, 0)
            total_no = 0
            total_objs = set()
            total_size = 0.0
            total_xpos = 0.0
            total_ypos = 0.0
            total_speed = 0.0
            for c in cctvs:
                # metamon = Meta.objects.filter(cctv=cctv)
                #for m in Meta.objects.filter(cctv=c):
                for m in Meta.objects.raw("SELECT * FROM `all_meta` WHERE `all_meta`.`cctv_id` = '%s'" % c.pk):
                    time_min, time_max = None, None
                    #metamon = Row.objects.filter(meta=m)
                    metamon = Row.objects.raw("SELECT * FROM `all_row` WHERE `all_row`.`meta_id` = '%s'" % m.pk)
                    for r in metamon:
                        #print(r.time_stamp)
                        if time_min == None or time_min > r.time_stamp:
                            time_min = r.time_stamp
                        if time_max == None or time_max < r.time_stamp:
                            time_max = r.time_stamp
                    #print(c, time_min, time_max)
                    if time_max != None and time_min != None and t1 <= time_min and time_max <= t2:
                        if request.POST.get('delete', False):
                            m.delete()
                            continue
                        avg_size, avg_xpos, avg_ypos, avg_speed = 0, 0, 0, 0
                        objs = set()
                        time_min = None
                        time_max = None
                        meta_row = Row.objects.raw("SELECT * FROM `all_row` WHERE `all_row`.`meta_id` = '%s'" % m.pk)
                        for r in meta_row:
                            avg_size += r.size
                            total_size += r.size
                            avg_xpos += r.xpos
                            total_xpos += r.xpos
                            avg_ypos += r.ypos
                            total_ypos += r.ypos
                            avg_speed += r.speed
                            total_speed += r.speed
                            objs.add(r.obj_id)
                            total_objs.add(r.obj_id)
                            total_no += 1
                            if time_min == None or time_min > r.time_stamp:
                                time_min = r.time_stamp
                            if time_max == None or time_max < r.time_stamp:
                                time_max = r.time_stamp
                        cnt = cnt = len(list(meta_row))
                        avg_size /= cnt
                        avg_xpos /= cnt
                        avg_ypos /= cnt
                        avg_speed /= cnt
                        dtime = time_max - time_min
                        metas.append({'meta':m, 'pk':m.pk, 'name':m.name, 'cctv':m.cctv, 'video':m.video, 'avg_size':avg_size, 'avg_xpos':avg_xpos, 'avg_ypos':avg_ypos, 'avg_speed':avg_speed, 'rec_no':cnt, 'obj_no':len(objs), 'time_len':'%s:%s:%s' % (dtime.seconds // 3600, dtime.seconds % 3600 // 60, dtime.seconds % 60)})
            if request.POST.get('delete', False):
                return HttpResponseRedirect('/meta')
            data = {
                'meta': metas,
                'total_no': total_no,
                'total_objs_no': len(total_objs),
                'avg_size': total_size / total_no if total_no > 0 else 0.0,
                'avg_xpos': total_xpos / total_no if total_no > 0 else 0.0,
                'avg_ypos': total_ypos / total_no if total_no > 0 else 0.0,
                'avg_speed': total_speed / total_no if total_no > 0 else 0.0,
            }
            with open('media/meta_avg.csv', 'w') as fp:
                fp.write(','.join(map(str, [data['total_no'], data['total_objs_no'], data['avg_size'], data['avg_xpos'], data['avg_ypos'], data['avg_speed']])))
            return render(request, 'all/meta.html', data)

    total_no = 0
    total_objs = set()
    total_size = 0.0
    total_xpos = 0.0
    total_ypos = 0.0
    total_speed = 0.0
    for c in cctvs:
        #for m in Meta.objects.filter(cctv=c):
        for m in Meta.objects.raw("SELECT * FROM `all_meta` WHERE `all_meta`.`cctv_id` = '%s'" % c.pk):
            if request.POST.get('delete', False):
                m.delete()
                continue
            avg_size, avg_xpos, avg_ypos, avg_speed = 0, 0, 0, 0
            objs = set()
            time_min = None
            time_max = None
            #for r in Row.objects.filter(meta=m):
            metamon = Row.objects.raw("SELECT * FROM `all_row` WHERE `all_row`.`meta_id` = '%s'" % m.pk)
            for r in metamon:
                avg_size += r.size
                total_size += r.size
                avg_xpos += r.xpos
                total_xpos += r.xpos
                avg_ypos += r.ypos
                total_ypos += r.ypos
                avg_speed += r.speed
                total_speed += r.speed
                objs.add(r.obj_id)
                total_objs.add(r.obj_id)
                total_no += 1
                if time_min == None or time_min > r.time_stamp:
                    time_min = r.time_stamp
                if time_max == None or time_max < r.time_stamp:
                    time_max = r.time_stamp
            cnt = len(list(metamon))
            if cnt != 0:
                avg_size /= cnt
                avg_xpos /= cnt
                avg_ypos /= cnt
                avg_speed /= cnt
                dtime = time_max - time_min
                metas.append({'meta':m, 'pk':m.pk, 'name':m.name, 'cctv':m.cctv, 'video':m.video, 'avg_size':avg_size, 'avg_xpos':avg_xpos, 'avg_ypos':avg_ypos, 'avg_speed':avg_speed, 'rec_no':cnt, 'obj_no':len(objs), 'time_len':'%s:%s:%s' % (dtime.seconds // 3600, dtime.seconds % 3600 // 60, dtime.seconds % 60)})
    if request.POST.get('delete', False):
        return HttpResponseRedirect('/meta')
    data = {
        'meta': metas,
        'total_no': total_no,
        'total_objs_no': len(total_objs),
        'avg_size': total_size / total_no if total_no > 0 else 0.0,
        'avg_xpos': total_xpos / total_no if total_no > 0 else 0.0,
        'avg_ypos': total_ypos / total_no if total_no > 0 else 0.0,
        'avg_speed': total_speed / total_no if total_no > 0 else 0.0,
    }
    with open('media/meta_avg.csv', 'w') as fp:
        fp.write(','.join(map(str, [data['total_no'], data['total_objs_no'], data['avg_size'], data['avg_xpos'], data['avg_ypos'], data['avg_speed']])))
    return render(request, 'all/meta.html', data)

def meta_specific(request, meta_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    #userinfo = Manager.objects.filter(user=request.user)
    userinfo = Manager.objects.raw("SELECT * FROM `all_manager` WHERE `all_manager`. `user_id` = '%s'" % request.user.pk)
    if len(list(userinfo)) != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    #meta_list = Meta.objects.filter(pk=meta_id)
    meta_list = Meta.objects.raw("SELECT `all_meta`.`id`, `all_meta`.`name`, `all_meta`.`cctv_id`, `all_meta`.`video_id` FROM `all_meta` WHERE `all_meta`.`id` = '%s'" % meta_id)
    if len(list(meta_list)) > 0:
        meta = meta_list[0]
        if userinfo.charge == False and meta.cctv.manager != userinfo:
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')
    row = []
    #row_list = Row.objects.filter(meta=meta)
    row_list = Row.objects.raw("SELECT * FROM `all_row` WHERE `all_row`.`meta_id` = '%s'" % meta.pk)
    #print(row_list.query)
    if len(list(row_list)) > 0:
        row+=list(row_list)
    data = {
        'meta': meta,
        'row': row,
    }
    return render(request, 'all/meta_specific.html', data)

def remove_meta(request, meta_id):
    #meta = Meta.objects.filter(pk=meta_id)
    meta = Meta.objects.raw("SELECT `all_meta`.`id`, `all_meta`.`name`, `all_meta`.`cctv_id`, `all_meta`.`video_id` FROM `all_meta` WHERE `all_meta`.`id` = '%s'" % meta_id)
    if len(list(meta)) != 1:
        return HttpResponseRedirect('/')
    meta[0].delete()

    return HttpResponseRedirect('/meta')

def neighbor(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    #userinfo = Manager.objects.filter(user=request.user)
    userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" % request.user.pk)
    #print(userinfo.query)
    if len(list(userinfo)) != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    ret = []
    spotlist = []
    #print(userinfo.pk)
    if userinfo.charge:
        #ret = Neighbor.objects.all()
        #print(ret.query)
        ret = Neighbor.objects.raw("SELECT `all_neighbor`.`id`, `all_neighbor`.`name`, `all_neighbor`.`spot1_id`, `all_neighbor`.`spot2_id` FROM `all_neighbor`")
    else:
        #cc = Cctv.objects.filter(manager=userinfo)
        #print(cc.query)
        #print(userinfo.pk)
        cc = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`manager_id` = '%s'" % userinfo.pk)
        #print(cc.query)
        for i in range(len(list(cc))):
            s = Spot.objects.raw("SELECT `all_spot`.`id`, `all_spot`.`indoor_loc`, `all_spot`.`floor_no`, `all_spot`.`dep_name`, `all_spot`.`address` FROM `all_spot` INNER JOIN `all_cctv_spots` ON (`all_spot`.`id` = `all_cctv_spots`.`spot_id`) WHERE `all_cctv_spots`.`cctv_id` = '%s'" % cc[i].pk)
            spot = list(s)
            for j in range(len(spot)):
                if not spot[j] in spotlist:
                    spotlist = spotlist + [spot[j]]
            #print(spotlist)
        for s in spotlist:
            for l in spotlist:
                temp = Neighbor.objects.raw("SELECT `all_neighbor`.`id`, `all_neighbor`.`name`, `all_neighbor`.`spot1_id`, `all_neighbor`.`spot2_id` FROM `all_neighbor` WHERE (`all_neighbor`.`spot1_id` = '%s' AND `all_neighbor`.`spot2_id` = '%s')" % (l.pk,s.pk))
                #print(temp.query)
                for n in temp:
                    if not n in ret:
                        #print(n)
                        ret.append(n)
            #print(ret)
    #ret = Neighbor.objects.all()
    if request.method == 'POST':
        o = request.POST.get('option', False)
        q = request.POST.get('neighbor_query', False)
        f = request.POST.get('form-type',False)
        add = request.POST.get('neighbor-add', False)
        name = request.POST.get('neighbor-name', False)
        #n = Neighbor.objects.filter(name=q)
        n = Neighbor.objects.raw("SELECT `all_neighbor`.`id`, `all_neighbor`.`name`, `all_neighbor`.`spot1_id`, `all_neighbor`.`spot2_id` FROM `all_neighbor` WHERE `all_neighbor`.`name` = '%s'" % q)
        #print(n.query)
        #print(n)
        if o == 'name':
            if len(list(n))>0: 
                ret = n
            else:
                ret = None
        elif o == 'spot':
            ret = []
            spot = Spot.objects.raw("SELECT `all_spot`.`id`, `all_spot`.`indoor_loc`, `all_spot`.`floor_no`, `all_spot`.`dep_name`, `all_spot`.`address` FROM `all_spot` WHERE `all_spot`.`indoor_loc` = '%s'" % q)
            #print(spot.query)
            if str(spot) == '<QuerySet []>':
                ret = None
            else:
                for s in spot:
                    #print(s)
                    for l in spotlist:
                        neighbor1 = Neighbor.objects.raw("SELECT `all_neighbor`.`id`, `all_neighbor`.`name`, `all_neighbor`.`spot1_id`, `all_neighbor`.`spot2_id` FROM `all_neighbor` WHERE (`all_neighbor`.`spot1_id` = '%s' AND `all_neighbor`.`spot2_id` = '%s')" % (s.pk,l.pk))
                        neighbor2 = Neighbor.objects.raw("SELECT `all_neighbor`.`id`, `all_neighbor`.`name`, `all_neighbor`.`spot1_id`, `all_neighbor`.`spot2_id` FROM `all_neighbor` WHERE (`all_neighbor`.`spot1_id` = '%s' AND `all_neighbor`.`spot2_id` = '%s')" % (l.pk,s.pk))
                        for n in neighbor1:
                            #print(n)
                            if not n in ret:
                                ret.append(n)
                        for n in neighbor2:
                            #print(n)
                            if not n in ret:
                                ret.append(n)
        if f == 'add-neighbor':
            if userinfo.charge:
                s1 = Spot.objects.raw("SELECT `all_spot`.`id`, `all_spot`.`indoor_loc`, `all_spot`.`floor_no`, `all_spot`.`dep_name`, `all_spot`.`address` FROM `all_spot` WHERE `all_spot`.`indoor_loc` = '%s'" % add.split('-')[0][1:])[0]
                s2 = Spot.objects.raw("SELECT `all_spot`.`id`, `all_spot`.`indoor_loc`, `all_spot`.`floor_no`, `all_spot`.`dep_name`, `all_spot`.`address` FROM `all_spot` WHERE `all_spot`.`indoor_loc` = '%s'" % add.split('-')[-1][:-1])[0]
                #print(temp.query)
                #s1 = Spot.objects.get(indoor_loc=add.split('-')[0][1:])
                #s2 = Spot.objects.get(indoor_loc=add.split('-')[-1][:-1])
                #print(s1, s2)
                #nn = Neighbor.objects.create(spot1=s1, spot2=s2)
                with connection.cursor() as c:
                    c.execute(
                        "INSERT INTO `all_neighbor` (`name`, `spot1_id`, `spot2_id`) VALUES ('%s', '%s', '%s')" % (
                            name,
                            str(s1.pk),
                            str(s2.pk)
                        ))
                #print(nn)
                #nn.name = name
                #nn.save()
    data = {
        'neighbor': ret,
    }
    return render(request, 'all/neighbor.html', data)

def neighbor_specific(request, neighbor_id):
    neighbor = Neighbor.objects.raw("SELECT `all_neighbor`.`id`, `all_neighbor`.`name`, `all_neighbor`.`spot1_id`, `all_neighbor`.`spot2_id` FROM `all_neighbor` WHERE `all_neighbor`.`id` = '%s'" % neighbor_id)
    #print(neighbor)
    if len(list(neighbor)) > 0:
        neighbor = neighbor[0]
    #spot = Spot.objects.all()
    spot = Spot.objects.raw("SELECT `all_spot`.`id`, `all_spot`.`indoor_loc`, `all_spot`.`floor_no`, `all_spot`.`dep_name`, `all_spot`.`address` FROM `all_spot`")
    print(spot.query)
    if request.method == 'POST':
        if request.POST['form-type'] == 'edit-info':
            name = request.POST['neighbor-name']
            neighbor.name = name
            neighbor.save()
    data = {
        'neighbor': neighbor
    }

    return render(request, 'all/neighbor_specific.html', data)

def sequence(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    #userinfo = Manager.objects.filter(user=request.user)
    userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" %request.user.pk)
    #print(userinfo.query)
    if len(list(userinfo)) != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    neighbor = []
    spotlist = []
    ##cc = Cctv.objects.filter(manager=userinfo)
    cc = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`manager_id` = '%s'" %userinfo.pk)
    #print(cc.query)
    for i in range(len(list(cc))):
        #spot = list(Spot.objects.filter(spot_cctvs=(cc[i])))
        spot = Spot.objects.raw("SELECT `all_spot`.`id`, `all_spot`.`indoor_loc`, `all_spot`.`floor_no`, `all_spot`.`dep_name`, `all_spot`.`address` FROM `all_spot` INNER JOIN `all_cctv_spots` ON (`all_spot`.`id` = `all_cctv_spots`.`spot_id`) WHERE `all_cctv_spots`.`cctv_id` = '%s'" % cc[i].pk)
        #print(spot.query)
        for j in range(len(list(spot))):
            if not spot[j] in spotlist:
                spotlist = spotlist + [spot[j]]
        #print(spotlist)
    for s in spotlist:
        for l in spotlist:
            nei = Neighbor.objects.raw("SELECT `all_neighbor`.`id`, `all_neighbor`.`name`, `all_neighbor`.`spot1_id`, `all_neighbor`.`spot2_id` FROM `all_neighbor` WHERE (`all_neighbor`.`spot1_id` = '%s' AND `all_neighbor`.`spot2_id` = '%s')"%(l.pk, s.pk))
            #print(nei.query)
            for n in nei:
                if not n in neighbor:
                    #print(n)
                    neighbor.append(n)
    if userinfo.charge:
        #ret = Sequence.objects.all()
        #print(ret.query)
        ret = Sequence.objects.raw("SELECT `all_sequence`.`id` FROM `all_sequence`")
        seq = Sequence.objects.raw("SELECT `all_sequence`.`id` FROM `all_sequence`")
        #seq = Sequence.objects.all()
        #print(seq.query)
    else:
        sequence = []
        #seqnum = Sequence.objects.all()
        seqnum = Sequence.objects.raw("SELECT `all_sequence`.`id` FROM `all_sequence`")
        #print(seqnum.query)
        for seq in seqnum:
            match = False
            temp = seq.neighbors.all()
            print(temp.query)
            for nei in seq.neighbors.all():
                for n in neighbor:
                    if nei == n:
                        match = True
                        break
                    match = False
            if match == True:
                sequence = sequence + [seq]
        seq = sequence
        ret = sequence
    if request.method == 'POST':
        ret = []
        o = request.POST.get('option', False)
        q = request.POST['sequence_query']
        if o == 'neighbor':
            for s in seq:
                temp1 = list(s.neighbors.all())
                temp2 = [temp1[0]]
                num = len(temp1)-1
                while num > 0:
                    for n1 in temp1:
                        #print(temp2[0])
                        if temp2[0].spot1 == n1.spot2:
                            temp2 = [n1] + temp2
                            num-=1
                            #print("front", num)
                            break
                    for n1 in temp1:
                        if temp2[-1].spot2 == n1.spot1:
                            temp2 = temp2 + [n1]
                            num-=1
                            #print("after", num)
                            break
                #temp2 is a sorted list
                s_ = ''.join('<%s-%s>' % (n.spot1.indoor_loc, n.spot2.indoor_loc) for n in temp2)
                q_ = ''.join(q.split(","))
                if q_ in s_ :
                    ret = ret + [s]
        elif o == 'add-sequence':
            if userinfo.charge:
                new_seq = Sequence.objects.create()
                new_seq.save()
                for n in q.split(','):
                    #s1 = Spot.objects.filter(indoor_loc=n.split('-')[0][1:])
                    s1 = Spot.objects.raw("SELECT `all_spot`.`id`, `all_spot`.`indoor_loc`, `all_spot`.`floor_no`, `all_spot`.`dep_name`, `all_spot`.`address` FROM `all_spot` WHERE `all_spot`.`indoor_loc` = '%s'" % n.split('-')[0][1:])[0]
                    #print(s1.query)
                    #s2 = Spot.objects.get(indoor_loc=n.split('-')[-1][:-1])
                    s2 = Spot.objects.raw("SELECT `all_spot`.`id`, `all_spot`.`indoor_loc`, `all_spot`.`floor_no`, `all_spot`.`dep_name`, `all_spot`.`address` FROM `all_spot` WHERE `all_spot`.`indoor_loc` = '%s'" % n.split('-')[-1][:-1])[0]
                    #nn = Neighbor.objects.get(spot1=s1, spot2=s2)
                    nn = Neighbor.objects.raw("SELECT `all_neighbor`.`id`, `all_neighbor`.`name`, `all_neighbor`.`spot1_id`, `all_neighbor`.`spot2_id` FROM `all_neighbor` WHERE (`all_neighbor`.`spot1_id` = '%s' AND `all_neighbor`.`spot2_id` = '%s')" % (s1.pk, s2.pk))[0]
                    #print(nn.query)
                    new_seq.neighbors.add(nn)
                new_seq.save()
    data = {
        'sequence': ret,
    }
    return render(request, 'all/sequence.html', data)

def sequence_specific(request, sequence_id):
    sequence = None
    temp = Sequence.objects.raw("SELECT `all_sequence`.`id` FROM `all_sequence` WHERE `all_sequence`.`id` = '%s'" % sequence_id)
    if len(list(temp)) > 0:
        sequence = temp[0]
    if request.method == 'POST':
        if request.POST['form-type'] == 'add-neighbor':
            nid = request.POST['neighbor-id']
            # add_n = Neighbor.objects.get(pk=int(nid))
            add_n = Neighbor.objects.raw("SELECT `all_neighbor`.`id`, `all_neighbor`.`name`, `all_neighbor`.`spot1_id`, `all_neighbor`.`spot2_id` FROM `all_neighbor` WHERE `all_neighbor`.`id` = '%s'" % nid)
            add_n = add_n[0]
            sequence.neighbors.add(add_n)
            sequence.save()
    data = {
        'sequence': sequence,
    }

    return render(request, 'all/sequence_specific.html', data)

def sequence_remove_neighbor(request, sequence_id, neighbor_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    # userinfo = Manager.objects.filter(user=request.user)
    userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" % request.user.pk)
    if len(list(userinfo)) != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    if not userinfo.charge:
        return HttpResponseRedirect('/')
    # sequence = Sequence.objects.filter(pk=sequence_id)
    sequence = Sequence.objects.raw("SELECT `all_sequence`.`id` FROM `all_sequence` WHERE `all_sequence`.`id` = '%s'" % sequence_id)
    if len(list(sequence)) != 1:
        return HttpResponseRedirect('/')
    sequence = sequence[0]
    # neighbor = Neighbor.objects.filter(pk=neighbor_id)
    neighbor = Neighbor.objects.raw("SELECT `all_neighbor`.`id`, `all_neighbor`.`name`, `all_neighbor`.`spot1_id`, `all_neighbor`.`spot2_id` FROM `all_neighbor` WHERE `all_neighbor`.`id` = '%s'" % neighbor_id)
    if len(list(neighbor)) != 1:
        return HttpResponseRedirect('/')
    neighbor = neighbor[0]
    sequence.neighbors.remove(neighbor)
    sequence.save()
    if sequence.neighbors.count() == 0:
        sequence.delete()
        return HttpResponseRedirect('/sequence')
    return HttpResponseRedirect('/sequence_specific/%s' % sequence_id)

def manage_edit(request, user_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    # userinfo = Manager.objects.filter(user=request.user)
    userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" % request.user.pk)
    if len(list(userinfo)) != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    if not userinfo.charge:
        return HttpResponseRedirect('/')
    # user = User.objects.filter(pk=user_id)
    user = User.objects.raw("SELECT `auth_user`.`id`, `auth_user`.`password`, `auth_user`.`last_login`, `auth_user`.`is_superuser`, `auth_user`.`username`, `auth_user`.`first_name`, `auth_user`.`last_name`, `auth_user`.`email`, `auth_user`.`is_staff`, `auth_user`.`is_active`, `auth_user`.`date_joined` FROM `auth_user` WHERE `auth_user`.`id` = '%s'" % user_id)
    if len(list(user)) != 1:
        return HttpResponseRedirect('/')
    user = user[0]
    # userinfo = Manager.objects.get(user=user)
    userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" % user.pk)
    userinfo = userinfo[0]
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
            # cctv = Cctv.objects.get(pk=cctv_id)
            cctv = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`id` = '%s'" % cctv_id)
            cctv.manager = userinfo
            cctv.save()
    # cctvs =  Cctv.objects.filter(manager=userinfo)
    cctvs = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`manager_id` = '%s'" % userinfo.pk)
    data = {
        'userinfo': userinfo,
        'cctvs': cctvs,
    }
    return render(request, 'all/manage_edit.html', data)


def my(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    # userinfo = Manager.objects.filter(user=request.user)
    userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" % request.user.pk)
    if len(list(userinfo)) != 1:
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
            # userinfo = Manager.objects.get(user=request.user)
            userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" % request.user.pk)
            userinfo = userinfo[0]
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
    # userinfo = Manager.objects.filter(user=request.user)
    userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" % request.user.pk)
    if len(list(userinfo)) != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    if not userinfo.charge:
        return HttpResponseRedirect('/')
    # users = Manager.objects.filter(charge=False)
    users = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`charge` = False")
    if request.method == 'POST':
        if request.POST['form-type'] == 'add-user':
            id = request.POST['user-id']
            user_pw = request.POST['user-pw']
            name = request.POST['user-name']
            cell = request.POST['user-cell']
            user = User.objects.create(username=id, email='test@test.com', password=user_pw)
            #Manager.objects.create(user=user, name=name, cell=cell)
            with connection.cursor() as c:
                c.execute(
                    "INSERT INTO `all_manager` (`user_id`, `name`, `cell`, `charge`) VALUES ('%s', '%s', '%s', False)" % (
                        str(user.pk),
                        name,
                        cell
                    ))
            # users = Manager.objects.filter(charge=False)
            users = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`charge` = False")
        elif request.POST['form-type'] == 'search':
            o = request.POST.get('option', False)
            q = request.POST.get('query', False)
            if o == 'id':
                # users = users.filter(user__username=q)
                users = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` INNER JOIN `auth_user` ON (`all_manager`.`user_id` = `auth_user`.`id`) WHERE (`all_manager`.`charge` = False AND `auth_user`.`username` = '%s')" % q)
            elif o == 'name':
                # users = users.filter(name=q)
                users = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE (`all_manager`.`charge` = False AND `all_manager`.`name` = '%s')" % q)
            elif o == 'cell':
                # users = users.filter(cell=q)
                users = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE (`all_manager`.`charge` = False AND `all_manager`.`cell` = '%s')" % q)
            elif o == 'cctv':
                # cctvs = Cctv.objects.filter(name=q)
                cctvs = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`name` = '%s'" % q)
                if len(list(cctvs)) == 1:
                    users = [cctvs[0].manager]
                else:
                    users = []
    data = {
        'userinfo': userinfo,
        'users': users,
    }
    return render(request, 'all/manage.html', data)

def manage_edit(request, user_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    # userinfo = Manager.objects.filter(user=request.user)
    userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" % request.user.pk)
    if len(list(userinfo)) != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    if not userinfo.charge:
        return HttpResponseRedirect('/')
    # user = User.objects.filter(pk=user_id)
    user = User.objects.raw("SELECT `auth_user`.`id`, `auth_user`.`password`, `auth_user`.`last_login`, `auth_user`.`is_superuser`, `auth_user`.`username`, `auth_user`.`first_name`, `auth_user`.`last_name`, `auth_user`.`email`, `auth_user`.`is_staff`, `auth_user`.`is_active`, `auth_user`.`date_joined` FROM `auth_user` WHERE `auth_user`.`id` = '%s'" % user_id)
    if len(list(user)) != 1:
        return HttpResponseRedirect('/')
    user = user[0]
    # userinfo = Manager.objects.filter(user=user)
    userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" % user_id)
    if len(list(userinfo)) != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    if request.method == 'POST':
        if request.POST['form-type'] == 'edit-info':
            pw = request.POST['user-pw']
            name = request.POST['user-name']
            cell = request.POST['user-cell']
            userinfo.name = name
            userinfo.cell = cell
            userinfo.save()
            user.set_password(pw)
            user.save()
        elif request.POST['form-type'] == 'add-cctv':
            cctv_id = request.POST['cctv-id']
            cctv = Cctv.objects.get(pk=cctv_id)
            cctv.manager = userinfo
            cctv.save()
    # cctvs =  Cctv.objects.filter(manager=userinfo)
    cctvs = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`manager_id` = '%s'" % userinfo.pk)
    data = {
        'userinfo': userinfo,
        'cctvs': cctvs,
    }
    return render(request, 'all/manage_edit.html', data)

def manage_remove_user(request, user_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    # userinfo = Manager.objects.filter(user=request.user)
    userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" % request.user.pk)
    if len(list(userinfo)) != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    if not userinfo.charge:
        return HttpResponseRedirect('/')
    # user = User.objects.filter(pk=user_id)
    user = User.objects.raw("SELECT `auth_user`.`id`, `auth_user`.`password`, `auth_user`.`last_login`, `auth_user`.`is_superuser`, `auth_user`.`username`, `auth_user`.`first_name`, `auth_user`.`last_name`, `auth_user`.`email`, `auth_user`.`is_staff`, `auth_user`.`is_active`, `auth_user`.`date_joined` FROM `auth_user` WHERE `auth_user`.`id` = '%s'" % user_id)
    if len(list(user)) != 1:
        return HttpResponseRedirect('/')
    user = user[0]
    user.delete()
    return HttpResponseRedirect('/manage')

def manage_remove_cctv(request, user_id, cctv_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    # userinfo = Manager.objects.filter(user=request.user)
    userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" % request.user.pk)
    if len(list(userinfo)) != 1:
        return HttpResponseRedirect('/')
    userinfo = userinfo[0]
    if not userinfo.charge:
        return HttpResponseRedirect('/')
    # user = User.objects.filter(pk=user_id)
    user = User.objects.raw("SELECT `auth_user`.`id`, `auth_user`.`password`, `auth_user`.`last_login`, `auth_user`.`is_superuser`, `auth_user`.`username`, `auth_user`.`first_name`, `auth_user`.`last_name`, `auth_user`.`email`, `auth_user`.`is_staff`, `auth_user`.`is_active`, `auth_user`.`date_joined` FROM `auth_user` WHERE `auth_user`.`id` = '%s'" % user_id)
    if len(list(user)) != 1:
        return HttpResponseRedirect('/')
    user = user[0]
    # cctv = Cctv.objects.filter(pk=cctv_id)
    cctv = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`id` = '%s'" % cctv_id)
    if len(list(cctv)) != 1:
        return HttpResponseRedirect('/')
    cctv = cctv[0]
    cctv.manager = None
    cctv.save()
    return HttpResponseRedirect('/manage/edit/%s' % user_id)

def download_meta(request, meta_id):
    meta = Meta.objects.filter(pk=meta_id)
    if meta.count() != 1:
        return HttpResponseRedirect('/')
    meta = meta[0]
    data = []
    for r in Row.objects.filter(meta=meta):
        data.append(','.join([r.obj_id, str(r.time_stamp), str(r.size), str(r.xpos), str(r.ypos), str(r.speed), r.color]))
    data = '\n'.join(data)
    response = HttpResponse(data, content_type='text/csv')
    response['Content-Disposition'] = "attachment; filename*=UTF-8\'\'{0}".format(meta.name)
    response['Content-Length'] = len(data.encode())
    return response

def download_meta_avg(request):
    with open('media/meta_avg.csv', 'rb') as fp:
        data = fp.read()
    response = HttpResponse(data, content_type=mimetypes.guess_type('media/meta_avg.csv')[0])
    response['Content-Disposition'] = "attachment; filename*=UTF-8\'\'{0}".format('media/meta_avg.csv')
    response['Content-Length'] = os.path.getsize('media/meta_avg.csv')
    return response

def download_video(request, meta_id):
    meta = Meta.objects.filter(pk=meta_id)
    if meta.count() != 1:
        return HttpResponseRedirect('/')
    meta = meta[0]
    video = meta.video
    with open('media/%s.%s' % (video.name, video.ext), 'rb') as fp:
        data = fp.read()
    response = HttpResponse(data, content_type=mimetypes.guess_type('media/%s.%s' % (video.name, video.ext))[0])
    response['Content-Disposition'] = "attachment; filename*=UTF-8\'\'{0}.{1}".format(video.name, video.ext)
    response['Content-Length'] = os.path.getsize('media/%s.%s' % (video.name, video.ext))
    return response

def api(request, query):
    q = query.split('/')
    if q[0] == 'cctv_list':
        if request.GET['user_id'] != '-1':
            # user = User.objects.filter(pk=request.GET['user_id'])
            user = User.objects.raw("SELECT `auth_user`.`id`, `auth_user`.`password`, `auth_user`.`last_login`, `auth_user`.`is_superuser`, `auth_user`.`username`, `auth_user`.`first_name`, `auth_user`.`last_name`, `auth_user`.`email`, `auth_user`.`is_staff`, `auth_user`.`is_active`, `auth_user`.`date_joined` FROM `auth_user` WHERE `auth_user`.`id` = '%s'" % request.GET['user_id'])
            user = user[0]
            # manager = Manager.objects.get(user=user)
            manager = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" % user.pk)
            # cctvs = Cctv.objects.filter(manager=manager)
            cctvs = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`manager_id` = '%s'" % manager.pk)
        else:
            # cctvs = Cctv.objects.all()
            cctvs = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv`")
        names = [{'id':c.pk, 'name':c.name, 'start_date':str(c.start_date), 'spots':' '.join([s.address for s in c.spots.all()]) } for c in cctvs]
        jsondata = json.dumps(names)
        return HttpResponse(jsondata, content_type='application/json')
    elif q[0] == 'spot_list':
        # userinfo = Manager.objects.filter(user=request.user)
        userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" % request.user.pk)
        if len(list(userinfo)) != 1:
            return HttpResponseRedirect('/')
        userinfo = userinfo[0]
        names = []
        if userinfo.charge:
            # spot = Spot.objects.all()
            spot = Spot.objects.raw("SELECT `all_spot`.`id`, `all_spot`.`indoor_loc`, `all_spot`.`floor_no`, `all_spot`.`dep_name`, `all_spot`.`address` FROM `all_spot`")
            names = [{'id': s.pk, 'indoor_loc': s.indoor_loc, 'floor_no': s.floor_no, 'dep_name': s.dep_name,
                      'address': s.address} for s in spot]
        else:
            cctvs = Cctv.objects.raw("SELECT `all_cctv`.`id`, `all_cctv`.`name`, `all_cctv`.`start_date`, `all_cctv`.`manager_id` FROM `all_cctv` WHERE `all_cctv`.`manager_id` = '%s'" % userinfo.pk)
            for c in cctvs:
                spot = c.spots.all()
                for s in spot:
                    names.append({'id':s.pk, 'indoor_loc':s.indoor_loc, 'floor_no':s.floor_no, 'dep_name':s.dep_name, 'address':s.address})
        jsondata = json.dumps(names)
        return HttpResponse(jsondata, content_type='application/json')
    elif q[0] == 'manager_list':
        # userinfo = Manager.objects.filter(user=request.user)
        userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" % request.user.pk)
        if len(list(userinfo)) != 1:
            return HttpResponseRedirect('/')
        userinfo = userinfo[0]
        names = []
        if userinfo.charge:
            # manager = Manager.objects.all()
            manager = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager`")
            names = [{'id': m.pk, 'user': m.user.username, 'name': m.name, 'cell': m.cell} for m in manager]
        else:
            pass
        jsondata = json.dumps(names)
        return HttpResponse(jsondata, content_type='application/json')
    elif q[0] == 'neighbor_list':
        # userinfo = Manager.objects.filter(user=request.user)
        userinfo = Manager.objects.raw("SELECT `all_manager`.`id`, `all_manager`.`user_id`, `all_manager`.`name`, `all_manager`.`cell`, `all_manager`.`charge` FROM `all_manager` WHERE `all_manager`.`user_id` = '%s'" % request.user.pk)
        if len(list(userinfo)) != 1:
            return HttpResponseRedirect('/')
        userinfo = userinfo[0]
        names = []
        if not userinfo.charge:
            return HttpResponseRedirect('/')
        # neighbor = Neighbor.objects.all()
        neighbor = Neighbor.objects.raw("SELECT `all_neighbor`.`id`, `all_neighbor`.`name`, `all_neighbor`.`spot1_id`, `all_neighbor`.`spot2_id` FROM `all_neighbor`")
        names = [{'id': n.pk, 'spot1': n.spot1.indoor_loc, 'spot2': n.spot2.indoor_loc, 'name': n.name} for n in neighbor]
        jsondata = json.dumps(names)
        return HttpResponse(jsondata, content_type='application/json')