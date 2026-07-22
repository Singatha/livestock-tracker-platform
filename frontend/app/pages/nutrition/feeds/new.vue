<script setup lang="ts">
import type { Feed } from '~/types/api'

const { request, selectedFarmId } = useApi()
const submitting = ref(false)
const errorMessage = ref('')
const form = reactive({ name: '', category: 'forage', suitability: 'both', unit: 'kg', quantity_on_hand: '', reorder_level: '', unit_cost: '', notes: '' })

async function submit() {
  if (!selectedFarmId.value) { errorMessage.value = 'Select or create a farm first.'; return }
  submitting.value = true; errorMessage.value = ''
  try {
    await request<Feed>('/nutrition/feeds/', { method: 'POST', body: { ...form, quantity_on_hand: form.quantity_on_hand || '0', reorder_level: form.reorder_level || '0', unit_cost: form.unit_cost || null } })
    await navigateTo('/nutrition')
  } catch { errorMessage.value = 'The feed item could not be saved. Check its name and quantities.' } finally { submitting.value = false }
}
</script>

<template><section class="form-card wide"><p class="eyebrow">Feed inventory</p><h1>Add feed</h1><p>Record stock in one consistent unit for reliable totals.</p><form class="form-grid" @submit.prevent="submit"><label>Feed name <input v-model="form.name" maxlength="200" required autofocus></label><label>Category <select v-model="form.category"><option value="forage">Forage</option><option value="concentrate">Concentrate</option><option value="mineral">Mineral</option><option value="supplement">Supplement</option><option value="other">Other</option></select></label><label>Suitable for <select v-model="form.suitability"><option value="both">Sheep and goats</option><option value="sheep">Sheep only</option><option value="goat">Goats only</option></select></label><label>Stock unit <input v-model="form.unit" maxlength="20" required></label><label>Quantity on hand <input v-model="form.quantity_on_hand" type="number" min="0" step="0.01" inputmode="decimal"></label><label>Low-stock level <input v-model="form.reorder_level" type="number" min="0" step="0.01" inputmode="decimal"></label><label>Cost per unit <input v-model="form.unit_cost" type="number" min="0" step="0.01" inputmode="decimal"></label><label class="full">Notes <textarea v-model="form.notes" rows="3" /></label><p v-if="errorMessage" class="error full" role="alert">{{ errorMessage }}</p><div class="actions full"><Button as-child variant="ghost"><NuxtLink to="/nutrition">Cancel</NuxtLink></Button><Button type="submit" :disabled="submitting">{{ submitting ? 'Saving…' : 'Save feed' }}</Button></div></form></section></template>
