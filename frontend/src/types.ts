export interface PredictionResult {
  driver: string
  track: string
  qualifying_position: number
  win_probability: number
}

export interface RacePredictionRequest {
  track: string
  drivers: string[]
  qualifying_positions: Record<string, number>
  assumptions?: Record<string, any>
}

export interface RacePredictionResponse {
  predictions: PredictionResult[]
  message: string
}

export interface HealthResponse {
  status: string
  model_loaded: boolean
  model_name?: string
}

