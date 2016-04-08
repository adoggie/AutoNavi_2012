rem 复位数据库，创建根用户，添加配置信息
set DJANGO_SETTINGS_MODULE=taxserver.settings
manage reset core
python taxserver.py
pause
