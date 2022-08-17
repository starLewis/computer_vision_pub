// var fs = require("fs");

// var data = '';

// //build file stream
// var readerStream = fs.createReadStream('input.txt');

// //encode utf8
// readerStream.setEncoding('UTF8');

// //handler stream
// readerStream.on('data', function(chunk){
//     data += chunk;
// });

// readerStream.on('end', function(){
//     console.log(data);
// });

// readerStream.on('error', function(err){
//     console.log(err.stack);
// });

// console.log("程序执行完毕.");

// var fs = require("fs");
// var data = '菜鸟教程官网地址: www.runoob.com';

// //
// var writerStream = fs.createWriteStream('output.txt');

// //
// writerStream.write(data, 'UTF8');

// //
// writerStream.end();

// //
// writerStream.on('finish', function(){
//     console.log('写入完成.');
// });

// writerStream.on('error', function(err){
//     console.log(err.stack);
// });

// console.log("程序执行完毕.");


// var fs = require("fs");

// //build a read stream
// var readerStream = fs.createReadStream('input.txt');

// //build a write stream
// var writerStream = fs.createWriteStream('output.txt');

// //
// readerStream.pipe(writerStream);

// console.log("程序执行完毕.");


//compress
var fs = require("fs");
var zlib = require("zlib");

//
fs.createReadStream('input.txt')
    .pipe(zlib.createGzip())
    .pipe(fs.createWriteStream('input.txt.gz'));

console.log("文件压缩完成.");