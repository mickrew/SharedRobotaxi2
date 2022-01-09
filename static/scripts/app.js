let socket = new WebSocket('ws://localhost:5000/status');

socket.onmessage = function (event){
    console.log(event.data);
     let data = JSON.parse(event.data)
        if(data['status'] === 'update'){
            for(const update of data['update']){
                if($('#current_user').children()[0] === undefined){
                    $('#' + update['user']).css('background-color', 'lightsteelblue')
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
        $('#status').text("Ready")
    }
    else{
        $('#status').text(JSON.parse(event.data)['status'])
    }
}
socket.onerror = function (event){console.log(event)}
socket.onclose = function (){console.log("ws closed")}

$(document).ready(function(){
    $('#show_user').click(show_users)
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

/*let recorder;
let audio_stream;

function startRecording() {

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function (stream) {
            audio_stream = stream;
            recorder = new MediaRecorder(stream);

            recorder.ondataavailable = function (e) {
                const blobDataInWebaFormat = e.data; // .weba = webaudio; subset of webm
                const wavFile = new Blob([blobDataInWebaFormat], { type : 'audio/wav; codecs=ms_pcm' });

                let formData = new FormData();
                formData.append("track", wavFile)
                formData.append("fname", "pippo");
                formData.append("lname", "pippo");
                $.ajax({
                    url: "/enroll",
                    type: "POST",
                    data: formData,
                    processData: false,
                    contentType: false
                });
            };
            console.log("Record started")
            recorder.start();
        });
}

function stopRecording() {
    recorder.stop();
    audio_stream.getAudioTracks()[0].stop();

    console.log("Record stopped");
}
*/

    /*let socket = new WebSocket('ws://localhost:5000/record_samples');

    socket.onerror = function (event){console.log(event)}
    socket.onmessage = function (event){
        let response = JSON.parse(event.data)
        switch (response['action']){
            case 'start':
                console.log(response['action']);
                countdown = setInterval(countdown_handler, 1000)

                break;
            case 'stop':
                 alert("User registered successfully !");
                window.location.href = '/'
                break;
            case 'already enrolled':
                alert('Error: user already enrolled')
        }
    }
    socket.onopen = function (){
        socket.send(JSON.stringify({fname: $('#fname').val(), lname: $('#lname').val(), command:'start'}))
    }
    socket.onclose = function (){console.log("ws closed")}*/