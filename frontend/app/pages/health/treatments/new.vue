<script setup lang="ts">
import type { Animal, Paginated, Treatment } from '~/types/api'

const route = useRoute()
const { request, selectedFarmId } = useApi()
const animals = ref<Animal[]>([])
const submitting = ref(false)
const errorMessage = ref('')
const form = reactive({
  animal: (route.query.animal as string) || '', product: '', dosage: '', route: 'other', reason: '', withdrawal_end_date: '', follow_up_date: '', notes: '',
})
const cancelTo = computed(() => form.animal ? `/animals/${form.animal}` : '/animals')

onMounted(async () => {
  if (!selectedFarmId.value) return
  animals.value = (await request<Paginated<Animal>>('/animals/?status=active')).results
})

async function submit() {
  submitting.value = true
  errorMessage.value = ''
  try {
    await request<Treatment>('/health/treatments/', {
      method: 'POST',
      body: { ...form, withdrawal_end_date: form.withdrawal_end_date || null, follow_up_date: form.follow_up_date || null },
    })
    await navigateTo(`/animals/${form.animal}`)
  } catch {
    errorMessage.value = 'The treatment could not be recorded.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="form-card wide">
    <p class="eyebrow">Treatment history</p><h1>Record administered treatment</h1>
    <p>This form records what was administered; it does not recommend products or doses.</p>
    <form class="form-grid" @submit.prevent="submit">
      <label class="full">Animal <select v-model="form.animal" required><option value="" disabled>Select animal</option><option v-for="animal in animals" :key="animal.id" :value="animal.id">{{ animal.ear_tag }} {{ animal.name }}</option></select></label>
      <label>Product <input v-model="form.product" maxlength="200" required></label>
      <label>Dose as administered <input v-model="form.dosage" maxlength="100"></label>
      <label>Route <select v-model="form.route"><option value="oral">Oral</option><option value="injection">Injection</option><option value="topical">Topical</option><option value="other">Other</option></select></label>
      <label>Reason <input v-model="form.reason" maxlength="200"></label>
      <label>Withdrawal end date <input v-model="form.withdrawal_end_date" type="date"></label>
      <label>Follow-up date <input v-model="form.follow_up_date" type="date"></label>
      <label class="full">Notes <textarea v-model="form.notes" rows="4" /></label>
      <p v-if="errorMessage" class="error full" role="alert">{{ errorMessage }}</p>
      <div class="actions full"><Button as-child variant="ghost"><NuxtLink :to="cancelTo">Cancel</NuxtLink></Button><button type="submit" :disabled="submitting">{{ submitting ? 'Saving…' : 'Save treatment' }}</button></div>
    </form>
  </section>
</template>
