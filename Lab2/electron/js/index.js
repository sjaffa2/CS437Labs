document.onkeydown = updateKey;
document.onkeyup = resetKey;

var server_port = 65432;
var server_addr = "192.168.11.11";

const watchingParameters = {
    battery:"battery", 
    dir: "carDirection", 
    speed: "speedGauge", 
    power: "powerGauge", 
    distance: "distance", 
    temperature: "tempGauge"
};
const allDirs = ["dirForward", "dirBackward", "dirLeft", "dirRight", "dirStop"];

// https://cslab.in/coding-in-sikar-creating-a-cool-battery-charging-animation-with-html-and-css/
function updateBattery(percent) {
    const charge = document.getElementById('batteryCharge');
    const classesToRemove = Array.from(charge.classList).filter(className =>
        className.startsWith('charge-')
    );
    classesToRemove.forEach(className => {
        charge.classList.remove(className);
    });

    if (percent == 0) {
        charge.classList.add('charge-0');
    } else if (percent <= 25) {
        charge.classList.add('charge-25');
    } else if (percent <= 50) {
        charge.classList.add('charge-50');
    } else if (percent <= 75) {
        charge.classList.add('charge-75');
    } else if (percent <= 100) {
        charge.classList.add('charge-100');
    }
}

function updateElement(element, data) {
    if (element == "battery") {
        updateBattery(data);
    } else if (["speed", "power", "temperature"].includes(element)) {
        document.getElementById(watchingParameters[element]).setAttribute("value", data);
    } else if (["dir", "distance"].includes(element)) {
        document.getElementById(watchingParameters[element]).innerHTML = data;
    }
}

function client(input){
    
    const net = require('net');
    if (!(input)) {
        input = document.getElementById("message").value;
    }

    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        // 'connect' listener.
        console.log('connected to server!');

        // send the message
        const message = {
            service: input,
        };
        client.write(JSON.stringify(message) + '\n');
    });
    
    // get the data from the server
    client.on('data', (data) => {
        try {
            const jsonData = JSON.parse(data.toString());
            console.log(`jsonData: ${jsonData}`);
            document.getElementById("returnedData").innerHTML = JSON.stringify(jsonData);
            for (const key in watchingParameters) {
                if (!(key in jsonData)) {
                    continue;
                }
                var newValue = jsonData[key];
                if (!(isNaN(newValue))) {
                    newValue = (newValue < 1) ? 0 : Number(newValue);
                }
                updateElement(key, newValue);
            }
        } catch (err) {
            console.error('Failed to parse JSON:', err);
        }
        client.end();
        client.destroy();
    });

    client.on('end', () => {
        console.log('disconnected from server');
    });

}

// update data for every 50ms
function update_data(){
    client();
}

function update_all(){
    client('all');
}


function updateDirection(dir) {
    allDirs.forEach(el => {
        const element = document.getElementById(el);
        if(dir == element.id) {
            element.classList.remove('btn-light');
            element.classList.add('btn-danger');
        } else {
            element.classList.remove('btn-danger');
            element.classList.add('btn-light');
        }
    });

    client("dir."+dir[3].toLowerCase());
}

// for detecting which key is been pressed w,a,s,d
function updateKey(e) {
    const tag = document.activeElement.tagName.toLowerCase();
    const isEditable = document.activeElement.isContentEditable;

    if (tag === 'input' || tag === 'textarea' || isEditable) {
        return;
    }

    e = e || window.event;

    if (e.keyCode == '87') {
        // up (w)
        updateDirection("dirForward");
    }
    else if (e.keyCode == '83') {
        // down (s)
        updateDirection("dirBackward");
    }
    else if (e.keyCode == '65') {
        // left (a)
        updateDirection("dirLeft");
    }
    else if (e.keyCode == '68') {
        // right (d)
        updateDirection("dirRight");
    }
    else if (e.keyCode == '32') {
        // stop (spacebar)
        updateDirection("dirStop");
    }
}

// reset the key to the start state 
function resetKey(e) {

    e = e || window.event;

    allDirs.forEach(el => {
        const element = document.getElementById(el);
        element.classList.remove('btn-danger');
        element.classList.add('btn-light');
    });
}

function toggle_camera() {
    document.getElementById("livefeed").classList.toggle('hidden');
    document.getElementById("defaultImg").classList.toggle('hidden');
}
