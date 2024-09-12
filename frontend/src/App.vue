<template>
  <div id="app">
    <AudioStream/>
    <Record/>
  </div>
</template>

<script>
import AudioStream from './views/AudioStream.vue'
import Record from './views/Record.vue'
export default {
  name: 'App',
  components: {
    AudioStream,
    Record
  }
}
</script>