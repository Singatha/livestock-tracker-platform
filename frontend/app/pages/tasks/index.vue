<script setup lang="ts">
import type { HusbandryTask, Paginated } from '~/types/api'

const { request, selectedFarmId } = useApi()
const tasks = ref<HusbandryTask[]>([])
const filter = ref('scheduled')
const errorMessage = ref('')

async function loadTasks() {
  if (!selectedFarmId.value) return
  const query = filter.value ? `?status=${filter.value}` : ''
  tasks.value = (await request<Paginated<HusbandryTask>>(`/husbandry/tasks/${query}`)).results
}

async function complete(task: HusbandryTask) {
  errorMessage.value = ''
  try {
    await request(`/husbandry/tasks/${task.id}/complete/`, {
      method: 'POST',
      body: { completion_notes: '' },
    })
    await loadTasks()
  } catch {
    errorMessage.value = 'The task could not be completed.'
  }
}

onMounted(loadTasks)
watch(filter, loadTasks)
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">Husbandry</p><h1>Tasks</h1></div>
      <NuxtLink class="button-link" to="/tasks/new">Schedule task</NuxtLink>
    </div>
    <div class="toolbar">
      <label>Status <select v-model="filter"><option value="scheduled">Scheduled</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option><option value="">All</option></select></label>
    </div>
    <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>
    <div class="task-list">
      <article v-for="task in tasks" :key="task.id" :class="{ overdue: task.status === 'scheduled' && task.due_date < new Date().toISOString().slice(0, 10) }">
        <div><p class="timeline-meta">{{ task.task_type.replace('_', ' ') }} · due {{ new Date(`${task.due_date}T00:00:00`).toLocaleDateString() }}</p><h2>{{ task.title }}</h2><p v-if="task.notes">{{ task.notes }}</p><p v-if="task.recurrence_days">Repeats every {{ task.recurrence_days }} days</p></div>
        <button v-if="task.status === 'scheduled'" type="button" @click="complete(task)">Mark complete</button>
        <span v-else class="status">{{ task.status }}</span>
      </article>
      <p v-if="!tasks.length" class="empty-row">No tasks match this filter.</p>
    </div>
  </section>
</template>
