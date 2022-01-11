let socket = new WebSocket('ws://localhost:5000/status');

$(document).ready(function(){
    socket.onmessage = function (event){
        console.log(event.data);
        let data = JSON.parse(event.data)
        if(data['status'] === 'update'){
            for(const update of data['update']){
                if($('#current_user').children()[0] === undefined){
                    if(update['phrases'].length > 0){
                        $('#' + update['user']).css('background-color', 'lightsteelblue')
                        $('#' + update['user']).find('.last_activity').text(update['phrases'].at(-1)[1].toString().substring(0,10))
                    }
                }
                else{
                    let current_user = $('#current_user').find('.user').attr('id')
                    if(current_user === update['user']){
                        if($('#phrases').children()[0].toString().includes('Heading')){
                            $('#phrases').html("<ul></ul>")
                        }
                        for(const phrase of update['phrases']){
                            $(
                                '<li>' +
                                    '<div class="phrase">' +
                                        '<span><b>Timestamp: </b>' + phrase[1] + '</span>' +
                                        '<br>\n' +
                                            '<span><b>Text: </b>' + phrase[0] + '</span>' +
                                    '</div>' +
                                '</li>' +
                                '<hr>'
                            ).appendTo($('#phrases').children()[0])
                        }
                        $('#current_user').find('.user').find('.last_activity').text(update['phrases'].at(-1)[1].toString().substring(0,10))
                    }
                }
            }
        }
        else{
            $('#status').text(JSON.parse(event.data)['status'])
        }
    }
    socket.onerror = function (event){console.log(event)}
    socket.onclose = function (){console.log("ws closed");}
    socket.onopen = function (){console.log('ws opened');}

    $('#show_user').click(show_users)
    $('#app').click(start)
    $('#upload_track').click(select_track)
    $('#track_picker').change(upload_track)
    $('.user').click(show_detail)
});

function show_users(){
    $.ajax({
        url: '/user_list',
        type: 'GET',
        processData: false,
        contentType: false,
        success: function (data) {
            $('#content').html(data)
            $('.user').click(show_detail)
        },
        error: function (data){
            $('#status').text("Ready")
            alert("Error: " + data['responseJSON']['msg']);
        }
    });
}

function show_detail(){
        let id = $(this).attr('id')
        let fname = id.split('_')[0]
        let lname = id.split('_')[1]
        let lastActivity = $(this).find('.last_activity').text()
        $.ajax({
        url: '/details?fname=' + fname + '&lname=' + lname + '&lastActivity=' + lastActivity,
        type: 'GET',
        processData: false,
        contentType: false,
        success: function (data) {
            $('#content').html(data)
        },
        error: function (data){
            $('#status').text("Ready")
            alert("Error: " + data['responseJSON']['msg']);
        }
    });
}

function start(){
    $.ajax({
        url: '/start_recording',
        type: 'GET',
        processData: false,
        contentType: false,
        success: function (data) {
            $('#status').text("Ready")
        },
        error: function (data){
            $('#status').text("Ready")
            alert("Error: " + data['responseJSON']['msg']);
        }
    });
    $('#app').off('click',start)
    $('#app').text('Stop')
    $('#app').click(stop)
}

function stop(){
    $.ajax({
        url: '/stop_recording',
        type: 'GET',
        processData: false,
        contentType: false,
        success: function (data) {
        },
        error: function (data){
            $('#status').text("Ready")
            alert("Error: " + data['responseJSON']['msg']);
        }
    });

    $('#app').off('click',stop)
    $('#app').text('Start')
    $('#app').click(start)
}

function select_track(){
    $('#track_picker').click();
}

function upload_track(){
    let formData = new FormData();
    let track = $("#track_picker")[0].files[0]
    formData.append(track.name, track)

    $.ajax({
        url: 'upload_track',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function (data) {
             $('#status').text("Ready")
        },
        error: function (data){
            $('#status').text("Ready")
            alert("Error: " + data['responseJSON']['msg']);
        }
    });
    $('#status').text("Uploading files")
}