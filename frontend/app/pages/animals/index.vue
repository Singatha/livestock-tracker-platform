<script setup lang="ts">
import { ChevronRight, PawPrint, Plus, Search } from '@lucide/vue'
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
      <Table v-if="animals.length" class="hidden table-fixed sm:table">
        <TableHeader><TableRow><TableHead class="w-[36%] pl-4">Animal</TableHead><TableHead class="w-[28%]">Classification</TableHead><TableHead class="w-[26%]">Status</TableHead><TableHead class="w-[10%]"><span class="sr-only">Open</span></TableHead></TableRow></TableHeader>
        <TableBody><TableRow v-for="animal in animals" :key="animal.id" class="group"><TableCell class="pl-4"><NuxtLink class="table-link text-base" :to="`/animals/${animal.id}`">{{ animal.ear_tag }}</NuxtLink><small class="mt-0.5 block truncate text-muted-foreground">{{ animal.name || 'Unnamed animal' }}</small></TableCell><TableCell><span class="block capitalize">{{ animal.species }} · {{ animal.sex }}</span><small class="text-muted-foreground">{{ animal.breed || 'Breed not recorded' }}</small></TableCell><TableCell><AnimalStatusBadge :status="animal.status" :attention="animal.needs_attention" /></TableCell><TableCell class="pr-4 text-right"><Button as-child variant="ghost" size="icon"><NuxtLink :to="`/animals/${animal.id}`" :aria-label="`Open ${animal.ear_tag}`"><ChevronRight class="transition-transform group-hover:translate-x-0.5" /></NuxtLink></Button></TableCell></TableRow></TableBody>
      </Table>
      <div v-if="animals.length" class="divide-y sm:hidden"><NuxtLink v-for="animal in animals" :key="animal.id" :to="`/animals/${animal.id}`" class="flex items-center gap-3 p-4"><span class="grid size-10 shrink-0 place-items-center rounded-full bg-secondary text-primary"><PawPrint class="size-5" /></span><span class="min-w-0 flex-1"><strong class="block">{{ animal.ear_tag }}<span v-if="animal.name" class="font-normal text-muted-foreground"> · {{ animal.name }}</span></strong><small class="block truncate capitalize text-muted-foreground">{{ animal.species }} · {{ animal.sex }} · {{ animal.breed || 'Breed not recorded' }}</small></span><AnimalStatusBadge :status="animal.status" :attention="animal.needs_attention" /><ChevronRight class="size-4 shrink-0 text-muted-foreground" /></NuxtLink></div>
      <div v-if="!loading && !animals.length" class="empty-row"><PawPrint class="mx-auto mb-3 size-8 opacity-40" /><p>No animals found.</p><Button as-child variant="link"><NuxtLink to="/animals/new">Register your first animal</NuxtLink></Button></div>
    </div>
  </section>
</template>
