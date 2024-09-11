<template>
  <div>
    <button @click="connectToServer">Connect to Server</button>
    <button @click="disconnectFromServer">Disconnect from Server</button>
    <button @click="startRecording">Start Recording</button>
    <button @click="stopRecording">Stop Recording</button>
    <audio ref="audioPlayer" controls></audio>
  </div>
</template>

<script>
import { io } from "socket.io-client";

export default {
  name: "AudioStreamer",
  data() {
    return {
      mediaRecorder: null,
      socket: null,
      mediaSource: null,
      sourceBuffer: null,
    };
  },
  mounted() {
    this.mediaSource = new MediaSource();
    this.$refs.audioPlayer.src = URL.createObjectURL(this.mediaSource);
    this.mediaSource.addEventListener("sourceopen", () => {
      this.sourceBuffer = this.mediaSource.addSourceBuffer('audio/webm; codecs="opus"');
    });
  },
  methods: {
    connectToServer() {
      if (!this.socket || !this.socket.connected) {
        this.socket = io("http://localhost:5000");
        this.socket.on("audio_stream", (data) => {
            if (this.sourceBuffer && !this.sourceBuffer.updating) {
                this.sourceBuffer.appendBuffer(data);
            }
        });
        console.log("Connected to server.");
      } else {
        console.log("Already connected to server.");
      }
    },
    disconnectFromServer() {
      if (this.socket && this.socket.connected) {
        this.socket.disconnect();
        console.log("Disconnected from server.");
      } else {
        console.log("No active connection to disconnect.");
      }
    },
    async startRecording() {
      if (!this.socket || !this.socket.connected) {
        alert("Please connect to the server first.");
        return;
      }
      console.log("start record.");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);
      this.mediaRecorder.ondataavailable = (e) => {
        this.socket.emit("audio_stream", e.data);
      };
      this.mediaRecorder.start(100); // Start recording with 100ms slices
      console.log("end record.");
    },
    
    stopRecording() {
      if (this.mediaRecorder) {
        this.mediaRecorder.stop();
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
      }
      if (this.mediaSource.readyState === "open") {
        this.mediaSource.endOfStream();  // End the media source stream
      }
    },
  },
};
</script>
