// Code for the dashboard

// Creates a html table https://stackoverflow.com/questions/15164655/generate-html-table-from-2d-javascript-array
function createTableBody(tableData) {
    var tableBody = $("<tbody>");

    tableData.forEach(rowData => {
        var row = $("<tr>");

        rowData.forEach(cellData => {
            row.append($("<td>").text(cellData));
        });

        tableBody.append(row);
    });
    return tableBody;
    // document.body.appendChild(table);
}

$(document).ready(function () {
    // Socket
    var socket = io.connect();

    // Keep track of version
    _verlock = false;
    var _version = "none";

    // Get all editable elements
    // let countdown_elm = document.getElementById("mission_time");
    // let subtitle_elm = document.getElementById("subtitle");
    // let promo_elm = document.getElementById("promoImage");

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
        $("#mission_time").text(msg.date);
        $("#subtitle").text(msg.next_meeting);
        $("#promoImage").attr("src", msg.promo_path);

        // Update table
        // let discord_elm = document.getElementById("discord_table");
        // discord_elm.parentNode.replaceChild(createTable(msg.discord, "discord_table"), discord_elm);
        $("#discord_table > tbody").replaceWith(createTableBody(msg.discord));

        // Scroll table
        $("#discord").scrollTop($('#discord').prop('scrollHeight'));
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
