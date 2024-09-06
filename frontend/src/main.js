import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

const recordBtn = document.getElementById('recordBtn');
let mediaRecorder;
let audioChunks = [];

navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };
        mediaRecorder.onstop = () => {
            // 这里可以将音频数据发送到服务器
            const audioBlob = new Blob(audioChunks);
            sendAudioToServer(audioBlob);
            audioChunks = [];
        };
    });

recordBtn.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        recordBtn.textContent = 'Start Recording';
    } else {
        mediaRecorder.start();
        recordBtn.textContent = 'Stop Recording';
    }
});

function sendAudioToServer(audioBlob) {
    // 使用WebSocket或其他方式发送到服务器
}
