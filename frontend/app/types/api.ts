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
