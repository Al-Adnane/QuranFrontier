import React, { useState } from 'react';

interface Tafsir {
  id: string;
  scholar: string;
  school: string;
  text: string;
  edition: string;
  approved: boolean;
}

interface TafsirPanelProps {
  tafsirs: Tafsir[];
  verseId: string;
}

export default function TafsirPanel({ tafsirs, verseId }: TafsirPanelProps) {
  const [selectedScholar, setSelectedScholar] = useState<string | null>(null);
  const [selectedSchool, setSelectedSchool] = useState<string | null>(null);

  const schools = [...new Set(tafsirs.map((t) => t.school))];
  const scholars = [...new Set(tafsirs.map((t) => t.scholar))];

  const filteredTafsirs = tafsirs.filter(
    (t) =>
      (!selectedScholar || t.scholar === selectedScholar) &&
      (!selectedSchool || t.school === selectedSchool)
  );

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6">Tafsir Commentary - {verseId}</h2>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div>
          <label className="block text-sm font-semibold mb-2">Scholar</label>
          <select
            value={selectedScholar || ''}
            onChange={(e) => setSelectedScholar(e.target.value || null)}
            className="input-field"
          >
            <option value="">All Scholars</option>
            {scholars.map((scholar) => (
              <option key={scholar} value={scholar}>
                {scholar}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-semibold mb-2">School</label>
          <select
            value={selectedSchool || ''}
            onChange={(e) => setSelectedSchool(e.target.value || null)}
            className="input-field"
          >
            <option value="">All Schools</option>
            {schools.map((school) => (
              <option key={school} value={school}>
                {school}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Tafsir Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredTafsirs.map((tafsir) => (
          <div
            key={tafsir.id}
            className={`border rounded-lg p-4 ${
              tafsir.approved
                ? 'border-green-500 bg-green-50'
                : 'border-gray-300 bg-gray-50'
            }`}
          >
            <div className="flex justify-between items-start mb-3">
              <div>
                <h3 className="font-bold">{tafsir.scholar}</h3>
                <p className="text-sm text-gray-600">
                  {tafsir.school} - {tafsir.edition}
                </p>
              </div>
              {tafsir.approved && (
                <span className="bg-green-500 text-white text-xs px-2 py-1 rounded">
                  ✓ Approved
                </span>
              )}
            </div>
            <p className="text-sm leading-relaxed">{tafsir.text}</p>
          </div>
        ))}
      </div>

      {filteredTafsirs.length === 0 && (
        <p className="text-center text-gray-500 py-8">
          No tafsirs found matching your filters
        </p>
      )}
    </div>
  );
}
