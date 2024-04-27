
$(document).ready(function() {
    // Function to send message using AJAX
    $('#messageForm').submit(function(event) {
        event.preventDefault();
        var message = $('#message').val();
        $.ajax({
            type: 'POST',
            url: '/send_message',
            contentType: 'application/json',
            data: JSON.stringify({'message': message}),
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    // Function to receive and display messages using Websockets
    var socket = new WebSocket('ws://' + window.location.host + '/ws');
    socket.onopen = function() {
        console.log('Websocket connection established.');
    };
    socket.onmessage = function(event) {
        var message = JSON.parse(event.data);
        $('#messages').append('<p>' + message.content + '</p>');
    };
});









