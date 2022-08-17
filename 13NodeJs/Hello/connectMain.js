var events = require('events');
var eventEmitter = new events.EventEmitter();

// listen #1
var listener1 = function listener1(){
    console.log('listen listener1 run.');
}

// listen #2
var listener2 = function listener2(){
    console.log('listen listener2 run.');
}

// bind connection event, handler function: listener1
eventEmitter.addListener('connection', listener1);

// bind connection event, handler function: listener2
eventEmitter.on('connection', listener2);

var eventListeners = eventEmitter.listenerCount('connection');
console.log(eventListeners + "个监听器监听连接事件。");

 // handler connection event
 eventEmitter.emit('connection');

 // remove listener1 function
 eventEmitter.removeListener('connection', listener1);
 console.log("listener1 不再受监听。");

 // emit connection event
 eventEmitter.emit('connection');

 eventListeners = eventEmitter.listenerCount('connection');
 console.log(eventListeners + "个监听器监听连接事件。");

 console.log("程序执行完毕。");