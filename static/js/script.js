function startListening() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = false; // Capture a single phrase
    recognition.interimResults = false;

    recognition.onstart = function() {
        document.getElementById('status').innerText = 'Listening...';
        console.log('Microphone is on, start speaking...');
    };

    recognition.onspeechend = function() {
        recognition.stop();
        document.getElementById('status').innerText = 'Processing...';
        console.log('Speech ended, processing...');
    };

    recognition.onresult = function(event) {
        const speechText = event.results[0][0].transcript;
        document.getElementById('status').innerText = 'You said: ' + speechText;
        console.log('Recognized text:', speechText);
        processSpeech(speechText);
    };

    recognition.onerror = function(event) {
        let errorMessage = 'Error occurred in recognition: ' + event.error;
        switch (event.error) {
            case 'network':
                errorMessage = 'Network error: Please check your internet connection.';
                break;
            case 'not-allowed':
                errorMessage = 'Permission error: Please allow microphone access.';
                break;
            case 'service-not-allowed':
                errorMessage = 'Service error: The recognition service is not allowed.';
                break;
            case 'no-speech':
                errorMessage = 'No speech detected: Please try again.';
                break;
            default:
                errorMessage = 'An unknown error occurred: ' + event.error;
        }
        console.error(errorMessage);
        document.getElementById('status').innerText = errorMessage;
    };

    recognition.start();
}

function processSpeech(speechText) {
    const formData = new FormData();
    formData.append('speech_text', speechText);

    fetch('/process', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const tableBody = document.getElementById('treeTable').getElementsByTagName('tbody')[0];
        tableBody.innerHTML = '';
        data.forEach(tree => {
            const row = tableBody.insertRow();
            row.insertCell(0).innerText = tree['Tree Name'];
            row.insertCell(1).innerText = tree['Status'];
            row.insertCell(2).innerText = tree['Color'];
        });
    })
    .catch(error => console.error('Error:', error));
}
