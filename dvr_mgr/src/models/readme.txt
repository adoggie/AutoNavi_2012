====================================================
����django����ʹ��django�����ݳ־û����� 
���û������� :  set DJANGO_SETTINGS_MODULE=kqstock.settings
���PYTHONPATH·�� sys.path.append('e:/works/newgis/django')
����app ����
  import giscore.models
  vp = giscore.models.VisitedPoint()

====================================================
geoExt-1.0
ext-3.2.0
openlayer-2.8
django-1.1
====================================================


django Ĭ�� DataTimeField����ʱ�������ǲ��ò�ʹ��ʱ����ʽ�洢��
���Խ�postgresql/creation.py ���ǵ�C:\Python26\Lib\site-packages\django\db\backends\postgresql

python django-amin startapp
python manage.py reset giscore  #�������ݿ�
python manage.py runserver localhost:8000

��ʼ�����ݿ� ../src/das/initdb.py
