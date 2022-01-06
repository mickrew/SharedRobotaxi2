$(document).ready(function(){
    $('#start_app').click(start)
});

let periodicCheck
/*
function start(){
    $.ajax({
        url: 'start',
        type: 'POST',
        processData: false,
        contentType: false,
        success: function (data) {
            if (data['msg'] === 'started') {
                let button;
                button = $('#start_app');
                button.text('Stop');
                button.off('click')
                button.on('click', stop);
                periodicCheck = setInterval(check, 1000);
            }
        },
        error: function (data){
            alert("Error: " + data['responseJSON'])
        }
    });
}

function stop(){
    $.ajax({
        url: 'stop',
        type: 'POST',
        processData: false,
        contentType: false,
        success: function (data) {
           if(data['msg'] === 'stopped'){
               let button = $('#start_app');
               button.text('Start');
               button.off('click')
               button.on('click', start)
               clearInterval(periodicCheck)
           }
        },
        error: function (data){
            alert("Error: " + data['responseJSON'])
        }
    });
}*/

function check(){
        $.ajax({
        url: 'check',
        type: 'GET',
        processData: false,
        contentType: false,
        success: function (data) {
           let button = $('#start_app');
           if(data['msg'] === 'recording'){
               button.text('Recording ...');
               button.off('click')
           }
           else{
                button.text('Stop');
                button.off('click')
                button.on('click',stop)
           }
        },
        error: function (data){
            alert("Error: " + data['responseJSON'])
        }
    });
}