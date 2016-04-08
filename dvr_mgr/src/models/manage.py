#!/usr/bin/env python

import socket,sys,traceback

#s = socket.socket()
#try:
#    s.bind(('127.0.0.1',4977))
#except:
#    traceback.print_exc()
#    sys.exit()

from django.core.management import execute_manager



try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)


if __name__ == "__main__":
    #import sys,os
    #sys.path = sys.path[1:]
    #print sys.path
    #sys.stdout = open('syslog.txt','a+')
    execute_manager(settings)
