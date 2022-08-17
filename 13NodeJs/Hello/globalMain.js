// console.log(__filename);

// console.log(__dirname);

// var x = 0;

// function printHello(){
//     console.log("Hello, World!");
//     x += 1;
// }

// // block 2s
// var t = setTimeout(printHello, 2000);

// // clear clock
// clearTimeout(t);

// // set interval
// var intervalT = setInterval(printHello, 2000);

// function lookX(){
//     console.log("x: " + x);
//     if (x > 5){
//         clearInterval(intervalT);
//     }
// }

// intervalX = setInterval(lookX, 2000);

// console.log('Hello World');
// console.log("by void %d iovyb");
// console.log('by void %d iovyb', 1991);

// console.trace();

// console.info("程序开始执行: ");
// console.time("获取数据");

// //
// var counter = 10;
// console.log("计数: %d", counter);
// //

// console.timeEnd('获取数据');
// console.info("程序执行完毕.");

// process.on('exit', function(code){
//     //
//     setTimeout(function(){
//         console.log("该代码不会执行.");
//     }, 0);

//     console.log("退出码为: ", code);
// });

// console.log("程序执行结束.");

// //
// process.stdout.write("Hello World!" + "\n");

// //
// process.argv.forEach(function(val, index, array){
//     console.log(index + ": " + val);
// });

// //
// console.log(process.execPath);

// //
// console.log(process.platform);

// console.log("当前目录： " + process.cwd());

// console.log("当前版本: " + process.version);

// console.log(process.memoryUsage());

// var util = require('util');
// function Base(){
//     this.name = 'base';
//     this.base = 1991;
//     this.sayHello = function(){
//         console.log('Hello ' + this.name);
//     };
// }

// Base.prototype.showName = function(){
//     console.log(this.name);
// };
// Base.prototype.sayHello = function(){
//     console.log('Hello '  + this.name);
// }

// function Sub(){
//     this.name = 'sub';
// }

// util.inherits(Sub, Base);
// var objBase = new Base();
// objBase.showName();
// objBase.sayHello();
// console.log(objBase);

// var objSub = new Sub();
// objSub.showName();
// objSub.sayHello();
// console.log(objSub);


// var util = require('util');
// function Person(){
//     this.name = 'byvoid';
//     this.toString = function(){
//         return this.name;
//     };
// }

// var obj = new Person();
// console.log(util.inspect(obj));
// console.log(util.inspect(obj, true));

// var util = require('util');

// a1 = util.isArray([])

// a2 = util.isArray(new Array)

// a3 = util.isArray({})

// console.log(a1, a2, a3);

// var util = require('util');
// b1 = util.isRegExp(/some regexp/);

// b2 = util.isRegExp(new RegExp('another regexp'));

// b3 = util.isRegExp({})

// console.log(b1, b2, b3);

// var util = require('util');

// c1 = util.isDate(new Date());

// c2 = util.isDate(Date());

// c3 = util.isDate({});
// console.log(c1, c2, c3);

var util = require('util');

d1 = util.isError(new Error());

d2 = util.isError(new TypeError());

d3 = util.isError({name: 'Error', message: 'an error occurred'})

console.log(d1, d2, d3);