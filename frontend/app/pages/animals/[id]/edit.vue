<script setup lang="ts">
import type { Animal } from '~/types/api'

const route = useRoute()
const animalId = route.params.id as string
const { request } = useApi()
const loading = ref(true)
const submitting = ref(false)
const errorMessage = ref('')
const form = reactive({
  ear_tag: '', name: '', breed: '', sex: 'unknown', date_of_birth: '', needs_attention: false, notes: '',
})

onMounted(async () => {
  try {
    const animal = await request<Animal>(`/animals/${animalId}/`)
    Object.assign(form, {
      ear_tag: animal.ear_tag,
      name: animal.name,
      breed: animal.breed,
      sex: animal.sex,
      date_of_birth: animal.date_of_birth || '',
      needs_attention: animal.needs_attention,
      notes: animal.notes,
    })
  } catch {
    errorMessage.value = 'The animal record could not be loaded.'
  } finally {
    loading.value = false
  }
})

async function submit() {
  submitting.value = true
  errorMessage.value = ''
  try {
    await request<Animal>(`/animals/${animalId}/`, {
      method: 'PATCH',
      body: { ...form, date_of_birth: form.date_of_birth || null },
    })
    await navigateTo(`/animals/${animalId}`)
  } catch {
    errorMessage.value = 'The animal could not be updated. Check the fields and try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="form-card wide">
    <template v-if="!loading">
      <p class="eyebrow">Animal register</p>
      <h1>Edit animal details</h1>
      <p>Use lifecycle management to change status or flock so those changes remain auditable.</p>
      <form class="form-grid" @submit.prevent="submit">
        <label>Ear tag <input v-model="form.ear_tag" maxlength="100" required autofocus></label>
        <label>Name <input v-model="form.name" maxlength="100"></label>
        <label>Sex <select v-model="form.sex"><option value="female">Female</option><option value="male">Male</option><option value="unknown">Unknown</option></select></label>
        <label>Breed <input v-model="form.breed" maxlength="100"></label>
        <label>Date of birth <input v-model="form.date_of_birth" type="date"></label>
        <label><input v-model="form.needs_attention" type="checkbox"> Needs attention</label>
        <label class="full">Notes <textarea v-model="form.notes" rows="4" /></label>
        <p v-if="errorMessage" class="error full" role="alert">{{ errorMessage }}</p>
        <div class="actions full"><NuxtLink :to="`/animals/${animalId}`">Cancel</NuxtLink><button type="submit" :disabled="submitting">{{ submitting ? 'Saving…' : 'Save changes' }}</button></div>
      </form>
    </template>
    <p v-else>Loading animal…</p>
  </section>
</template>
