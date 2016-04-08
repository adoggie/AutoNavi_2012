#--coding:utf-8--
'''
Created on 2012-7-5

@author: DTR
'''
from django import forms
from django.forms import ModelForm
from system.models import User,encrypt
from md5 import md5
#from device.models import Vehicle
#VEHICLE_STATUS=(('1',u'可用'),('0',u'禁用'))

class UserModelForm(ModelForm):
    password = forms.CharField(label="密码",widget=forms.PasswordInput)
    password2 = forms.CharField(label="密码确认",widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('username','password','password2','real_name','gender','tel','email','role',)
        
    def save(self, commit=True):
        self.instance.set_password(self.cleaned_data['password'])
        if commit:
            self.instance.save()
        return self.instance
    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password!=password2:
            raise forms.ValidationError(u"两次密码不一致!")

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField("原密码", widget=forms.PasswordInput)
    new_password1 = forms.CharField("新密码", widget=forms.PasswordInput)
    new_password2 = forms.CharField("密码确认", widget=forms.PasswordInput)
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("两次密码不一致")
        return password2
    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if encrypt(old_password) != self.user.password:
            raise forms.ValidationError("原密码错误,请重新输入")
        return old_password
    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
#        self.user.password = self.cleaned_data['new_password1']
        if commit:
            self.user.save()
        return self.user    
class LoginForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(label="Username", max_length=30)
    password = forms.CharField(label="Password",max_length=30,widget=forms.PasswordInput)
    
    def clean_password(self):
        """
        Validates that the password field is correct.
        """
        username = self.cleaned_data.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(u"当前用户不存在!")
#        except:
#            raise forms.ValidationError(u"未知错误!")
        else:
            self.user = user
            d = self.cleaned_data.get('password')
            if  self.user.check_password(d):
                return True
            else:
                raise forms.ValidationError(u'用户名密码不匹配!')

  