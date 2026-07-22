<script setup lang="ts">
import { PawPrint, Plus, Search } from '@lucide/vue'
import type { Animal, Paginated } from '~/types/api'

const { request, selectedFarmId } = useApi()
const animals = ref<Animal[]>([])
const search = ref('')
const loading = ref(false)

async function loadAnimals() {
  if (!selectedFarmId.value) return
  loading.value = true
  try {
    const query = search.value ? `?search=${encodeURIComponent(search.value)}` : ''
    const response = await request<Paginated<Animal>>(`/animals/${query}`)
    animals.value = response.results
  } finally {
    loading.value = false
  }
}

onMounted(loadAnimals)
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">Livestock register</p><h1>Animals</h1><p>Search and manage individual livestock records.</p></div>
      <Button as-child><NuxtLink to="/animals/new"><Plus /> Register animal</NuxtLink></Button>
    </div>
    <form class="search" @submit.prevent="loadAnimals">
      <div class="relative flex-1"><Search class="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" /><Input v-model="search" class="pl-9" placeholder="Search by ear tag" aria-label="Search by ear tag" /></div>
      <Button type="submit">Search</Button>
    </form>
    <div class="table-card">
      <Table>
        <TableHeader><TableRow><TableHead>Ear tag</TableHead><TableHead>Name</TableHead><TableHead>Species</TableHead><TableHead>Breed</TableHead><TableHead>Status</TableHead></TableRow></TableHeader>
        <TableBody><TableRow v-for="animal in animals" :key="animal.id"><TableCell><NuxtLink class="table-link" :to="`/animals/${animal.id}`">{{ animal.ear_tag }}</NuxtLink></TableCell><TableCell class="font-medium">{{ animal.name || '—' }}</TableCell><TableCell class="capitalize">{{ animal.species }}</TableCell><TableCell>{{ animal.breed || '—' }}</TableCell><TableCell><AnimalStatusBadge :status="animal.status" :attention="animal.needs_attention" /></TableCell></TableRow></TableBody>
      </Table>
      <div v-if="!loading && !animals.length" class="empty-row"><PawPrint class="mx-auto mb-3 size-8 opacity-40" /><p>No animals found.</p><Button as-child variant="link"><NuxtLink to="/animals/new">Register your first animal</NuxtLink></Button></div>
    </div>
  </section>
</template>
