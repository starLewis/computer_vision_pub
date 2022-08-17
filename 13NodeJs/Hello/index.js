var server = require("./serverMain");
var router = require("./router");

server.start(router.route);