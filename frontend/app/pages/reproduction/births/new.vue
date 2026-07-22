<script setup lang="ts">
import type { BirthRecord, BreedingRecord, Paginated } from '~/types/api'

const { request } = useApi()
const breedings = ref<BreedingRecord[]>([])
const submitting = ref(false)
const errorMessage = ref('')
const form = reactive({ breeding: '', birth_date: '', total_born: 1, born_alive: 1, stillborn: 0, notes: '' })

onMounted(async () => { breedings.value = (await request<Paginated<BreedingRecord>>('/reproduction/breedings/')).results.filter(item => item.status !== 'completed' && item.status !== 'not_pregnant') })
async function submit() {
  submitting.value = true; errorMessage.value = ''
  try { await request<BirthRecord>('/reproduction/births/', { method: 'POST', body: form }); await navigateTo('/reproduction') }
  catch { errorMessage.value = 'The birth could not be recorded. Alive and stillborn must equal total born.' }
  finally { submitting.value = false }
}
</script>

<template><section class="form-card wide"><p class="eyebrow">Reproduction</p><h1>Record a birth</h1><form class="form-grid" @submit.prevent="submit"><label>Breeding record <select v-model="form.breeding" required><option value="">Select expected birth</option><option v-for="item in breedings" :key="item.id" :value="item.id">{{ item.dam_name }} · expected {{ item.expected_birth_date }}</option></select></label><label>Birth date <input v-model="form.birth_date" type="date" required></label><label>Total born <input v-model.number="form.total_born" type="number" min="1" required></label><label>Born alive <input v-model.number="form.born_alive" type="number" min="0" required></label><label>Stillborn <input v-model.number="form.stillborn" type="number" min="0" required></label><label class="full">Notes <textarea v-model="form.notes" rows="4" /></label><p v-if="errorMessage" class="error full">{{ errorMessage }}</p><div class="actions full"><NuxtLink to="/reproduction">Cancel</NuxtLink><button :disabled="submitting">{{ submitting ? 'Saving…' : 'Record birth' }}</button></div></form></section></template>
