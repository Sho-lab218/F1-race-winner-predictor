interface HeaderProps {
  apiHealth: boolean | null
}

export default function Header({ apiHealth }: HeaderProps) {
  return (
    <header className="bg-f1-red text-white shadow-lg">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">🏎️ F1 Race Winner Predictor</h1>
            <p className="text-red-100 mt-1">
              Probabilistic ML predictions for Formula 1 races
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            {apiHealth !== null && (
              <div className="flex items-center gap-2">
                <div
                  className={`w-3 h-3 rounded-full ${
                    apiHealth ? 'bg-green-400' : 'bg-red-400'
                  }`}
                />
                <span className="text-sm">
                  {apiHealth ? 'API Connected' : 'API Disconnected'}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

