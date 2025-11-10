const WS_SERVER_URL = "ws://localhost:8080";
let ws, mediaRecorder, stream;
const statusBox = document.getElementById("status");
const startBtn = document.getElementById("startCallBtn");
const endBtn = document.getElementById("endCallBtn");

startBtn.onclick = async () => {
  startBtn.disabled = true;
  endBtn.disabled = false;
  statusBox.textContent = "Connecting…";

  ws = new WebSocket(WS_SERVER_URL);
  ws.binaryType = "arraybuffer";
  ws.onopen = async () => {
    statusBox.textContent = "Connected. Speak!";
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (e) => { if (ws.readyState === ws.OPEN) ws.send(e.data); };
    mediaRecorder.start(250);
  };

  ws.onmessage = (event) => {
    // If server sends back audio, play it!
    if (event.data instanceof ArrayBuffer) {
      const audioBlob = new Blob([event.data], { type: "audio/wav" });
      const url = URL.createObjectURL(audioBlob);
      const audio = new Audio(url);
      audio.play();
      statusBox.textContent = "Assistant replied (voice)";
    } else {
      statusBox.textContent = event.data;
    }
  };

  ws.onerror = (e) => statusBox.textContent = "Error: " + e.message;
  ws.onclose = () => statusBox.textContent = "Disconnected.";
};

endBtn.onclick = () => {
  startBtn.disabled = false;
  endBtn.disabled = true;
  if (mediaRecorder && mediaRecorder.state !== "inactive") mediaRecorder.stop();
  if (stream) stream.getTracks().forEach(t => t.stop());
  if (ws) { ws.send("__END__"); ws.close(); }
  statusBox.textContent = "Call ended.";
};