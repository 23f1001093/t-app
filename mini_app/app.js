let ws, mediaRecorder, stream;

const startBtn = document.getElementById("startCallBtn");
const endBtn = document.getElementById("endCallBtn");
const statusBox = document.getElementById("status");

// Initially, only Start enabled
startBtn.disabled = false;
endBtn.disabled = true;

startBtn.onclick = async () => {
    startBtn.disabled = true;
    endBtn.disabled = false;
    ws = new WebSocket("ws://localhost:8080");
    ws.onopen = async () => {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
        mediaRecorder.ondataavailable = (event) => {
            console.log("Chunk type:", typeof event.data, "Instance:", event.data instanceof Blob, "Size:", event.data.size);
            if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
                ws.send(event.data);
                statusBox.textContent = "Sent audio chunk to server...";
            }
        };
        mediaRecorder.start(300); // Start recording, chunk every 300ms
    };
    ws.onmessage = (event) => {
        if (event.data instanceof ArrayBuffer) {
            const audioBlob = new Blob([event.data], { type: "audio/wav" });
            const url = URL.createObjectURL(audioBlob);
            const audio = new Audio(url);
            audio.play();
            statusBox.textContent = "Assistant replied (voice)";
        } else {
            statusBox.textContent = event.data;
        }
        startBtn.disabled = false;
        endBtn.disabled = true;
    };
};

endBtn.onclick = () => {
    endBtn.disabled = true;
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
    }
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send("__END__");
        statusBox.textContent = "Call ended. Processing response...";
    }
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
};