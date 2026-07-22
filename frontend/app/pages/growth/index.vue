<script setup lang="ts">
import { Scale, TrendingDown, TrendingUp } from '@lucide/vue'
import type { AnimalGrowthSummary } from '~/types/api'

const { request, selectedFarmId } = useApi()
const summaries = ref<AnimalGrowthSummary[]>([])
const loading = ref(true)
const errorMessage = ref('')
const search = ref('')
const visible = computed(() => summaries.value.filter(item => `${item.ear_tag} ${item.name}`.toLowerCase().includes(search.value.toLowerCase())))

async function load() {
  if (!selectedFarmId.value) return
  try { summaries.value = await request<AnimalGrowthSummary[]>('/growth/summary/') }
  catch { errorMessage.value = 'Growth records could not be loaded.' }
  finally { loading.value = false }
}
onMounted(load)
watch(selectedFarmId, load)
</script>

<template><section><div class="page-heading"><div><p class="eyebrow">Performance</p><h1>Weight and growth</h1><p>Compare recent measurements and monitor average daily gain.</p></div><Button as-child><NuxtLink to="/growth/new"><Scale /> Record weight</NuxtLink></Button></div><div class="search"><Input v-model="search" placeholder="Search by ear tag or name" /></div><p v-if="errorMessage" class="error">{{ errorMessage }}</p><div v-if="loading" class="grid gap-4"><Skeleton class="h-32" /><Skeleton class="h-32" /></div><div v-else class="table-card"><Table><TableHeader><TableRow><TableHead>Animal</TableHead><TableHead>Flock</TableHead><TableHead>Latest</TableHead><TableHead>Change</TableHead><TableHead>Average daily gain</TableHead><TableHead>Measured</TableHead></TableRow></TableHeader><TableBody><TableRow v-for="item in visible" :key="item.animal"><TableCell><NuxtLink class="table-link" :to="`/animals/${item.animal}`">{{ item.ear_tag }}</NuxtLink><small v-if="item.name" class="block text-muted-foreground">{{ item.name }}</small></TableCell><TableCell>{{ item.flock_name || 'No flock' }}</TableCell><TableCell class="font-semibold">{{ item.latest_weight_kg }} kg</TableCell><TableCell><span v-if="item.change_kg !== null" class="inline-flex items-center gap-1" :class="Number(item.change_kg) < 0 ? 'text-destructive' : 'text-emerald-700'"><TrendingDown v-if="Number(item.change_kg) < 0" class="size-4" /><TrendingUp v-else class="size-4" />{{ Number(item.change_kg) > 0 ? '+' : '' }}{{ item.change_kg }} kg</span><span v-else>First reading</span></TableCell><TableCell>{{ item.average_daily_gain_kg === null ? '—' : `${item.average_daily_gain_kg} kg/day` }}</TableCell><TableCell>{{ new Date(item.latest_measured_on).toLocaleDateString() }}</TableCell></TableRow></TableBody></Table><div v-if="!visible.length" class="empty-row"><Scale class="mx-auto mb-3 size-8 opacity-40" /><p>No weight measurements found.</p></div></div></section></template>
