$(document).ready(function(){
    $('#enroll').click(function(){

        let formData = new FormData();
        let samples = $("#sample_upload")[0].files

        for(let t of samples){
            formData.append(t.name, t)
        }
        formData.append("fname", $('#fname').val());
        formData.append("lname", $('#lname').val());

        $.ajax({
            url: "/enroll",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false
        });
    });

    $('#start_record').click(function () {
        startRecording()
    });

    $('#stop_record').click(function () {
        stopRecording()
    });
});

let recorder;
let audio_stream;

function startRecording() {

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function (stream) {
            audio_stream = stream;
            recorder = new MediaRecorder(stream);

            recorder.ondataavailable = function (e) {
                const blobDataInWebaFormat = e.data; // .weba = webaudio; subset of webm
                //const wavFile = new Blob([blobDataInWebaFormat], { type : 'audio/wav; codecs=ms_pcm' });

                let formData = new FormData();
                formData.append("track", e.data)
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

    console.log("Record stopped")

    /*let formData = new FormData();
    formData.append("track",  audio_stream.getAudioTracks()[0])
    formData.append("fname", "pippo");
    formData.append("lname", "pippo");
    $.ajax({
        url: "/enroll",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false
    });*/
}
