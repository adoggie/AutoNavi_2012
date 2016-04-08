#--encoding:utf-8--
'''
Created on 2012-4-22
@author: DTR
'''
from django.shortcuts import render_to_response,get_object_or_404
from utils.pageHandle import devidePage
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
import datetime
from system.forms import UserModelForm,LoginForm,ChangePasswordForm
from django.utils import simplejson

from system.models import *
#################################
############ 车辆管理 ############                          
#################################
def user_add(request,user_id="",template="system/useradd.html"):
    user = ""
    if user_id:
        try:
            user_id = int(user_id)
            
        except:
            return Http404()
        else:
            user = get_object_or_404(User,pk=user_id)
            
    instance =user               
    if request.method == 'POST':
        if instance:
            form = UserModelForm(data=request.POST,instance=instance)
        else:
            form = UserModelForm(data=request.POST)
        if form.is_valid():
#            return HttpResponse(u"success")
            form.save(commit=True) #form.save(commit==False)
            tip = u'添加成功'
            context = Context({
            'tip':tip,
            })
            return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))
    else:
        if instance:
            form = UserModelForm(instance=instance)
        else:
            form = UserModelForm()
    context = Context({
        'form': form,
        'title':'用户添加',
        })
    return render_to_response(template,context,context_instance=RequestContext(request))
#    return render_to_response('vehicle/vehicle_add.html',context,context_instance=RequestContext(request))
def user_edit(request,user_id="",template="system/useradd.html"):
    if user_id:
        try:
            user_id = int(user_id)
            
        except:
            return Http404()
        else:
            user = get_object_or_404(User,pk=user_id)
            if request.method == 'POST':
                form = UserModelForm(data=request.POST,instance=user)
                if form.is_valid():
                    form.save(commit=True) #form.save(commit==False)
                    tip = u'修改成功'
                    context = Context({
                    'tip':tip,
                    })
                    return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))
            else:
                form = UserModelForm(instance=user)
            context = Context({
                'form': form,
                'title':'用户修改',
                })
            return render_to_response(template,context,context_instance=RequestContext(request))
        
def user_delete(request,user_id):
    try:
        user_id = int(user_id)
        user = get_object_or_404(User,pk=user_id)
        user.delete()
        return HttpResponseRedirect("/system/user_list/")
    except:
        return HttpResponse("error")
    
    
def user_list(request):
    ids=[]
    if 'ids' in request.POST and request.POST['ids'] is not None:
        ids = request.POST.getlist('ids')
        u = User.objects.filter(id__in=ids)
        u.delete()
    user_list = User.objects.all()
    context = Context({
        'title':'用户管理',
        'results': devidePage(request,user_list,10),
    })
#    return render_to_response('system/updateAdminUsers.html',context,context_instance=RequestContext(request))
    return render_to_response('system/userlist.html',context,context_instance=RequestContext(request))
    
def changePassword(request,template="system/changePassword.html"):
    user = User.objects.getCurrentUser(request)    
    if request.method == 'POST':
        form = ChangePasswordForm(user=user,data=request.POST)
        if form.is_valid():
#            return HttpResponse(u"success")
            form.save(commit=True) #form.save(commit==False)
            tip = u'密码修改成功'
            context = Context({
            'tip':tip,
            })
            return render_to_response("autoRedirect.html",context,context_instance=RequestContext(request))
    else:
        form = ChangePasswordForm(user=user)
    context = Context({
        'form': form,
        'title':'用户添加',
        })
    return render_to_response(template,context,context_instance=RequestContext(request))

################################login in模块###################################################
def checkLogin(user):
    if  user:
        return True
    else:
        return False
    
def requires_login(view):
    def new_view(request, *args, **kwargs):
        user = User.objects.getCurrentUser(request)
        if not checkLogin(user):
            return HttpResponseRedirect('/login/')
        else:
            return view(request, *args, **kwargs)
    return new_view
def login(request, error='',template="login/login.html"):
    user = User.objects.getCurrentUser(request)
    if not checkLogin(user):
        if request.method == "POST":
            LF = LoginForm(request.POST)
            if LF.is_valid():
                request.session['user_id'] = LF.user.id
                return HttpResponseRedirect("/index/")
        else:
            LF = LoginForm()
        context = Context({
            'form': LF,
            'title':'DVR采集管理系统登入界面',
            'error':error,
            })
        return render_to_response(template, context, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/index/")   
def index(request):
    request.session.set_expiry(0) #session保存时间，单位为秒
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
    #                return render_to_response("home.html")
#    urls =  request.session.get('urls')
#    client_ip = request.META['REMOTE_ADDR']
#    user_agent = request.META['HTTP_USER_AGENT']
    context = Context({
               'title':'高德软件DVR采集管理系统主页',
               'hello': 'hello',
               })
    
    return render_to_response("login/index.html",context,context_instance=RequestContext(request))#render_to_response("home.html") #HttpResponseRedirect("/system/index")

#def hasDepartmentPremession(department): 
#    return department in Department.objects.getManageDepartment(department)    

################################login out###################################################   
def logout(request):
    try:
        del request.session['user_id']
#        del request.session['login_time']
#        del request.session['client_ip']
#        del request.session['url']
#        del request.session['sources']
        print "del success"
    except KeyError,e:
        print e
    finally:
        return HttpResponseRedirect('/login/')
def top(request):
    return render_to_response('login/Top.html')
        
def main(request):
#    try: 
#        client_ip = request.META['REMOTE_ADDR']
#    except KeyError,e:
#        print('no key REMOTE_ADDR')
#        
#    login_time = request.session.get('login_time')
#    user = request.session.get('user')
#    depts = Department.objects.getManageDepartment(request)
##    notices = Notice.objects.filter(department__in=depts)[:3]
#    ancestor_departments = Department.objects.getAncestors(user)
#    notices = Notice.objects.filter(status=True,department__in=ancestor_departments).order_by("-publish_time")[:3]
#    context=Context({
#                     'client_ip':client_ip,
#                     'login_time':login_time,
#                     'user':user,
#                     'notices':notices,
#                     })
#    return render_to_response('main.html',context,context_instance=RequestContext(request))
    return render_to_response('login/main.html')

def left(request):
#    try: 
#        client_ip = request.META['REMOTE_ADDR']
#    except KeyError,e:
#        print('no key REMOTE_ADDR')
#    login_time = request.session.get('login_time')
#    user = request.session.get('user')    
#    if user is not None:
#        if user.super_admin:
#            role = "超级管理员"
#        else:
#            role = user.role.name
#        photo = user.touxiang    
#    context=Context({
#                     'user':user,
#                     'client_ip':client_ip,
#                     'login_time':login_time,
#                     'role':role,
#                     'photo':photo,
#                     })
    return render_to_response("login/Left.html")

    