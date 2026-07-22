<script setup lang="ts">
import { Bell, CalendarClock, CheckCheck } from '@lucide/vue'
import type { Notification, Paginated } from '~/types/api'

const { request, selectedFarmId } = useApi()
const notifications = ref<Notification[]>([])
const loading = ref(true)
const errorMessage = ref('')

async function loadNotifications() {
  if (!selectedFarmId.value) {
    loading.value = false
    return
  }
  try {
    notifications.value = (await request<Paginated<Notification>>('/notifications/')).results
  } catch {
    errorMessage.value = 'Notifications could not be loaded.'
  } finally {
    loading.value = false
  }
}

async function markRead(notification: Notification) {
  if (!notification.is_read) await request(`/notifications/${notification.id}/mark-read/`, { method: 'POST', body: {} })
  notification.is_read = true
  await navigateTo(notification.link)
}

async function markAllRead() {
  await request('/notifications/mark-all-read/', { method: 'POST', body: {} })
  notifications.value.forEach(notification => { notification.is_read = true })
}

onMounted(loadNotifications)
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">Inbox</p><h1>Notifications</h1><p>Upcoming and overdue work for the selected farm.</p></div>
      <Button v-if="notifications.some(item => !item.is_read)" variant="outline" @click="markAllRead"><CheckCheck /> Mark all read</Button>
    </div>
    <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>
    <div v-if="loading" class="grid gap-3"><Skeleton v-for="item in 4" :key="item" class="h-24 rounded-xl" /></div>
    <div v-else-if="notifications.length" class="grid gap-3">
      <button v-for="notification in notifications" :key="notification.id" type="button" class="flex h-auto w-full items-start gap-4 rounded-xl border bg-card p-4 text-left shadow-sm transition-colors hover:bg-muted/50 sm:p-5" :class="!notification.is_read ? 'border-primary/30' : 'opacity-75'" @click="markRead(notification)">
        <span class="grid size-10 shrink-0 place-items-center rounded-lg" :class="notification.kind === 'task_overdue' ? 'bg-destructive/10 text-destructive' : 'bg-secondary text-primary'"><CalendarClock /></span>
        <span class="min-w-0 flex-1"><span class="flex items-center gap-2"><strong class="font-heading">{{ notification.title }}</strong><span v-if="!notification.is_read" class="size-2 rounded-full bg-primary" aria-label="Unread" /></span><span class="mt-1 block text-sm text-muted-foreground">{{ notification.message }}</span><small class="mt-2 block text-muted-foreground">{{ new Date(notification.created_at).toLocaleString() }}</small></span>
      </button>
    </div>
    <div v-else class="empty-state"><Bell class="mx-auto mb-3 size-9 text-muted-foreground" /><h2>You’re all caught up</h2><p class="text-sm text-muted-foreground">Task reminders will appear here when work is due.</p></div>
  </section>
</template>
