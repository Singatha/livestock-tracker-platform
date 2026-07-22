<script setup lang="ts">
import { BarChart3, Bell, CalendarCheck2, ChevronDown, LayoutDashboard, Menu, PawPrint, Plus, Settings, Wheat } from '@lucide/vue'
import type { Notification, Paginated } from '~/types/api'

const selectedFarmId = useCookie<string | null>('selected-farm-id', {
  default: () => null,
  sameSite: 'lax',
})

const route = useRoute()
const mobileOpen = ref(false)
const notifications = ref<Notification[]>([])
const { request } = useApi()
const unreadCount = computed(() => notifications.value.filter(item => !item.is_read).length)
const navigation = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Animals', to: '/animals', icon: PawPrint },
  { label: 'Tasks', to: '/tasks', icon: CalendarCheck2 },
  { label: 'Nutrition', to: '/nutrition', icon: Wheat },
  { label: 'Reports', to: '/reports', icon: BarChart3 },
]

function isActive(to: string) {
  return to === '/' ? route.path === '/' : route.path.startsWith(to)
}

async function loadNotifications() {
  if (!selectedFarmId.value) return
  try {
    notifications.value = (await request<Paginated<Notification>>('/notifications/?unread=true')).results.slice(0, 5)
  } catch {
    notifications.value = []
  }
}

async function openNotification(notification: Notification) {
  await request(`/notifications/${notification.id}/mark-read/`, { method: 'POST', body: {} })
  notifications.value = notifications.value.filter(item => item.id !== notification.id)
  await navigateTo(notification.link)
}

onMounted(loadNotifications)
watch(selectedFarmId, loadNotifications)
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
          <DropdownMenu>
            <DropdownMenuTrigger as-child><Button class="relative" variant="ghost" size="icon" aria-label="Notifications"><Bell /><span v-if="unreadCount" class="absolute right-0.5 top-0.5 grid min-w-4 place-items-center rounded-full bg-destructive px-1 text-[10px] font-bold leading-4 text-white">{{ unreadCount > 9 ? '9+' : unreadCount }}</span></Button></DropdownMenuTrigger>
            <DropdownMenuContent align="end" class="w-80">
              <DropdownMenuLabel class="flex items-center justify-between">Notifications <Badge v-if="unreadCount" variant="secondary">{{ unreadCount }} new</Badge></DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem v-for="notification in notifications" :key="notification.id" class="items-start py-3" @select="openNotification(notification)"><span class="grid gap-1"><strong class="text-sm">{{ notification.title }}</strong><small class="text-muted-foreground">{{ notification.message }}</small></span></DropdownMenuItem>
              <DropdownMenuItem v-if="!notifications.length" disabled class="py-5 text-center">You’re all caught up</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem as-child><NuxtLink class="justify-center font-semibold" to="/notifications">View all notifications</NuxtLink></DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
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
