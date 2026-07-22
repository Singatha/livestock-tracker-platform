<script setup lang="ts">
import type { BirthRecord, BreedingRecord, Paginated } from '~/types/api'

const { request, selectedFarmId } = useApi()
const breedings = ref<BreedingRecord[]>([])
const births = ref<BirthRecord[]>([])
const loading = ref(true)
const errorMessage = ref('')

async function load() {
  if (!selectedFarmId.value) return
  try {
    const [breedingResponse, birthResponse] = await Promise.all([
      request<Paginated<BreedingRecord>>('/reproduction/breedings/'),
      request<Paginated<BirthRecord>>('/reproduction/births/'),
    ])
    breedings.value = breedingResponse.results
    births.value = birthResponse.results
  } catch { errorMessage.value = 'Reproduction records could not be loaded.' }
  finally { loading.value = false }
}

onMounted(load)
watch(selectedFarmId, load)
</script>

<template>
  <section>
    <div class="page-heading"><div><p class="eyebrow">Herd growth</p><h1>Breeding and births</h1><p>Track services, pregnancy outcomes, and lambing or kidding records.</p></div><div class="actions wrap"><Button as-child variant="outline"><NuxtLink to="/reproduction/births/new">Record birth</NuxtLink></Button><Button as-child><NuxtLink to="/reproduction/breedings/new">Record breeding</NuxtLink></Button></div></div>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <div v-if="loading" class="grid gap-4"><Skeleton class="h-32" /><Skeleton class="h-32" /></div>
    <template v-else>
      <Card><CardHeader><CardTitle>Breeding register</CardTitle><CardDescription>Expected dates use 147 days for sheep and 150 days for goats unless overridden.</CardDescription></CardHeader><CardContent><Table class="min-w-[44rem]"><TableHeader><TableRow><TableHead class="w-[22%] pl-4">Dam</TableHead><TableHead class="w-[22%]">Sire</TableHead><TableHead class="w-[18%]">Breeding date</TableHead><TableHead class="w-[20%]">Expected birth</TableHead><TableHead class="pr-4 text-right">Status</TableHead></TableRow></TableHeader><TableBody><TableRow v-for="item in breedings" :key="item.id"><TableCell class="pl-4 font-semibold">{{ item.dam_name }}</TableCell><TableCell class="text-muted-foreground">{{ item.sire_name || 'Not recorded' }}</TableCell><TableCell class="whitespace-nowrap">{{ new Date(item.breeding_date).toLocaleDateString() }}</TableCell><TableCell class="whitespace-nowrap">{{ new Date(item.expected_birth_date).toLocaleDateString() }}</TableCell><TableCell class="pr-4 text-right"><NuxtLink :to="`/reproduction/breedings/${item.id}`"><Badge variant="secondary" class="capitalize">{{ item.status.replaceAll('_', ' ') }}</Badge></NuxtLink></TableCell></TableRow><TableRow v-if="!breedings.length"><TableCell colspan="5" class="h-32 text-center text-muted-foreground">No breeding records yet.</TableCell></TableRow></TableBody></Table></CardContent></Card>
      <Card class="mt-6"><CardHeader><CardTitle>Recent births</CardTitle><CardDescription>Recorded lambing and kidding outcomes for this farm.</CardDescription></CardHeader><CardContent><Table class="min-w-[38rem]"><TableHeader><TableRow><TableHead class="w-[30%] pl-4">Dam</TableHead><TableHead class="w-[25%]">Birth date</TableHead><TableHead class="text-right">Total born</TableHead><TableHead class="text-right">Born alive</TableHead><TableHead class="pr-4 text-right">Stillborn</TableHead></TableRow></TableHeader><TableBody><TableRow v-for="item in births" :key="item.id"><TableCell class="pl-4 font-semibold">{{ item.dam_name }}</TableCell><TableCell class="whitespace-nowrap">{{ new Date(item.birth_date).toLocaleDateString() }}</TableCell><TableCell class="text-right font-semibold tabular-nums">{{ item.total_born }}</TableCell><TableCell class="text-right tabular-nums text-emerald-700">{{ item.born_alive }}</TableCell><TableCell class="pr-4 text-right tabular-nums" :class="item.stillborn ? 'text-destructive' : 'text-muted-foreground'">{{ item.stillborn }}</TableCell></TableRow><TableRow v-if="!births.length"><TableCell colspan="5" class="h-32 text-center text-muted-foreground">No births recorded yet.</TableCell></TableRow></TableBody></Table></CardContent></Card>
    </template>
  </section>
</template>
