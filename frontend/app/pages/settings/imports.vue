<script setup lang="ts">
import { AlertTriangle, CheckCircle2, Download, Upload } from '@lucide/vue'
import type { ImportJob } from '~/types/api'

const { download, request, selectedFarmId } = useApi()
const jobs = ref<ImportJob[]>([]); const preview = ref<ImportJob | null>(null); const file = ref<File | null>(null)
const submitting = ref(false); const errorMessage = ref(''); const successMessage = ref('')
const form = reactive({ kind: 'animals', mode: 'all_or_nothing' })
const kindLabels: Record<string, string> = { flocks: 'Flocks', animals: 'Animals', weights: 'Weights', medicine_batches: 'Medicine batches' }

async function load() { if (!selectedFarmId.value) return; try { jobs.value = await request<ImportJob[]>('/imports/') } catch { errorMessage.value = 'Only farm owners and managers can use bulk imports.' } }
onMounted(load); watch(selectedFarmId, load)
function selectFile(event: Event) { file.value = (event.target as HTMLInputElement).files?.[0] || null; preview.value = null }
async function createPreview() {
  if (!file.value) return
  submitting.value = true; errorMessage.value = ''; successMessage.value = ''
  const body = new FormData(); body.set('kind', form.kind); body.set('mode', form.mode); body.set('file', file.value)
  try { preview.value = await request<ImportJob>('/imports/preview/', { method: 'POST', body }); await load() }
  catch { errorMessage.value = 'The CSV could not be previewed. Confirm the template, encoding, and file size.' }
  finally { submitting.value = false }
}
async function commit() {
  if (!preview.value) return
  submitting.value = true; errorMessage.value = ''; successMessage.value = ''
  try { preview.value = await request<ImportJob>(`/imports/${preview.value.id}/commit/`, { method: 'POST', body: {} }); successMessage.value = `${preview.value.rows_succeeded} rows imported.`; await load() }
  catch { errorMessage.value = 'The import could not be committed. All-or-nothing imports require every row to be valid.' }
  finally { submitting.value = false }
}
</script>

<template><section><div class="page-heading"><div><p class="eyebrow">Farm onboarding</p><h1>Bulk data imports</h1><p>Preview and validate CSV records before changing farm data.</p></div></div><p v-if="successMessage" class="success">{{ successMessage }}</p><p v-if="errorMessage" class="error">{{ errorMessage }}</p><div class="grid gap-6 xl:grid-cols-[1fr_1.4fr]"><Card><CardHeader><CardTitle class="flex items-center gap-2"><Upload /> Upload CSV</CardTitle><CardDescription>Maximum 2 MB and 5,000 rows. Use a template for the required columns.</CardDescription></CardHeader><CardContent><form class="stack" @submit.prevent="createPreview"><label>Record type <select v-model="form.kind"><option v-for="(label, value) in kindLabels" :key="value" :value="value">{{ label }}</option></select></label><Button type="button" variant="outline" @click="download(`/imports/templates/${form.kind}/`, `${form.kind}-template.csv`)"><Download /> Download template</Button><label>Import mode <select v-model="form.mode"><option value="all_or_nothing">All or nothing</option><option value="partial">Import valid rows</option></select></label><label>CSV file <input type="file" accept=".csv,text/csv" required @change="selectFile"></label><Button type="submit" :disabled="submitting || !file">{{ submitting ? 'Validating…' : 'Preview import' }}</Button></form></CardContent></Card><Card><CardHeader><CardTitle>Preview result</CardTitle><CardDescription>Commit revalidates every row against current farm data.</CardDescription></CardHeader><CardContent v-if="preview"><div class="grid grid-cols-3 gap-3"><div><small>Total rows</small><strong class="block text-2xl">{{ preview.rows_total }}</strong></div><div><small>Valid rows</small><strong class="block text-2xl text-emerald-700">{{ preview.valid_rows }}</strong></div><div><small>Invalid rows</small><strong class="block text-2xl" :class="preview.rows_failed ? 'text-destructive' : ''">{{ preview.rows_failed }}</strong></div></div><div v-if="preview.errors.length" class="mt-5 max-h-64 overflow-auto rounded-lg border"><div v-for="item in preview.errors" :key="item.row" class="border-b p-3 text-sm"><strong>Row {{ item.row }}</strong><pre class="mt-1 whitespace-pre-wrap text-xs text-destructive">{{ JSON.stringify(item.errors, null, 2) }}</pre></div></div><div class="actions mt-5"><Button v-if="preview.errors.length" variant="outline" @click="download(`/imports/${preview.id}/errors/`, `${preview.kind}-errors.csv`)"><Download /> Error report</Button><Button :disabled="submitting || preview.status !== 'previewed' || (preview.mode === 'all_or_nothing' && preview.rows_failed > 0)" @click="commit"><CheckCircle2 /> Commit import</Button></div></CardContent><CardContent v-else class="empty-row">Upload a CSV to see row-level validation.</CardContent></Card></div><Card class="mt-6"><CardHeader><CardTitle>Import history</CardTitle></CardHeader><CardContent><div class="overflow-x-auto"><table><thead><tr><th>File</th><th>Type</th><th>Mode</th><th>Status</th><th>Result</th><th>Date</th></tr></thead><tbody><tr v-for="job in jobs" :key="job.id"><td>{{ job.original_filename }}</td><td>{{ kindLabels[job.kind] }}</td><td>{{ job.mode.replaceAll('_', ' ') }}</td><td><Badge :variant="job.status === 'completed' ? 'secondary' : 'outline'">{{ job.status }}</Badge></td><td>{{ job.rows_succeeded }} succeeded · {{ job.rows_failed }} failed</td><td>{{ new Date(job.created_at).toLocaleString() }}</td></tr></tbody></table></div><p v-if="!jobs.length" class="empty-row">No imports yet.</p></CardContent></Card></section></template>
