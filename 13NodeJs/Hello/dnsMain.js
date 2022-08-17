var dns = require('dns');

dns.lookup('www.github.com', function onLookup(err, address, family){
    console.log('ip site: ', address);
    dns.reverse(address, function(err, hostnames){
        if(err){
            console.log(err.stack);
        }

        console.log('反向解析' + address + ":" + JSON.stringify(hostnames));
    });
});