### What is django-socketio-events?

Simply adds socket.io functionality to Django applications by proxying Django behind a Nodejs/SocketIO server.

Any callback function defined in an `app_folder` is exposed to Socket.IO as the target `my_app.callback_fn`. See examples below.

### Usage

```
    python manage.py runserverjs <hostname> <public port> <proxy port> <socket port>
```

In any Django template that you want a Socket IO connection, add this templatetag to your HEAD:

```
{% load nodjango %}
<!doctype html>
<html>
<head>
    <script type="text/javascript" src="//code.jquery.com/jquery-2.1.1.min.js"></script>
    {% socketio_head_scripts %}
</head>
<body>
    <button>Click Me</button>
    <script type="text/javascript">
        socket.on('my_callback', function(data){
            console.log(JSON.stringify(data));
        });

        $('button').on('click', function(){
            socket.emit('django', {
                'event': 'my_app.change_color',
                'callback': 'my_callback',
                'color': 'red'
            });
        });
    </script>
</body>
</html>
```

```
# my_app/socketio.py

def change_color(color):
    # change color
    # ...
    # profit
    return {'result': 42}
```

### Installation

```
    pip install django-socketio-events
```

And then add `nodjango` to your `INSTALLED_APPS`.

### Under the hood

*   [virtual-node](https://github.com/elbaschid/virtual-node) for installing [node.js](http://nodejs.org/) in a Python virtualenv.
*   [Django](https://www.djangoproject.com/) web framework