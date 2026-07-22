<script setup lang="ts">
import { AlertTriangle, ClipboardList, PackageOpen, Plus, Wheat } from '@lucide/vue'
import type { Feed, FeedingPlan, Paginated } from '~/types/api'

const { request, selectedFarmId } = useApi()
const feeds = ref<Feed[]>([])
const plans = ref<FeedingPlan[]>([])
const loading = ref(true)
const errorMessage = ref('')
const lowStock = computed(() => feeds.value.filter(feed => feed.is_low_stock))

onMounted(async () => {
  if (!selectedFarmId.value) { loading.value = false; return }
  try {
    const [feedResponse, planResponse] = await Promise.all([
      request<Paginated<Feed>>('/nutrition/feeds/'),
      request<Paginated<FeedingPlan>>('/nutrition/plans/?active=true'),
    ])
    feeds.value = feedResponse.results
    plans.value = planResponse.results
  } catch {
    errorMessage.value = 'Nutrition records could not be loaded.'
  } finally { loading.value = false }
})
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">Feed management</p><h1>Nutrition</h1><p>Track feed inventory and flock feeding plans.</p></div>
      <div class="flex flex-wrap gap-2"><Button as-child variant="outline"><NuxtLink to="/nutrition/feeds/new"><Plus /> Add feed</NuxtLink></Button><Button as-child><NuxtLink to="/nutrition/plans/new"><ClipboardList /> Create plan</NuxtLink></Button></div>
    </div>
    <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>
    <div v-if="loading" class="grid gap-4 sm:grid-cols-3"><Skeleton v-for="item in 3" :key="item" class="h-32 rounded-xl" /></div>
    <template v-else>
      <div class="mb-8 grid gap-4 sm:grid-cols-3">
        <MetricCard label="Feed products" :value="feeds.length" :icon="Wheat" />
        <MetricCard label="Active plans" :value="plans.length" :icon="ClipboardList" />
        <MetricCard label="Low stock" :value="lowStock.length" :icon="AlertTriangle" :tone="lowStock.length ? 'warning' : 'default'" />
      </div>
      <div class="grid gap-6 xl:grid-cols-2">
        <Card><CardHeader><CardTitle>Feed inventory</CardTitle><CardDescription>Current quantities and reorder levels.</CardDescription></CardHeader><CardContent class="grid gap-3"><div v-for="feed in feeds" :key="feed.id" class="flex items-center justify-between gap-4 rounded-lg border p-4"><div><strong class="block">{{ feed.name }}</strong><small class="capitalize text-muted-foreground">{{ feed.category }} · {{ feed.suitability }}</small></div><div class="text-right"><strong class="block tabular-nums">{{ feed.quantity_on_hand }} {{ feed.unit }}</strong><Badge v-if="feed.is_low_stock" variant="outline" class="border-amber-200 bg-amber-50 text-amber-800">Low stock</Badge></div></div><div v-if="!feeds.length" class="empty-row"><PackageOpen class="mx-auto mb-2 size-8 opacity-40" />No feed recorded.</div></CardContent></Card>
        <Card><CardHeader><CardTitle>Active feeding plans</CardTitle><CardDescription>Plans are records, not veterinary prescriptions.</CardDescription></CardHeader><CardContent class="grid gap-3"><div v-for="plan in plans" :key="plan.id" class="rounded-lg border p-4"><div class="flex justify-between gap-3"><div><strong class="block">{{ plan.name }}</strong><small class="capitalize text-muted-foreground">{{ plan.flock_name }} · {{ plan.life_stage }}</small></div><Badge variant="secondary">{{ plan.items.length }} feeds</Badge></div><div v-if="plan.compatibility_warnings.length" class="mt-3 rounded-lg bg-amber-50 p-3 text-xs font-medium text-amber-900"><p v-for="warning in plan.compatibility_warnings" :key="warning">{{ warning }}</p></div></div><div v-if="!plans.length" class="empty-row"><ClipboardList class="mx-auto mb-2 size-8 opacity-40" />No active feeding plans.</div></CardContent></Card>
      </div>
    </template>
  </section>
</template>
