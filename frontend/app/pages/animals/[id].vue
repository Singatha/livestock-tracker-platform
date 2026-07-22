<script setup lang="ts">
import type { Animal, TimelineEvent } from '~/types/api'

const route = useRoute()
const animalId = route.params.id as string
const { request } = useApi()
const animal = ref<Animal | null>(null)
const timeline = ref<TimelineEvent[]>([])
const errorMessage = ref('')

onMounted(async () => {
  try {
    ;[animal.value, timeline.value] = await Promise.all([
      request<Animal>(`/animals/${animalId}/`),
      request<TimelineEvent[]>(`/animals/${animalId}/timeline/`),
    ])
  } catch {
    errorMessage.value = 'The animal record could not be loaded.'
  }
})
</script>

<template>
  <section v-if="animal">
    <div class="page-heading">
      <div><p class="eyebrow">{{ animal.species }}</p><h1>{{ animal.name || animal.ear_tag }}</h1><p>Ear tag {{ animal.ear_tag }} · {{ animal.breed || 'Breed not recorded' }}</p></div>
      <div class="actions wrap">
        <NuxtLink class="secondary-link" :to="`/animals/${animal.id}/edit`">Edit details</NuxtLink>
        <NuxtLink class="secondary-link" :to="`/animals/${animal.id}/lifecycle`">Manage lifecycle</NuxtLink>
        <NuxtLink class="secondary-link" :to="`/growth/new?animal=${animal.id}`">Record weight</NuxtLink>
        <NuxtLink class="secondary-link" :to="`/health/observations/new?animal=${animal.id}`">Record observation</NuxtLink>
        <NuxtLink class="secondary-link" :to="`/health/treatments/new?animal=${animal.id}`">Record treatment</NuxtLink>
        <NuxtLink class="button-link" :to="`/tasks/new?animal=${animal.id}`">Schedule task</NuxtLink>
      </div>
    </div>
    <div class="detail-grid">
      <article><span>Status</span><strong>{{ animal.status }}</strong></article>
      <article><span>Sex</span><strong>{{ animal.sex }}</strong></article>
      <article><span>Attention</span><strong>{{ animal.needs_attention ? 'Required' : 'No flag' }}</strong></article>
      <article><span>Date of birth</span><strong>{{ animal.date_of_birth ? new Date(animal.date_of_birth).toLocaleDateString() : 'Not recorded' }}</strong></article>
    </div>
    <section class="timeline-section">
      <h2>History and upcoming work</h2>
      <ol v-if="timeline.length" class="timeline">
        <li v-for="event in timeline" :key="`${event.kind}-${event.id}`">
          <div class="timeline-marker" />
          <div><p class="timeline-meta">{{ event.kind }} · {{ new Date(event.date).toLocaleDateString() }} · {{ event.status }}</p><h3>{{ event.title }}</h3><p v-if="event.details">{{ event.details }}</p></div>
        </li>
      </ol>
      <p v-else class="empty-row">No history or upcoming work yet.</p>
    </section>
  </section>
  <p v-else-if="errorMessage" class="error">{{ errorMessage }}</p>
</template>
