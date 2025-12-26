import { useState, useEffect } from 'react'
import axios from 'axios'
import PredictionForm from './components/PredictionForm'
import PredictionResults from './components/PredictionResults'
import Header from './components/Header'
import { PredictionResult } from './types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [predictions, setPredictions] = useState<PredictionResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [apiHealth, setApiHealth] = useState<boolean | null>(null)

  useEffect(() => {
    // Check API health on mount
    checkApiHealth()
  }, [])

  const checkApiHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`)
      setApiHealth(response.data.model_loaded)
    } catch (err) {
      setApiHealth(false)
    }
  }

  const handlePredict = async (
    track: string,
    drivers: string[],
    qualifyingPositions: Record<string, number>
  ) => {
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_BASE_URL}/api/predict`, {
        track,
        drivers,
        qualifying_positions: qualifyingPositions,
      })

      setPredictions(response.data.predictions)
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        'Failed to get predictions. Make sure the API is running and models are trained.'
      )
      setPredictions([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-f1-dark via-gray-900 to-f1-dark">
      <Header apiHealth={apiHealth} />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
          <div className="lg:sticky lg:top-8 lg:h-fit">
            <PredictionForm 
              onPredict={handlePredict} 
              loading={loading}
              error={error}
            />
          </div>
          
          <div>
            <PredictionResults predictions={predictions} loading={loading} />
          </div>
        </div>
      </main>
    </div>
  )
}

export default App

