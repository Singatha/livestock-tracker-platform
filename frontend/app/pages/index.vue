<script setup lang="ts">
import type { DashboardSummary, Farm, Paginated } from '~/types/api'

const { request, selectedFarmId } = useApi()
const farms = ref<Farm[]>([])
const summary = ref<DashboardSummary | null>(null)
const errorMessage = ref('')

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
  }
})
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">Overview</p><h1>Farm dashboard</h1></div>
      <select v-if="farms.length" :value="selectedFarmId || ''" aria-label="Selected farm" @change="selectFarm(($event.target as HTMLSelectElement).value)">
        <option v-for="farm in farms" :key="farm.id" :value="farm.id">{{ farm.name }}</option>
      </select>
    </div>
    <div v-if="summary" class="metric-grid">
      <article><span>Total active</span><strong>{{ summary.total }}</strong></article>
      <article><span>Sheep</span><strong>{{ summary.sheep }}</strong></article>
      <article><span>Goats</span><strong>{{ summary.goats }}</strong></article>
      <article class="attention"><span>Need attention</span><strong>{{ summary.needs_attention }}</strong></article>
    </div>
    <div v-else class="empty-state">
      <h2>{{ errorMessage || 'No farm selected' }}</h2>
      <NuxtLink v-if="errorMessage" class="button-link" to="/login">Sign in</NuxtLink>
      <NuxtLink v-else class="button-link" to="/farms/new">Create your first farm</NuxtLink>
    </div>
  </section>
</template>
