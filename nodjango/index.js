// parse args
var public_port = process.argv[2];
var django_port = process.argv[3];
var socket_port = process.argv[4];

var app = require('express')();
var express = require('express');
var http = require('http');
var www = require('http').Server(app);
var local = require('http').Server(app);

/* 1.0 -- 0.9 */
//var io = require('socket.io')(http);
var io = require('socket.io').listen(www);
var django = require('socket.io').listen(local, {log: false});
/**************/

var proxy = require('express-http-proxy');

app.use('/', proxy('127.0.0.1:' + django_port, {
  forwardPath: function(req, res) {
    return require('url').parse(req.url).path;
  }
}));

app.use(express.static(__dirname + '/www', {maxAge: 1}));

django.on('connection', function(socket){
    console.log('django connected');

    socket.on('callback', function(data){
        var io_socket = io.sockets.connected[data.socket_id];
        io_socket.emit(data.callback, data.payload);
    });

    socket.on('python_exception', function(data){
        var io_socket = io.sockets.connected[data.socket_id];
        delete data.socket_id;
        io_socket.emit('python_exception', data);
    });
});

io.on('connection', function(socket){
    console.log('client connected');

    socket.on('broadcast', function(data){
        io.sockets.emit(data.event, data);
    });

    socket.on('django', function(data){
        data.socket_id = socket.id;
        django.sockets.emit('django', data);
    });

});

www.listen(public_port, function(){
    console.log('listening for clients on *:' + public_port);
});

local.listen(socket_port, function(){
    console.log('listening to Django on *:' + socket_port);
});