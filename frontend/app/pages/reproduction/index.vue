<script setup lang="ts">
import type { BirthRecord, BreedingRecord, Paginated } from '~/types/api'

const { request, selectedFarmId } = useApi()
const breedings = ref<BreedingRecord[]>([])
const births = ref<BirthRecord[]>([])
const loading = ref(true)
const errorMessage = ref('')

async function load() {
  if (!selectedFarmId.value) return
  try {
    const [breedingResponse, birthResponse] = await Promise.all([
      request<Paginated<BreedingRecord>>('/reproduction/breedings/'),
      request<Paginated<BirthRecord>>('/reproduction/births/'),
    ])
    breedings.value = breedingResponse.results
    births.value = birthResponse.results
  } catch { errorMessage.value = 'Reproduction records could not be loaded.' }
  finally { loading.value = false }
}

onMounted(load)
watch(selectedFarmId, load)
</script>

<template>
  <section>
    <div class="page-heading"><div><p class="eyebrow">Herd growth</p><h1>Breeding and births</h1><p>Track services, pregnancy outcomes, and lambing or kidding records.</p></div><div class="actions wrap"><Button as-child variant="outline"><NuxtLink to="/reproduction/births/new">Record birth</NuxtLink></Button><Button as-child><NuxtLink to="/reproduction/breedings/new">Record breeding</NuxtLink></Button></div></div>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <div v-if="loading" class="grid gap-4"><Skeleton class="h-32" /><Skeleton class="h-32" /></div>
    <template v-else>
      <Card><CardHeader><CardTitle>Breeding register</CardTitle><CardDescription>Expected dates use 147 days for sheep and 150 days for goats unless overridden.</CardDescription></CardHeader><CardContent><div v-if="breedings.length" class="overflow-x-auto"><table><thead><tr><th>Dam</th><th>Sire</th><th>Bred</th><th>Expected</th><th>Status</th></tr></thead><tbody><tr v-for="item in breedings" :key="item.id"><td>{{ item.dam_name }}</td><td>{{ item.sire_name || 'Not recorded' }}</td><td>{{ new Date(item.breeding_date).toLocaleDateString() }}</td><td>{{ new Date(item.expected_birth_date).toLocaleDateString() }}</td><td><NuxtLink :to="`/reproduction/breedings/${item.id}`"><Badge variant="secondary">{{ item.status.replaceAll('_', ' ') }}</Badge></NuxtLink></td></tr></tbody></table></div><p v-else class="empty-row">No breeding records yet.</p></CardContent></Card>
      <Card class="mt-6"><CardHeader><CardTitle>Recent births</CardTitle></CardHeader><CardContent><div v-if="births.length" class="overflow-x-auto"><table><thead><tr><th>Dam</th><th>Date</th><th>Total</th><th>Born alive</th><th>Stillborn</th></tr></thead><tbody><tr v-for="item in births" :key="item.id"><td>{{ item.dam_name }}</td><td>{{ new Date(item.birth_date).toLocaleDateString() }}</td><td>{{ item.total_born }}</td><td>{{ item.born_alive }}</td><td>{{ item.stillborn }}</td></tr></tbody></table></div><p v-else class="empty-row">No births recorded yet.</p></CardContent></Card>
    </template>
  </section>
</template>
