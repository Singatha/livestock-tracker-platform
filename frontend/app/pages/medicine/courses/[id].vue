<script setup lang="ts">
import type { DoseAdministration, MedicineBatch, Paginated, TreatmentCourse } from '~/types/api'

const route = useRoute(); const courseId = route.params.id as string; const { request } = useApi()
const course = ref<TreatmentCourse | null>(null); const batches = ref<MedicineBatch[]>([]); const doses = ref<DoseAdministration[]>([])
const submitting = ref(false); const errorMessage = ref(''); const successMessage = ref('')
const form = reactive({ batch: '', administered_at: new Date().toISOString().slice(0, 16), quantity_used: '', notes: '' })
async function load() {
  course.value = await request<TreatmentCourse>(`/medicine/courses/${courseId}/`)
  const [batchResponse, doseResponse] = await Promise.all([request<Paginated<MedicineBatch>>(`/medicine/batches/?product=${course.value.product}`), request<Paginated<DoseAdministration>>(`/medicine/administrations/?course=${courseId}`)])
  batches.value = batchResponse.results.filter(item => !item.is_expired && Number(item.quantity_on_hand) > 0); doses.value = doseResponse.results
}
onMounted(async () => { try { await load() } catch { errorMessage.value = 'The treatment course could not be loaded.' } })
async function administer() {
  submitting.value = true; errorMessage.value = ''; successMessage.value = ''
  try { await request<DoseAdministration>('/medicine/administrations/', { method: 'POST', body: { ...form, course: courseId } }); form.quantity_used = ''; form.notes = ''; await load(); successMessage.value = 'Dose administered and inventory updated.' }
  catch { errorMessage.value = 'The dose could not be recorded. Check the batch, expiry, and stock quantity.' }
  finally { submitting.value = false }
}
</script>

<template><section v-if="course"><div class="page-heading"><div><p class="eyebrow">Treatment course</p><h1>{{ course.animal_ear_tag }} · {{ course.product_name }}</h1><p>{{ course.reason }} · {{ course.dosage }} {{ course.route }}</p></div><NuxtLink class="secondary-link" to="/medicine">Back to medicine</NuxtLink></div><div class="detail-grid"><article><span>Status</span><strong>{{ course.status }}</strong></article><article><span>Doses</span><strong>{{ course.doses_administered }} / {{ course.planned_doses }}</strong></article><article><span>Meat withdrawal ends</span><strong>{{ course.meat_withdrawal_end_date || 'None' }}</strong></article><article><span>Milk withdrawal ends</span><strong>{{ course.milk_withdrawal_end_date || 'None' }}</strong></article></div><div class="mt-6 grid gap-6 lg:grid-cols-2"><form class="form-card" @submit.prevent="administer"><p class="eyebrow">Stock transaction</p><h2>Administer dose</h2><label>Batch <select v-model="form.batch" required :disabled="course.status !== 'active'"><option value="">Select unexpired batch</option><option v-for="item in batches" :key="item.id" :value="item.id">{{ item.batch_number }} · {{ item.quantity_on_hand }} {{ item.stock_unit }}</option></select></label><label>Administered at <input v-model="form.administered_at" type="datetime-local" required></label><label>Inventory quantity used <input v-model="form.quantity_used" type="number" min="0.01" step="0.01" required></label><label>Notes <textarea v-model="form.notes" rows="3" /></label><p v-if="successMessage" class="success">{{ successMessage }}</p><p v-if="errorMessage" class="error">{{ errorMessage }}</p><button v-if="course.status === 'active'" :disabled="submitting">{{ submitting ? 'Recording…' : 'Administer dose' }}</button><p v-else>This course no longer accepts doses.</p></form><Card><CardHeader><CardTitle>Administration history</CardTitle></CardHeader><CardContent><div v-for="item in doses" :key="item.id" class="border-b py-3"><strong class="block">{{ new Date(item.administered_at).toLocaleString() }}</strong><small>Batch {{ item.batch_number }} · {{ item.quantity_used }} used</small><p v-if="item.notes">{{ item.notes }}</p></div><p v-if="!doses.length" class="empty-row">No doses administered yet.</p></CardContent></Card></div></section><p v-else-if="errorMessage" class="error">{{ errorMessage }}</p></template>
