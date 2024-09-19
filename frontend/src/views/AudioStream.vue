<template>
  <div>
    <label> <input type="radio" value="client" v-model="role" /> Client </label>
    <label> <input type="radio" value="staff" v-model="role" /> Staff </label>
    <button @click="connectToServer">Connect to Server</button>
    <button @click="disconnectFromServer">Disconnect from Server</button>
    <button @click="startRecording">Start Recording</button>
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
      role: null
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
          this.socket = io('http://192.168.33.71:15000', { query: `role=${this.role}` })
          this.socket.on('connection_response', (data) => {
            if (data.status === 'rejected') {
              console.log('Connection rejected by the server.')
              this.socket.disconnect(true)
            } else if (data.status === 'accepted') {
              console.log(`Connected to server as ${data.role}.`)
              console.log(`this.socket: ${this.socket}, this.socket.connected: ${this.socket.connected}`)
            } else if (data.status === 'already_connected') {
              console.log('Already connected to server.')
            }
          })
          this.socket.on('audio_stream_output', (data) => {
            console.log(data)
            if (this.sourceBuffer && !this.sourceBuffer.updating) {
              this.sourceBuffer.appendBuffer(data)
            }
          })
        }
      } catch (error) {
        console.error('Failed to connect to server:', error)
      }
    },
    disconnectFromServer() {
      try {
        if (this.socket && this.socket.connected) {
          this.socket.disconnect(true)
          this.socket.on('disconnection_response', (data) => {
            if (data.status === 'accepted') {
              console.log('execute disconnected.')
            } else if (data.status === 'already_disconnected') {
              console.log('Already disconnected.')
            }
          })
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
      this.mediaRecorder.ondataavailable = (e) => {
        this.socket.emit('audio_stream', e.data)
      }
      this.mediaRecorder.start(200)
    }
  }
}
</script>
