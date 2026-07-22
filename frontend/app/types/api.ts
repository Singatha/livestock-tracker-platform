export interface Farm {
  id: string
  name: string
  role: 'owner' | 'manager' | 'worker' | 'viewer'
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface DashboardSummary {
  total: number
  sheep: number
  goats: number
  needs_attention: number
  open_health_concerns: number
  overdue_tasks: number
  due_next_7_days: number
}

export interface Flock {
  id: string
  name: string
  description: string
}

export interface Animal {
  id: string
  ear_tag: string
  name: string
  species: 'sheep' | 'goat'
  breed: string
  sex: 'female' | 'male' | 'unknown'
  flock: string | null
  date_of_birth: string | null
  status: 'active' | 'sold' | 'deceased' | 'missing'
  needs_attention: boolean
  notes: string
}

export interface AnimalLifecycleEvent {
  id: string
  event_type: 'registered' | 'status_changed' | 'flock_transferred'
  effective_date: string
  from_status: Animal['status'] | ''
  to_status: Animal['status'] | ''
  from_flock: string | null
  from_flock_name: string | null
  to_flock: string | null
  to_flock_name: string | null
  reason: string
  recorded_by_name: string
  created_at: string
}

export interface HealthObservation {
  id: string
  animal: string
  observed_at: string
  category: string
  severity: 'low' | 'medium' | 'high' | 'urgent'
  summary: string
  notes: string
  is_resolved: boolean
}

export interface Treatment {
  id: string
  animal: string
  administered_at: string
  product: string
  dosage: string
  route: string
  reason: string
  withdrawal_end_date: string | null
  follow_up_date: string | null
}

export interface HusbandryTask {
  id: string
  animal: string | null
  flock: string | null
  task_type: string
  title: string
  due_date: string
  status: 'scheduled' | 'completed' | 'cancelled'
  recurrence_days: number | null
  reminder_days_before: number
  notes: string
}

export interface Notification {
  id: string
  kind: 'task_due' | 'task_overdue'
  title: string
  message: string
  link: string
  is_read: boolean
  read_at: string | null
  created_at: string
}

export interface Feed {
  id: string
  name: string
  category: 'forage' | 'concentrate' | 'mineral' | 'supplement' | 'other'
  suitability: 'sheep' | 'goat' | 'both'
  unit: string
  quantity_on_hand: string
  reorder_level: string
  unit_cost: string | null
  notes: string
  is_low_stock: boolean
}

export interface FeedingPlanItem {
  id: string
  feed: string
  feed_name: string
  unit: string
  quantity_per_animal: string
  feeding_time: string
}

export interface FeedingPlan {
  id: string
  flock: string
  flock_name: string
  name: string
  life_stage: string
  start_date: string
  end_date: string | null
  is_active: boolean
  notes: string
  items: FeedingPlanItem[]
  compatibility_warnings: string[]
}

export interface ReportSummary {
  animals: number
  active_animals: number
  needs_attention: number
  health_observations: number
  open_health_concerns: number
  treatments: number
  completed_tasks: number
  overdue_tasks: number
  low_stock_feeds: number
  inventory_value: string
}

export interface MonthlyActivity {
  month: string
  animals_registered: number
  health_observations: number
  tasks_completed: number
}

export interface TimelineEvent {
  id: string
  kind: 'observation' | 'treatment' | 'task' | 'lifecycle'
  date: string
  title: string
  details: string
  status: string
}
