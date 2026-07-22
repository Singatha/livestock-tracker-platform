<script setup lang="ts">
const selectedFarmId = useCookie<string | null>('selected-farm-id', {
  default: () => null,
  sameSite: 'lax',
})
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <NuxtLink class="brand" to="/">Flockwise</NuxtLink>
      <nav aria-label="Primary navigation">
        <NuxtLink to="/">Dashboard</NuxtLink>
        <NuxtLink to="/animals">Animals</NuxtLink>
        <NuxtLink to="/tasks">Tasks</NuxtLink>
      </nav>
      <span v-if="selectedFarmId" class="farm-indicator">Farm selected</span>
    </header>
    <main class="page-container">
      <slot />
    </main>
  </div>
</template>
