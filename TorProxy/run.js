var TorControl = require('tor-control');
var spawn = require('child_process').spawn;

var config = {
    "start": function () {
        console.log("Start Tor Connection");
        var tor = spawn('tor.exe', ["-f", "torrc"]);
        tor.on('exit', (code) => {
            console.log(`Tor exited with code ${code}`)
        });
        tor.stdout.on('data', (data) => {
            if (data.toString().indexOf("100%:") !== -1) {
                console.log("Tor is connected successfully!");
            }
        });
        tor.stderr.on('data', (data) => {
            console.log(data.toString())
        });
    },
    "close": function () {
        console.log("Tor Shutdown");
        var control = new TorControl();
        control.signalHalt(function (error, status) {
            if (error) return console.log("> error: ", error);
            else console.log("> status: ", status.messages[0]);
        });
    },
    "restart": function () {
        console.log("Restart tor");
        var control = new TorControl();
        control.signalHalt(function (error, status) {
            if (error) return console.log("> error: ", error);
            else config.start();
        });
    }
};


var net = require("net");


var server = net.createServer(function (socket) {
    socket.on('data', function (data) {
        data = '' + data;
        if (data === 'start') {
            config.start();
            socket.write('tor started');
        }
        if (data === 'restart') {
            config.restart();
            socket.write('tor restarted');
        }
        if (data === 'stop') {
            config.close();
            socket.write('tor stopped');
        }
    });
});

server.listen(9088, function () {
});
config.start();