<script setup lang="ts">
import type { Animal, Flock, Paginated } from '~/types/api'

const { request, selectedFarmId } = useApi()
const flocks = ref<Flock[]>([])
const submitting = ref(false)
const errorMessage = ref('')
const form = reactive({
  ear_tag: '', name: '', species: 'sheep', breed: '', sex: 'unknown', flock: '', date_of_birth: '', notes: '',
})

onMounted(async () => {
  if (!selectedFarmId.value) return
  const response = await request<Paginated<Flock>>('/animals/flocks/')
  flocks.value = response.results
})

async function submit() {
  if (!selectedFarmId.value) {
    errorMessage.value = 'Select or create a farm first.'
    return
  }
  submitting.value = true
  errorMessage.value = ''
  try {
    const payload = {
      ...form,
      flock: form.flock || null,
      date_of_birth: form.date_of_birth || null,
    }
    await request<Animal>('/animals/', { method: 'POST', body: payload })
    await navigateTo('/animals')
  } catch {
    errorMessage.value = 'The animal could not be registered. Check the ear tag and fields.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="form-card wide">
    <p class="eyebrow">Animal register</p>
    <h1>Register an animal</h1>
    <form class="form-grid" @submit.prevent="submit">
      <label>Ear tag <input v-model="form.ear_tag" maxlength="100" required autofocus></label>
      <label>Name <input v-model="form.name" maxlength="100"></label>
      <label>Species <select v-model="form.species"><option value="sheep">Sheep</option><option value="goat">Goat</option></select></label>
      <label>Sex <select v-model="form.sex"><option value="female">Female</option><option value="male">Male</option><option value="unknown">Unknown</option></select></label>
      <label>Breed <input v-model="form.breed" maxlength="100"></label>
      <label>Flock <select v-model="form.flock"><option value="">No flock</option><option v-for="flock in flocks" :key="flock.id" :value="flock.id">{{ flock.name }}</option></select></label>
      <label>Date of birth <input v-model="form.date_of_birth" type="date"></label>
      <label class="full">Notes <textarea v-model="form.notes" rows="4" /></label>
      <p v-if="errorMessage" class="error full" role="alert">{{ errorMessage }}</p>
      <div class="actions full"><NuxtLink to="/animals">Cancel</NuxtLink><button type="submit" :disabled="submitting">{{ submitting ? 'Registering…' : 'Register animal' }}</button></div>
    </form>
  </section>
</template>
