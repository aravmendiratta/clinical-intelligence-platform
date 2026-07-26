import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MagnifyingGlassIcon } from '@heroicons/react/24/solid';

let debounceTimer: NodeJS.Timeout;

const SearchBar: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      if (value.trim()) {
        performSearch(value.trim());
      } else {
        setResults([]);
      }
    }, 400);
  };

  const performSearch = async (term: string) => {
    setLoading(true);
    try {
      const res = await axios.get('/api/search', { params: { q: term } });
      setResults(res.data);
    } catch (err) {
      console.error('Search failed', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-xl mb-6">
      <div className="flex items-center bg-glass backdrop-blur-xs rounded-xl p-2 border border-white/20">
        <MagnifyingGlassIcon className="h-5 w-5 text-primary mx-2" />
        <input
          type="text"
          placeholder="Search medical records..."
          value={query}
          onChange={handleChange}
          className="flex-1 bg-transparent text-white placeholder-gray-300 focus:outline-none"
        />
        {loading && <span className="text-primary text-sm mr-2">Loading...</span>}
      </div>
      {results.length > 0 && (
        <div className="mt-2 bg-glass backdrop-blur-xs rounded-xl border border-white/20 max-h-60 overflow-y-auto p-2">
          {results.map((item, idx) => (
            <div key={idx} className="p-2 border-b border-white/10 last:border-b-0">
              <p className="text-white">{JSON.stringify(item)}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchBar;
