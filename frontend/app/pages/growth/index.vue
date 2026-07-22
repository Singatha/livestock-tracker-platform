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

<template><section><div class="page-heading"><div><p class="eyebrow">Performance</p><h1>Weight and growth</h1><p>Compare recent measurements and monitor average daily gain.</p></div><Button as-child><NuxtLink to="/growth/new"><Scale /> Record weight</NuxtLink></Button></div><div class="search"><Input v-model="search" placeholder="Search by ear tag or name" /></div><p v-if="errorMessage" class="error">{{ errorMessage }}</p><div v-if="loading" class="grid gap-4"><Skeleton class="h-32" /><Skeleton class="h-32" /></div><div v-else class="table-card"><Table v-if="visible.length" class="hidden table-fixed sm:table"><TableHeader><TableRow><TableHead class="w-[28%] pl-4">Animal</TableHead><TableHead class="w-[24%]">Latest measurement</TableHead><TableHead class="w-[30%]">Growth trend</TableHead><TableHead class="w-[18%] pr-4 text-right">Flock</TableHead></TableRow></TableHeader><TableBody><TableRow v-for="item in visible" :key="item.animal"><TableCell class="pl-4"><NuxtLink class="table-link text-base" :to="`/animals/${item.animal}`">{{ item.ear_tag }}</NuxtLink><small v-if="item.name" class="mt-0.5 block text-muted-foreground">{{ item.name }}</small></TableCell><TableCell><strong class="block text-base tabular-nums">{{ item.latest_weight_kg }} kg</strong><small class="text-muted-foreground">{{ new Date(item.latest_measured_on).toLocaleDateString() }}</small></TableCell><TableCell><span v-if="item.change_kg !== null" class="inline-flex items-center gap-1 font-semibold" :class="Number(item.change_kg) < 0 ? 'text-destructive' : 'text-emerald-700'"><TrendingDown v-if="Number(item.change_kg) < 0" class="size-4" /><TrendingUp v-else class="size-4" />{{ Number(item.change_kg) > 0 ? '+' : '' }}{{ item.change_kg }} kg</span><span v-else class="text-muted-foreground">First reading</span><small class="mt-0.5 block text-muted-foreground">{{ item.average_daily_gain_kg === null ? 'More readings needed' : `${item.average_daily_gain_kg} kg/day average` }}</small></TableCell><TableCell class="pr-4 text-right">{{ item.flock_name || 'No flock' }}</TableCell></TableRow></TableBody></Table><div v-if="visible.length" class="divide-y sm:hidden"><NuxtLink v-for="item in visible" :key="item.animal" :to="`/animals/${item.animal}`" class="block p-4"><div class="flex items-start justify-between gap-3"><span><strong class="text-primary">{{ item.ear_tag }}</strong><small v-if="item.name" class="ml-1 text-muted-foreground">· {{ item.name }}</small></span><strong class="text-lg tabular-nums">{{ item.latest_weight_kg }} kg</strong></div><div class="mt-2 flex items-center justify-between gap-3 text-sm"><span v-if="item.change_kg !== null" class="inline-flex items-center gap-1 font-semibold" :class="Number(item.change_kg) < 0 ? 'text-destructive' : 'text-emerald-700'"><TrendingDown v-if="Number(item.change_kg) < 0" class="size-4" /><TrendingUp v-else class="size-4" />{{ Number(item.change_kg) > 0 ? '+' : '' }}{{ item.change_kg }} kg</span><span v-else class="text-muted-foreground">First reading</span><span class="text-muted-foreground">{{ new Date(item.latest_measured_on).toLocaleDateString() }}</span></div></NuxtLink></div><div v-if="!visible.length" class="empty-row"><Scale class="mx-auto mb-3 size-8 opacity-40" /><p>No weight measurements found.</p></div></div></section></template>
