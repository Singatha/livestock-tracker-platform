<script setup lang="ts">
import type { Flock } from '~/types/api'

const name = ref('')
const description = ref('')
const submitting = ref(false)
const errorMessage = ref('')
const { request, selectedFarmId } = useApi()

async function submit() {
  if (!selectedFarmId.value) {
    errorMessage.value = 'Select or create a farm first.'
    return
  }
  submitting.value = true
  errorMessage.value = ''
  try {
    await request<Flock>('/animals/flocks/', {
      method: 'POST',
      body: { name: name.value, description: description.value },
    })
    await navigateTo('/animals/new')
  } catch {
    errorMessage.value = 'The flock could not be created.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="form-card">
    <p class="eyebrow">Organization</p>
    <h1>Create a flock</h1>
    <p>Use flocks to group animals that are managed together.</p>
    <form class="stack" @submit.prevent="submit">
      <label>Flock name <input v-model="name" maxlength="200" required autofocus></label>
      <label>Description <textarea v-model="description" rows="4" /></label>
      <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>
      <button type="submit" :disabled="submitting">{{ submitting ? 'Creating…' : 'Create flock' }}</button>
    </form>
  </section>
</template>
