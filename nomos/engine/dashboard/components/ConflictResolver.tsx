import React, { useState } from 'react';

interface Opinion {
  madhab: string;
  opinion: string;
  evidence: string;
  authority: string;
}

interface ConflictResolverProps {
  verseId: string;
  opinions: Opinion[];
  scholarNotes?: string;
  resolutionStatus?: 'pending' | 'documented' | 'resolved';
}

export default function ConflictResolver({
  verseId,
  opinions,
  scholarNotes = '',
  resolutionStatus = 'pending',
}: ConflictResolverProps) {
  const [notes, setNotes] = useState(scholarNotes);
  const [status, setStatus] = useState(resolutionStatus);
  const [selectedOpinion, setSelectedOpinion] = useState<string | null>(null);

  const madhabs = ['Hanafi', 'Maliki', 'Shafi\'i', 'Hanbali'];

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Madhab Conflict Resolution - {verseId}</h2>
        <div className="flex gap-2">
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value as any)}
            className="input-field px-3 py-2 text-sm"
          >
            <option value="pending">Pending Review</option>
            <option value="documented">Documented Disagreement</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>

      {/* Madhab Opinions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {madhabs.map((madhab) => {
          const opinion = opinions.find((o) => o.madhab === madhab);
          return (
            <div
              key={madhab}
              className={`border-2 rounded-lg p-4 cursor-pointer transition ${
                selectedOpinion === madhab
                  ? 'border-quranic-gold bg-yellow-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onClick={() =>
                setSelectedOpinion(selectedOpinion === madhab ? null : madhab)
              }
            >
              <h3 className="text-lg font-bold mb-3">{madhab} School</h3>

              {opinion ? (
                <>
                  <div className="mb-3">
                    <p className="text-sm font-semibold text-gray-600">Opinion</p>
                    <p className="text-sm leading-relaxed">{opinion.opinion}</p>
                  </div>
                  <div className="mb-3">
                    <p className="text-sm font-semibold text-gray-600">Evidence</p>
                    <p className="text-sm text-blue-600 hover:underline cursor-pointer">
                      {opinion.evidence}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-600">Authority</p>
                    <p className="text-xs text-gray-500">{opinion.authority}</p>
                  </div>
                </>
              ) : (
                <p className="text-gray-500 text-sm">No recorded position</p>
              )}
            </div>
          );
        })}
      </div>

      {/* Scholar Notes */}
      <div className="mb-6">
        <label className="block text-sm font-semibold mb-2">Scholar Notes</label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Add commentary explaining alignments with evidence..."
          className="input-field p-3 h-32"
        />
      </div>

      {/* Evidence Chain */}
      {selectedOpinion && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold mb-3">Evidence Chain for {selectedOpinion}</h3>
          <div className="space-y-2 text-sm">
            <p>📖 Quranic References: 2 verses</p>
            <p>📚 Hadith References: 5 authentic hadiths</p>
            <p>🔗 Qiyas (Analogy): 1 clear analogy</p>
            <p>⚖️ Scholarly Consensus: Mentioned in 3 fiqh texts</p>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2 justify-end">
        <button className="btn-secondary">Document as Valid Disagreement</button>
        <button className="btn-primary">Flag for Further Study</button>
      </div>
    </div>
  );
}
