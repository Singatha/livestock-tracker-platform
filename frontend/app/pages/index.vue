<script setup lang="ts">
import { AlertTriangle, Beef, CalendarClock, ClipboardPlus, HeartHandshake, HeartPulse, PawPrint, Pill, Plus, Scale } from '@lucide/vue'
import type { DashboardSummary, Farm, Paginated } from '~/types/api'

const { request, selectedFarmId } = useApi()
const farms = ref<Farm[]>([])
const summary = ref<DashboardSummary | null>(null)
const errorMessage = ref('')
const loading = ref(true)

async function loadSummary() {
  if (!selectedFarmId.value) return
  summary.value = await request<DashboardSummary>('/dashboard/')
}

async function selectFarm(farmId: string) {
  selectedFarmId.value = farmId
  await loadSummary()
}

onMounted(async () => {
  try {
    const response = await request<Paginated<Farm>>('/farms/')
    farms.value = response.results
    if (!selectedFarmId.value && farms.value[0]) selectedFarmId.value = farms.value[0].id
    await loadSummary()
  } catch {
    errorMessage.value = 'Sign in to view your dashboard.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">Overview</p><h1>Good morning</h1><p>Here’s what needs your attention across the farm.</p></div>
      <div class="flex flex-wrap gap-2">
        <select v-if="farms.length" class="min-w-48" :value="selectedFarmId || ''" aria-label="Selected farm" @change="selectFarm(($event.target as HTMLSelectElement).value)"><option v-for="farm in farms" :key="farm.id" :value="farm.id">{{ farm.name }}</option></select>
        <Button as-child><NuxtLink to="/animals/new"><Plus /> Add animal</NuxtLink></Button>
      </div>
    </div>
    <div v-if="loading" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><Skeleton v-for="item in 4" :key="item" class="h-36 rounded-xl" /></div>
    <template v-else-if="summary">
      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Total livestock" :value="summary.total" :icon="PawPrint" hint="Active animals" />
        <MetricCard label="Sheep" :value="summary.sheep" :icon="Beef" />
        <MetricCard label="Need attention" :value="summary.needs_attention" :icon="AlertTriangle" tone="warning" hint="Review health status" />
        <MetricCard label="Overdue tasks" :value="summary.overdue_tasks" :icon="CalendarClock" tone="danger" hint="Action required" />
        <MetricCard label="Losing weight" :value="summary.animals_losing_weight" :icon="Scale" :tone="summary.animals_losing_weight ? 'warning' : 'default'" hint="Compared with previous measurement" />
      </div>
      <div class="mt-8 grid gap-6 lg:grid-cols-[1.5fr_1fr]">
        <Card>
          <CardHeader><CardTitle>Care overview</CardTitle><CardDescription>Health concerns and work due soon.</CardDescription></CardHeader>
          <CardContent class="grid gap-3 sm:grid-cols-2">
            <NuxtLink to="/animals" class="flex items-center gap-4 rounded-xl border p-4 transition-colors hover:bg-muted/60"><span class="grid size-10 place-items-center rounded-lg bg-red-50 text-destructive"><HeartPulse /></span><span><strong class="block text-2xl">{{ summary.open_health_concerns }}</strong><small class="text-muted-foreground">Open health concerns</small></span></NuxtLink>
            <NuxtLink to="/tasks" class="flex items-center gap-4 rounded-xl border p-4 transition-colors hover:bg-muted/60"><span class="grid size-10 place-items-center rounded-lg bg-secondary text-primary"><CalendarClock /></span><span><strong class="block text-2xl">{{ summary.due_next_7_days }}</strong><small class="text-muted-foreground">Due in the next 7 days</small></span></NuxtLink>
            <NuxtLink to="/reproduction" class="flex items-center gap-4 rounded-xl border p-4 transition-colors hover:bg-muted/60"><span class="grid size-10 place-items-center rounded-lg bg-pink-50 text-pink-700"><HeartHandshake /></span><span><strong class="block text-2xl">{{ summary.expected_births_next_30_days }}</strong><small class="text-muted-foreground">Births expected in 30 days</small></span></NuxtLink>
            <NuxtLink to="/reproduction" class="flex items-center gap-4 rounded-xl border p-4 transition-colors hover:bg-muted/60"><span class="grid size-10 place-items-center rounded-lg bg-amber-50 text-amber-700"><AlertTriangle /></span><span><strong class="block text-2xl">{{ summary.overdue_expected_births }}</strong><small class="text-muted-foreground">Expected births overdue</small></span></NuxtLink>
            <NuxtLink to="/medicine" class="flex items-center gap-4 rounded-xl border p-4 transition-colors hover:bg-muted/60"><span class="grid size-10 place-items-center rounded-lg bg-sky-50 text-sky-700"><Pill /></span><span><strong class="block text-2xl">{{ summary.active_treatment_courses }}</strong><small class="text-muted-foreground">Active treatment courses</small></span></NuxtLink>
            <NuxtLink to="/medicine" class="flex items-center gap-4 rounded-xl border p-4 transition-colors hover:bg-muted/60"><span class="grid size-10 place-items-center rounded-lg bg-red-50 text-destructive"><AlertTriangle /></span><span><strong class="block text-2xl">{{ summary.animals_under_withdrawal }}</strong><small class="text-muted-foreground">Animals under withdrawal</small></span></NuxtLink>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Quick actions</CardTitle><CardDescription>Keep farm records up to date.</CardDescription></CardHeader>
          <CardContent class="grid gap-2">
            <Button as-child variant="outline" class="h-11 justify-start"><NuxtLink to="/tasks/new"><ClipboardPlus /> Schedule care task</NuxtLink></Button>
            <Button as-child variant="outline" class="h-11 justify-start"><NuxtLink to="/flocks/new"><Beef /> Create a flock</NuxtLink></Button>
            <Button as-child variant="outline" class="h-11 justify-start"><NuxtLink to="/animals/new"><Plus /> Register an animal</NuxtLink></Button>
            <Button as-child variant="outline" class="h-11 justify-start"><NuxtLink to="/reproduction/breedings/new"><HeartHandshake /> Record breeding</NuxtLink></Button>
            <Button as-child variant="outline" class="h-11 justify-start"><NuxtLink to="/growth/new"><Scale /> Record weight</NuxtLink></Button>
            <Button as-child variant="outline" class="h-11 justify-start"><NuxtLink to="/medicine/courses/new"><Pill /> Start treatment course</NuxtLink></Button>
          </CardContent>
        </Card>
      </div>
    </template>
    <div v-else class="empty-state">
      <PawPrint class="mx-auto mb-4 size-9 text-muted-foreground" />
      <h2>{{ errorMessage || 'Create your first farm' }}</h2>
      <p class="mx-auto mb-5 max-w-md text-sm text-muted-foreground">Start with a farm workspace, then add flocks and animals.</p>
      <Button as-child><NuxtLink :to="errorMessage ? '/login' : '/farms/new'">{{ errorMessage ? 'Sign in' : 'Create farm' }}</NuxtLink></Button>
    </div>
  </section>
</template>
