<script setup lang="ts">
import type { Animal, Paginated, WeightMeasurement } from '~/types/api'

const route = useRoute()
const { request } = useApi()
const animals = ref<Animal[]>([])
const submitting = ref(false)
const errorMessage = ref('')
const form = reactive({ animal: (route.query.animal as string) || '', measured_on: new Date().toISOString().slice(0, 10), weight_kg: '', body_condition_score: '', notes: '' })

onMounted(async () => { animals.value = (await request<Paginated<Animal>>('/animals/?status=active')).results })
async function submit() {
  submitting.value = true; errorMessage.value = ''
  try {
    await request<WeightMeasurement>('/growth/weights/', { method: 'POST', body: { ...form, body_condition_score: form.body_condition_score || null } })
    await navigateTo(form.animal ? `/animals/${form.animal}` : '/growth')
  } catch { errorMessage.value = 'The weight could not be recorded. Check the value, date, and whether a reading already exists for that day.' }
  finally { submitting.value = false }
}
</script>

<template><section class="form-card wide"><p class="eyebrow">Growth tracking</p><h1>Record weight</h1><form class="form-grid" @submit.prevent="submit"><label>Animal <select v-model="form.animal" required><option value="">Select animal</option><option v-for="animal in animals" :key="animal.id" :value="animal.id">{{ animal.ear_tag }} · {{ animal.name || animal.species }}</option></select></label><label>Measurement date <input v-model="form.measured_on" type="date" required></label><label>Weight (kg) <input v-model="form.weight_kg" type="number" min="0.01" step="0.01" required></label><label>Body condition score <select v-model="form.body_condition_score"><option value="">Not assessed</option><option v-for="score in ['1.0','1.5','2.0','2.5','3.0','3.5','4.0','4.5','5.0']" :key="score" :value="score">{{ score }}</option></select></label><label class="full">Notes <textarea v-model="form.notes" rows="4" /></label><p v-if="errorMessage" class="error full">{{ errorMessage }}</p><div class="actions full"><NuxtLink :to="form.animal ? `/animals/${form.animal}` : '/growth'">Cancel</NuxtLink><button :disabled="submitting">{{ submitting ? 'Saving…' : 'Record weight' }}</button></div></form></section></template>
