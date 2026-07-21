<script setup lang="ts">
const selectedFarmId = useState<string | null>('selected-farm-id', () => null)
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <NuxtLink class="brand" to="/">Flockwise</NuxtLink>
      <nav aria-label="Primary navigation">
        <NuxtLink to="/">Dashboard</NuxtLink>
        <NuxtLink to="/animals">Animals</NuxtLink>
        <NuxtLink to="/flocks/new">New flock</NuxtLink>
      </nav>
      <span v-if="selectedFarmId" class="farm-indicator">Farm selected</span>
    </header>
    <main class="page-container">
      <slot />
    </main>
  </div>
</template>
