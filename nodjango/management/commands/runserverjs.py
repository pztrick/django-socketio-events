from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import importlib
from inspect import getmembers, isfunction
# from django.apps import get_apps
# from django.core.management import call_command
import json
import traceback
import time

import logging
logging.basicConfig(level=logging.WARNING)

from socketIO_client import SocketIO, BaseNamespace

from django.core import serializers
from django.db.models import get_model

from subprocess import Popen
import signal
import sys
import os

nodjango_root = os.path.join(os.path.dirname(__file__), '../..')
nodjango_indexjs = os.path.join(nodjango_root, 'index.js')

class DjangoNamespace(BaseNamespace):
    def __init__(self, *args, **kwargs):
        super(DjangoNamespace, self).__init__(*args, **kwargs)

        # scan INSTALLED_APPS and register handlers
        self.handlers = {}
        for app_name in settings.INSTALLED_APPS:
            try:
                module = importlib.import_module("%s.socketio" % app_name)
                handlers = filter(lambda (x, y): isfunction(y), getmembers(module))
                namespaced_handlers = map(lambda (x, y): ("%s.%s" % (app_name, x), y), handlers)
                self.handlers.update(namespaced_handlers)
            except ImportError:
                pass

        print "\nAvailable Python handlers for socket.io:"
        for key in self.handlers.keys():
            print "\t%s" % (key, )
        print  #line

    def on_django(self, data):
        socket_id = data.pop('socket_id')
        response = {
            'socket_id': socket_id
        }
        try:
            callback = data.pop('callback', None)
            event = data.pop('event')
            payload = self.handlers.get(event)(data)

            response.update({
                'payload': payload,
                'callback': callback,
            })

            # print response
            self.emit('callback', response)
        except:
            response.update({
                'exception': traceback.format_exc()
            })
            # print response
            self.emit('python_exception', response)


class Command(BaseCommand):
    args = '<hostname> <public port> <runserver port> <socket port>'
    help = 'Listens over socket.io websocket'

    def handle(self, *args, **options):
        if len(args) != 4:
            raise Exception("Arguments needed: %s" % self.args)

        # parse arguments
        runserver_host = "%s:%s" % (args[0], args[2])
        runserver_cmd = "python manage.py runserver %s" % runserver_host
        nodejs_cmd = "node %s %s %s %s" % (nodjango_indexjs, args[1], args[2], args[3])

        try:
            # start nodejs proxy
            proc2 = Popen(nodejs_cmd, shell=True, preexec_fn=os.setsid, stdout=sys.stdout, stderr=sys.stderr)

            # start django runserver
            proc1 = Popen(runserver_cmd, shell=True, preexec_fn=os.setsid, stdout=sys.stdout, stderr=sys.stderr)

            time.sleep(2)

            # start django private socketio
            self.socket = SocketIO('127.0.0.1', int(args[3]), Namespace=DjangoNamespace)
            print '* * *\t django socket started'
            self.socket.wait()

        finally:
            print 'killing...'
            os.killpg(proc1.pid, signal.SIGTERM)
            os.killpg(proc2.pid, signal.SIGTERM)
            print 'killed!'