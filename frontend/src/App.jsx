import React, { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export default function App() {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [file, setFile] = useState(null)

  async function submitText(e) {
    e.preventDefault()
    const form = new FormData()
    form.append('text', text)
    const res = await fetch(`${API_BASE}/predict/text`, { method: 'POST', body: form })
    const json = await res.json()
    setResult(json)
  }

  async function submitImage(e) {
    e.preventDefault()
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    const res = await fetch(`${API_BASE}/predict/image`, { method: 'POST', body: form })
    const json = await res.json()
    setResult(json)
  }

  async function factcheck(e) {
    e.preventDefault()
    const form = new FormData()
    form.append('text', text)
    const res = await fetch(`${API_BASE}/factcheck/text`, { method: 'POST', body: form })
    const json = await res.json()
    setResult(json)
  }

  const renderFactCheck = () => {
    if (!result?.claims) {
      return <pre className="bg-gray-50 p-3 mt-2 rounded-md shadow-inner overflow-auto text-sm">{result ? JSON.stringify(result, null, 2) : 'No result yet'}</pre>
    }

    return (
      <div className="space-y-4 mt-2">
        {result.claims.map((claim, index) => (
          <div key={index} className="rounded-lg border border-slate-200 p-4 bg-slate-50">
            <div className="flex flex-col gap-3 mb-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm text-slate-500">Claim</p>
                <p className="text-base font-semibold text-slate-800">{claim.claim}</p>
              </div>
              <div className="text-right">
                <p className="text-xs uppercase tracking-wide text-slate-500">Verdict</p>
                <p className={`mt-1 font-semibold ${claim.verdict === 'Likely true' ? 'text-emerald-600' : claim.verdict === 'Likely false' ? 'text-rose-600' : 'text-amber-600'}`}>
                  {claim.verdict || 'Unknown'}
                </p>
              </div>
            </div>
            {claim.support_words?.length ? (
              <p className="text-sm text-slate-600 mb-3">
                Supported words: <span className="font-medium text-slate-800">{claim.support_words.join(', ')}</span>
              </p>
            ) : null}
            <div className="space-y-2">
              {claim.top_matches.length > 0 ? (
                claim.top_matches.map((match, matchIndex) => (
                  <div key={matchIndex} className="rounded-md bg-white p-3 border border-slate-200">
                    {match.title ? <p className="text-sm font-semibold text-slate-900">{match.title}</p> : null}
                    <p className="text-sm text-slate-700">{match.snippet}</p>
                    {match.url ? (
                      <a className="text-indigo-600 hover:text-indigo-700 text-sm" href={match.url} target="_blank" rel="noreferrer">Open Wikipedia</a>
                    ) : null}
                    <p className="text-xs text-slate-500">Score: {match.score?.toFixed(2)}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-600">No matches found for this claim.</p>
              )}
            </div>
            {claim.note ? <p className="text-xs text-slate-500 mt-2">{claim.note}</p> : null}
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-100 p-6">
      <div className="max-w-4xl mx-auto bg-white/80 backdrop-blur-md shadow-lg rounded-xl p-8 border border-gray-100">
        <header className="flex items-center gap-4 mb-6">
          <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-pink-500 rounded-md flex items-center justify-center text-white font-bold">FN</div>
          <div>
            <h1 className="text-2xl font-extrabold">Fake News Detection</h1>
            <p className="text-sm text-gray-500">Quickly analyze text or image content and check claims.</p>
          </div>
        </header>

        <form onSubmit={submitText} className="mb-4">
          <label className="block text-sm font-medium mb-1">Enter text</label>
          <textarea className="w-full border p-3 mb-2 rounded-md shadow-sm" value={text} onChange={e => setText(e.target.value)} rows={5} />
          <div className="flex gap-3">
            <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md shadow" type="submit">Analyze Text</button>
            <button className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md shadow" onClick={factcheck}>Fact-check</button>
          </div>
        </form>

        <form onSubmit={submitImage} className="mb-4">
          <label className="block text-sm font-medium mb-1">Upload image (contains text)</label>
          <input className="block" type="file" accept="image/*" onChange={e => setFile(e.target.files[0])} />
          <div className="mt-2">
            <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-md shadow" type="submit">Analyze Image</button>
          </div>
        </form>

        <div className="mt-6">
          <h2 className="font-semibold">Result</h2>
          {renderFactCheck()}
        </div>
      </div>
    </div>
  )
}
