<script setup lang="ts">
import { CheckCircle2, CircleAlert, Info, X } from '@lucide/vue'

const { messages, dismiss } = useToast()
const icons = { success: CheckCircle2, error: CircleAlert, info: Info }
</script>

<template>
  <div class="fixed bottom-4 right-4 z-[100] grid w-[calc(100%-2rem)] max-w-sm gap-3" aria-live="polite">
    <TransitionGroup name="toast">
      <div v-for="message in messages" :key="message.id" class="flex items-start gap-3 rounded-xl border bg-card p-4 shadow-lg">
        <component :is="icons[message.variant]" class="mt-0.5 size-5 shrink-0" :class="message.variant === 'error' ? 'text-destructive' : 'text-primary'" />
        <div class="min-w-0 flex-1">
          <p class="text-sm font-semibold">{{ message.title }}</p>
          <p v-if="message.description" class="mt-1 text-sm text-muted-foreground">{{ message.description }}</p>
        </div>
        <button class="rounded-md p-1 text-muted-foreground hover:bg-muted hover:text-foreground" type="button" aria-label="Dismiss notification" @click="dismiss(message.id)"><X class="size-4" /></button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: all 180ms ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(0.5rem); }
</style>
