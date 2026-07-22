<script setup lang="ts">
import type { Animal, BreedingRecord, Paginated } from '~/types/api'

const { request } = useApi()
const animals = ref<Animal[]>([])
const submitting = ref(false)
const errorMessage = ref('')
const form = reactive({ dam: '', sire: '', breeding_date: '', expected_birth_date: '', method: 'natural', notes: '' })
const dams = computed(() => animals.value.filter(item => item.sex === 'female' && item.status === 'active'))
const sires = computed(() => animals.value.filter(item => item.sex === 'male' && item.status === 'active' && (!form.dam || item.species === animals.value.find(animal => animal.id === form.dam)?.species)))

onMounted(async () => { animals.value = (await request<Paginated<Animal>>('/animals/?status=active')).results })

async function submit() {
  submitting.value = true; errorMessage.value = ''
  try {
    await request<BreedingRecord>('/reproduction/breedings/', { method: 'POST', body: { ...form, sire: form.sire || null, expected_birth_date: form.expected_birth_date || undefined } })
    await navigateTo('/reproduction')
  } catch { errorMessage.value = 'The breeding record could not be saved. Check animal sex, species, and dates.' }
  finally { submitting.value = false }
}
</script>

<template><section class="form-card wide"><p class="eyebrow">Reproduction</p><h1>Record breeding</h1><form class="form-grid" @submit.prevent="submit"><label>Dam <select v-model="form.dam" required><option value="">Select female</option><option v-for="animal in dams" :key="animal.id" :value="animal.id">{{ animal.ear_tag }} · {{ animal.name || animal.species }}</option></select></label><label>Sire <select v-model="form.sire"><option value="">Unknown or not recorded</option><option v-for="animal in sires" :key="animal.id" :value="animal.id">{{ animal.ear_tag }} · {{ animal.name || animal.species }}</option></select></label><label>Breeding date <input v-model="form.breeding_date" type="date" required></label><label>Expected birth date <input v-model="form.expected_birth_date" type="date"><small>Leave blank to calculate automatically.</small></label><label>Method <select v-model="form.method"><option value="natural">Natural service</option><option value="artificial">Artificial insemination</option><option value="unknown">Unknown</option></select></label><label class="full">Notes <textarea v-model="form.notes" rows="4" /></label><p v-if="errorMessage" class="error full">{{ errorMessage }}</p><div class="actions full"><NuxtLink to="/reproduction">Cancel</NuxtLink><button :disabled="submitting">{{ submitting ? 'Saving…' : 'Save breeding record' }}</button></div></form></section></template>
