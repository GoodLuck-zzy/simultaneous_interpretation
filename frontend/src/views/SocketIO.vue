<template>
  <div>
    <h2>WebSocket</h2>
    <p>Status: {{ connectionStatus }}</p>
    <button @click="sendMessage">发送消息到服务器</button>
    <p>接收到的消息: {{ receivedMessage }}</p>
  </div>
</template>

<script>
import { io } from "socket.io-client";

export default {
  data() {
    return {
      socket: null,
      connectionStatus: "未连接",
      receivedMessage: "",
    };
  },
  methods: {
    connectToWebSocket() {
      this.socket = io("http://localhost:15000/");
      this.socket.on("connect", () => {
        this.connectionStatus = `已连接 (ID: ${this.socket.id})`;
        this.socket.emit("client", "客户端已连接！");
      });

      this.socket.on("server", (msg) => {
        console.log("收到消息: ", msg);
        this.receivedMessage = msg;
      });

      this.socket.on("disconnect", () => {
        this.connectionStatus = "已断开连接";
      });
    },
    sendMessage() {
      if (this.socket) {
        this.socket.emit("client", "how are you");
      }
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
