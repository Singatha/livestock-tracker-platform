<script setup lang="ts">
import { Bell, CalendarCheck2, ChevronDown, LayoutDashboard, Menu, PawPrint, Plus, Settings } from '@lucide/vue'

const selectedFarmId = useCookie<string | null>('selected-farm-id', {
  default: () => null,
  sameSite: 'lax',
})

const route = useRoute()
const mobileOpen = ref(false)
const navigation = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Animals', to: '/animals', icon: PawPrint },
  { label: 'Tasks', to: '/tasks', icon: CalendarCheck2 },
]

function isActive(to: string) {
  return to === '/' ? route.path === '/' : route.path.startsWith(to)
}
</script>

<template>
  <div class="min-h-screen bg-background lg:grid lg:grid-cols-[16rem_1fr]">
    <aside class="hidden min-h-screen border-r border-sidebar-border bg-sidebar text-sidebar-foreground lg:sticky lg:top-0 lg:block lg:h-screen">
      <div class="flex h-full flex-col p-4">
        <NuxtLink class="flex items-center gap-3 px-2 py-3" to="/">
          <span class="grid size-9 place-items-center rounded-xl bg-white/10"><PawPrint class="size-5" /></span>
          <span><strong class="block font-heading text-lg">Flockwise</strong><small class="text-white/55">Livestock care</small></span>
        </NuxtLink>
        <nav class="mt-7 grid gap-1" aria-label="Primary navigation">
          <NuxtLink v-for="item in navigation" :key="item.to" :to="item.to" class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition-colors" :class="isActive(item.to) ? 'bg-sidebar-accent text-sidebar-accent-foreground' : 'text-white/70 hover:bg-white/5 hover:text-white'">
            <component :is="item.icon" class="size-4.5" />{{ item.label }}
          </NuxtLink>
        </nav>
        <div class="mt-auto rounded-xl border border-white/10 bg-white/5 p-3">
          <p class="text-xs font-semibold text-white/50">Active workspace</p>
          <p class="mt-1 truncate text-sm font-semibold">{{ selectedFarmId ? 'Farm selected' : 'No farm selected' }}</p>
        </div>
      </div>
    </aside>

    <div class="min-w-0">
      <header class="sticky top-0 z-30 flex h-16 items-center border-b bg-background/90 px-4 backdrop-blur sm:px-6 lg:px-8">
        <Sheet v-model:open="mobileOpen">
          <SheetTrigger as-child><Button class="lg:hidden" variant="ghost" size="icon" aria-label="Open navigation"><Menu /></Button></SheetTrigger>
          <SheetContent side="left" class="w-72 bg-sidebar text-sidebar-foreground">
            <SheetHeader><SheetTitle class="flex items-center gap-2 text-white"><PawPrint /> Flockwise</SheetTitle><SheetDescription class="text-white/55">Livestock care workspace</SheetDescription></SheetHeader>
            <nav class="mt-7 grid gap-1 px-4" aria-label="Mobile navigation">
              <NuxtLink v-for="item in navigation" :key="item.to" :to="item.to" class="flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-semibold" :class="isActive(item.to) ? 'bg-sidebar-accent text-white' : 'text-white/70'" @click="mobileOpen = false"><component :is="item.icon" class="size-4.5" />{{ item.label }}</NuxtLink>
            </nav>
          </SheetContent>
        </Sheet>
        <NuxtLink class="ml-2 font-heading font-bold lg:hidden" to="/">Flockwise</NuxtLink>
        <div class="ml-auto flex items-center gap-2">
          <Button variant="ghost" size="icon" aria-label="Notifications"><Bell /></Button>
          <DropdownMenu>
            <DropdownMenuTrigger as-child><Button variant="outline"><span class="hidden sm:inline">Quick add</span><Plus class="sm:hidden" /><ChevronDown class="hidden size-3.5 sm:block" /></Button></DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem as-child><NuxtLink to="/animals/new">Register animal</NuxtLink></DropdownMenuItem>
              <DropdownMenuItem as-child><NuxtLink to="/flocks/new">Create flock</NuxtLink></DropdownMenuItem>
              <DropdownMenuItem as-child><NuxtLink to="/tasks/new">Schedule task</NuxtLink></DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem as-child><NuxtLink to="/farms/new"><Settings /> Create farm</NuxtLink></DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>
      <main class="page-container"><slot /></main>
    </div>
  </div>
</template>
