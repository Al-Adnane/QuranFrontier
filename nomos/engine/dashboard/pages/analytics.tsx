import React, { useState } from 'react';
import Head from 'next/head';

interface AnalyticsData {
  usageStats: {
    totalApiCalls: number;
    topEndpoints: Array<{ endpoint: string; calls: number }>;
    topSearchTerms: Array<{ term: string; count: number }>;
    topTafsirs: Array<{ tafsir: string; views: number }>;
  };
  errorTracking: {
    failedCorrections: number;
    apiErrors: number;
    dataInconsistencies: number;
    rejectionReasons: Record<string, number>;
  };
  performanceMetrics: {
    avgQueryLatency: number;
    searchAccuracy: number;
    graphQueryPerformance: number;
  };
  correctionVelocity: {
    submittedThisWeek: number;
    approvedThisWeek: number;
    approvalRate: number;
    averageReviewTime: string;
  };
}

export default function Analytics() {
  const [timeframe, setTimeframe] = useState('week');

  const [analytics] = useState<AnalyticsData>({
    usageStats: {
      totalApiCalls: 156234,
      topEndpoints: [
        { endpoint: '/api/verses', calls: 45230 },
        { endpoint: '/api/tafsirs', calls: 38920 },
        { endpoint: '/api/hadiths', calls: 32105 },
        { endpoint: '/api/search', calls: 28904 },
        { endpoint: '/api/conflicts', calls: 11075 },
      ],
      topSearchTerms: [
        { term: 'Surah Al-Fatiha', count: 8932 },
        { term: 'Tawheed (Oneness of God)', count: 6234 },
        { term: 'Hadith on Charity', count: 5128 },
        { term: 'Madhab differences', count: 4156 },
        { term: 'Riba (Usury)', count: 3845 },
      ],
      topTafsirs: [
        { tafsir: 'Tafsir Ibn Kathir', views: 45230 },
        { tafsir: 'Tafsir Al-Qurtubi', views: 32890 },
        { tafsir: 'Tafsir Al-Tabari', views: 28456 },
        { tafsir: 'Tafsir As-Sa\'di', views: 21340 },
        { tafsir: 'Tafsir Al-Jalalayn', views: 18920 },
      ],
    },
    errorTracking: {
      failedCorrections: 23,
      apiErrors: 156,
      dataInconsistencies: 8,
      rejectionReasons: {
        'Insufficient Evidence': 12,
        'Contradicts Islamic Principles': 5,
        'Already Documented': 4,
        'Requires More Review': 2,
      },
    },
    performanceMetrics: {
      avgQueryLatency: 145,
      searchAccuracy: 96.7,
      graphQueryPerformance: 234,
    },
    correctionVelocity: {
      submittedThisWeek: 12,
      approvedThisWeek: 7,
      approvalRate: 58.3,
      averageReviewTime: '2.4 days',
    },
  });

  const [userDemographics] = useState({
    researchers: 28,
    scholars: 42,
    publicUsers: 272,
  });

  return (
    <>
      <Head>
        <title>Analytics - NOMOS</title>
      </Head>

      <div>
        <h1 className="text-3xl font-bold mb-8">System Usage & Performance Analytics</h1>

        {/* Timeframe Selector */}
        <div className="card mb-8">
          <div className="flex gap-2">
            {['day', 'week', 'month', 'year'].map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-4 py-2 rounded-lg font-semibold capitalize transition ${
                  timeframe === tf
                    ? 'bg-quranic-gold text-quranic-dark'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        {/* Usage Statistics */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold mb-6">Usage Statistics</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* Total API Calls */}
            <div>
              <h3 className="font-semibold mb-4">Total API Calls</h3>
              <p className="text-4xl font-bold text-quranic-gold mb-2">
                {(analytics.usageStats.totalApiCalls / 1000).toFixed(1)}K
              </p>
              <p className="text-sm text-gray-600">
                +12.5% from last period
              </p>
            </div>

            {/* User Demographics */}
            <div>
              <h3 className="font-semibold mb-4">User Demographics</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between items-center">
                  <span>Public Users</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{
                          width: `${
                            (userDemographics.publicUsers /
                              (userDemographics.researchers +
                                userDemographics.scholars +
                                userDemographics.publicUsers)) *
                            100
                          }%`,
                        }}
                      ></div>
                    </div>
                    <span className="font-semibold">
                      {userDemographics.publicUsers}
                    </span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span>Scholars</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-purple-500 h-2 rounded-full"
                        style={{
                          width: `${
                            (userDemographics.scholars /
                              (userDemographics.researchers +
                                userDemographics.scholars +
                                userDemographics.publicUsers)) *
                            100
                          }%`,
                        }}
                      ></div>
                    </div>
                    <span className="font-semibold">
                      {userDemographics.scholars}
                    </span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span>Researchers</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{
                          width: `${
                            (userDemographics.researchers /
                              (userDemographics.researchers +
                                userDemographics.scholars +
                                userDemographics.publicUsers)) *
                            100
                          }%`,
                        }}
                      ></div>
                    </div>
                    <span className="font-semibold">
                      {userDemographics.researchers}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Top Endpoints */}
          <div className="mb-6">
            <h3 className="font-semibold mb-3">Top API Endpoints</h3>
            <div className="space-y-2">
              {analytics.usageStats.topEndpoints.map((endpoint, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <span className="text-sm">{endpoint.endpoint}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-48 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{
                          width: `${
                            (endpoint.calls /
                              analytics.usageStats.totalApiCalls) *
                            100
                          }%`,
                        }}
                      ></div>
                    </div>
                    <span className="text-sm font-semibold">
                      {endpoint.calls.toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Search Terms */}
          <div className="mb-6">
            <h3 className="font-semibold mb-3">Most Searched Terms</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analytics.usageStats.topSearchTerms.map((term, idx) => (
                <div
                  key={idx}
                  className="bg-gradient-to-r from-blue-50 to-transparent p-3 rounded-lg"
                >
                  <p className="font-semibold text-sm">{term.term}</p>
                  <p className="text-xs text-gray-600">
                    {term.count.toLocaleString()} searches
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Top Tafsirs */}
          <div>
            <h3 className="font-semibold mb-3">Most Accessed Tafsirs</h3>
            <div className="space-y-3">
              {analytics.usageStats.topTafsirs.map((tafsir, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg"
                >
                  <span className="font-semibold text-sm">{tafsir.tafsir}</span>
                  <span className="text-sm text-gray-600">
                    {tafsir.views.toLocaleString()} views
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Error Tracking */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold mb-6">Error Tracking</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-red-50 p-4 rounded-lg">
              <p className="text-3xl font-bold text-red-600">
                {analytics.errorTracking.failedCorrections}
              </p>
              <p className="text-sm text-gray-600">Failed Corrections</p>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <p className="text-3xl font-bold text-orange-600">
                {analytics.errorTracking.apiErrors}
              </p>
              <p className="text-sm text-gray-600">API Errors</p>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <p className="text-3xl font-bold text-yellow-600">
                {analytics.errorTracking.dataInconsistencies}
              </p>
              <p className="text-sm text-gray-600">Data Inconsistencies</p>
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-3">Rejection Reasons</h3>
            <div className="space-y-2">
              {Object.entries(analytics.errorTracking.rejectionReasons).map(
                ([reason, count]) => (
                  <div key={reason} className="flex items-center justify-between">
                    <span className="text-sm">{reason}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-40 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-red-500 h-2 rounded-full"
                          style={{
                            width: `${
                              (count /
                                Object.values(
                                  analytics.errorTracking.rejectionReasons
                                ).reduce((a, b) => a + b, 0)) *
                              100
                            }%`,
                          }}
                        ></div>
                      </div>
                      <span className="text-sm font-semibold">{count}</span>
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold mb-6">Performance Metrics</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-green-600">
                {analytics.performanceMetrics.avgQueryLatency}ms
              </p>
              <p className="text-sm text-gray-600 mt-2">
                Avg Query Latency
              </p>
              <p className="text-xs text-gray-500 mt-1">Target: &lt;200ms</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-600">
                {analytics.performanceMetrics.searchAccuracy}%
              </p>
              <p className="text-sm text-gray-600 mt-2">
                Semantic Search Accuracy
              </p>
              <p className="text-xs text-gray-500 mt-1">Target: &gt;95%</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-purple-600">
                {analytics.performanceMetrics.graphQueryPerformance}ms
              </p>
              <p className="text-sm text-gray-600 mt-2">
                Graph Query P95
              </p>
              <p className="text-xs text-gray-500 mt-1">Target: &lt;300ms</p>
            </div>
          </div>
        </div>

        {/* Correction Velocity */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Correction Velocity</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="mb-6">
                <p className="text-sm text-gray-600 mb-2">This Week</p>
                <p className="text-4xl font-bold text-quranic-gold">
                  {analytics.correctionVelocity.submittedThisWeek}
                </p>
                <p className="text-sm text-gray-500">Corrections Submitted</p>
              </div>

              <div>
                <p className="text-sm text-gray-600 mb-2">Approved This Week</p>
                <p className="text-3xl font-bold text-green-600">
                  {analytics.correctionVelocity.approvedThisWeek}
                </p>
                <p className="text-sm text-gray-500">
                  {analytics.correctionVelocity.approvalRate}% approval rate
                </p>
              </div>
            </div>

            <div className="bg-blue-50 p-6 rounded-lg">
              <h3 className="font-semibold mb-4">Velocity Metrics</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span>Avg Review Time</span>
                  <span className="font-semibold">
                    {analytics.correctionVelocity.averageReviewTime}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Weekly Throughput</span>
                  <span className="font-semibold">
                    {analytics.correctionVelocity.submittedThisWeek} submitted
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Monthly Projection</span>
                  <span className="font-semibold">
                    {Math.round(analytics.correctionVelocity.submittedThisWeek * 4.3)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
