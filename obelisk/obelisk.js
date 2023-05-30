console.log('hi from obelisk.js')

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

        xhr.send(JSON.stringify(Object.fromEntries(formData)));

        xhr.onreadystatechange = function() {
            if (xhr.readyState == XMLHttpRequest.DONE) {
                obeliskForm.reset(); //reset form after AJAX success or do something else
                obeliskAnswer.innerText = xhr.responseText;
                obeliskAnswer.classList.toggle('hidden');
            }
        }
    }
});
