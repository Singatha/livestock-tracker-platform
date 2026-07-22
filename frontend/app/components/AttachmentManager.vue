<script setup lang="ts">
import { Download, FileImage, FileText, Trash2, Upload } from '@lucide/vue'
import type { Animal, Attachment, Paginated } from '~/types/api'

const props = defineProps<{ animalId?: string }>()
const { download, request, selectedFarmId } = useApi()
const attachments = ref<Attachment[]>([])
const animals = ref<Animal[]>([])
const loading = ref(true)
const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const form = reactive({ animal: props.animalId || '', category: 'photo', title: '', description: '' })
const categories = [
  ['photo', 'Animal photo'],
  ['veterinary', 'Veterinary document'],
  ['prescription', 'Prescription'],
  ['lab_result', 'Lab result'],
  ['certificate', 'Certificate'],
  ['invoice', 'Invoice'],
  ['other', 'Other'],
] as const

function fileChanged(event: Event) {
  selectedFile.value = (event.target as HTMLInputElement).files?.[0] || null
  if (selectedFile.value && !form.title) form.title = selectedFile.value.name.replace(/\.[^.]+$/, '')
}

function formatSize(bytes: number) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

async function load() {
  if (!selectedFarmId.value) { loading.value = false; return }
  loading.value = true; errorMessage.value = ''
  try {
    const query = props.animalId ? `?animal=${props.animalId}` : ''
    const requests: [Promise<Paginated<Attachment>>, Promise<Paginated<Animal>>?] = [
      request<Paginated<Attachment>>(`/attachments/${query}`),
    ]
    if (!props.animalId) requests.push(request<Paginated<Animal>>('/animals/?status=active'))
    const [attachmentResponse, animalResponse] = await Promise.all(requests)
    attachments.value = attachmentResponse.results
    if (animalResponse) animals.value = animalResponse.results
  } catch { errorMessage.value = 'Documents could not be loaded.' }
  finally { loading.value = false }
}

async function uploadFile() {
  if (!selectedFile.value) return
  submitting.value = true; errorMessage.value = ''; successMessage.value = ''
  const body = new FormData()
  body.append('file', selectedFile.value)
  body.append('category', form.category)
  body.append('title', form.title)
  body.append('description', form.description)
  if (form.animal) body.append('animal', form.animal)
  try {
    await request<Attachment>('/attachments/', { method: 'POST', body })
    form.title = ''; form.description = ''; selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
    await load()
    successMessage.value = 'File uploaded securely.'
  } catch { errorMessage.value = 'Upload failed. Use JPG, PNG, WebP, PDF, Word, or CSV files up to 10 MB.' }
  finally { submitting.value = false }
}

async function downloadFile(item: Attachment) {
  try { await download(`/attachments/${item.id}/content/`, item.original_filename) }
  catch { errorMessage.value = 'The file could not be downloaded.' }
}

async function removeFile(item: Attachment) {
  if (!confirm(`Delete ${item.original_filename}? This cannot be undone.`)) return
  try {
    await request(`/attachments/${item.id}/`, { method: 'DELETE' })
    attachments.value = attachments.value.filter(value => value.id !== item.id)
  } catch { errorMessage.value = 'You do not have permission to delete this file.' }
}

onMounted(load)
watch(selectedFarmId, load)
</script>

<template>
  <div class="grid gap-6 xl:grid-cols-[1fr_1.35fr]">
    <Card><CardHeader><p class="eyebrow">Private farm storage</p><CardTitle>Upload file</CardTitle><CardDescription>Add a photo or supporting document up to 10 MB.</CardDescription></CardHeader><CardContent><form class="stack" @submit.prevent="uploadFile">
        <label>File <input ref="fileInput" type="file" accept=".jpg,.jpeg,.png,.webp,.pdf,.doc,.docx,.csv" required @change="fileChanged"></label>
        <label>Category <select v-model="form.category"><option v-for="category in categories" :key="category[0]" :value="category[0]">{{ category[1] }}</option></select></label>
        <label v-if="!animalId">Animal (optional) <select v-model="form.animal"><option value="">Farm-wide document</option><option v-for="animal in animals" :key="animal.id" :value="animal.id">{{ animal.ear_tag }} · {{ animal.name || animal.species }}</option></select></label>
        <label>Title <input v-model="form.title" maxlength="200" required></label>
        <label>Description <textarea v-model="form.description" rows="3" /></label>
        <p v-if="successMessage" class="success" role="status">{{ successMessage }}</p><p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>
        <Button type="submit" :disabled="submitting || !selectedFile"><Upload /> {{ submitting ? 'Uploading…' : 'Upload securely' }}</Button>
      </form></CardContent></Card>
    <Card><CardHeader><CardTitle>Files</CardTitle><CardDescription>Downloads require an active membership in the selected farm.</CardDescription></CardHeader><CardContent>
      <div v-if="loading" class="grid gap-3"><Skeleton v-for="item in 4" :key="item" class="h-16" /></div>
      <div v-for="item in attachments" v-else :key="item.id" class="flex items-center gap-3 border-b py-3 last:border-0">
        <span class="grid size-10 shrink-0 place-items-center rounded-lg bg-secondary text-primary"><FileImage v-if="item.content_type.startsWith('image/')" class="size-5" /><FileText v-else class="size-5" /></span>
        <div class="min-w-0 flex-1"><strong class="block truncate">{{ item.title }}</strong><small class="block truncate text-muted-foreground">{{ item.original_filename }} · {{ formatSize(item.size_bytes) }} · {{ item.uploaded_by_name }}</small></div>
        <Button variant="ghost" size="icon" :aria-label="`Download ${item.title}`" @click="downloadFile(item)"><Download /></Button><Button variant="ghost" size="icon" :aria-label="`Delete ${item.title}`" @click="removeFile(item)"><Trash2 /></Button>
      </div>
      <p v-if="!loading && !attachments.length" class="empty-row">No files uploaded yet.</p>
    </CardContent></Card>
  </div>
</template>
