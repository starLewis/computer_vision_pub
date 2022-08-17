// yinru events module
var events = require('events');

// build eventEmitter object
var eventEmitter = new events.EventEmitter();

// build event handler
var connectHandler = function connected(){
    console.log('连接成功.');

    //data_received event
    eventEmitter.emit('data_received');
}

// band connection event handler procedure
eventEmitter.on('connection',connectHandler);

eventEmitter.on('data_received', function(){
    console.log('数据接收成功.');
});

// connection event
eventEmitter.emit('connection');

console.log("程序执行完毕.");