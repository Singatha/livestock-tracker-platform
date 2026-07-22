<script setup lang="ts">
import type { BirthRecord, BreedingRecord, Paginated } from '~/types/api'

const { request } = useApi()
const breedings = ref<BreedingRecord[]>([])
const loading = ref(true)
const submitting = ref(false)
const errorMessage = ref('')
const form = reactive({ breeding: '', birth_date: new Date().toISOString().slice(0, 10), total_born: 1, born_alive: 1, stillborn: 0, notes: '' })

onMounted(async () => {
  try { breedings.value = (await request<Paginated<BreedingRecord>>('/reproduction/breedings/?eligible_for_birth=true')).results }
  catch { errorMessage.value = 'Eligible breeding records could not be loaded.' }
  finally { loading.value = false }
})
async function submit() {
  submitting.value = true; errorMessage.value = ''
  try { await request<BirthRecord>('/reproduction/births/', { method: 'POST', body: form }); await navigateTo('/reproduction') }
  catch { errorMessage.value = 'The birth could not be recorded. Alive and stillborn must equal total born.' }
  finally { submitting.value = false }
}
</script>

<template><section class="form-card wide"><p class="eyebrow">Reproduction</p><h1>Record a birth</h1><p>Choose the open breeding record for the dam, then record the lambing or kidding outcome.</p><div v-if="!loading && !breedings.length" class="mt-7 rounded-xl border border-amber-200 bg-amber-50 p-5 text-amber-950"><strong class="block">No breeding is ready for a birth record</strong><p class="mt-1 text-sm">Record a breeding first, or update an existing breeding that was marked not pregnant or completed.</p><Button as-child class="mt-4"><NuxtLink to="/reproduction/breedings/new">Record breeding</NuxtLink></Button></div><form class="form-grid" @submit.prevent="submit"><label>Breeding record <select v-model="form.breeding" required :disabled="loading || !breedings.length"><option value="" disabled>{{ loading ? 'Loading breeding records…' : 'Select expected birth' }}</option><option v-for="item in breedings" :key="item.id" :value="item.id">{{ item.dam_name }} · expected {{ new Date(item.expected_birth_date).toLocaleDateString() }}</option></select><small>Select an exposed or pregnancy-confirmed breeding without a recorded birth.</small></label><label>Birth date <input v-model="form.birth_date" type="date" required></label><label>Total born <input v-model.number="form.total_born" type="number" min="1" required></label><label>Born alive <input v-model.number="form.born_alive" type="number" min="0" required></label><label>Stillborn <input v-model.number="form.stillborn" type="number" min="0" required></label><label class="full">Notes <textarea v-model="form.notes" rows="4" /></label><p v-if="errorMessage" class="error full">{{ errorMessage }}</p><div class="actions full"><NuxtLink to="/reproduction">Cancel</NuxtLink><button :disabled="submitting || loading || !breedings.length || !form.breeding">{{ submitting ? 'Saving…' : 'Record birth' }}</button></div></form></section></template>
