<script setup lang="ts">
import { Activity, BarChart3, Bell, CalendarCheck2, ChevronDown, Files, HeartHandshake, LayoutDashboard, LogOut, Menu, PawPrint, Pill, Plus, Scale, Settings, Upload, UserCircle, Wheat } from '@lucide/vue'
import type { Farm, Notification, Paginated, User } from '~/types/api'

const selectedFarmId = useCookie<string | null>('selected-farm-id', {
  default: () => null,
  sameSite: 'lax',
})

const route = useRoute()
const mobileOpen = ref(false)
const notifications = ref<Notification[]>([])
const farms = ref<Farm[]>([])
const currentUser = ref<User | null>(null)
const signingOut = ref(false)
const { request, resetCsrfToken } = useApi()
const toast = useToast()
const unreadCount = computed(() => notifications.value.filter(item => !item.is_read).length)
const currentFarm = computed(() => farms.value.find(farm => farm.id === selectedFarmId.value))
const navigation = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Animals', to: '/animals', icon: PawPrint },
  { label: 'Tasks', to: '/tasks', icon: CalendarCheck2 },
  { label: 'Breeding', to: '/reproduction', icon: HeartHandshake },
  { label: 'Growth', to: '/growth', icon: Scale },
  { label: 'Medicine', to: '/medicine', icon: Pill },
  { label: 'Nutrition', to: '/nutrition', icon: Wheat },
  { label: 'Reports', to: '/reports', icon: BarChart3 },
  { label: 'Documents', to: '/documents', icon: Files },
  { label: 'Team', to: '/settings/team', icon: Settings },
  { label: 'Imports', to: '/settings/imports', icon: Upload },
  { label: 'Activity', to: '/settings/activity', icon: Activity },
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

async function loadFarms() {
  try {
    farms.value = (await request<Paginated<Farm>>('/farms/')).results
    if (!currentFarm.value && farms.value[0]) selectedFarmId.value = farms.value[0].id
  } catch {
    farms.value = []
  }
}

async function loadCurrentUser() {
  try {
    currentUser.value = await request<User>('/auth/me/')
  } catch {
    await navigateTo('/login')
  }
}

async function signOut() {
  signingOut.value = true
  try {
    await request('/auth/logout/', { method: 'POST' })
    selectedFarmId.value = null
    resetCsrfToken()
    toast.success('Signed out', 'Your session has ended safely.')
    await navigateTo('/login')
  } catch {
    toast.error('Could not sign out', 'Please try again.')
  } finally {
    signingOut.value = false
  }
}

function selectFarm(farmId: string) {
  selectedFarmId.value = farmId
}

async function openNotification(notification: Notification) {
  await request(`/notifications/${notification.id}/mark-read/`, { method: 'POST', body: {} })
  notifications.value = notifications.value.filter(item => item.id !== notification.id)
  await navigateTo(notification.link)
}

onMounted(async () => {
  await loadCurrentUser()
  await loadFarms()
  await loadNotifications()
})
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
          <label for="desktop-farm" class="text-xs font-semibold text-white/50">Active farm</label>
          <select v-if="farms.length" id="desktop-farm" class="mt-2 h-9 border-white/10 bg-white/5 px-2 text-sm font-semibold text-white shadow-none focus-visible:border-white/30 focus-visible:ring-white/10" :value="selectedFarmId || ''" @change="selectFarm(($event.target as HTMLSelectElement).value)"><option v-for="farm in farms" :key="farm.id" class="bg-sidebar text-white" :value="farm.id">{{ farm.name }}</option></select>
          <p v-else class="mt-2 truncate text-sm font-semibold">No farm selected</p>
          <p v-if="currentFarm" class="mt-2 text-xs capitalize text-white/50">{{ currentFarm.role }} access</p>
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
              <DropdownMenuItem as-child><NuxtLink to="/reproduction/breedings/new">Record breeding</NuxtLink></DropdownMenuItem>
              <DropdownMenuItem as-child><NuxtLink to="/growth/new">Record weight</NuxtLink></DropdownMenuItem>
              <DropdownMenuItem as-child><NuxtLink to="/medicine/courses/new">Start treatment course</NuxtLink></DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem as-child><NuxtLink to="/farms/new"><Settings /> Create farm</NuxtLink></DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <DropdownMenu>
            <DropdownMenuTrigger as-child><Button variant="ghost" class="gap-2 px-2 sm:px-3"><UserCircle class="size-5" /><span class="hidden max-w-32 truncate sm:inline">{{ currentUser?.first_name || currentUser?.username || 'Account' }}</span><ChevronDown class="hidden size-3.5 sm:block" /></Button></DropdownMenuTrigger>
            <DropdownMenuContent align="end" class="w-56">
              <DropdownMenuLabel><span class="block truncate">{{ currentUser ? `${currentUser.first_name} ${currentUser.last_name}`.trim() || currentUser.username : 'Account' }}</span><span class="block truncate text-xs font-normal text-muted-foreground">{{ currentUser?.email || currentUser?.username }}</span></DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem variant="destructive" :disabled="signingOut" @select="signOut"><LogOut />{{ signingOut ? 'Signing out…' : 'Sign out' }}</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>
      <main class="page-container"><slot /></main>
    </div>
  </div>
</template>
