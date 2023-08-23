// Code for the dashboard

// Creates a html table https://stackoverflow.com/questions/15164655/generate-html-table-from-2d-javascript-array
function createTable(tableData, name) {
    var table = document.createElement('table');
    var tableBody = document.createElement('tbody');

    // Set ID so we can find it again later using getElementById
    table.id = name;

    tableData.forEach(function (rowData) {
        var row = document.createElement('tr');

        rowData.forEach(function (cellData) {
            var cell = document.createElement('td');
            cell.appendChild(document.createTextNode(cellData));
            row.appendChild(cell);
        });

        tableBody.appendChild(row);
    });

    table.appendChild(tableBody);
    return table;
    // document.body.appendChild(table);
}

$(document).ready(function () {
    // Socket
    var socket = io.connect();

    // Keep track of version
    _verlock = false;
    var _version = "none";

    // Get all editable elements
    let countdown_elm = document.getElementById("mission_time");
    let subtitle_elm = document.getElementById("subtitle");
    let promo_elm = document.getElementById("promoImage");

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
        promoImage.src = msg.promo_path;

        // Update table
        let discord_elm = document.getElementById("discord_table");
        discord_elm.parentNode.replaceChild(createTable(msg.discord, "discord_table"), discord_elm);
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
