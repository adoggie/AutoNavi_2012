#-*- coding=utf-8 -*
import thread
from django.shortcuts import render_to_response,get_object_or_404
from utils.pageHandle import devidePage
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
import datetime
from strategy.forms import AreaModelForm,StrategyModelForm,AreagroupModelForm,Strategy_groupModelForm
from strategy.models import Strategy,Area,Areagroup,Strategy_group
from device.models import Vehicle
from utils.coordConvert import *
from utils.MyEncoder import *

#################################
############ 区域管理 ############                          
#################################

def area_group_add(request):
    if request.method == 'POST':
        form = AreagroupModelForm(data=request.POST)
        if form.is_valid():
        #            return HttpResponse(u"success")
            form.save() #form.save(commit==False)
            tip = u'添加成功'
        else:
            tip = u'未正确填写,添加失败'
        context = Context({
            'tip':tip,
            'reurl':'',
            })
        return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))
    else:
        form = AreagroupModelForm()
        context = Context({
            'form': form,
            'title':'区域组添加',
            })

        return render_to_response('strategy/addareagroup.html',context,context_instance=RequestContext(request))
def area_add(request):
    if request.method == 'POST':
        form = AreaModelForm(data=request.POST)
        if form.is_valid():
        #            return HttpResponse(u"success")
            try:
                instance = form.instance
                area_gps = areamap2gps(instance.area_map)
                instance.area_gps = area_gps
    #            instance.area_gps ="aa"
                instance.save() #form.save(commit==False)
                return HttpResponse("1")
            except:
                return HttpResponse("0")
        else:
            return HttpResponse("0")
    else:
        form = AreaModelForm()
        context = Context({
            'form': form,
            'title':'区域添加',
            })

        return render_to_response('strategy/areas.html',context,context_instance=RequestContext(request))



def area_edit(request,area_id,template="strategy/areas.html"):
        try:
            area_id = int(area_id)
        except ValueError,e:
            return HttpResponse("0")
        else:
            area = get_object_or_404(Area,pk=area_id)
            if request.method == 'POST':
                form =  AreaModelForm(data=request.POST,instance=area)
                if form.is_valid():
                    form.save() #form.save(commit==False)
                    return HttpResponse("1")
                else:
                    return HttpResponse("0")
                    #        return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))
            else:
                form = AreaModelForm(instance=area)
                context = Context({
                    'form': form,
                    'title':'区域修改',
                    })
                return render_to_response(template,context,context_instance=RequestContext(request))

def area_list(request,template="strategy/arealist.html"):
    area_groups = Areagroup.objects.all()
    
    area=Area.objects.all()
    context = Context({
        'title':'修改区域',
        'results': devidePage(request, area,10),
        'groups':area_groups
        })

    return render_to_response(template,context,context_instance=RequestContext(request))
'''
通过组区域组id获取区域,返回json格式区域集
'''
def get_area_by_group(request,areagroup_id):
    try:
        area_queryset = Area.objects.filter(group__id=areagroup_id)
        content = getJson(status="success",areas=area_queryset)
        return HttpResponse(content,"application/javascript")
    except:
        content = getJson(failure="success") 
def area_view(request,template="strategy/areaview.html"):
    area=Area.objects.all()
    context = Context({
    'title':'区域查看',
    'results': devidePage(request, area,10),
    })

    return render_to_response(template,context,context_instance=RequestContext(request))

def area_delete(request, area_id):
    try:
        area_id = int( area_id)
        area = get_object_or_404(Area,pk= area_id)
        area.delete()
        return HttpResponseRedirect("/strategy/area/list/")
    except:
        raise Http404()
    
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
def  strategy_add(request):
    if request.method == 'POST':
        form = StrategyModelForm(data=request.POST)
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
        form = StrategyModelForm()
    context = Context({
        'form': form,
        'title':'策略添加',
        })
    return render_to_response("strategy/addstrategy.html",context,context_instance=RequestContext(request))
def strategy_group_add(request):
    if request.method == 'POST':
        form = Strategy_groupModelForm(data=request.POST)
        if form.is_valid():
        #            return HttpResponse(u"success")
            form.save() #form.save(commit==False)
            tip = u'添加成功'
        else:
            tip = u'未正确填写,添加失败'
        context = Context({
            'tip':tip,
            'reurl':'',
            })
        return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))
    else:
        form = Strategy_groupModelForm()
        context = Context({
            'form': form,
            'title':'策略组添加',
            })
        return render_to_response('strategy/addstrategygroup.html',context,context_instance=RequestContext(request))

def strategy_edit(request,strategy_id,template="strategy/addstrategy.html"):
    try:
        strategy_id = int(strategy_id)
    except ValueError,e:
        raise Http404()
    else:
        strategy = get_object_or_404(Strategy,pk=strategy_id)
        if request.method == 'POST':
            form =  StrategyModelForm(data=request.POST,instance=strategy)
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
            form = StrategyModelForm(instance=strategy)
        context = Context({
            'form': form,
            'title':'策略修改',
            })
        return render_to_response(template,context,context_instance=RequestContext(request))


def strategy_list(request,template="strategy/updatestry.html"):

    strategy = Strategy.objects.all()
    context = Context({
        'title':'修改策略',
        'results': devidePage(request,strategy,10),
        })

    return render_to_response(template,context,context_instance=RequestContext(request))

def strategy_delete(request):
    if request.method == "POST":
        try:
            ids = request.POST.get('ids')
            ids = unicode.encode(ids,'utf-8')
            id_list = ids.split(",")
            stras =  Strategy.objects.filter(id__in=id_list)
            count = len(stras)
            stras.delete()
            return HttpResponse("1")
        except:
            return HttpResponse("0")
    else:
        return HttpResponse("0")
#def strategy_delete(request,strategy_id):
#    try:
#        strategy_id = int(strategy_id)
#        strategy = get_object_or_404(Strategy,pk=strategy_id)
#        strategy.delete()
#        return HttpResponseRedirect("/strategy/strategy/list/")
#    except:
#        raise Http404()
    
def  vehicle_strategy(request):
    vehicles = Vehicle.objects.all();
    for vehicle in vehicles:
        print vehicle
    if request.method == 'POST':
        form = StrategyModelForm(data=request.POST)
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
        form = StrategyModelForm()
    context = Context({
        'form': form,
        'title':'策略添加',
        "vehicles":vehicles,
        })
    return render_to_response("strategy/vehicle_strategy.html",context,context_instance=RequestContext(request))

def vehicle_getstrategy(request,vehicle_id):
    '''获取车辆,不存在返回404错误
                    获取车辆已经关联的策略
        获取未关联的策略
    '''
    try:
        vehicle_id = int(vehicle_id)
    except ValueError,e:
        content = getJson(status="failure")
        return HttpResponse(content,"appliacation/javascript")
    else:
        try: 
            vehicle = Vehicle.objects.get(pk=vehicle_id)
        except Vehicle.DoesNotExist,e :
            content = getJson(status="failure")
            return HttpResponse(content,"appliacation/javascript")
        else:
            content = getstrategy(vehicle)
            return HttpResponse(content,"appliacation/javascript")
            
def getstrategy(vehicle): 
    hasStras  = vehicle.vechicle_strategy_r.all()
    strategy_ids = hasStras.values_list('id',flat=True)
    avaStras = Strategy.objects.all().exclude(id__in=strategy_ids)
    content = getJson(status="success",avaStras=avaStras,hasStras=hasStras)
    return content
           
def assign_stragety(request):
    #取得按钮信息
    #取得车辆信息,和选中的策略信息
    #备选策略->已选策略,则添加记录
    #已选策略->已选策略,则删除记录
    if request.method == "GET":
        button = request.GET.get("button")  #点击的是哪个按钮 'button1'还是''button2'
        try:
            vehicle_id = int(request.GET.get("vehicle_id"))  
            strategy_ids = request.GET.get("ids")
            vehicle = Vehicle.objects.get(pk=vehicle_id)
        except:
            return HttpResponse("error")
        else:
            try:
                strategy_ids = unicode.encode(strategy_ids,'utf-8')
            except:
                return HttpResponse("error")
            strategy_ids = strategy_ids.split(",")
            strategys = Strategy.objects.filter(id__in=strategy_ids)
            if button == "button1":
                for strategy in strategys:
                    vehicle.vechicle_strategy_r.add(strategy)
            else:
                for strategy in strategys:
                    vehicle.vechicle_strategy_r.remove(strategy)
            content = getstrategy(vehicle)
            return HttpResponse(content,"appliacation/javascript") 
