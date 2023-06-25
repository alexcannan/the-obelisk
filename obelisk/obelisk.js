console.log('hi from obelisk.js')

function playAnswerAnimation(text) {
    const obeliskAnswer = document.getElementById("obelisk-answer");
    const obeliskAudio = document.getElementById("obelisk-audio");

    obeliskAnswer.innerText = text;

    obeliskAnswer.style.opacity = 1;
    obeliskAnswer.style.transform = "scale(1)";
    obeliskAudio.play();

    // Fade out after a delay
    setTimeout(() => {
        obeliskAnswer.style.opacity = 0;
    }, 10000);

    setTimeout(() => {
        obeliskAnswer.style.transform = "scale(0.8)";
    }, 13000);
}

window.addEventListener("DOMContentLoaded", (event) => {
    console.log("DOM fully loaded and parsed");
    var obeliskForm = document.getElementById('obelisk-form');
    var obeliskAnswer = document.getElementById('obelisk-answer');
    obeliskForm.onsubmit = function(event) {
        event.preventDefault();
        var xhr = new XMLHttpRequest();
        var formData = new FormData(obeliskForm);
        xhr.open(obeliskForm.method, obeliskForm.action)
        xhr.setRequestHeader("Content-Type", "application/json");

        obeliskForm.reset();

        xhr.send(JSON.stringify(Object.fromEntries(formData)));

        xhr.onreadystatechange = function() {
            if (xhr.readyState == XMLHttpRequest.DONE) {
                if (xhr.status == 200) {
                    playAnswerAnimation(xhr.responseText);
                }
            }
        }
    }
});
