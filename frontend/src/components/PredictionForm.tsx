import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface PredictionFormProps {
  onPredict: (
    track: string,
    drivers: string[],
    qualifyingPositions: Record<string, number>
  ) => void
  loading: boolean
  error: string | null
}

export default function PredictionForm({ onPredict, loading, error }: PredictionFormProps) {
  const [tracks, setTracks] = useState<string[]>([])
  const [drivers, setDrivers] = useState<string[]>([])
  const [selectedTrack, setSelectedTrack] = useState('')
  const [selectedDrivers, setSelectedDrivers] = useState<string[]>([])
  const [qualifyingPositions, setQualifyingPositions] = useState<Record<string, number>>({})

  useEffect(() => {
    // Fetch tracks and drivers from API
    const fetchData = async () => {
      try {
        const [tracksRes, driversRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/api/tracks`),
          axios.get(`${API_BASE_URL}/api/drivers`),
        ])
        setTracks(tracksRes.data)
        setDrivers(driversRes.data)
        setSelectedTrack(tracksRes.data[0] || '')
        setSelectedDrivers(driversRes.data.slice(0, 8))
      } catch (err) {
        console.error('Failed to fetch tracks/drivers:', err)
        // Fallback data
        setTracks(['Monaco', 'Silverstone', 'Spa-Francorchamps'])
        setDrivers(['VER', 'LEC', 'NOR', 'HAM', 'PER', 'SAI', 'RUS', 'ALO'])
        setSelectedTrack('Monaco')
        setSelectedDrivers(['VER', 'LEC', 'NOR', 'HAM', 'PER', 'SAI', 'RUS', 'ALO'])
      }
    }
    fetchData()
  }, [])

  useEffect(() => {
    // Initialize qualifying positions
    const initialPositions: Record<string, number> = {}
    selectedDrivers.forEach((driver, index) => {
      initialPositions[driver] = index + 1
    })
    setQualifyingPositions(initialPositions)
  }, [selectedDrivers])

  const handleDriverToggle = (driver: string) => {
    if (selectedDrivers.includes(driver)) {
      setSelectedDrivers(selectedDrivers.filter(d => d !== driver))
      const newPositions = { ...qualifyingPositions }
      delete newPositions[driver]
      setQualifyingPositions(newPositions)
    } else {
      setSelectedDrivers([...selectedDrivers, driver])
      setQualifyingPositions({
        ...qualifyingPositions,
        [driver]: selectedDrivers.length + 1,
      })
    }
  }

  const handlePositionChange = (driver: string, position: number) => {
    setQualifyingPositions({
      ...qualifyingPositions,
      [driver]: position,
    })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (selectedTrack && selectedDrivers.length > 0) {
      onPredict(selectedTrack, selectedDrivers, qualifyingPositions)
    }
  }

  return (
    <div className="bg-gray-800 rounded-lg shadow-xl p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Race Configuration</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Track Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Select Track
          </label>
          <select
            value={selectedTrack}
            onChange={(e) => setSelectedTrack(e.target.value)}
            className="w-full bg-gray-700 text-white rounded-lg px-4 py-2 border border-gray-600 focus:border-f1-red focus:outline-none"
          >
            {tracks.map((track) => (
              <option key={track} value={track}>
                {track}
              </option>
            ))}
          </select>
        </div>

        {/* Driver Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-3">
            Select Drivers ({selectedDrivers.length} selected)
          </label>
          <div className="grid grid-cols-4 gap-2 max-h-48 overflow-y-auto bg-gray-900 p-3 rounded-lg">
            {drivers.map((driver) => (
              <button
                key={driver}
                type="button"
                onClick={() => handleDriverToggle(driver)}
                className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                  selectedDrivers.includes(driver)
                    ? 'bg-f1-red text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {driver}
              </button>
            ))}
          </div>
        </div>

        {/* Qualifying Positions */}
        {selectedDrivers.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Qualifying Positions
            </label>
            <div className="space-y-2">
              {selectedDrivers.map((driver) => (
                <div key={driver} className="flex items-center gap-3">
                  <span className="text-white font-medium w-12">{driver}</span>
                  <input
                    type="number"
                    min="1"
                    max="20"
                    value={qualifyingPositions[driver] || 1}
                    onChange={(e) =>
                      handlePositionChange(driver, parseInt(e.target.value) || 1)
                    }
                    className="flex-1 bg-gray-700 text-white rounded px-3 py-2 border border-gray-600 focus:border-f1-red focus:outline-none"
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/30 border border-red-600 rounded-lg p-3">
            <p className="text-red-200 text-sm">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !selectedTrack || selectedDrivers.length === 0}
          className="w-full bg-f1-red hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-colors"
        >
          {loading ? 'Calculating...' : '🔮 Predict Race Winner'}
        </button>
      </form>
    </div>
  )
}

