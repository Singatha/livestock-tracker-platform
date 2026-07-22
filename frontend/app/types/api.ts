export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
}

export interface Farm {
  id: string
  name: string
  role: 'owner' | 'manager' | 'worker' | 'viewer'
}

export interface FarmMembership {
  id: string
  user: string
  email: string
  name: string
  role: 'owner' | 'manager' | 'worker' | 'viewer'
  is_active: boolean
  created_at: string
}

export interface FarmInvitation {
  id: string
  email: string
  role: FarmMembership['role']
  token: string
  status: 'pending' | 'accepted' | 'revoked'
  expires_at: string
  is_expired: boolean
  created_at: string
}

export interface FarmMembershipAudit {
  id: string
  event_type: 'invited' | 'accepted' | 'role_changed' | 'deactivated' | 'reactivated' | 'invitation_revoked'
  subject_email: string
  from_role: FarmMembership['role'] | ''
  to_role: FarmMembership['role'] | ''
  actor_name: string
  created_at: string
}

export interface ImportError {
  row: number
  errors: Record<string, unknown> | string
}

export interface ImportJob {
  id: string
  kind: 'flocks' | 'animals' | 'weights' | 'medicine_batches'
  mode: 'all_or_nothing' | 'partial'
  status: 'previewed' | 'completed' | 'failed'
  original_filename: string
  rows_total: number
  rows_succeeded: number
  rows_failed: number
  valid_rows: number
  errors: ImportError[]
  created_at: string
  completed_at: string | null
}

export interface AuditEvent {
  id: string
  action: 'created' | 'updated' | 'deleted'
  resource_type: string
  resource_id: string
  resource_name: string
  animal_id: string | null
  changes: Record<string, unknown>
  actor_name: string
  created_at: string
}

export interface Attachment {
  id: string
  animal: string | null
  category: 'photo' | 'veterinary' | 'prescription' | 'lab_result' | 'certificate' | 'invoice' | 'other'
  title: string
  description: string
  original_filename: string
  content_type: string
  size_bytes: number
  uploaded_by_name: string
  created_at: string
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
  expected_births_next_30_days: number
  overdue_expected_births: number
  animals_losing_weight: number
  active_treatment_courses: number
  low_stock_medicines: number
  expiring_medicine_batches: number
  animals_under_withdrawal: number
}

export interface MedicineProduct {
  id: string
  name: string
  active_ingredient: string
  concentration: string
  stock_unit: string
  reorder_level: string
  meat_withdrawal_days: number
  milk_withdrawal_days: number
  instructions: string
  total_quantity: string
  is_low_stock: boolean
}

export interface MedicineBatch {
  id: string
  product: string
  product_name: string
  batch_number: string
  expiry_date: string
  quantity_on_hand: string
  stock_unit: string
  is_expired: boolean
}

export interface TreatmentCourse {
  id: string
  animal: string
  animal_ear_tag: string
  product: string
  product_name: string
  reason: string
  dosage: string
  route: string
  started_on: string
  planned_doses: number
  frequency_hours: number | null
  status: 'active' | 'completed' | 'cancelled'
  meat_withdrawal_end_date: string | null
  milk_withdrawal_end_date: string | null
  notes: string
  doses_administered: number
}

export interface DoseAdministration {
  id: string
  course: string
  batch: string
  batch_number: string
  product_name: string
  administered_at: string
  quantity_used: string
  notes: string
}

export interface WeightMeasurement {
  id: string
  animal: string
  animal_ear_tag: string
  measured_on: string
  weight_kg: string
  body_condition_score: string | null
  notes: string
}

export interface AnimalGrowthSummary {
  animal: string
  ear_tag: string
  name: string
  flock_name: string | null
  latest_weight_kg: string
  latest_measured_on: string
  previous_weight_kg: string | null
  change_kg: string | null
  average_daily_gain_kg: string | null
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
  kind: 'observation' | 'treatment' | 'task' | 'lifecycle' | 'reproduction' | 'growth' | 'medicine'
  date: string
  title: string
  details: string
  status: string
}

export interface BreedingRecord {
  id: string
  dam: string
  dam_name: string
  sire: string | null
  sire_name: string | null
  breeding_date: string
  expected_birth_date: string
  method: 'natural' | 'artificial' | 'unknown'
  status: 'exposed' | 'confirmed' | 'not_pregnant' | 'completed'
  pregnancy_checked_on: string | null
  notes: string
}

export interface BirthRecord {
  id: string
  breeding: string
  dam: string
  dam_name: string
  birth_date: string
  total_born: number
  born_alive: number
  stillborn: number
  notes: string
}
