import React from 'react';

interface VerseViewerProps {
  verseId: string;
  arabic: string;
  english: string;
  confidenceScore: number;
  sources?: string[];
  onReportError?: () => void;
}

export default function VerseViewer({
  verseId,
  arabic,
  english,
  confidenceScore,
  sources = [],
  onReportError,
}: VerseViewerProps) {
  const getConfidenceClass = () => {
    if (confidenceScore >= 99) return 'confidence-high';
    if (confidenceScore >= 80) return 'confidence-medium';
    return 'confidence-low';
  };

  const getConfidenceLabel = () => {
    if (confidenceScore >= 99) return 'Very High';
    if (confidenceScore >= 80) return 'High';
    return 'Medium';
  };

  return (
    <div className="card">
      <div className="mb-4">
        <p className="text-sm text-gray-500 mb-2">Verse {verseId}</p>
        <p className="text-3xl font-bold text-right mb-4 leading-loose text-xl">
          {arabic}
        </p>
        <p className="text-base leading-relaxed text-gray-700 mb-4">
          {english}
        </p>
      </div>

      {/* Confidence Score */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-sm text-gray-600 mb-1">Confidence Score</p>
          <div className="w-48 bg-gray-200 rounded-full h-2.5">
            <div
              className={`h-2.5 rounded-full ${
                confidenceScore >= 99
                  ? 'bg-green-500'
                  : confidenceScore >= 80
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
              }`}
              style={{ width: `${confidenceScore}%` }}
            ></div>
          </div>
        </div>
        <span className={`${getConfidenceClass()} font-semibold`}>
          {confidenceScore}% - {getConfidenceLabel()}
        </span>
      </div>

      {/* Sources */}
      {sources.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold mb-2 text-gray-700">
            Supporting Sources
          </h4>
          <div className="space-y-1">
            {sources.map((source, idx) => (
              <p
                key={idx}
                className="text-sm text-blue-600 hover:underline cursor-pointer"
              >
                • {source}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2 mt-4">
        <button
          onClick={onReportError}
          className="btn-secondary text-sm"
        >
          Report Error
        </button>
        <button className="btn-secondary text-sm">View Related Verses</button>
      </div>
    </div>
  );
}
