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
  status: 'active' | 'sold' | 'deceased' | 'missing'
  needs_attention: boolean
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

export interface TimelineEvent {
  id: string
  kind: 'observation' | 'treatment' | 'task'
  date: string
  title: string
  details: string
  status: string
}
