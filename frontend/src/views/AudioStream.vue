<template>
  <div>
    <label> <input type="radio" value="client" v-model="role" /> Client </label>
    <label> <input type="radio" value="staff" v-model="role" /> Staff </label>
    <button @click="connectToServer">Connect to Server</button>
    <button @click="disconnectFromServer">Disconnect from Server</button>
    <button @click="startRecording">Start Recording</button>
    <button @click="stopRecording">Stop Recording</button>
    <audio ref="audioPlayer" controls></audio>
  </div>
</template>

<script>
import { io } from 'socket.io-client'

export default {
  name: 'AudioStreamer',
  data() {
    return {
      mediaRecorder: null,
      socket: null,
      mediaSource: null,
      sourceBuffer: null,
      role: null,
      audioChunks: [], // 用于暂存音频数据块
      audioBuffer: new Uint8Array(320), // 预分配320字节的缓冲区
      bufferIndex: 0 // 缓冲区当前索引
    }
  },
  mounted() {
    this.mediaSource = new MediaSource()
    this.$refs.audioPlayer.src = URL.createObjectURL(this.mediaSource)
    this.mediaSource.addEventListener('sourceopen', () => {
      this.sourceBuffer = this.mediaSource.addSourceBuffer('audio/webm; codecs="opus"')
    })
  },
  methods: {
    connectToServer() {
      if (!this.role) {
        alert('Please select a role before connecting.')
        return
      }
      try {
        if (!this.socket || !this.socket.connected) {
          this.socket = io('http://localhost:15000', { query: `role=${this.role}` })
          this.socket.on('connection_response', (data) => {
            if (data.status === 'rejected') {
              console.log('Connection rejected by the server.')
              this.socket.disconnect(true)
            } else if (data.status === 'accepted') {
              console.log(`Connected to server as ${data.role}.`)
            } else if (data.status === 'already_connected') {
              console.log('Already connected to server.')
            }
          })
          this.socket.on('audio_stream_output', (data) => {
            if (this.sourceBuffer && !this.sourceBuffer.updating) {
              this.sourceBuffer.appendBuffer(data)
            }
          })
          console.log('Connection attempt made.')
        }
      } catch (error) {
        console.error('Failed to connect to server:', error)
      }
    },
    disconnectFromServer() {
      if (this.bufferIndex > 0) {
        const remainingData = this.audioBuffer.slice(0, this.bufferIndex);
        this.socket.emit('audio_stream', remainingData);
      }
      try {
        if (this.socket && this.socket.connected) {
          this.socket.disconnect()
          console.log('Disconnected from server.')
          this.initMediaSource() // Reinitialize the media source
        } else {
          console.log('No active connection to disconnect.')
        }
      } finally {
        if (this.mediaRecorder) {
          this.mediaRecorder.stop()
          this.mediaRecorder.stream.getTracks().forEach((track) => track.stop())
          this.mediaRecorder = null
        }
      }
    },
    initMediaSource() {
      if (this.mediaSource && this.mediaSource.readyState === 'open') {
        this.mediaSource.endOfStream()
      }
      this.mediaSource = new MediaSource()
      this.$refs.audioPlayer.src = URL.createObjectURL(this.mediaSource)
      this.mediaSource.addEventListener('sourceopen', () => {
        this.sourceBuffer = this.mediaSource.addSourceBuffer('audio/webm; codecs="opus"')
      })
    },
    async startRecording() {
      if (!this.socket || !this.socket.connected) {
        alert('Please connect to the server first.')
        return
      }
      this.initMediaSource()
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      this.mediaRecorder = new MediaRecorder(stream)
      this.mediaRecorder.ondataavailable = async (e) => {
        const data = new Uint8Array(await e.data.arrayBuffer()) // 将Blob转换为Uint8Array
        for (let i = 0; i < data.length; i++) {
          this.audioBuffer[this.bufferIndex++] = data[i]
          if (this.bufferIndex === 320) {
            // 当达到320字节时发送数据
            console.log("send 320 datas:")
            console.log(this.audioBuffer)
            this.socket.emit('audio_stream', this.audioBuffer)
            this.bufferIndex = 0 // 重置索引
          }
        }
      }
      this.mediaRecorder.start(200) // 可以调整时间片以优化数据收集
    },

    stopRecording() {
      if (this.mediaRecorder) {
        this.mediaRecorder.stop()
        this.mediaRecorder.stream.getTracks().forEach((track) => track.stop())
        this.mediaRecorder = null
      }
      if (this.mediaSource.readyState === 'open') {
        this.mediaSource.endOfStream()
      }
    }
  }
}
</script>
