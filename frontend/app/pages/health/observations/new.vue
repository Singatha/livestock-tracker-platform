<script setup lang="ts">
import type { Animal, HealthObservation, Paginated } from '~/types/api'

const route = useRoute()
const { request, selectedFarmId } = useApi()
const animals = ref<Animal[]>([])
const submitting = ref(false)
const errorMessage = ref('')
const form = reactive({
  animal: (route.query.animal as string) || '', category: 'general', severity: 'low', summary: '', notes: '',
})

onMounted(async () => {
  if (!selectedFarmId.value) return
  animals.value = (await request<Paginated<Animal>>('/animals/?status=active')).results
})

async function submit() {
  submitting.value = true
  errorMessage.value = ''
  try {
    await request<HealthObservation>('/health/observations/', { method: 'POST', body: form })
    await navigateTo(`/animals/${form.animal}`)
  } catch {
    errorMessage.value = 'The observation could not be recorded.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="form-card wide">
    <p class="eyebrow">Health record</p><h1>Record an observation</h1>
    <p>Record what was observed. Diagnosis and treatment decisions should be made by a qualified professional.</p>
    <form class="form-grid" @submit.prevent="submit">
      <label class="full">Animal <select v-model="form.animal" required><option value="" disabled>Select animal</option><option v-for="animal in animals" :key="animal.id" :value="animal.id">{{ animal.ear_tag }} {{ animal.name }}</option></select></label>
      <label>Category <select v-model="form.category"><option value="general">General health</option><option value="injury">Injury</option><option value="illness">Illness</option><option value="parasite">Parasite concern</option><option value="reproductive">Reproductive</option><option value="other">Other</option></select></label>
      <label>Severity <select v-model="form.severity"><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="urgent">Urgent</option></select></label>
      <label class="full">Summary <input v-model="form.summary" maxlength="200" required></label>
      <label class="full">Notes <textarea v-model="form.notes" rows="5" /></label>
      <p v-if="errorMessage" class="error full" role="alert">{{ errorMessage }}</p>
      <div class="actions full"><button type="submit" :disabled="submitting">{{ submitting ? 'Saving…' : 'Save observation' }}</button></div>
    </form>
  </section>
</template>
