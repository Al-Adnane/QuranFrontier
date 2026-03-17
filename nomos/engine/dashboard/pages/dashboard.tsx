import React, { useState, useEffect } from 'react';
import Head from 'next/head';

interface HealthMetrics {
  uptime: number;
  errorRate: number;
  apiLatency: number;
}

interface SystemStats {
  totalVerses: number;
  totalTafsirs: number;
  totalHadiths: number;
  activeUsers: number;
}

interface PendingCorrection {
  id: string;
  type: string;
  status: string;
  submittedBy: string;
  createdAt: Date;
  title: string;
}

interface ScholarBoardMember {
  id: string;
  name: string;
  expertise: string;
  canApprove: boolean;
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<HealthMetrics>({
    uptime: 99.94,
    errorRate: 0.23,
    apiLatency: 145,
  });

  const [stats, setStats] = useState<SystemStats>({
    totalVerses: 6236,
    totalTafsirs: 48,
    totalHadiths: 7275,
    activeUsers: 342,
  });

  const [pendingCorrections, setPendingCorrections] = useState<PendingCorrection[]>([
    {
      id: 'CORR-001',
      type: 'Hadith Grade',
      status: 'submitted',
      submittedBy: 'Dr. Ahmed Al-Ansari',
      createdAt: new Date('2024-03-10'),
      title: 'Sahih Al-Bukhari 5434 - Grade Review',
    },
    {
      id: 'CORR-002',
      type: 'Verse Commentary',
      status: 'under_review',
      submittedBy: 'Prof. Fatima Zahra',
      createdAt: new Date('2024-03-09'),
      title: 'Tafsir for Surah Al-Fatiha Verse 3',
    },
    {
      id: 'CORR-003',
      type: 'Linguistic Error',
      status: 'submitted',
      submittedBy: 'Dr. Mustafa Hassan',
      createdAt: new Date('2024-03-08'),
      title: 'Spelling correction in Arabic transliteration',
    },
  ]);

  const [scholars, setScholars] = useState<ScholarBoardMember[]>([
    {
      id: 'SCHOL-01',
      name: 'Dr. Ahmed Al-Ansari',
      expertise: 'Hadith Authentication',
      canApprove: true,
    },
    {
      id: 'SCHOL-02',
      name: 'Prof. Fatima Zahra',
      expertise: 'Quranic Exegesis',
      canApprove: true,
    },
    {
      id: 'SCHOL-03',
      name: 'Dr. Mustafa Hassan',
      expertise: 'Islamic Jurisprudence',
      canApprove: false,
    },
    {
      id: 'SCHOL-04',
      name: 'Prof. Aisha Mohammed',
      expertise: 'Linguistic Studies',
      canApprove: true,
    },
  ]);

  const [notifications, setNotifications] = useState<string[]>([
    '📖 New Hadith Collection Added: 45 new authenticated hadiths',
    '⚠️ Conflict Detected: Madhab disagreement in Surah 2:219',
    '✓ Correction Approved: Linguistic error fix in Al-Qamus',
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'submitted':
        return 'bg-blue-100 text-blue-800';
      case 'under_review':
        return 'bg-yellow-100 text-yellow-800';
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <>
      <Head>
        <title>Scholar Board Dashboard - NOMOS</title>
      </Head>

      <div>
        <h1 className="text-3xl font-bold mb-8">Scholar Board Dashboard</h1>

        {/* System Health Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="metric-card">
            <div className="text-4xl font-bold text-green-600 mb-2">
              {metrics.uptime}%
            </div>
            <p className="text-sm text-gray-600">System Uptime</p>
          </div>
          <div className="metric-card">
            <div className="text-4xl font-bold text-blue-600 mb-2">
              {metrics.errorRate}%
            </div>
            <p className="text-sm text-gray-600">Error Rate</p>
          </div>
          <div className="metric-card">
            <div className="text-4xl font-bold text-purple-600 mb-2">
              {metrics.apiLatency}ms
            </div>
            <p className="text-sm text-gray-600">API Latency</p>
          </div>
        </div>

        {/* Quick Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card text-center">
            <p className="text-3xl font-bold text-quranic-gold">{stats.totalVerses}</p>
            <p className="text-gray-600">Total Verses</p>
          </div>
          <div className="card text-center">
            <p className="text-3xl font-bold text-quranic-gold">{stats.totalTafsirs}</p>
            <p className="text-gray-600">Tafsir Collections</p>
          </div>
          <div className="card text-center">
            <p className="text-3xl font-bold text-quranic-gold">{stats.totalHadiths}</p>
            <p className="text-gray-600">Authenticated Hadiths</p>
          </div>
          <div className="card text-center">
            <p className="text-3xl font-bold text-quranic-gold">{stats.activeUsers}</p>
            <p className="text-gray-600">Active Users</p>
          </div>
        </div>

        {/* Notifications */}
        <div className="card mb-8">
          <h2 className="text-xl font-bold mb-4">Recent Notifications</h2>
          <div className="space-y-3">
            {notifications.map((notif, idx) => (
              <div
                key={idx}
                className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded"
              >
                <p className="text-sm">{notif}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Pending Corrections */}
        <div className="card mb-8">
          <h2 className="text-xl font-bold mb-4">Recent Pending Corrections</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-100 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold">ID</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Title</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Type</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Status</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">
                    Submitted By
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Date</th>
                </tr>
              </thead>
              <tbody>
                {pendingCorrections.map((correction) => (
                  <tr key={correction.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-mono">
                      {correction.id}
                    </td>
                    <td className="px-4 py-3 text-sm">{correction.title}</td>
                    <td className="px-4 py-3 text-sm">{correction.type}</td>
                    <td className="px-4 py-3 text-sm">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(
                          correction.status
                        )}`}
                      >
                        {correction.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">{correction.submittedBy}</td>
                    <td className="px-4 py-3 text-sm">
                      {correction.createdAt.toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4">
            <a href="/corrections" className="btn-primary">
              View All Corrections →
            </a>
          </div>
        </div>

        {/* Scholar Board Members */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Scholar Board Members</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {scholars.map((scholar) => (
              <div
                key={scholar.id}
                className="border rounded-lg p-4 hover:shadow-lg transition"
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold">{scholar.name}</h3>
                  {scholar.canApprove && (
                    <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                      Can Approve
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600">{scholar.expertise}</p>
                <p className="text-xs text-gray-500 mt-2">ID: {scholar.id}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
