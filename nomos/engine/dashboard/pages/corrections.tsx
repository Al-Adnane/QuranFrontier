import React, { useState } from 'react';
import Head from 'next/head';

interface Correction {
  id: string;
  type: 'hadith_grade' | 'verse_commentary' | 'linguistic_error';
  status: 'submitted' | 'under_review' | 'approved' | 'rejected';
  title: string;
  originalText: string;
  proposedChange: string;
  justification: string;
  submittedBy: string;
  submittedAt: Date;
  evidence: string[];
  scholarComments: Array<{ scholar: string; comment: string; date: Date }>;
  affectedUsers?: number;
}

export default function Corrections() {
  const [corrections, setCorrections] = useState<Correction[]>([
    {
      id: 'CORR-001',
      type: 'hadith_grade',
      status: 'under_review',
      title: 'Sahih Al-Bukhari 5434 - Grade Review',
      originalText: 'Classified as Sahih (Authentic)',
      proposedChange: 'Reclassify as Hasan (Fair)',
      justification: 'Recent analysis of the isnad reveals a weak link in the third transmitter',
      submittedBy: 'Dr. Ahmed Al-Ansari',
      submittedAt: new Date('2024-03-10'),
      evidence: [
        'Al-Bukhari Collection Analysis',
        'Transmitter Authentication Database',
      ],
      scholarComments: [
        {
          scholar: 'Prof. Fatima Zahra',
          comment: 'I concur with the analysis. The transmitter Sulaiman was noted as mudallil.',
          date: new Date('2024-03-11'),
        },
      ],
      affectedUsers: 142,
    },
    {
      id: 'CORR-002',
      type: 'verse_commentary',
      status: 'submitted',
      title: 'Tafsir for Surah Al-Fatiha Verse 3',
      originalText:
        'Traditional Tafsir: "The Day of Judgment will come..."',
      proposedChange:
        'Expanded Tafsir: "The Day of Judgment encompasses both individual and cosmic accountability..."',
      justification: 'Incorporates recent scholarly consensus on multi-dimensional interpretation',
      submittedBy: 'Prof. Fatima Zahra',
      submittedAt: new Date('2024-03-09'),
      evidence: [
        'Tafsir Ibn Kathir',
        'Al-Tabari Exegesis',
        'Modern Islamic Scholarship Review',
      ],
      scholarComments: [],
      affectedUsers: 312,
    },
    {
      id: 'CORR-003',
      type: 'linguistic_error',
      status: 'approved',
      title: 'Arabic Transliteration Correction',
      originalText: '"Alhamdulilah" (incorrect romanization)',
      proposedChange: '"Alhamdulillah" (correct romanization)',
      justification: 'Follows standard Islamic Studies transliteration guidelines (ALA-LC)',
      submittedBy: 'Dr. Mustafa Hassan',
      submittedAt: new Date('2024-03-08'),
      evidence: ['ALA-LC Transliteration Standards', 'ISO 233-3 Arabic Romanization'],
      scholarComments: [
        {
          scholar: 'Prof. Aisha Mohammed',
          comment: 'Approved. Aligns with our linguistics standards.',
          date: new Date('2024-03-08'),
        },
      ],
      affectedUsers: 8642,
    },
  ]);

  const [selectedCorrection, setSelectedCorrection] = useState<Correction | null>(
    null
  );
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedForBulk, setSelectedForBulk] = useState<string[]>([]);

  const filteredCorrections = corrections.filter(
    (c) =>
      (typeFilter === 'all' || c.type === typeFilter) &&
      (statusFilter === 'all' || c.status === statusFilter)
  );

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      hadith_grade: 'Hadith Grade',
      verse_commentary: 'Verse Commentary',
      linguistic_error: 'Linguistic Error',
    };
    return labels[type] || type;
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      submitted: 'bg-blue-100 text-blue-800',
      under_review: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const toggleBulkSelection = (id: string) => {
    setSelectedForBulk((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const handleApproveSelected = () => {
    setCorrections((prev) =>
      prev.map((c) =>
        selectedForBulk.includes(c.id) ? { ...c, status: 'approved' } : c
      )
    );
    setSelectedForBulk([]);
  };

  const handleRejectSelected = () => {
    setCorrections((prev) =>
      prev.map((c) =>
        selectedForBulk.includes(c.id) ? { ...c, status: 'rejected' } : c
      )
    );
    setSelectedForBulk([]);
  };

  return (
    <>
      <Head>
        <title>Pending Corrections - NOMOS</title>
      </Head>

      <div>
        <h1 className="text-3xl font-bold mb-8">Pending Corrections Review</h1>

        {/* Filters */}
        <div className="card mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2">
                Filter by Type
              </label>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="input-field"
              >
                <option value="all">All Types</option>
                <option value="hadith_grade">Hadith Grade</option>
                <option value="verse_commentary">Verse Commentary</option>
                <option value="linguistic_error">Linguistic Error</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">
                Filter by Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="input-field"
              >
                <option value="all">All Status</option>
                <option value="submitted">Submitted</option>
                <option value="under_review">Under Review</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">
                Quick Stats
              </label>
              <div className="text-sm text-gray-600">
                <p>Pending: {filteredCorrections.filter(c => c.status !== 'approved' && c.status !== 'rejected').length}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Bulk Actions */}
        {selectedForBulk.length > 0 && (
          <div className="card mb-6 bg-blue-50 border-l-4 border-blue-500">
            <div className="flex justify-between items-center">
              <p className="font-semibold">
                {selectedForBulk.length} correction(s) selected
              </p>
              <div className="flex gap-2">
                <button
                  onClick={handleApproveSelected}
                  className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                >
                  Approve Selected
                </button>
                <button
                  onClick={handleRejectSelected}
                  className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                >
                  Reject Selected
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Corrections List */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Corrections Table */}
          <div className="lg:col-span-2 card">
            <table className="w-full">
              <thead className="bg-gray-100 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold">
                    <input
                      type="checkbox"
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedForBulk(filteredCorrections.map((c) => c.id));
                        } else {
                          setSelectedForBulk([]);
                        }
                      }}
                      checked={
                        selectedForBulk.length === filteredCorrections.length &&
                        filteredCorrections.length > 0
                      }
                    />
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">
                    Title
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">
                    Type
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">
                    Users Affected
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredCorrections.map((correction) => (
                  <tr
                    key={correction.id}
                    className="border-b hover:bg-gray-50 cursor-pointer"
                    onClick={() => setSelectedCorrection(correction)}
                  >
                    <td className="px-4 py-3">
                      <input
                        type="checkbox"
                        checked={selectedForBulk.includes(correction.id)}
                        onChange={() => toggleBulkSelection(correction.id)}
                        onClick={(e) => e.stopPropagation()}
                      />
                    </td>
                    <td className="px-4 py-3 text-sm font-medium">
                      {correction.title}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      {getTypeLabel(correction.type)}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(
                          correction.status
                        )}`}
                      >
                        {correction.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm font-mono">
                      {correction.affectedUsers || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Detail Panel */}
          <div>
            {selectedCorrection ? (
              <div className="card sticky top-8">
                <h2 className="text-xl font-bold mb-4">
                  {selectedCorrection.id}
                </h2>

                <div className="space-y-4 text-sm">
                  <div>
                    <p className="font-semibold text-gray-600">Original</p>
                    <p className="bg-red-50 p-2 rounded mt-1">
                      {selectedCorrection.originalText}
                    </p>
                  </div>

                  <div>
                    <p className="font-semibold text-gray-600">Proposed</p>
                    <p className="bg-green-50 p-2 rounded mt-1">
                      {selectedCorrection.proposedChange}
                    </p>
                  </div>

                  <div>
                    <p className="font-semibold text-gray-600">Justification</p>
                    <p className="text-gray-700 mt-1">
                      {selectedCorrection.justification}
                    </p>
                  </div>

                  <div>
                    <p className="font-semibold text-gray-600">Evidence</p>
                    <ul className="mt-1 space-y-1">
                      {selectedCorrection.evidence.map((e, idx) => (
                        <li key={idx} className="text-blue-600">
                          • {e}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <p className="font-semibold text-gray-600">
                      Scholar Comments ({selectedCorrection.scholarComments.length})
                    </p>
                    <div className="mt-2 space-y-2">
                      {selectedCorrection.scholarComments.map((comment, idx) => (
                        <div
                          key={idx}
                          className="bg-blue-50 p-2 rounded border-l-2 border-blue-500"
                        >
                          <p className="font-semibold text-xs">
                            {comment.scholar}
                          </p>
                          <p className="text-xs text-gray-700">
                            {comment.comment}
                          </p>
                          <p className="text-xs text-gray-500">
                            {comment.date.toLocaleDateString()}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex gap-2 pt-4">
                    <button className="btn-primary text-sm flex-1">
                      Approve
                    </button>
                    <button className="btn-secondary text-sm flex-1">
                      Reject
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="card text-center text-gray-500">
                <p>Select a correction to view details</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
