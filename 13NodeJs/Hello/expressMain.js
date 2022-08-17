// //
// var express = require('express');
// var app = express();

// app.get('/', function(req, res){
//     res.send('Hello Wrold');
// });

// var server = app.listen(8081, function(){
//     var host = server.address().address
//     var port = server.address().port

//     console.log("application instance, visit site: http://%s:%s", host, port);
// });

// //******** */
// var express = require('express');
// var app = express();

// app.get('/', function(req, res){
//     console.log("主页 Get 请求");
//     res.send("Hello GET");
// });

// // Post
// app.post('/', function(req, res){
//     console.log("主页 POST 请求");
//     res.send("Hello Post");
// });

// // del_user
// app.get('/del_user', function(req, res){
//     console.log("/del_user 响应 Delete请求");
//     res.send('删除页面');
// });

// // list_user 页面Get 请求
// app.get('/list_user', function(req, res){
//     console.log("/list_user Get 请求");
//     res.send("用户列表页面");
// });

// // 对页面 abcd, abxcd, ab123cd, 等响应Get请求
// app.get('/ab*cd', function(req, res){
//     console.log("/ab*cd GET 请求");
//     res.send('正则匹配');
// });

// var server = app.listen(8081, function(){
//     var host = server.address().address
//     var port = server.address().port

//     console.log("application instance, visit address: http://%s:%s", host, port);
// });

var express = require('express');
var app = express();

app.use(express.static('public'));
app.get('/', function(req, res){
    res.send("Hello World!");
});

var server = app.listen(8081, function(){
    var host = server.address().address;
    var port = server.address().port;

    console.log("application instance, visit address: http://%s:%s", host, port);
});