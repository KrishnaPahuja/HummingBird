const micBtn = document.querySelector('#mic');
const playback = document.querySelector('.playback');
const downloadLink = document.createElement('a');

micBtn.addEventListener('click', toggleMic);

let canRecord = false;
let isRecording = false;
let recorder = null;
let chunks = [];

function setupAudio() {
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(setupStream)
      .catch(console.error);
  }
}

setupAudio();

function setupStream(stream) {
  recorder = new MediaRecorder(stream);
  recorder.ondataavailable = e => {
    chunks.push(e.data);
  };

  recorder.onstop = e => {
    const blob = new Blob(chunks, { type: 'audio/ogg; codecs=opus' });
    chunks = [];

    const audioURL = window.URL.createObjectURL(blob);
    playback.src = audioURL;

    const wavBlob = new Blob([blob], { type: 'audio/wav' }); // Convert to WAV

    downloadLink.href = window.URL.createObjectURL(wavBlob);
    downloadLink.download = "recording.wav";
    downloadLink.style.display = "none";
    document.body.appendChild(downloadLink);

    downloadLink.click();
    window.URL.revokeObjectURL(downloadLink.href);
  };

  canRecord = true;
}

function toggleMic() {
  if (!canRecord) return;
  isRecording = !isRecording;

  if (isRecording) {
    recorder.start();
    micBtn.classList.add("is-recording", "glow");
    setTimeout(() => {
      recorder.stop();
      micBtn.classList.remove("is-recording", "glow");
    }, 10000);
  } else {
    recorder.stop();
    micBtn.classList.remove("is-recording", "glow");
  }
}

document.addEventListener("DOMContentLoaded", function() {
  const fileInput = document.getElementById("formFile");
  const audioElement = document.querySelector(".playback");

  document.querySelector(".submit-btn.preview").addEventListener("click", function() {
    const file = fileInput.files[0];

    if (file) {
      const reader = new FileReader();

      reader.onload = function(e) {
        audioElement.src = e.target.result;
        audioElement.play();
        micBtn.classList.add("is-playing");
      };

      reader.readAsDataURL(file);
    }
  });

  audioElement.addEventListener("ended", function() {
    micBtn.classList.remove("is-playing");
  });
});
