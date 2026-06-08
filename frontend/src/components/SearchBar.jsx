import { useState } from 'react'
import '../styles/SearchBar.css'

function SearchBar({ onSearch, players }) {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState([])

  function handleChange(e) {
    const value = e.target.value
    setQuery(value)

    if (value.length < 2) {
      setSuggestions([])
      return
    }

    const filtered = players
      .filter(p => p.toLowerCase().includes(value.toLowerCase()))
      .slice(0, 6)

    setSuggestions(filtered)
  }

  function handleSelect(name) {
    setQuery(name)
    setSuggestions([])
    onSearch(name)
  }

  function handleClick() {
    onSearch(query)
    setSuggestions([])
  }

  return (
    <div className="searchbar">
      <div className="searchbar-input-wrap">
        <input
          className="searchbar-input"
          type="text"
          placeholder="Search player..."
          value={query}
          onChange={handleChange}
        />
        {suggestions.length > 0 && (
          <div className="searchbar-dropdown">
            {suggestions.map(name => (
              <div
                key={name}
                className="searchbar-suggestion"
                onClick={() => handleSelect(name)}
              >
                {name}
              </div>
            ))}
          </div>
        )}
      </div>
      <button className="searchbar-btn" onClick={handleClick}>
        Predict
      </button>
    </div>
  )
}

export default SearchBar