
$(document).ready(function(){
    $('#enroll').click(enroll);
    $('#upload').click(select_samples);
    $('#sample_picker').change(upload_samples);
    $('#record').click(record_samples);

});

function enroll() {
    let formData = new FormData();
    formData.append('fname', $('#fname').val())
    formData.append('lname', $('#lname').val())

    $.ajax({
        url: '/enroll',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function (data) {
            alert("Success: " + data['msg'])
        },
        error: function (data){
            alert("Error: " + data['responseJSON']['msg'])
        }
    });
}

function select_samples(){
    $('#sample_picker').click();
}

function upload_samples(){
    let formData = new FormData();
    formData.append('fname', $('#fname').val())
    formData.append('lname', $('#lname').val())
    let samples = $("#sample_picker")[0].files

    for (let t of samples) {
        console.log(t.name)
        formData.append(t.name, t)
    }

    $.ajax({
        url: 'upload_sample',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function (data) {
            alert("Success: " + data['msg'])
        },
        error: function (data){
            alert("Error: " + data['responseJSON']['msg'])
        }
    });

}

let countdown;

function countdown_handler(){
    let count = $('#countdown')
    let bar = $('#bar')
    let current = parseInt(count.text());

    if(current > 0){
        count.text(current-1);
        bar.css('width',(current-1) / 0.75  + '%');
    }
    else{
        clearInterval()
    }
}

function record_samples(){
    let socket = new WebSocket('ws://raspberrypi:5000/record_samples');
    socket.onerror = function (event){console.log(event)}
    socket.onmessage = function (event){
        let response = JSON.parse(event.data)
        switch (response['action']){
            case 'start':
                console.log(response['action']);
                countdown = setInterval(countdown_handler, 1000)
                $('#content').html(
                    '<div id="timer"><div id="bar"><span id="countdown">60</span></div></div><div id="sample_text">'
                                + response['text'] + '</div>'
                )
                break;
            case 'stop':
                alert("Success: users registered !")
                window.location.href = '/'
                break;
            case 'already enrolled':
                alert('Error: user already enrolled')
        }
    }
    socket.onopen = function (){
        socket.send(JSON.stringify({fname: $('#fname').val(), lname: $('#lname').val(), command:'start'}))
    }
    socket.onclose = function (){console.log("ws closed")}
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