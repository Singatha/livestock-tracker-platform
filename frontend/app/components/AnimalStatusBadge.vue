<script setup lang="ts">
const props = defineProps<{ status: string; attention?: boolean }>()
const badgeClass = computed(() => props.attention ? 'border-amber-200 bg-amber-50 text-amber-800' : props.status === 'active' ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-border bg-muted text-muted-foreground')
</script>

<template><Badge variant="outline" class="capitalize" :class="badgeClass">{{ attention ? 'Needs attention' : status }}</Badge></template>
