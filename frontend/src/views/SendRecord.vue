<template>
  <div>
    <h2>WebSocket</h2>
    <p>Status: {{ connectionStatus }}</p>
    <button @click="toggleRecording">{{ recording ? '停止录音' : '开始录音' }}</button>
    <p>正在接收数据...</p>
  </div>
</template>

<script>
import { io } from "socket.io-client";

export default {
  data() {
    return {
      socket: null,
      connectionStatus: "未连接",
      mediaRecorder: null,
      recording: false,
      audioContext: new (window.AudioContext || window.webkitAudioContext)(),
    };
  },
  methods: {
    async connectToWebSocket() {
      this.socket = io("http://localhost:15000/");
      this.socket.binaryType = 'arraybuffer';
      this.socket.on("connect", () => {
        this.connectionStatus = `已连接 (ID: ${this.socket.id})`;
      });

      this.socket.on("server", async (audioBlob) => {
        console.log("收到语音数据");
        let arrayBuffer;
        if (this.audioContext && this.audioContext.decodeAudioData) {
            try {
                if (audioBlob instanceof Blob) {
                    arrayBuffer = await audioBlob.arrayBuffer();
                } else if (audioBlob instanceof ArrayBuffer) {
                    console.log("ArrayBuffer");
                    arrayBuffer = audioBlob;
                }
                const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
                const source = this.audioContext.createBufferSource();
                source.buffer = audioBuffer;
                source.connect(this.audioContext.destination);
                source.start(0); // 立即播放
            } catch (error) {
            console.error('解码音频数据失败', error);
            }
        }
      });

      this.socket.on("disconnect", () => {
        this.connectionStatus = "已断开连接";
      });
    },
    async toggleRecording() {
      if (this.recording) {
        this.stopRecording();
      } else {
        await this.startRecording();
      }
      this.recording = !this.recording;
    },
    async startRecording() {
      if (!navigator.mediaDevices) {
        alert("您的浏览器不支持录音功能。");
        return;
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

      // 当有音频数据可用时，发送这些数据
      this.mediaRecorder.ondataavailable = e => {
        if (e.data.size > 0 && this.socket) {
          this.socket.emit("client", e.data);
        }
      };

      this.mediaRecorder.start(250); // 每250ms发送一次数据
    },
    stopRecording() {
      if (!this.mediaRecorder) {
        return;
      }
      this.mediaRecorder.stop();
    },
  },
  mounted() {
    this.connectToWebSocket();
  },
  beforeUnmount() {
    if (this.socket) {
      this.socket.close();
    }
  },
};
</script>
