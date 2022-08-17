// var fs = require("fs");

// //
// fs.readFile('input.txt', function(err, data){
//     if(err){
//         return console.error(err);
//     }
//     console.log("异步读取: " + data.toString());
// });

// // read file sync
// var data = fs.readFileSync('input.txt');
// console.log("同步读取: " + data.toString());

// console.log("程序执行完毕。");

// var fs = require("fs");

// //
// console.log("准备打开文件!");

// fs.open('input.txt', 'r+', function(err, fd){
//     if(err){
//         return console.error(err);
//     }
//     console.log("文件打开成功!");
// });


// var fs = require('fs');

// fs.stat('/home/lewisliu/Clobotics/Codes/CVTestCodes/13NodeJs/Hello/fileMain.js', function(err, stats){
//     console.log(stats.isFile());
// });


// var fs = require("fs");
// console.log("parepare to open a file!");
// fs.stat('input.txt', function(err, stats){
//     if(err){
//         return console.error(err);
//     }

//     console.log(stats);
//     console.log("read file successfully!");

//     console.log("is File ? : " + stats.isFile());
//     console.log("is Directory ?: " + stats.isDirectory());
// });

// var fs = require("fs");

// console.log("prepare to write file!");
// fs.writeFile('input.txt', 'Write file through fs.writeFile', function(err){
//     if(err){
//         return console.error(err);
//     }

//     console.log("write file successfully!");
//     console.log("--------------i am cut of rule ---------");
//     console.log("read the written data!");
//     fs.readFile('input.txt', function(err, data){
//         if(err){
//             return console.error(err);
//         }

//         console.log("异步读取文件数据: " + data.toString());
//     });
// });

// console.log("the actions have finished!");

// var fs = require("fs");
// var buf = new Buffer.alloc(1024);

// console.log("prepare to open the existed file!");
// fs.open('input.txt', 'r+', function(err, fd){
//     if(err){
//         return  console.error(err);
//     }

//     console.log("open file successfully");
//     console.log("prepare to read file: ");
//     fs.read(fd, buf, 0, buf.length, 0, function(err, bytes){
//         if(err){
//             console.log(err);
//         }
//         console.log(bytes + " bytes have been read out!");

//         if(bytes > 0){
//             console.log(buf.slice(0, bytes).toString());
//         }

//         // close file
//         fs.close(fd, function(err){
//             if(err){
//                 console.log(err);
//             }
//             console.log("file closed successfully!");
//         });
//     });
// });

// var fs = require("fs");
// var buf = new Buffer.alloc(1024);

// console.log("prepare to open file!");
// fs.open('input.txt', 'r+', function(err, fd){
//     if(err){
//         return console.error(err);
//     }
//     console.log("file open successfully!");
//     console.log("cut 10 bytes, remove other content.");

//     fs.ftruncate(fd, 10, function(err){
//         if(err){
//             console.log(err);
//         }
//         console.log("cut file succussfully!");
//         console.log("read the same file!");

//         fs.read(fd, buf, 0, buf.length, 0, function(err, bytes){
//             if(err){
//                 console.log(err);
//             }

//             if(bytes > 0){
//                 console.log(buf.slice(0, bytes).toString());
//             }

//             //close file
//             fs.close(fd, function(err){
//                 if(err){
//                     console.log(err);
//                 }
//                 console.log("close file successfully!");
//             });
//         });
//     });
// });

// //** delete file */
// var fs = require("fs");

// console.log("prepare to delete the file!");
// fs.unlink('input.txt.gz', function(err){
//     if(err){
//         return console.error(err);
//     }

//     console.log("delete file successfully!");
// });

// //**create a directory */
// var fs = require("fs");
// console.log("build a directory: /tmp/test/");
// fs.mkdir("/tmp/test/", function(err){
//     if(err){
//         return console.error(err);
//     }
//     console.log("direcotry build sucessfully!");
// });

//** read directory */
// var fs = require("fs");
// console.log("look for /temp directory");
// fs.readdir("/tmp/",function(err, files){
//     if(err){
//         return console.error(err);
//     }

//     files.forEach(function(file){
//         console.log(file);
//     });
// });

var fs = require("fs");
console.log("prepare to delete /tmp/test");
fs.rmdir("/tmp/test", function(err){
    if(err){
        return console.err(err);
    }

    console.log("read /tmp directory");
    fs.readdir("/tmp/", function(err, files){
        if(err){
            return console.error(err);
        }
        files.forEach(function(file){
            console.log(file);
        });
    });
});