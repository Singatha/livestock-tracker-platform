<script setup lang="ts">
import type { Farm } from '~/types/api'

const name = ref('')
const submitting = ref(false)
const errorMessage = ref('')
const { request, selectedFarmId } = useApi()

async function submit() {
  submitting.value = true
  errorMessage.value = ''
  try {
    const farm = await request<Farm>('/farms/', {
      method: 'POST',
      body: { name: name.value },
    })
    selectedFarmId.value = farm.id
    await navigateTo('/flocks/new')
  } catch {
    errorMessage.value = 'The farm could not be created.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="form-card">
    <p class="eyebrow">Getting started</p>
    <h1>Create a farm</h1>
    <p>A farm keeps its members, flocks, animals, and records isolated from other farms.</p>
    <form class="stack" @submit.prevent="submit">
      <label>Farm name <input v-model="name" maxlength="200" required autofocus></label>
      <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>
      <button type="submit" :disabled="submitting">{{ submitting ? 'Creating…' : 'Create farm' }}</button>
    </form>
  </section>
</template>
