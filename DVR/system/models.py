#-*- coding=utf-8 -*
from django.db import models
import datetime
from django.db import connection
from django import forms
from django.contrib.auth.models import get_hexdigest,check_password
from django.db.models import Q
from md5 import md5
UNUSABLE_PASSWORD = '!' # This will never be a valid hash

GENDER_CHOICES = (
    (u'M', u'男'),
    (u'F', u'女'),
    )
ROLE_CHOICES = (
    (1, u'管理员'),
    (0, u'用户'),
    )

def encrypt(raw_str):
    raw_str = md5(md5(raw_str).hexdigest()).hexdigest()
    return  raw_str
#class Department_relatetionship(models.Model):
#    parent_id = models.ForeignKey(Department)
class UserManager(models.Manager):
    def getCurrentUser(self,request):
        userid = request.session.get("user_id",'')
        if userid:
            user = self.getUser(userid)
            return user
        
    def getUser(self,id):
        try:
            user = User.objects.get(pk=id)
            return user
        except:
            return ''
        
    def make_random_password(self, length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
        "Generates a random password with the given length and given allowed_chars"
        # Note that default value of allowed_chars does not have "I" or letters
        # that look like it -- just to avoid confusion.
        from random import choice
        return ''.join([choice(allowed_chars) for i in range(length)])


class User(models.Model):
    username = models.CharField(verbose_name=u'用户名',max_length=100,unique=True)
    password = models.CharField(verbose_name=u'密码',max_length=100)
    real_name = models.CharField(verbose_name=u'姓名',max_length=100)
    gender = models.CharField(verbose_name=u'性别',max_length=2, choices=GENDER_CHOICES)
    tel = models.CharField(verbose_name=u'电话',max_length=100,blank=True)
    email = models.EmailField(verbose_name=u'邮箱',blank=True)
    role = models.IntegerField(verbose_name=u'用户类型',choices=ROLE_CHOICES)
    
    

    objects = UserManager()

    class Meta:
        verbose_name = 'user'
        ordering = ['id']

    def __unicode__(self):
        return self.username

    def set_password(self, raw_password):
        if raw_password is None:
            self.set_unusable_password()
        else:
            self.password = encrypt(raw_password)
            
    def check_password(self, raw_password):
        '比较密码是否正确'
        raw_password =  encrypt(raw_password)
        return self.password == raw_password


    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = UNUSABLE_PASSWORD

    def is_admin(self):
        return self.admin_or_not

    def is_super_admin(self):
        return self.super_admin

#    def admin_depts(self):
#        return self.admin_depts
#class Log(models.Model):
#    user = models.ForeignKey(User)
#    action = models.TextField()
#    time = models.DateTimeField("aticon Time", auto_now_add=True,blank=True, null=True)
#    def __unicode__(self):
#        return self.user
#    class Meta:
#        db_table = 'action_log'
#        ordering = ['id']    
