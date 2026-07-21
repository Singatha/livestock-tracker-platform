<script setup lang="ts">
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
      <div><p class="eyebrow">Register</p><h1>Animals</h1></div>
      <NuxtLink class="button-link" to="/animals/new">Register animal</NuxtLink>
    </div>
    <form class="search" @submit.prevent="loadAnimals">
      <input v-model="search" placeholder="Search by ear tag" aria-label="Search by ear tag">
      <button type="submit">Search</button>
    </form>
    <div class="table-card">
      <table>
        <thead><tr><th>Ear tag</th><th>Name</th><th>Species</th><th>Breed</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="animal in animals" :key="animal.id">
            <td><NuxtLink class="table-link" :to="`/animals/${animal.id}`">{{ animal.ear_tag }}</NuxtLink></td><td>{{ animal.name || '—' }}</td><td>{{ animal.species }}</td><td>{{ animal.breed || '—' }}</td><td><span class="status">{{ animal.status }}</span></td>
          </tr>
        </tbody>
      </table>
      <p v-if="!loading && !animals.length" class="empty-row">No animals found.</p>
    </div>
  </section>
</template>
