<script setup lang="ts">
import { Activity, FilePenLine, Plus, Trash2 } from '@lucide/vue'
import type { AuditEvent, Paginated } from '~/types/api'

const { request, selectedFarmId } = useApi()
const events = ref<AuditEvent[]>([])
const loading = ref(true)
const errorMessage = ref('')
const filters = reactive({ action: '', resource_type: '', date_from: '', date_to: '' })
const resourceTypes = computed(() => [...new Set(events.value.map(item => item.resource_type))].sort())

function queryString() {
  const query = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => { if (value) query.set(key, value) })
  return query.toString() ? `?${query}` : ''
}

function iconFor(action: AuditEvent['action']) {
  return action === 'created' ? Plus : action === 'deleted' ? Trash2 : FilePenLine
}

function changeSummary(event: AuditEvent) {
  const fields = Object.keys(event.changes).filter(field => !field.endsWith('_by') && field !== 'recorded_by')
  if (event.action === 'updated') return fields.length ? `Changed ${fields.slice(0, 3).join(', ')}${fields.length > 3 ? ` and ${fields.length - 3} more` : ''}` : 'Record updated'
  return event.action === 'created' ? 'New record added' : 'Record removed'
}

async function loadEvents() {
  if (!selectedFarmId.value) { loading.value = false; return }
  loading.value = true; errorMessage.value = ''
  try { events.value = (await request<Paginated<AuditEvent>>(`/audit/${queryString()}`)).results }
  catch { errorMessage.value = 'Activity history could not be loaded.' }
  finally { loading.value = false }
}

onMounted(loadEvents)
watch(selectedFarmId, loadEvents)
</script>

<template>
  <section>
    <div class="page-heading"><div><p class="eyebrow">Accountability</p><h1>Farm activity</h1><p>Review changes to livestock, care, breeding, nutrition, and medicine records.</p></div></div>
    <Card class="mb-6"><CardHeader><CardTitle>Filter activity</CardTitle><CardDescription>Only owners and managers can view this immutable history.</CardDescription></CardHeader><CardContent><form class="grid gap-4 sm:grid-cols-2 lg:grid-cols-5" @submit.prevent="loadEvents"><label>Action <select v-model="filters.action"><option value="">All actions</option><option value="created">Created</option><option value="updated">Updated</option><option value="deleted">Deleted</option></select></label><label>Record type <select v-model="filters.resource_type"><option value="">All record types</option><option v-for="type in resourceTypes" :key="type" :value="type">{{ type }}</option></select></label><label>From <input v-model="filters.date_from" type="date"></label><label>To <input v-model="filters.date_to" type="date"></label><div class="flex items-end"><Button type="submit">Apply filters</Button></div></form></CardContent></Card>
    <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>
    <div v-if="loading" class="grid gap-3"><Skeleton v-for="item in 5" :key="item" class="h-20" /></div>
    <Card v-else><CardHeader><CardTitle class="flex items-center gap-2"><Activity class="size-5" /> Recent changes</CardTitle><CardDescription>Showing the latest {{ events.length }} events.</CardDescription></CardHeader><CardContent><div v-for="event in events" :key="event.id" class="flex gap-4 border-b py-4 last:border-0"><span class="grid size-9 shrink-0 place-items-center rounded-full bg-secondary text-primary"><component :is="iconFor(event.action)" class="size-4" /></span><div class="min-w-0 flex-1"><div class="flex flex-wrap items-center gap-2"><strong>{{ event.actor_name }}</strong><span class="text-muted-foreground">{{ event.action }}</span><Badge variant="outline">{{ event.resource_type }}</Badge></div><p class="mt-1 truncate font-medium">{{ event.resource_name }}</p><small class="text-muted-foreground">{{ changeSummary(event) }} · {{ new Date(event.created_at).toLocaleString() }}</small></div></div><p v-if="!events.length" class="empty-row">No activity matches these filters.</p></CardContent></Card>
  </section>
</template>
