
$(document).ready(function(){
    $('#upload').click(select_samples);
    $('#sample_picker').change(upload_samples);
    $('#record').click(get_text);
});

function select_samples(){
    $('#sample_picker').click();
}

function upload_samples(){
    let formData = new FormData();
    fname = $('#fname').val();
    lname = $('#lname').val();

    if(fname === '' ||  lname === ''){
        alert("Insert name and surname !")
        return
    }
    formData.append('fname', fname)
    formData.append('lname', lname)

    let samples = $("#sample_picker")[0].files

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
            set_blink(false)
             $('#status').text("Ready")
            addUser($('#fname').val(),$('#lname').val());
            alert("User registered successfully !");
        },
        error: function (data){
            set_blink(false)
            $('#status').text("Ready")
            alert("Error: " + data['responseJSON']['msg']);
        }
    });
    set_blink(true)
    $('#status').text("Uploading files")
}

function get_text(){
    let fname = $('#fname').val();
    let lname = $('#lname').val();


    if(fname === '' ||  lname === ''){
        alert("Insert name and surname !")
        return
    }

    $.ajax({
        url: '/text?fname=' + fname + '&lname=' + lname,
        type: 'GET',
        processData: false,
        contentType: false,
        success: function (data) {
            $('#content').html(
                '<div id="timer"><div id="bar"><span id="countdown">60</span></div></div><div id="button_container"><button id="start_recording">Start</button></div><div id="sample_text">'
                                + data['text'] + '</div>'
            )
            $('#start_recording').click(start_recording);
        },
                error: function (data){
            set_blink(false)
            $('#status').text("Ready")
            alert("Error: " + data['responseJSON']['msg']);
        }
    });
}

function start_recording(){
    let formData = new FormData();
    fname = $('#fname').val()
    lname = $('#lname').val()
    formData.append('fname',fname)
    formData.append('lname',  lname)

    $.ajax({
        url: '/record_samples',
        type: 'POST',
        processData: false,
        contentType: false,
        data: formData,
        success: function (data) {
             show_users()
             set_blink(false)
             $('#status').text("Ready")
             alert("User registered successfully !");
        },
        error: function (data){
            clearInterval(countdown)
            set_blink(false)
            $('#status').text("Ready")
            alert("Error: " + data['responseJSON']['msg']);
        }
    });
    countdown = setInterval(countdown_handler, 1000)
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
        clearInterval(countdown)
    }
}

function addUser(fname, lname){
    let content = $('#content')
    let id = fname.charAt(0).toUpperCase() + fname.slice(1)+  '_' + lname.charAt(0).toUpperCase() + lname.slice(1)
    content.append(
        '   <div id="'+  id + '" class="user">' +
        '       <img class="user_icon" src="../static/images/man_icon.png" alt="user"/>' +
        '       <ul class="user_info">' +
        '           <li><span><b>Name: </b><i>' + fname.charAt(0).toUpperCase() + fname.slice(1) + '</i></span></li>' +
        '           <li><span><b>Surname: </b><i>' + lname.charAt(0).toUpperCase() + lname.slice(1) + '</i></span></li>' +
        '           <li><span><b>Last activity: </b><i class="last_activity">None</i></span></li>' +
        '       </ul>' +
        '   </div>'
    )
    $('#' + id).click(show_detail)
}