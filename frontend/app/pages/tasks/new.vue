<script setup lang="ts">
import type { Animal, Flock, HusbandryTask, Paginated } from '~/types/api'

const route = useRoute()
const { request, selectedFarmId } = useApi()
const animals = ref<Animal[]>([])
const flocks = ref<Flock[]>([])
const submitting = ref(false)
const errorMessage = ref('')
const form = reactive({
  animal: (route.query.animal as string) || '', flock: '', task_type: 'health_check', title: '', due_date: '', recurrence_days: '', notes: '',
})

onMounted(async () => {
  if (!selectedFarmId.value) return
  const [animalResponse, flockResponse] = await Promise.all([
    request<Paginated<Animal>>('/animals/?status=active'),
    request<Paginated<Flock>>('/animals/flocks/'),
  ])
  animals.value = animalResponse.results
  flocks.value = flockResponse.results
})

async function submit() {
  submitting.value = true
  errorMessage.value = ''
  try {
    await request<HusbandryTask>('/husbandry/tasks/', {
      method: 'POST',
      body: {
        ...form,
        animal: form.animal || null,
        flock: form.flock || null,
        recurrence_days: form.recurrence_days ? Number(form.recurrence_days) : null,
      },
    })
    await navigateTo(form.animal ? `/animals/${form.animal}` : '/tasks')
  } catch {
    errorMessage.value = 'The task could not be scheduled.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="form-card wide">
    <p class="eyebrow">Husbandry</p><h1>Schedule a task</h1>
    <form class="form-grid" @submit.prevent="submit">
      <label>Task type <select v-model="form.task_type"><option value="vaccination">Vaccination</option><option value="parasite">Parasite assessment or deworming</option><option value="shearing">Shearing</option><option value="hoof_care">Hoof care</option><option value="weighing">Weighing</option><option value="health_check">Health check</option><option value="breeding">Breeding</option><option value="other">Other</option></select></label>
      <label>Due date <input v-model="form.due_date" type="date" required></label>
      <label class="full">Title <input v-model="form.title" maxlength="200" required></label>
      <label>Animal <select v-model="form.animal"><option value="">No individual animal</option><option v-for="animal in animals" :key="animal.id" :value="animal.id">{{ animal.ear_tag }} {{ animal.name }}</option></select></label>
      <label>Flock <select v-model="form.flock"><option value="">No flock</option><option v-for="flock in flocks" :key="flock.id" :value="flock.id">{{ flock.name }}</option></select></label>
      <label>Repeat every number of days <input v-model="form.recurrence_days" type="number" min="1" inputmode="numeric"></label>
      <label class="full">Notes <textarea v-model="form.notes" rows="4" /></label>
      <p v-if="errorMessage" class="error full" role="alert">{{ errorMessage }}</p>
      <div class="actions full"><button type="submit" :disabled="submitting">{{ submitting ? 'Scheduling…' : 'Schedule task' }}</button></div>
    </form>
  </section>
</template>
