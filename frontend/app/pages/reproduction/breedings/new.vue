<script setup lang="ts">
import type { Animal, BreedingRecord, Paginated } from '~/types/api'

const { request } = useApi()
const dams = ref<Animal[]>([])
const availableSires = ref<Animal[]>([])
const loading = ref(true)
const submitting = ref(false)
const errorMessage = ref('')
const form = reactive({ dam: '', sire: '', breeding_date: new Date().toISOString().slice(0, 10), expected_birth_date: '', method: 'natural', notes: '' })
const selectedDam = computed(() => dams.value.find(animal => animal.id === form.dam))
const sires = computed(() => availableSires.value.filter(item => !selectedDam.value || item.species === selectedDam.value.species))

onMounted(async () => {
  try {
    const [damResponse, sireResponse] = await Promise.all([
      request<Paginated<Animal>>('/animals/?status=active&sex=female'),
      request<Paginated<Animal>>('/animals/?status=active&sex=male'),
    ])
    dams.value = damResponse.results
    availableSires.value = sireResponse.results
  } catch { errorMessage.value = 'Eligible animals could not be loaded.' }
  finally { loading.value = false }
})

async function submit() {
  submitting.value = true; errorMessage.value = ''
  try {
    await request<BreedingRecord>('/reproduction/breedings/', { method: 'POST', body: { ...form, sire: form.sire || null, expected_birth_date: form.expected_birth_date || undefined } })
    await navigateTo('/reproduction')
  } catch { errorMessage.value = 'The breeding record could not be saved. Check animal sex, species, and dates.' }
  finally { submitting.value = false }
}
</script>

<template><section class="form-card wide"><p class="eyebrow">Reproduction</p><h1>Record breeding</h1><p>Record a service for an active female animal. The sire is optional.</p><div v-if="!loading && !dams.length" class="mt-7 rounded-xl border border-amber-200 bg-amber-50 p-5 text-amber-950"><strong class="block">No eligible dam in this farm</strong><p class="mt-1 text-sm">Add an active female animal or update an existing animal whose sex is currently unknown.</p><Button as-child class="mt-4"><NuxtLink to="/animals/new">Register female animal</NuxtLink></Button></div><form class="form-grid" @submit.prevent="submit"><label>Dam <select v-model="form.dam" required :disabled="loading || !dams.length"><option value="" disabled>{{ loading ? 'Loading female animals…' : 'Select female' }}</option><option v-for="animal in dams" :key="animal.id" :value="animal.id">{{ animal.ear_tag }} · {{ animal.name || animal.species }}</option></select><small>Only active animals recorded as female are shown.</small></label><label>Sire <select v-model="form.sire" :disabled="loading"><option value="">Unknown or not recorded</option><option v-for="animal in sires" :key="animal.id" :value="animal.id">{{ animal.ear_tag }} · {{ animal.name || animal.species }}</option></select><small>Only active males of the same species are shown.</small></label><label>Breeding date <input v-model="form.breeding_date" type="date" required></label><label>Expected birth date <input v-model="form.expected_birth_date" type="date"><small>Leave blank to calculate automatically.</small></label><label>Method <select v-model="form.method"><option value="natural">Natural service</option><option value="artificial">Artificial insemination</option><option value="unknown">Unknown</option></select></label><label class="full">Notes <textarea v-model="form.notes" rows="4" /></label><p v-if="errorMessage" class="error full">{{ errorMessage }}</p><div class="actions full"><NuxtLink to="/reproduction">Cancel</NuxtLink><button :disabled="submitting || loading || !dams.length || !form.dam">{{ submitting ? 'Saving…' : 'Save breeding record' }}</button></div></form></section></template>
