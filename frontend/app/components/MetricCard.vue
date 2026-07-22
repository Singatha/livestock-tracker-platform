<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{ label: string; value: number; icon: Component; tone?: 'default' | 'warning' | 'danger'; hint?: string }>()
</script>

<template>
  <Card class="overflow-hidden shadow-sm transition-shadow hover:shadow-md" :class="tone === 'danger' ? 'border-destructive/25' : tone === 'warning' ? 'border-warning/35' : ''">
    <CardHeader class="flex flex-row items-center justify-between pb-2">
      <CardDescription class="font-semibold">{{ label }}</CardDescription>
      <span class="grid size-9 place-items-center rounded-lg" :class="tone === 'danger' ? 'bg-destructive/10 text-destructive' : tone === 'warning' ? 'bg-warning-soft text-amber-700' : 'bg-secondary text-primary'">
        <component :is="icon" class="size-4.5" />
      </span>
    </CardHeader>
    <CardContent>
      <p class="font-heading text-3xl font-bold tabular-nums">{{ value }}</p>
      <p v-if="hint" class="mt-1 text-xs text-muted-foreground">{{ hint }}</p>
    </CardContent>
  </Card>
</template>
