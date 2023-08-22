// Code for the dashboard
$(document).ready(function () {
    // Socket
    var socket = io.connect();

    // Keep track of version
    _verlock = false;
    var _version = "none";

    // Get all editable elements
    let countdown_elm = document.getElementById("mission_time");
    let subtitle_elm = document.getElementById("subtitle");

    socket.on("updateSensorData", function (msg) {
        console.log("Received sensorData :: " + msg.date + " :: " + msg.version);

        // Check if server is updated
        if (_verlock && _version != msg.version) {
            console.log("AAH! Reload required!");
            window.location.reload();
        } else {
            _version = msg.version;
        }

        // Update updatable elements
        countdown_elm.textContent = msg.date;
        subtitle_elm.textContent = "We're online";
    });

    socket.on("reconnect", (socket) => {
        console.log("Just reconnected!");
        window.location.reload();
    });

    socket.on("disconnect", (reason) => {
        console.log("Disconnected! Reason was " + reason);
        _verlock = true;
    });
});



// function callme() {
//     //This promise will resolve when the network call succeeds
//     //Feel free to make a REST fetch using promises and assign it to networkPromise
//     var networkPromise = fetch('/get_time')
//         .then(response => response.json())
//         .then(data => {
//             console.log(data);
//             document.getElementById("mission_time").innerHTML = data["t"];
//             document.getElementById("subtitle").innerHTML = data["name"];
//         });;


//     //This promise will resolve when 2 seconds have passed
//     var timeOutPromise = new Promise(function (resolve, reject) {
//         // 2 Second delay
//         setTimeout(resolve, 2000, 'Timeout Done');
//     });

//     Promise.all(
//         [networkPromise, timeOutPromise]).then(function (values) {
//             console.log("Atleast 2 secs + TTL (Network/server)");
//             //Repeat
//             callme();
//         });
// }
// callme();