<script setup lang="ts">
import { AlertTriangle, Pill, Plus } from '@lucide/vue'
import type { MedicineBatch, MedicineProduct, Paginated, TreatmentCourse } from '~/types/api'

const { request, selectedFarmId } = useApi()
const products = ref<MedicineProduct[]>([])
const batches = ref<MedicineBatch[]>([])
const courses = ref<TreatmentCourse[]>([])
const loading = ref(true)
const errorMessage = ref('')
async function load() {
  if (!selectedFarmId.value) return
  try {
    const [p, b, c] = await Promise.all([request<Paginated<MedicineProduct>>('/medicine/products/'), request<Paginated<MedicineBatch>>('/medicine/batches/'), request<Paginated<TreatmentCourse>>('/medicine/courses/?status=active')])
    products.value = p.results; batches.value = b.results; courses.value = c.results
  } catch { errorMessage.value = 'Medicine records could not be loaded.' }
  finally { loading.value = false }
}
onMounted(load); watch(selectedFarmId, load)
</script>

<template><section><div class="page-heading"><div><p class="eyebrow">Clinical inventory</p><h1>Medicine and treatment courses</h1><p>Monitor stock, batches, expiry dates, doses, and withdrawal periods.</p></div><div class="actions wrap"><Button as-child variant="outline"><NuxtLink to="/medicine/products/new"><Plus /> Add product</NuxtLink></Button><Button as-child variant="outline"><NuxtLink to="/medicine/batches/new">Add batch</NuxtLink></Button><Button as-child><NuxtLink to="/medicine/courses/new"><Pill /> Start course</NuxtLink></Button></div></div><p v-if="errorMessage" class="error">{{ errorMessage }}</p><div v-if="loading" class="grid gap-4"><Skeleton class="h-32" /><Skeleton class="h-32" /></div><template v-else><Card><CardHeader><CardTitle>Products</CardTitle><CardDescription>Stock totals combine all batches.</CardDescription></CardHeader><CardContent><Table v-if="products.length" class="min-w-[42rem]"><TableHeader><TableRow><TableHead class="w-[30%] pl-4">Product</TableHead><TableHead class="w-[30%]">Active ingredient</TableHead><TableHead class="w-[20%] text-right">Stock on hand</TableHead><TableHead class="w-[20%] pr-4 text-right">Reorder level</TableHead></TableRow></TableHeader><TableBody><TableRow v-for="item in products" :key="item.id"><TableCell class="pl-4 font-semibold">{{ item.name }}</TableCell><TableCell class="text-muted-foreground">{{ item.active_ingredient || 'Not recorded' }}</TableCell><TableCell class="text-right tabular-nums"><span class="inline-flex items-center justify-end gap-2"><Badge v-if="item.is_low_stock" variant="destructive">Low</Badge><strong>{{ item.total_quantity }} {{ item.stock_unit }}</strong></span></TableCell><TableCell class="pr-4 text-right tabular-nums">{{ item.reorder_level }} {{ item.stock_unit }}</TableCell></TableRow></TableBody></Table><p v-else class="empty-row">No medicine products yet.</p></CardContent></Card><div class="mt-6 grid gap-6 xl:grid-cols-2"><Card><CardHeader><CardTitle>Batches</CardTitle><CardDescription>Expired batches cannot be administered.</CardDescription></CardHeader><CardContent><div v-for="item in batches" :key="item.id" class="flex items-center justify-between border-b py-3"><span><strong class="block">{{ item.product_name }}</strong><small>{{ item.batch_number }} · expires {{ item.expiry_date }}</small></span><span class="text-right"><strong>{{ item.quantity_on_hand }} {{ item.stock_unit }}</strong><Badge v-if="item.is_expired" variant="destructive" class="ml-2">Expired</Badge></span></div><p v-if="!batches.length" class="empty-row">No batches yet.</p></CardContent></Card><Card><CardHeader><CardTitle>Active courses</CardTitle><CardDescription>Dose progress and treatment status.</CardDescription></CardHeader><CardContent><NuxtLink v-for="item in courses" :key="item.id" :to="`/medicine/courses/${item.id}`" class="flex items-center justify-between border-b py-3 hover:text-primary"><span><strong class="block">{{ item.animal_ear_tag }} · {{ item.product_name }}</strong><small>{{ item.reason }}</small></span><span>{{ item.doses_administered }}/{{ item.planned_doses }} doses</span></NuxtLink><p v-if="!courses.length" class="empty-row">No active treatment courses.</p></CardContent></Card></div></template></section></template>
