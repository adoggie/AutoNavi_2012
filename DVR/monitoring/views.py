#-*- coding=utf-8 -*
import thread
from django.shortcuts import render_to_response,get_object_or_404
from utils.pageHandle import devidePage
from django.core.urlresolvers import reverse
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
import datetime
from device.models import Vehicle
from monitoring.models import GPS_LOG
from utils.MyEncoder import *
from django.utils import simplejson
import datetime
def track(request):
    return render_to_response("monitoring/track.html",{},context_instance=RequestContext(request))

def recentTrack(request):
    return render_to_response("monitoring/recentTrack.html",{},context_instance=RequestContext(request))

def disposition(request):
    return render_to_response("monitoring/disposition.html",{},context_instance=RequestContext(request))
def getDisposition(request):
    result ={"status":"success"}
    gps_logs_list = []
    vehicle_queryset = Vehicle.objects.all()
    for vehicle in  vehicle_queryset:
        gps_logs = GPS_LOG.objects.filter(vehicle = vehicle).order_by("-timetick")[:1]
        for gps_log in gps_logs:
            gps_logs_list.append(gps_log)
#        gps_log.add()
    content = getJson2(result,gps_logs=gps_logs_list)
    return HttpResponse(content,"application/javascript") 
def getTrack(request,vehicle_name="EN3870_1-6_FILE0039"):
    result ={"status":"error"}
    if request.method == "POST":
        vehicle_name = request.POST.get("vehicle_name")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        if vehicle_name and start_time and end_time:
            response = get_gps_log(result,vehicle_name,start_time,end_time)
            return response
    else:
        result = getJson2(result)
        return HttpResponse(result,"application/javascript")
        
def getRecentTrack(request,vehicle_name="EN3870_1-6_FILE0039"):
    result ={"status":"error"}
    if request.method == "POST":
        vehicle_name = request.POST.get("vehicle_name")
        recent = request.POST.get("recent")
        try:
            recent = int(recent)
        except ValueError,e:
            content = getJson2(result)
            return HttpResponse(content,mimetype='application/json')
        else:
            now = datetime.datetime.now()
            start_time = now - datetime.timedelta(hours=recent)
            end_time = now
            if vehicle_name and start_time and end_time:
                response = get_gps_log(result,vehicle_name,start_time,end_time)
                return response
    else:
        result = getJson2(result)
        return HttpResponse(result,"application/javascript")
        
        
def get_gps_log(result,vehicle_name,start_time,end_time):
    try:
        vehicle = Vehicle.objects.get(vehicle_num=vehicle_name)#get_object_or_404(Vehicle,vehicle_num=vehicle_name)
    except:
        content = getJson2(result)
        return HttpResponse(content,"application/javascript")  #表示查询的车辆不存在
    else:
        gps_logs = GPS_LOG.objects.filter(vehicle=vehicle,time__range=(start_time,end_time))
        result["status"] = "success"
#        dictaa={"aaaa":"aaa","bbb":"bbb",result:"success",gps_logs:gps_logs,}
        content = getJson2(result,gps_logs=gps_logs)
        return HttpResponse(content,"application/javascript") 
