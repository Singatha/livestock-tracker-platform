<script setup lang="ts">
import { WifiOff } from '@lucide/vue'
import { useOnline } from '@vueuse/core'

const online = useOnline()
</script>

<template>
  <Transition name="connection">
    <div v-if="!online" class="fixed inset-x-0 top-0 z-[110] flex items-center justify-center gap-2 bg-amber-600 px-4 py-2 text-center text-sm font-semibold text-white" role="status">
      <WifiOff class="size-4" /> You’re offline. Farm records will be available when your connection returns.
    </div>
  </Transition>
</template>

<style scoped>
.connection-enter-active, .connection-leave-active { transition: transform 180ms ease; }
.connection-enter-from, .connection-leave-to { transform: translateY(-100%); }
</style>
