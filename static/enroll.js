
$(document).ready(function(){
    $('#enroll').click(enroll);
    $('#upload').click(upload_sample);
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

function upload_sample(){
    let formData = new FormData();
    formData.append('fname', $('#fname').val())
    formData.append('lname', $('#lname').val())
    let samples = $("#sample_upload")[0].files

    for (let t of samples) {
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

function record_samples(){
    let socket = new WebSocket('ws://localhost:5000/record_samples');
    socket.onerror = function (event){console.log(event)}
    socket.onmessage = function (event){
        let response = JSON.parse(event.data)
        switch (response['action']){
            case 'start':
                console.log(response['action']);
                console.log(response['text'])
                break;
            case 'stop':
                console.log(response['action']);
                break;
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

    navigator.mediaDevices.getUserMedia({ audioCapture: true })
        .then(function (stream) {
            audio_stream = stream;
            recorder = new MediaRecorder(stream);

            recorder.ondataavailable = function (e) {
                const blobDataInWebaFormat = e.data; // .weba = webaudio; subset of webm
                const wavFile = new Blob([blobDataInWebaFormat], { type : 'audioCapture/wav; codecs=ms_pcm' });

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