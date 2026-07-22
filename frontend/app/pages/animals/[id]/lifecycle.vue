<script setup lang="ts">
import type { Animal, AnimalLifecycleEvent, AuditEvent, Flock, Paginated } from '~/types/api'

const route = useRoute()
const animalId = route.params.id as string
const { request } = useApi()
const animal = ref<Animal | null>(null)
const flocks = ref<Flock[]>([])
const events = ref<AnimalLifecycleEvent[]>([])
const auditEvents = ref<AuditEvent[]>([])
const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const today = new Date().toISOString().slice(0, 10)
const statusForm = reactive({ status: 'sold' as Animal['status'], effective_date: today, reason: '' })
const transferForm = reactive({ flock: '', effective_date: today, reason: '' })

async function load() {
  const [animalResponse, flockResponse, eventResponse] = await Promise.all([
    request<Animal>(`/animals/${animalId}/`),
    request<Paginated<Flock>>('/animals/flocks/'),
    request<AnimalLifecycleEvent[]>(`/animals/${animalId}/lifecycle-events/`),
  ])
  animal.value = animalResponse
  flocks.value = flockResponse.results
  events.value = eventResponse
  transferForm.flock = animalResponse.flock || ''
  try {
    auditEvents.value = (await request<Paginated<AuditEvent>>(`/audit/?animal=${animalId}`)).results
  } catch {
    auditEvents.value = []
  }
}

onMounted(async () => {
  try { await load() } catch { errorMessage.value = 'Lifecycle details could not be loaded.' }
})

async function changeStatus() {
  submitting.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    await request<Animal>(`/animals/${animalId}/change-status/`, { method: 'POST', body: statusForm })
    statusForm.reason = ''
    await load()
    successMessage.value = 'Animal status updated.'
  } catch {
    errorMessage.value = 'The status could not be changed. Check the transition and your permission.'
  } finally { submitting.value = false }
}

async function transferFlock() {
  submitting.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    await request<Animal>(`/animals/${animalId}/transfer-flock/`, {
      method: 'POST', body: { ...transferForm, flock: transferForm.flock || null },
    })
    transferForm.reason = ''
    await load()
    successMessage.value = 'Flock assignment updated.'
  } catch {
    errorMessage.value = 'The flock could not be changed. Only active animals can be transferred.'
  } finally { submitting.value = false }
}
</script>

<template>
  <section v-if="animal">
    <div class="page-heading">
      <div><p class="eyebrow">Lifecycle management</p><h1>{{ animal.name || animal.ear_tag }}</h1><p>Record status and flock changes with an effective date and audit trail.</p></div>
      <NuxtLink class="secondary-link" :to="`/animals/${animalId}`">Back to animal</NuxtLink>
    </div>
    <p v-if="successMessage" class="success" role="status">{{ successMessage }}</p>
    <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>
    <div class="form-grid">
      <form class="form-card" @submit.prevent="changeStatus">
        <p class="eyebrow">Current status: {{ animal.status }}</p><h2>Change status</h2>
        <div class="mt-6 grid gap-5">
          <label>New status <select v-model="statusForm.status"><option value="active">Active</option><option value="sold">Sold</option><option value="missing">Missing</option><option value="deceased">Deceased</option></select></label>
          <label>Effective date <input v-model="statusForm.effective_date" type="date" required></label>
          <label>Reason <textarea v-model="statusForm.reason" rows="3" maxlength="250" required /></label>
          <button class="justify-self-start" type="submit" :disabled="submitting || statusForm.status === animal.status">Update status</button>
        </div>
      </form>
      <form class="form-card" @submit.prevent="transferFlock">
        <p class="eyebrow">Flock assignment</p><h2>Transfer flock</h2>
        <div class="mt-6 grid gap-5">
          <label>Destination <select v-model="transferForm.flock"><option value="">No flock</option><option v-for="flock in flocks" :key="flock.id" :value="flock.id">{{ flock.name }}</option></select></label>
          <label>Effective date <input v-model="transferForm.effective_date" type="date" required></label>
          <label>Reason <textarea v-model="transferForm.reason" rows="3" maxlength="250" /></label>
          <button class="justify-self-start" type="submit" :disabled="submitting || animal.status !== 'active' || transferForm.flock === (animal.flock || '')">Transfer animal</button>
        </div>
      </form>
    </div>
    <section class="timeline-section">
      <h2>Lifecycle audit trail</h2>
      <ol v-if="events.length" class="timeline">
        <li v-for="event in events" :key="event.id"><div class="timeline-marker" /><div><p class="timeline-meta">{{ event.event_type.replaceAll('_', ' ') }} · {{ new Date(event.effective_date).toLocaleDateString() }}</p><h3 v-if="event.to_status">{{ event.from_status || 'New' }} → {{ event.to_status }}</h3><h3 v-else>{{ event.from_flock_name || 'No flock' }} → {{ event.to_flock_name || 'No flock' }}</h3><p v-if="event.reason">{{ event.reason }}</p><p>Recorded by {{ event.recorded_by_name || 'Farm team member' }}</p></div></li>
      </ol>
      <p v-else class="empty-row">No lifecycle events recorded.</p>
    </section>
    <Card v-if="auditEvents.length" class="mt-6"><CardHeader><CardTitle>Record activity</CardTitle><CardDescription>Changes to this animal and its directly related care records.</CardDescription></CardHeader><CardContent><div v-for="event in auditEvents" :key="event.id" class="flex flex-wrap items-center justify-between gap-2 border-b py-3 last:border-0"><span><strong class="block">{{ event.actor_name }} {{ event.action }} {{ event.resource_type.toLowerCase() }}</strong><small class="text-muted-foreground">{{ event.resource_name }}</small></span><time class="text-xs text-muted-foreground">{{ new Date(event.created_at).toLocaleString() }}</time></div></CardContent></Card>
  </section>
  <p v-else-if="errorMessage" class="error">{{ errorMessage }}</p>
</template>
