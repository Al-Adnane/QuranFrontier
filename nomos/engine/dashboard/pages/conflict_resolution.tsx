import React, { useState } from 'react';
import Head from 'next/head';
import ConflictResolver from '../components/ConflictResolver';

interface Conflict {
  id: string;
  verseId: string;
  topic: string;
  opinions: Array<{
    madhab: string;
    opinion: string;
    evidence: string;
    authority: string;
  }>;
  scholarNotes: string;
  resolutionStatus: 'pending' | 'documented' | 'resolved';
}

export default function ConflictResolution() {
  const [conflicts, setConflicts] = useState<Conflict[]>([
    {
      id: 'CONF-001',
      verseId: '2:219',
      topic: 'Permissibility of alcohol in medicine',
      opinions: [
        {
          madhab: 'Hanafi',
          opinion:
            'Alcohol used in medicine is permissible if no alternative exists',
          evidence: 'Qiyas on necessity (darura)',
          authority: 'Imam Abu Hanifa, Al-Mabsut',
        },
        {
          madhab: 'Maliki',
          opinion: 'Consumption of alcohol in any form is forbidden',
          evidence: 'Quranic prohibition and hadith',
          authority: 'Imam Malik, Al-Muwatta',
        },
        {
          madhab: 'Shafi\'i',
          opinion:
            'Medicinal use is permitted with strong necessity and no alternatives',
          evidence: 'Darurah principle with detailed conditions',
          authority: 'Imam Al-Shafi\'i, Al-Umm',
        },
        {
          madhab: 'Hanbali',
          opinion:
            'Medical use is allowed when the benefit is certain and necessity is proven',
          evidence: 'Maslaha (public interest) principle',
          authority: 'Imam Ahmad, Musnad',
        },
      ],
      scholarNotes:
        'This disagreement reflects different approaches to weighing necessity against divine prohibition. All schools agree on prohibition in normal circumstances.',
      resolutionStatus: 'documented',
    },
    {
      id: 'CONF-002',
      verseId: '5:6',
      topic: 'Intention requirement for wudu (ablution)',
      opinions: [
        {
          madhab: 'Hanafi',
          opinion: 'Intention is not required, only actual ablution',
          evidence: 'Historical practice and explicit hadith interpretation',
          authority: 'Imam Abu Hanifa, Fath Al-Qadir',
        },
        {
          madhab: 'Maliki',
          opinion: 'Intention is required at the start of ablution',
          evidence: 'Principle of niyyah in Islamic acts',
          authority: 'Imam Malik, Mukhtasar Al-Khalil',
        },
        {
          madhab: 'Shafi\'i',
          opinion: 'Intention must be present at the beginning',
          evidence: 'Quranic and hadith evidence on intention',
          authority: 'Imam Al-Shafi\'i, Minhaj Al-Talibin',
        },
        {
          madhab: 'Hanbali',
          opinion: 'Intention is required and must be sincere',
          evidence: 'Authentic hadith and scholarly consensus',
          authority: 'Imam Ahmad, Al-Mustaharaaj',
        },
      ],
      scholarNotes:
        'This is a classical disagreement on whether formal intention is required or if the act itself implies the intention.',
      resolutionStatus: 'pending',
    },
    {
      id: 'CONF-003',
      verseId: '23:6',
      topic: 'Marital relations during menstruation',
      opinions: [
        {
          madhab: 'Hanafi',
          opinion: 'Intercourse is forbidden; other relations may be permissible',
          evidence: 'Explicit Quranic prohibition and hadith',
          authority: 'Imam Abu Hanifa, Badai Al-Sanai',
        },
        {
          madhab: 'Maliki',
          opinion:
            'Complete abstinence is required; all relations are discouraged',
          evidence: 'Precautionary interpretation of revelation',
          authority: 'Imam Malik, Al-Mudawwana',
        },
        {
          madhab: 'Shafi\'i',
          opinion: 'Forbidden in the specific location mentioned',
          evidence: 'Literal interpretation with contextual understanding',
          authority: 'Imam Al-Shafi\'i, Kitab Al-Umm',
        },
        {
          madhab: 'Hanbali',
          opinion: 'All relations are forbidden during menstruation',
          evidence: 'Quranic verse and protective hadith interpretation',
          authority: 'Imam Ahmad, Al-Mustadarak',
        },
      ],
      scholarNotes:
        'Important disagreement on interpretation of Quranic verse. All schools agree on some level of restriction.',
      resolutionStatus: 'documented',
    },
  ]);

  const [selectedConflict, setSelectedConflict] = useState<Conflict | null>(
    conflicts[0]
  );
  const [filterStatus, setFilterStatus] = useState('all');

  const filteredConflicts = conflicts.filter(
    (c) =>
      filterStatus === 'all' ||
      c.resolutionStatus === filterStatus
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'documented':
        return 'bg-green-100 text-green-800';
      case 'resolved':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <>
      <Head>
        <title>Conflict Resolution - NOMOS</title>
      </Head>

      <div>
        <h1 className="text-3xl font-bold mb-8">Madhab Conflict Resolution</h1>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="card text-center">
            <p className="text-3xl font-bold text-quranic-gold">
              {conflicts.length}
            </p>
            <p className="text-gray-600">Total Conflicts</p>
          </div>
          <div className="card text-center">
            <p className="text-3xl font-bold text-green-600">
              {conflicts.filter((c) => c.resolutionStatus === 'documented').length}
            </p>
            <p className="text-gray-600">Documented</p>
          </div>
          <div className="card text-center">
            <p className="text-3xl font-bold text-yellow-600">
              {conflicts.filter((c) => c.resolutionStatus === 'pending').length}
            </p>
            <p className="text-gray-600">Pending Review</p>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Conflicts List */}
          <div className="lg:col-span-1">
            <div className="card">
              <h2 className="text-lg font-bold mb-4">Conflicts</h2>

              {/* Filter */}
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="input-field mb-4"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="documented">Documented</option>
                <option value="resolved">Resolved</option>
              </select>

              {/* List */}
              <div className="space-y-2">
                {filteredConflicts.map((conflict) => (
                  <div
                    key={conflict.id}
                    className={`p-3 rounded-lg cursor-pointer transition border-2 ${
                      selectedConflict?.id === conflict.id
                        ? 'border-quranic-gold bg-yellow-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedConflict(conflict)}
                  >
                    <p className="font-semibold text-sm">{conflict.verseId}</p>
                    <p className="text-xs text-gray-600 mt-1">
                      {conflict.topic}
                    </p>
                    <span
                      className={`text-xs px-2 py-1 rounded-full mt-2 inline-block ${getStatusColor(
                        conflict.resolutionStatus
                      )}`}
                    >
                      {conflict.resolutionStatus}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Conflict Detail */}
          <div className="lg:col-span-2">
            {selectedConflict ? (
              <ConflictResolver
                verseId={selectedConflict.verseId}
                opinions={selectedConflict.opinions}
                scholarNotes={selectedConflict.scholarNotes}
                resolutionStatus={selectedConflict.resolutionStatus}
              />
            ) : (
              <div className="card text-center text-gray-500">
                <p>Select a conflict to view details</p>
              </div>
            )}
          </div>
        </div>

        {/* Statistics Section */}
        <div className="card mt-8">
          <h2 className="text-xl font-bold mb-6">Disagreement Distribution</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-3">By Topic</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Ritual Practice (Ibadah)</span>
                  <span className="font-semibold">45%</span>
                </div>
                <div className="flex justify-between">
                  <span>Legal Matters (Muamalah)</span>
                  <span className="font-semibold">35%</span>
                </div>
                <div className="flex justify-between">
                  <span>Dietary Laws</span>
                  <span className="font-semibold">15%</span>
                </div>
                <div className="flex justify-between">
                  <span>Family Law</span>
                  <span className="font-semibold">5%</span>
                </div>
              </div>
            </div>
            <div>
              <h3 className="font-semibold mb-3">By Resolution Status</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Valid Disagreements</span>
                  <span className="font-semibold">67%</span>
                </div>
                <div className="flex justify-between">
                  <span>Under Resolution</span>
                  <span className="font-semibold">28%</span>
                </div>
                <div className="flex justify-between">
                  <span>Fully Resolved</span>
                  <span className="font-semibold">5%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
