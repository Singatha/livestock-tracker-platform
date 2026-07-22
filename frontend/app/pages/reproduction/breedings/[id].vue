<script setup lang="ts">
import type { BreedingRecord } from '~/types/api'

const route = useRoute()
const recordId = route.params.id as string
const { request } = useApi()
const record = ref<BreedingRecord | null>(null)
const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const form = reactive({ status: 'exposed', pregnancy_checked_on: '', notes: '' })

onMounted(async () => {
  try {
    record.value = await request<BreedingRecord>(`/reproduction/breedings/${recordId}/`)
    Object.assign(form, { status: record.value.status, pregnancy_checked_on: record.value.pregnancy_checked_on || '', notes: record.value.notes })
  } catch { errorMessage.value = 'The breeding record could not be loaded.' }
})

async function submit() {
  submitting.value = true; errorMessage.value = ''; successMessage.value = ''
  try {
    record.value = await request<BreedingRecord>(`/reproduction/breedings/${recordId}/`, { method: 'PATCH', body: { ...form, pregnancy_checked_on: form.pregnancy_checked_on || null } })
    successMessage.value = 'Pregnancy status updated.'
  } catch { errorMessage.value = 'The status could not be updated. Confirmed and not-pregnant outcomes require a check date.' }
  finally { submitting.value = false }
}
</script>

<template><section v-if="record" class="form-card wide"><p class="eyebrow">Pregnancy tracking</p><h1>{{ record.dam_name }}</h1><p>Expected birth {{ new Date(record.expected_birth_date).toLocaleDateString() }}</p><form class="form-grid" @submit.prevent="submit"><label>Status <select v-model="form.status" :disabled="record.status === 'completed'"><option value="exposed">Exposed</option><option value="confirmed">Pregnancy confirmed</option><option value="not_pregnant">Not pregnant</option><option v-if="record.status === 'completed'" value="completed">Birth recorded</option></select></label><label>Pregnancy check date <input v-model="form.pregnancy_checked_on" type="date" :required="form.status === 'confirmed' || form.status === 'not_pregnant'"></label><label class="full">Notes <textarea v-model="form.notes" rows="4" /></label><p v-if="successMessage" class="success full">{{ successMessage }}</p><p v-if="errorMessage" class="error full">{{ errorMessage }}</p><div class="actions full"><NuxtLink to="/reproduction">Back</NuxtLink><button v-if="record.status !== 'completed'" :disabled="submitting">{{ submitting ? 'Saving…' : 'Update pregnancy status' }}</button></div></form></section><p v-else-if="errorMessage" class="error">{{ errorMessage }}</p></template>
