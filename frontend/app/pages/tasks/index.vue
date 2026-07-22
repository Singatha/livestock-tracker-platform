<script setup lang="ts">
import { CalendarCheck2, Check, ClockAlert, Plus } from '@lucide/vue'
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
      <div><p class="eyebrow">Husbandry</p><h1>Care tasks</h1><p>Plan vaccinations, shearing, deworming, and routine work.</p></div>
      <Button as-child><NuxtLink to="/tasks/new"><Plus /> Schedule task</NuxtLink></Button>
    </div>
    <div class="toolbar">
      <label>Status <select v-model="filter"><option value="scheduled">Scheduled</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option><option value="">All</option></select></label>
    </div>
    <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>
    <div class="grid gap-3">
      <Card v-for="task in tasks" :key="task.id" :class="task.status === 'scheduled' && task.due_date < new Date().toISOString().slice(0, 10) ? 'border-destructive/30' : ''">
        <CardContent class="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex min-w-0 gap-4"><span class="grid size-10 shrink-0 place-items-center rounded-lg" :class="task.status === 'scheduled' && task.due_date < new Date().toISOString().slice(0, 10) ? 'bg-destructive/10 text-destructive' : 'bg-secondary text-primary'"><ClockAlert v-if="task.status === 'scheduled'" /><Check v-else /></span><div><p class="timeline-meta">{{ task.task_type.replace('_', ' ') }} · due {{ new Date(`${task.due_date}T00:00:00`).toLocaleDateString() }}</p><h2 class="mt-1 font-heading text-lg font-bold">{{ task.title }}</h2><p v-if="task.notes" class="mt-1 text-sm text-muted-foreground">{{ task.notes }}</p><p v-if="task.recurrence_days" class="mt-1 text-xs text-muted-foreground">Repeats every {{ task.recurrence_days }} days</p></div></div>
          <Button v-if="task.status === 'scheduled'" variant="outline" type="button" @click="complete(task)"><Check /> Mark complete</Button><Badge v-else variant="secondary" class="capitalize">{{ task.status }}</Badge>
        </CardContent>
      </Card>
      <div v-if="!tasks.length" class="empty-state"><CalendarCheck2 class="mx-auto mb-3 size-8 text-muted-foreground" /><h2>No tasks match this filter</h2><Button as-child variant="outline"><NuxtLink to="/tasks/new">Schedule a task</NuxtLink></Button></div>
    </div>
  </section>
</template>
