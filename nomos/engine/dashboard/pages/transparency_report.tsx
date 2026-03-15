import React, { useState } from 'react';
import Head from 'next/head';

interface TransparencyReport {
  period: string;
  reportDate: Date;
  summaryStats: {
    totalUsers: number;
    activeResearchers: number;
    totalCorrections: number;
    approvalRate: number;
  };
  corrections: {
    submitted: number;
    approved: number;
    rejected: number;
    types: Record<string, number>;
  };
  sources: {
    newHadiths: number;
    newTafsirs: number;
    newVerses: number;
    verifiedHadiths: number;
  };
  scholarBoard: {
    members: number;
    approvalPermissions: number;
    changes: string[];
  };
  technology: {
    improvements: string[];
    systemUptime: number;
    apiLatencyReduction: number;
    newFeatures: string[];
  };
  trustMetrics: {
    dataAccuracy: number;
    userSatisfaction: number;
    conflictResolution: number;
    transparencyScore: number;
  };
}

export default function TransparencyReport() {
  const [report] = useState<TransparencyReport>({
    period: 'Q1 2024 (January - March)',
    reportDate: new Date('2024-04-01'),
    summaryStats: {
      totalUsers: 342,
      activeResearchers: 28,
      totalCorrections: 47,
      approvalRate: 78.7,
    },
    corrections: {
      submitted: 47,
      approved: 37,
      rejected: 10,
      types: {
        'Hadith Grade Corrections': 18,
        'Verse Commentary': 15,
        'Linguistic Errors': 12,
        'Source Verification': 2,
      },
    },
    sources: {
      newHadiths: 45,
      newTafsirs: 3,
      newVerses: 0,
      verifiedHadiths: 142,
    },
    scholarBoard: {
      members: 4,
      approvalPermissions: 3,
      changes: [
        'Welcomed Dr. Ahmed Al-Ansari to board (February)',
        'Promoted Prof. Aisha Mohammed to chief analyst (March)',
      ],
    },
    technology: {
      improvements: [
        'Upgraded semantic search accuracy to 96.7%',
        'Reduced API latency by 23%',
        'Implemented real-time conflict detection',
        'Enhanced audit logging with cryptographic verification',
      ],
      systemUptime: 99.94,
      apiLatencyReduction: 23,
      newFeatures: [
        'Madhab conflict resolution interface',
        'Advanced analytics dashboard',
        'Immutable audit trail with hash verification',
        'Real-time scholar notifications',
      ],
    },
    trustMetrics: {
      dataAccuracy: 98.5,
      userSatisfaction: 4.6,
      conflictResolution: 89.2,
      transparencyScore: 92.1,
    },
  });

  return (
    <>
      <Head>
        <title>Transparency Report - NOMOS</title>
      </Head>

      <div>
        <h1 className="text-3xl font-bold mb-2">Public Transparency Report</h1>
        <p className="text-gray-600 mb-8">
          {report.period} • Published {report.reportDate.toLocaleDateString()}
        </p>

        {/* Trust Metrics Banner */}
        <div className="card mb-8 bg-gradient-to-r from-green-50 to-blue-50 border-l-4 border-green-600">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            🏆 Trust Metrics
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <p className="text-3xl font-bold text-green-600">
                {report.trustMetrics.dataAccuracy}%
              </p>
              <p className="text-sm text-gray-600">Data Accuracy</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-blue-600">
                {report.trustMetrics.userSatisfaction}/5.0
              </p>
              <p className="text-sm text-gray-600">User Satisfaction</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-purple-600">
                {report.trustMetrics.conflictResolution}%
              </p>
              <p className="text-sm text-gray-600">Conflict Resolution</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-quranic-gold">
                {report.trustMetrics.transparencyScore}%
              </p>
              <p className="text-sm text-gray-600">Transparency Score</p>
            </div>
          </div>
        </div>

        {/* Executive Summary */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold mb-4">Executive Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-2xl font-bold text-blue-600">
                {report.summaryStats.totalUsers}
              </p>
              <p className="text-sm text-gray-600">Total Users</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-2xl font-bold text-green-600">
                {report.summaryStats.activeResearchers}
              </p>
              <p className="text-sm text-gray-600">Active Researchers</p>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <p className="text-2xl font-bold text-yellow-600">
                {report.summaryStats.totalCorrections}
              </p>
              <p className="text-sm text-gray-600">Total Corrections</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-2xl font-bold text-purple-600">
                {report.summaryStats.approvalRate}%
              </p>
              <p className="text-sm text-gray-600">Approval Rate</p>
            </div>
          </div>
        </div>

        {/* Error Corrections This Period */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold mb-4">Error Corrections This Period</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-3">Correction Overview</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Submitted</span>
                  <span className="font-bold text-blue-600">
                    {report.corrections.submitted}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Approved ✓</span>
                  <span className="font-bold text-green-600">
                    {report.corrections.approved}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Rejected ✗</span>
                  <span className="font-bold text-red-600">
                    {report.corrections.rejected}
                  </span>
                </div>
              </div>
            </div>
            <div>
              <h3 className="font-semibold mb-3">By Type</h3>
              <div className="space-y-2 text-sm">
                {Object.entries(report.corrections.types).map(([type, count]) => (
                  <div key={type} className="flex justify-between">
                    <span>{type}</span>
                    <span className="font-semibold">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* New Sources Added */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold mb-4">Sources & Verification</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg">
              <h3 className="font-semibold mb-3">New Sources Added</h3>
              <div className="space-y-2 text-sm">
                <p>
                  📖 New Hadiths:{' '}
                  <span className="font-bold">{report.sources.newHadiths}</span>
                </p>
                <p>
                  📚 New Tafsir Collections:{' '}
                  <span className="font-bold">{report.sources.newTafsirs}</span>
                </p>
                <p>
                  ✨ Newly Verified Hadiths:{' '}
                  <span className="font-bold">{report.sources.verifiedHadiths}</span>
                </p>
              </div>
            </div>
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg">
              <h3 className="font-semibold mb-3">Verification Standards</h3>
              <ul className="space-y-2 text-sm">
                <li>✓ All hadiths graded by certified scholars</li>
                <li>✓ Chain of transmission (isnad) verified</li>
                <li>✓ Cross-referenced with classical collections</li>
                <li>✓ Immutable audit trail maintained</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Scholar Board Changes */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold mb-4">Scholar Board Updates</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-3">Board Composition</h3>
              <div className="space-y-3">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">
                    {report.scholarBoard.members}
                  </p>
                  <p className="text-sm text-gray-600">Total Members</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">
                    {report.scholarBoard.approvalPermissions}
                  </p>
                  <p className="text-sm text-gray-600">Can Approve Changes</p>
                </div>
              </div>
            </div>
            <div>
              <h3 className="font-semibold mb-3">This Period's Changes</h3>
              <ul className="space-y-2 text-sm">
                {report.scholarBoard.changes.map((change, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="mr-2">🔹</span>
                    <span>{change}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Technology Improvements */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold mb-4">Technology Improvements</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-3">Performance Enhancements</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between items-center bg-green-50 p-3 rounded">
                  <span>System Uptime</span>
                  <span className="font-bold text-green-600">
                    {report.technology.systemUptime}%
                  </span>
                </div>
                <div className="flex justify-between items-center bg-blue-50 p-3 rounded">
                  <span>API Latency Reduction</span>
                  <span className="font-bold text-blue-600">
                    {report.technology.apiLatencyReduction}%
                  </span>
                </div>
              </div>
            </div>
            <div>
              <h3 className="font-semibold mb-3">New Features Deployed</h3>
              <ul className="space-y-2 text-sm">
                {report.technology.newFeatures.map((feature, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="mr-2">✨</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="mt-6">
            <h3 className="font-semibold mb-3">System Improvements</h3>
            <ul className="space-y-2 text-sm">
              {report.technology.improvements.map((improvement, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="mr-2">✓</span>
                  <span>{improvement}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Commitment to Transparency */}
        <div className="card mb-8 bg-gradient-to-r from-purple-50 to-pink-50 border-l-4 border-purple-600">
          <h2 className="text-xl font-bold mb-3">Our Commitment to Transparency</h2>
          <p className="text-sm text-gray-700 mb-3">
            NOMOS is committed to the highest standards of transparency and accountability in Islamic scholarship. Every correction, approval, and system change is logged immutably and available for audit. We believe that trust is earned through openness and verifiable evidence.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
            <div className="flex items-start">
              <span className="mr-2">🔐</span>
              <span>All changes cryptographically verified</span>
            </div>
            <div className="flex items-start">
              <span className="mr-2">📋</span>
              <span>Complete audit trails maintained</span>
            </div>
            <div className="flex items-start">
              <span className="mr-2">👥</span>
              <span>Independent scholar review</span>
            </div>
          </div>
        </div>

        {/* Download Report */}
        <div className="card text-center">
          <h2 className="text-lg font-bold mb-4">Download Full Report</h2>
          <div className="flex gap-4 justify-center">
            <button className="btn-primary">📄 Download PDF</button>
            <button className="btn-secondary">📊 Download CSV Data</button>
          </div>
        </div>
      </div>
    </>
  );
}
