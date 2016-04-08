#-*- coding=utf-8 -*
import thread
from django.shortcuts import render_to_response,get_object_or_404
from utils.pageHandle import devidePage
from django.core.urlresolvers import reverse
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
import datetime
from device.forms import VehicleModelForm,DtuModelForm,VehicleGroupModelForm,VehicleGroupRModelForm,DtuGroupModelForm,DtuGroupRModeForm,UpdateVehicleForm
from system.models import User
from device.models import Dtu_group,Dtu_Group_r,Dtu,Vehicle,Vehicle_group,Vehicle_Group_r
from utils.MyEncoder import *
    
def device(request):
#    url = reverse("group_vehicle")
#    return HttpResponseRedirect(url)
    return render_to_response("device/device.html")
#################################
############ 车辆管理 ############                          
#################################
def vehicle_add(request,template="car/addcar.html"):
    if request.method == 'POST':
        form = VehicleModelForm(data=request.POST)
        if form.is_valid():
            form.save() #form.save(commit==False)
            tip = u'添加成功'
            context = Context({
            'tip':tip,
            'reurl':'',
            })
            return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))
#        return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))        
    else:
        form = VehicleModelForm()
    context = Context({
        'form': form,
        'title':'车辆添加',
        })
    return render_to_response(template,context,context_instance=RequestContext(request))

def vehicle_edit(request,vehicle_id,template="car/addcar.html"):
    try:
        vehicle_id = int(vehicle_id)
    except ValueError,e:
        raise Http404()
    else:
        vehicle = get_object_or_404(Vehicle,pk=vehicle_id)
        if request.method == 'POST':
            form = VehicleModelForm(data=request.POST,instance=vehicle)
            if form.is_valid():
                form.save() #form.save(commit==False)
                tip = u'修改成功'
                context = Context({
                'tip':tip,
                'reurl':'',
                })
                return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))
    #        return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))        
        else:
            form = VehicleModelForm(instance=vehicle)
        context = Context({
            'form': form,
            'title':'车辆修改',
            })
        return render_to_response(template,context,context_instance=RequestContext(request))
    

def vehicle_delete(request):
    if request.method == "POST":
        try:
            ids = request.POST.get('ids')
            ids = unicode.encode(ids,'utf-8')
            id_list = ids.split(",")
            vehicles =  Vehicle.objects.filter(id__in=id_list)
            count = len(vehicles)
            vehicles.delete()
            return HttpResponse("1")
        except:
            return HttpResponse("0")
    else:
        return HttpResponse("0")
        
        
        
#    try:
#        vehicle_id = int(vehicle_id)
#        vehicle = Vehicle.objects.get(pk=vehicle_id)
#        vehicle.delete()
#        return HttpResponse("1")
##        vehicle = get_object_or_404(Vehicle,pk=vehicle_id)
##        
##        return HttpResponseRedirect("/device/vehicle/list/")
#    except:
#        return HttpResponse("0")
#        raise Http404()
def dtu_delete(request):
    if request.method == "POST":
        try:
            ids = request.POST.get('ids')
            ids = unicode.encode(ids,'utf-8')
            id_list = ids.split(",")
            dtus =  Dtu.objects.filter(id__in=id_list)
            count = len(dtus)
            dtus.delete()
            return HttpResponse("1")
        except:
            return HttpResponse("0")
    else:
        return HttpResponse("0")
       
    
def vehicle_list(request,template="car/carlist.html"):
#    ids=[]
#    if 'ids' in request.POST and request.POST['ids'] is not None:
#        ids = request.POST.getlist('ids')
#        u = User.objects.filter(id__in=ids)
#        u.delete()
    vehicle = Vehicle.objects.all()
    context = Context({
        'title':'用户管理',
        'results': devidePage(request,vehicle,10),
    })
    return render_to_response(template,context,context_instance=RequestContext(request))

def vehicle_group_list(request,template="car/grouplist.html"):
    user = User.objects.getCurrentUser(request)
    groups = user.vehicle_group_set.all()
    context = Context({
        'title':'车辆组管理',
        'results': devidePage(request,groups,10),
    })
#    return render_to_response('system/updateAdminUsers.html',context,context_instance=RequestContext(request))
    return render_to_response(template,context,context_instance=RequestContext(request))
def vehicle_group_add(request):
    if request.method == 'POST':
        try:
            groupid = request.POST.get('id','')
            if groupid:
                vg = Vehicle_group.objects.get(pk=groupid)
                form = VehicleGroupModelForm(instance=vg,data=request.POST)
            else:
                form = VehicleGroupModelForm(data=request.POST)
            if form.is_valid():
                user = User.objects.getCurrentUser(request)
                vehicle_group = form.instance
                vehicle_group.user = user
                vehicle_group.save()
                return HttpResponse(1)
        except:
            return HttpResponse(0)
    else:
        return HttpResponse(0)
def vehicle_group_del(request):
    if request.method == "POST":
        try:
            ids = request.POST.get('ids')
            ids = unicode.encode(ids,'utf-8')
            id_list = ids.split(",")
            vehicle_groups =  Vehicle_group.objects.filter(id__in=id_list)
            count = len(vehicle_groups)
            vehicle_groups.delete()
            return HttpResponse("1")
        except:
            return HttpResponse("0")
    else:
        return HttpResponse("0")
    

def group_vehicle(request):
    if request.method == 'POST':
        form = VehicleGroupRModelForm(request,data=request.POST)
        if form.is_valid():
            form.save(commit=True);
#            user = User.objects.getCurrentUser(request)
#            dtu_group = form.instance
#            dtu_group.user = user
#            dtu_group.save()
            tip = u'添加成功'
        else:
            return render_to_response("vehicle/vehicle_add.html", {'form': form,}, context_instance=RequestContext(request))
            tip = u'未正确填写,添加失败'
        context = Context({
            'tip':tip,
            'reurl':'',
            })
        return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))        
    else:
        form = VehicleGroupRModelForm(request)
        context = Context({
            'form': form,
            'title':'车辆添加',
            })
        return render_to_response('vehicle/vehicle_add.html',context,context_instance=RequestContext(request))
def dtu_add(request,template="'device/adddevice.html'"):
    if request.method == 'POST':
        form = DtuModelForm(data=request.POST)
        if form.is_valid():
            form.save() #form.save(commit==False)
            tip = u'添加成功'
            context = Context({
            'tip':tip,
            'reurl':'',
            })
            return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))
#        return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))        
    else:
        form = DtuModelForm()
    context = Context({
        'form': form,
        'title':'车辆添加',
        })
    return render_to_response('device/adddevice.html',context,context_instance=RequestContext(request))

def dtu_edit(request,dtu_id,template="device/adddevice.html"):
    try:
        dtu_id = int(dtu_id)
    except ValueError,e:
        raise Http404()
    else:
        dtu = get_object_or_404(Dtu,pk=dtu_id)
        if request.method == 'POST':
            form = DtuModelForm(data=request.POST,instance=dtu)
            if form.is_valid():
                form.save() #form.save(commit==False)
                tip = u'修改成功'
                context = Context({
                'tip':tip,
                'reurl':'',
                })
                return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))
    #        return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))        
        else:
            form = DtuModelForm(instance=dtu)
        context = Context({
            'form': form,
            'title':'车辆修改',
            })
        return render_to_response(template,context,context_instance=RequestContext(request))
    
def dtu_list(request,template="device/devicelist.html"):
#    ids=[]
#    if 'ids' in request.POST and request.POST['ids'] is not None:
#        ids = request.POST.getlist('ids')
#        u = User.objects.filter(id__in=ids)
#        u.delete()
    dtu_list = Dtu.objects.all()
    context = Context({
        'title':'用户管理',
        'results': devidePage(request,dtu_list,10),
    })
    return render_to_response(template,context,context_instance=RequestContext(request))

def dtu_group_add(request):
    if request.method == 'POST':
        try:
            groupid = request.POST.get('id','')
            if groupid:
                dg = Dtu_group.objects.get(pk=groupid)
                form = DtuGroupModelForm(instance=dg,data=request.POST)
            else:
                form = DtuGroupModelForm(data=request.POST)
            if form.is_valid():
                user = User.objects.getCurrentUser(request)
                dtu_group = form.instance
                dtu_group.user = user
                dtu_group.save()
                return HttpResponse(1)
        except:
            return HttpResponse(0)
    else:
        return HttpResponse(0)
    
    
def dtu_group_del(request):
    if request.method == "POST":
        try:
            ids = request.POST.get('ids')
            ids = unicode.encode(ids,'utf-8')
            id_list = ids.split(",")
            dtu_groups =  Dtu_group.objects.filter(id__in=id_list)
            count = len(dtu_groups)
            dtu_groups.delete()
            return HttpResponse("1")
        except:
            return HttpResponse("0")
    else:
        return HttpResponse("0")    
def dtu_group_list(request,template="device/grouplist.html"):
    user = User.objects.getCurrentUser(request)
    groups = user.dtu_group_set.all()
    context = Context({
        'title':'DTU设备组管理',
        'results': devidePage(request,groups,10),
    })
#    return render_to_response('system/updateAdminUsers.html',context,context_instance=RequestContext(request))
    return render_to_response(template,context,context_instance=RequestContext(request))
#def dtu_group_add(request):
#    if request.method == 'POST':
#        form = DtuGroupModelForm(data=request.POST)
#        if form.is_valid():
#            form.save(commit=True);
#            tip = u'添加成功'
#        else:
#            return render_to_response("vehicle/vehicle_add.html", {'form': form,}, context_instance=RequestContext(request))
#            tip = u'未正确填写,添加失败'
#        context = Context({
#            'tip':tip,
#            'reurl':'',
#            })
#        return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))        
#    else:
#        form = DtuGroupModelForm()
#        context = Context({
#            'form': form,
#            'title':'车辆添加',
#            })
#        return render_to_response('vehicle/vehicle_add.html',context,context_instance=RequestContext(request))
def group_dtu(request):
    if request.method == 'POST':
##        user = User.objects.getCurrentUser(request)
##        group = devices  = user.dtu_group_set.all().get(name="user1设备组1")
#        devices  = user.dtu_group_set.all().get(name="user1设备组1").dtu_group_r.all()
#        for device in devices:
#            print device
#        for group in groups:
#            print group
        
        form = DtuGroupRModeForm(request,data=request.POST)
        if form.is_valid():
#            return HttpResponse(u"success")
            form.save(commit=True);
#            user = User.objects.getCurrentUser(request)
#            dtu_group = form.instance
#            dtu_group.user = user
#            dtu_group.save()
            tip = u'添加成功'
        else:
            return render_to_response("vehicle/vehicle_add.html", {'form': form,}, context_instance=RequestContext(request))
            tip = u'未正确填写,添加失败'
        context = Context({
            'tip':tip,
            'reurl':'',
            })
        return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))        
    else:
        form = DtuGroupRModeForm(request)
        context = Context({
            'form': form,
            'title':'车辆添加',
            })
        return render_to_response('vehicle/vehicle_add.html',context,context_instance=RequestContext(request))

def myvehiclegroup(request):
    if request.method == 'GET': 
        try:
            groupid = request.GET.get('groupid',"")
            if groupid: 
                vg = Vehicle_group.objects.get(pk=groupid)
                form = VehicleGroupModelForm(instance=vg)
            else:
                form = VehicleGroupModelForm()
            user = User.objects.getCurrentUser(request)
            groups = user.vehicle_group_set.all()
            vehicles = getvehicles_by_group(user,0)
            
            context = Context({
                'groups': groups,
                'vehicles': vehicles,
                'form':form
                })
        #    return render_to_response('vehicle/group_device.html',context,context_instance=RequestContext(request))
            return render_to_response('car/group.html',context,context_instance=RequestContext(request))
        except:
            raise Http404
    else:
        raise Http404
    
def mydtugroup(request,template="device/group.html"):
    if request.method == 'GET': 
        try:
            groupid = request.GET.get('groupid',"")
            if groupid: 
                dg = Dtu_group.objects.get(pk=groupid)
                form = DtuGroupModelForm(instance=dg)
            else:
                form = DtuGroupModelForm()
            user = User.objects.getCurrentUser(request)
            groups = user.dtu_group_set.all() 
            dtus = getDtus_by_group(user,0)
            
            context = Context({
                'groups': groups,
                'vehicles': dtus,
                'form':form
                })
            return render_to_response(template,context,context_instance=RequestContext(request))
        except:
            raise Http404
    else:
        raise Http404


def updateInstalldate(request,vehicle_id):
    vehicle = get_object_or_404(Vehicle,pk=vehicle_id)
    if request.method == 'POST':
        form = UpdateVehicleForm(data=request.POST,instance=vehicle)
        if form.is_valid():
            form.save(commit=True);
            tip = u'更新成功'
            context = Context({
            'tip':tip,
            'reurl':'',
            })
            return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))
        else:
            return render_to_response("car/vehicle_dtu.html", {'form': form}, context_instance=RequestContext(request))
            tip = u'未正确填写,添加失败'
                
    else:
        
        form = UpdateVehicleForm(instance=vehicle)
        context = Context({
            'form': form,
            'title':'车辆添加',
            })
        return render_to_response('car/vehicle_dtu.html',context,context_instance=RequestContext(request))

#def vehicle_dtu(request,vehicle_id):
#    try:
#        vehicle_id = int(vehicle_id)
#        vehicle = Vehicle.objects.get(pk=vehicle_id)
#        if request.method =="POST":
#            
#        
#        else:
#            pass
#        return render_to_response('car/vehicle_dtu.html',{"vehicles":vehicles},context_instance=RequestContext(request))
#    except:
#         raise Http404()
        
#    vehicles = Vehicle.objects.all()
    

def getvehicles_by_group(user,group_id):
    if group_id == 0:
        groups = user.vehicle_group_set.all()
        ingroupsVehicle = Vehicle_Group_r.objects.filter(vehicle_group__in=groups)
#            ingroupsVihicle = vehicle_Group_r
        ingroupsVehicle_ids =ingroupsVehicle.values_list('vehicle',flat=True)
        vehicles = Vehicle.objects.all().exclude(id__in=ingroupsVehicle_ids)
    else:
        vehicle_group = get_object_or_404(Vehicle_group,pk=group_id)
        vehicles_ids = Vehicle_Group_r.objects.filter(vehicle_group=vehicle_group).values_list('vehicle',flat=True)
        vehicles = Vehicle.objects.filter(id__in=vehicles_ids)
    return  vehicles   



def vehicles_by_group(request,group_id):
    
    try:
        group_id = int(group_id)
    except:
        return HttpResponse("error")
    
    else:
        mimetype = 'application/javascript'
        user = User.objects.getCurrentUser(request)
        vehicles =getvehicles_by_group(user,group_id)
        result = getJson(result="success",vehicles=vehicles)
        return HttpResponse(result,mimetype)
#        context = ({
#                    "results":vehicles,
#                    })
#        return render_to_response('results.html',context,context_instance=RequestContext(request))    
def getDtus_by_group(user,group_id):
    if group_id == 0:
        groups = user.dtu_group_set.all()
        ingroupsVihicle = Dtu_Group_r.objects.filter(dtu_group__in=groups)
#            ingroupsVihicle = vehicle_Group_r
        ingroupsVihicle_ids =ingroupsVihicle.values_list('dtu',flat=True)
        dtus = Dtu.objects.all().exclude(id__in=ingroupsVihicle_ids)
    else:
        dtu_group = get_object_or_404(Dtu_group,pk=group_id)
        dtus_ids = Dtu_Group_r.objects.filter(dtu_group=dtu_group).values_list('dtu',flat=True)
        dtus = Dtu.objects.filter(id__in=dtus_ids)
    return  dtus 
def dtus_by_group(request,group_id):
    
    try:
        group_id = int(group_id)
    except:
        return HttpResponse("error")
    
    else:
        mimetype = 'application/javascript'
        user = User.objects.getCurrentUser(request)
        dtus = getDtus_by_group(user,group_id)
        result = getJson(result="success",vehicles=dtus)
        return HttpResponse(result,mimetype)
      
def change_vehicles_group_r(request):
    user = User.objects.getCurrentUser(request)
    if request.method == "POST":
        button = request.POST.get("button")  #点击的是哪个按钮 'button1'还是''button2'
        try:
            group1_id = int(request.POST.get("groups1"))  
            group2_id = int(request.POST.get("groups2"))
            vehicle_ids = request.POST.get("ids")
        except:
            return HttpResponse("出错")
        else:
            try:
                vehicle_ids = unicode.encode(vehicle_ids,'utf-8')
            except:
                return HttpResponse("编码出错")
            vehicle_ids = vehicle_ids.split(",")
            vehicles = Vehicle.objects.filter(id__in=vehicle_ids)
            if button == "button1":
                fromGroup_id = group1_id
                toGroup_id = group2_id
            else:
                fromGroup_id = group2_id
                toGroup_id = group1_id
                
            if fromGroup_id == 0 and toGroup_id == 0 or fromGroup_id == toGroup_id:
                return HttpResponse("error")
            elif fromGroup_id == 0: 
                #若是从未分组移动到分组中则是添加记录
                toGroup = get_object_or_404(Vehicle_group,pk=toGroup_id)
                for vehicle in vehicles:
                    v_g_r = Vehicle_Group_r(vehicle=vehicle,vehicle_group=toGroup)
                    v_g_r.save() 
            elif toGroup_id == 0:
                fromGroup = get_object_or_404(Vehicle_group,pk=fromGroup_id)
                #若是从分组移动到未分组中则是删除记录
                v_g_r = Vehicle_Group_r.objects.filter(vehicle_group=fromGroup,vehicle__in=vehicles)
                v_g_r.delete()
            else:
                #从分组1移动到分组2,则是修改记录
                fromGroup = get_object_or_404(Vehicle_group,pk=fromGroup_id)
                toGroup = get_object_or_404(Vehicle_group,pk=toGroup_id)
                v_g_r = Vehicle_Group_r.objects.filter(vehicle_group=fromGroup,vehicle__in=vehicles)
                v_g_r.update(vehicle_group=toGroup)
            vehicles1 =getvehicles_by_group(user,group1_id)
            vehicles2 =getvehicles_by_group(user,group2_id)
            result = getJson(vehicles1=vehicles1,vehicles2=vehicles2)
            return HttpResponse(result)
        

def change_dtus_group_r(request):
    user = User.objects.getCurrentUser(request)
    if request.method == "POST":
        button = request.POST.get("button")  #点击的是哪个按钮 'button1'还是''button2'
        try:
            group1_id = int(request.POST.get("groups1"))  
            group2_id = int(request.POST.get("groups2"))
            dtu_ids = request.POST.get("ids")
        except:
            return HttpResponse("error")
        else:
            try:
                dtu_ids = unicode.encode(dtu_ids,'utf-8')
            except:
                return HttpResponse("error")
            dtu_ids = dtu_ids.split(",")
            dtus = Dtu.objects.filter(id__in=dtu_ids)
            if button == "button1":
                fromGroup_id = group1_id
                toGroup_id = group2_id
            else:
                fromGroup_id = group2_id
                toGroup_id = group1_id
                
            if fromGroup_id == 0 and toGroup_id == 0 or fromGroup_id == toGroup_id:
                return HttpResponse("error")
            elif fromGroup_id == 0: 
                #若是从未分组移动到分组中则是添加记录
                toGroup = get_object_or_404(Dtu_group,pk=toGroup_id)
                for dtu in dtus:
                    v_g_r = Dtu_Group_r(dtu=dtu,dtu_group=toGroup)
                    v_g_r.save() 
            elif toGroup_id == 0:
                fromGroup = get_object_or_404(Dtu_group,pk=fromGroup_id)
                #若是从分组移动到未分组中则是删除记录
                v_g_r = Dtu_Group_r.objects.filter(dtu_group=fromGroup,dtu__in=dtus)
                v_g_r.delete()
            else:
                #从分组1移动到分组2,则是修改记录
                fromGroup = get_object_or_404(Dtu_group,pk=fromGroup_id)
                toGroup = get_object_or_404(Dtu_group,pk=toGroup_id)
                v_g_r = Dtu_Group_r.objects.filter(dtu_group=fromGroup,dtu__in=dtus)
                v_g_r.update(dtu_group=toGroup)
            vehicles1 =getDtus_by_group(user,group1_id)
            vehicles2 =getDtus_by_group(user,group2_id)
            result = getJson(vehicles1=vehicles1,vehicles2=vehicles2)
            return HttpResponse(result)
#def role_list(request,department_id):
#    li = []
#    from django.shortcuts import get_object_or_404
#    from utils import json
#    city = get_object_or_404(Department, pk=department_id)
#    role_list = Role.objects.filter(department=city)
#    for object in role_list:
#        d = {}
#        d['label'] = object.name
#        d['text'] = object.id
#        li.append(d)

#    obj = json.write(li)
#    return HttpResponse(obj)            
#def inboxmessage2(request):
#    from django.utils import simplejson
#    from utils.MyEncoder import *
#    users = User.objects.all()
#    result = getJson(result="success",users=users)
#    return HttpResponse(result)