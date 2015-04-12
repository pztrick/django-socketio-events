from django import template
from django.conf import settings
from django.shortcuts import render_to_response

import os
import subprocess

register = template.Library()

@register.simple_tag
def socketio_head():
    return """
            <script src="/socket.io/socket.io.js"></script>
            <script type="text/javascript">
                var socket = io();
                socket.on('python_exception', function(data){
                    console.log("Python exception:");
                    console.log(data.exception);
                });
                function getCookie(name) {
                    var value = "; " + document.cookie;
                    var parts = value.split("; " + name + "=");
                    if (parts.length == 2) return parts.pop().split(";").shift();
                }
            </script>
            """
