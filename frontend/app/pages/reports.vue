<script setup lang="ts">
import { Activity, AlertTriangle, CalendarCheck2, Download, HeartPulse, PackageSearch, PawPrint, Stethoscope } from '@lucide/vue'
import type { Flock, MonthlyActivity, Paginated, ReportSummary } from '~/types/api'

const { download, request, selectedFarmId } = useApi()
const summary = ref<ReportSummary | null>(null)
const activity = ref<MonthlyActivity[]>([])
const flocks = ref<Flock[]>([])
const loading = ref(true)
const downloading = ref('')
const errorMessage = ref('')
const filters = reactive({ date_from: '', date_to: '', flock: '', species: '', status: '' })
const maxActivity = computed(() => Math.max(1, ...activity.value.flatMap(item => [item.animals_registered, item.health_observations, item.tasks_completed])))

function queryString() {
  const values = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => { if (value) values.set(key, value) })
  const query = values.toString()
  return query ? `?${query}` : ''
}

async function loadReports() {
  if (!selectedFarmId.value) { loading.value = false; return }
  loading.value = true; errorMessage.value = ''
  try {
    ;[summary.value, activity.value] = await Promise.all([
      request<ReportSummary>(`/reports/overview/${queryString()}`),
      request<MonthlyActivity[]>(`/reports/activity/${queryString()}`),
    ])
  } catch { errorMessage.value = 'Reports could not be loaded.' } finally { loading.value = false }
}

async function exportReport(type: string) {
  downloading.value = type
  try { await download(`/reports/export/${type}/${queryString()}`, `${type}-report.csv`) } finally { downloading.value = '' }
}

onMounted(async () => {
  if (selectedFarmId.value) flocks.value = (await request<Paginated<Flock>>('/animals/flocks/')).results
  await loadReports()
})
</script>

<template>
  <section>
    <div class="page-heading"><div><p class="eyebrow">Farm performance</p><h1>Reports & analytics</h1><p>Review livestock, care activity, and feed inventory for the selected farm.</p></div></div>
    <Card class="mb-6"><CardHeader><CardTitle>Report filters</CardTitle><CardDescription>Filters apply to dashboard figures and animal exports.</CardDescription></CardHeader><CardContent><form class="grid gap-4 sm:grid-cols-2 lg:grid-cols-5" @submit.prevent="loadReports"><label>From <input v-model="filters.date_from" type="date"></label><label>To <input v-model="filters.date_to" type="date"></label><label>Flock <select v-model="filters.flock"><option value="">All flocks</option><option v-for="flock in flocks" :key="flock.id" :value="flock.id">{{ flock.name }}</option></select></label><label>Species <select v-model="filters.species"><option value="">All species</option><option value="sheep">Sheep</option><option value="goat">Goats</option></select></label><label>Status <select v-model="filters.status"><option value="">All statuses</option><option value="active">Active</option><option value="sold">Sold</option><option value="deceased">Deceased</option><option value="missing">Missing</option></select></label><div class="sm:col-span-2 lg:col-span-5"><Button type="submit">Apply filters</Button></div></form></CardContent></Card>
    <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>
    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><Skeleton v-for="item in 8" :key="item" class="h-32 rounded-xl" /></div>
    <template v-else-if="summary">
      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><MetricCard label="Animals" :value="summary.animals" :icon="PawPrint" /><MetricCard label="Need attention" :value="summary.needs_attention" :icon="AlertTriangle" tone="warning" /><MetricCard label="Open health concerns" :value="summary.open_health_concerns" :icon="HeartPulse" tone="danger" /><MetricCard label="Completed tasks" :value="summary.completed_tasks" :icon="CalendarCheck2" /><MetricCard label="Health observations" :value="summary.health_observations" :icon="Activity" /><MetricCard label="Treatments" :value="summary.treatments" :icon="Stethoscope" /><MetricCard label="Overdue tasks" :value="summary.overdue_tasks" :icon="AlertTriangle" :tone="summary.overdue_tasks ? 'danger' : 'default'" /><MetricCard label="Low-stock feeds" :value="summary.low_stock_feeds" :icon="PackageSearch" :tone="summary.low_stock_feeds ? 'warning' : 'default'" /></div>
      <div class="mt-6 grid gap-6 xl:grid-cols-[1.5fr_1fr]">
        <Card><CardHeader><CardTitle>Monthly activity</CardTitle><CardDescription>Registrations, health observations, and completed tasks.</CardDescription></CardHeader><CardContent><div v-if="activity.length" class="overflow-x-auto"><div class="flex h-64 min-w-[32rem] items-end gap-5 border-b px-2 pb-7"><div v-for="item in activity" :key="item.month" class="relative flex h-full flex-1 items-end justify-center gap-1"><div class="w-4 rounded-t bg-primary" :style="{ height: `${(item.animals_registered / maxActivity) * 100}%` }" :title="`${item.animals_registered} animals registered`" /><div class="w-4 rounded-t bg-amber-400" :style="{ height: `${(item.health_observations / maxActivity) * 100}%` }" :title="`${item.health_observations} observations`" /><div class="w-4 rounded-t bg-sky-500" :style="{ height: `${(item.tasks_completed / maxActivity) * 100}%` }" :title="`${item.tasks_completed} tasks completed`" /><span class="absolute -bottom-6 text-xs text-muted-foreground">{{ new Date(`${item.month}T00:00:00`).toLocaleDateString(undefined, { month: 'short' }) }}</span></div></div><div class="mt-4 flex flex-wrap gap-4 text-xs"><span><i class="mr-1 inline-block size-2 rounded-full bg-primary" />Animals</span><span><i class="mr-1 inline-block size-2 rounded-full bg-amber-400" />Health</span><span><i class="mr-1 inline-block size-2 rounded-full bg-sky-500" />Tasks</span></div></div><div v-else class="empty-row">No activity in this period.</div></CardContent></Card>
        <div class="grid gap-6"><Card><CardHeader><CardTitle>Feed inventory value</CardTitle><CardDescription>Quantity multiplied by recorded unit cost.</CardDescription></CardHeader><CardContent><p class="font-heading text-4xl font-bold">{{ Number(summary.inventory_value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</p><p class="mt-2 text-xs text-muted-foreground">Currency follows your farm’s entered costs.</p></CardContent></Card><Card><CardHeader><CardTitle>Export CSV</CardTitle><CardDescription>Download records for spreadsheets or printing.</CardDescription></CardHeader><CardContent class="grid grid-cols-2 gap-2"><Button v-for="type in ['animals', 'health', 'tasks', 'feed', 'weights', 'medicine']" :key="type" variant="outline" :disabled="!!downloading" class="capitalize" @click="exportReport(type)"><Download /> {{ downloading === type ? 'Downloading…' : type }}</Button></CardContent></Card></div>
      </div>
    </template>
  </section>
</template>
