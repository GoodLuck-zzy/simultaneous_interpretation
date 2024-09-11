<template>
  <div id="app">
    <button @click="fetchMessage">点击获取后端消息</button>
    <p v-if="message">消息：{{ message }}</p>
  </div>
</template>

<script>
import { ref } from 'vue';

export default {
  setup() {
    const message = ref('');

    async function fetchMessage() {
      try {
        const response = await fetch('http://192.168.33.71:15000/demo/tranlate_model');
        const data = await response.json();
        message.value = data.models[0];
      } catch (error) {
        console.error("There was an error fetching the message:", error);
      }
    }

    return { message, fetchMessage };
  },
};
</script>

<style>
#app {
  text-align: center;
  margin-top: 5rem;
}
</style>
