# --coding:utf-8--
'''
Created on 2012-7-3

@author: DTR
'''
from django import forms
from django.forms import ModelForm
from device.models import Vehicle,Dtu,Vehicle_group,Dtu_group,Vehicle_Group_r,Dtu_Group_r
from system.models import User
STATUS=((0,u'禁用'),(1,u'启用'))

class VehicleModelForm(ModelForm):
    install_date = forms.DateField(label=u'设备安装日期',widget=forms.DateInput(attrs={"onFocus":"WdatePicker()"}))
    status = forms.ChoiceField(choices=STATUS,label=u'状态')
    descri = forms.CharField(widget=forms.Textarea(attrs={'rows': "5", 'cols': "20",}))
#    vehicle_num = forms.CharField(widget=forms.TextInput(attrs={'size': 10, 'title': 'Your name',}))
    class Meta:
        model = Vehicle
#        exclude = ('install_date','status','dtu')

class UpdateVehicleForm(ModelForm):
    vehicle_num = forms.CharField(widget=forms.TextInput(attrs={'readonly': "readonly",'style':"background-color:gray"}))
    name = forms.CharField(widget=forms.TextInput(attrs={'readonly': "readonly",'style':"background-color:gray"}))
    install_date = forms.DateField(label=u'设备安装日期',required=False,widget=forms.DateInput(attrs={"onFocus":"WdatePicker()"}))
    status = forms.ChoiceField(choices=STATUS,label=u'状态',required=False)
    dtu = forms.ModelChoiceField(queryset=Dtu.objects.all(),label=u'安装的设备',required=False)
    class Meta:
        model = Vehicle
        exclude = ('driver','tel','descri')
#    install_date = models.DateField(verbose_name=u'设备安装日期',blank=True,null=True)
#    status = models.IntegerField(verbose_name=u'设备状态',blank=True,null=True)
#    device = models.OneToOneField(Dtu,verbose_name=u'设备',blank=True,null=True)          

   
class VehicleGroupModelForm(ModelForm):
    class Meta:
        model = Vehicle_group
        exclude = ('vehicles','user')
#    def save(self, commit=True):
#        if commit:
#            self.instance.save()
#        return self.instance        
class VehicleGroupRModelForm(ModelForm):
    class Meta:
        model = Vehicle_Group_r
    def __init__(self,request,*args, **kwargs):
        super(VehicleGroupRModelForm, self).__init__(*args, **kwargs)
        user = User.objects.getCurrentUser(request)
        vehicle_group = user.vehicle_group_set.all()
        self.fields['vehicle_group'].queryset = vehicle_group
#        exclude = ('user')
        
class DtuModelForm(ModelForm):
    class Meta:
        model = Dtu
        
        
class DtuGroupModelForm(ModelForm):
#    user = forms.ModelChoiceField(queryset=User.objects.get(pk=1))
    class Meta:
        model = Dtu_group
        exclude = ('dtus','user')

class DtuGroupRModeForm(ModelForm):
#    user = forms.ModelChoiceField(queryset=User.objects.get(pk=1))
    class Meta:
        model = Dtu_Group_r
    def __init__(self,request,*args, **kwargs):
        super(DtuGroupRModeForm, self).__init__(*args, **kwargs)
        user = User.objects.getCurrentUser(request)
        dtu_group = user.dtu_group_set.all()
        self.fields['dtu_group'].queryset = dtu_group
