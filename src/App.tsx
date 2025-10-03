import { useState } from 'react'
import './App.css'

interface Winner {
  rank: number
  name: string
  score: number
}

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [topX, setTopX] = useState(5)
  const [results, setResults] = useState<{ballots_count: number, candidates_count: number, winners: Winner[]} | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const readFileAsText = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = reject
      reader.readAsText(file)
    })
  }

  const parseCSV = (csvText: string) => {
    const lines = csvText.split('\n').filter(line => line.trim())
    if (lines.length < 2) throw new Error('CSV must have at least a header and one data row')
    
    const headers = lines[0].split(',').map(h => h.trim())
    const rankHeaders = headers.filter(h => /^\s*Rank\s+\d+\s*$/i.test(h)).sort((a, b) => {
      const ai = parseInt(a.replace(/[^0-9]/g, ''), 10) || 9999
      const bi = parseInt(b.replace(/[^0-9]/g, ''), 10) || 9999
      return ai - bi
    })
    
    const ballots: string[][] = []
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim().replace(/^"|"$/g, ''))
      const row: {[key: string]: string} = {}
      headers.forEach((header, idx) => {
        row[header] = values[idx] || ''
      })
      
      const choices: string[] = []
      for (const header of rankHeaders) {
        const value = (row[header] || '').trim()
        if (value) choices.push(value)
      }
      if (choices.length > 0) ballots.push(choices)
    }
    
    return ballots
  }

  const computeBordaScores = (ballots: string[][]) => {
    const scores = new Map<string, number>()
    for (const ranked of ballots) {
      const k = ranked.length
      ranked.forEach((candidate, idx) => {
        const points = k - idx
        scores.set(candidate, (scores.get(candidate) || 0) + points)
      })
    }
    return scores
  }

  const getTopX = (scores: Map<string, number>, x: number) => {
    const arr = Array.from(scores.entries())
    arr.sort((a, b) => {
      if (b[1] !== a[1]) return b[1] - a[1]
      return a[0].localeCompare(b[0])
    })
    return arr.slice(0, x)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const csvText = await readFileAsText(file)
      const ballots = parseCSV(csvText)
      const scores = computeBordaScores(ballots)
      const winners = getTopX(scores, topX)

      setResults({
        ballots_count: ballots.length,
        candidates_count: scores.size,
        winners: winners.map(([name, score], idx) => ({
          rank: idx + 1,
          name,
          score
        }))
      })
    } catch (err) {
      setError(`Error processing CSV: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <div className="card">
        <h1>Ranked Ballot Calculator</h1>
        
        <form onSubmit={handleSubmit} className="form">
          <div className="form-group">
            <label htmlFor="csv">CSV file</label>
            <input
              type="file"
              id="csv"
              accept=".csv"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="top">Top X to display</label>
            <input
              type="number"
              id="top"
              min="1"
              value={topX}
              onChange={(e) => setTopX(parseInt(e.target.value) || 5)}
              required
            />
          </div>
          
          <button type="submit" disabled={loading || !file}>
            {loading ? 'Calculating...' : 'Calculate'}
          </button>
        </form>

        <div className="info">
          <p>Detects Rank 1..N columns automatically (no fixed length required).</p>
          <p>Method: Borda (Rank 1 gets k points, Rank k gets 1 point).</p>
        </div>

        {error && (
          <div className="error">
            <p>{error}</p>
          </div>
        )}

        {results && (
          <div className="results">
            <h2>Results</h2>
            <p>Ballots: {results.ballots_count} | Candidates: {results.candidates_count}</p>
            
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Candidate</th>
                  <th>Score</th>
                </tr>
              </thead>
              <tbody>
                {results.winners.map((winner) => (
                  <tr key={winner.rank}>
                    <td>{winner.rank}</td>
                    <td>{winner.name}</td>
                    <td>{winner.score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default App