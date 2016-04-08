# --coding:utf-8--
'''
Created on 2012-7-3

@author: DTR
'''
from django import forms
from django.forms import ModelForm
from strategy.models import Area,Strategy,Areagroup,Strategy_group


class AreagroupModelForm(ModelForm):
    class Meta:
        model = Areagroup
        
class AreaModelForm(ModelForm):
    area_map = forms.CharField(widget=forms.Textarea(attrs={'rows': "4", 'cols': "20","readonly":"readonly","style":"display:none",}))
    class Meta:
        model = Area
        exclude = ("area_gps")
#        fields = ("name","area","group")
        
        
class Strategy_groupModelForm(ModelForm):
    class Meta:
        model = Strategy_group
class StrategyModelForm(ModelForm):
    begin_date = forms.DateField(widget=forms.DateInput(attrs={"onFocus":"WdatePicker()"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"onFocus":"WdatePicker()"}))
    class Meta:
        model = Strategy
        exclude = ('vechicles_r')
