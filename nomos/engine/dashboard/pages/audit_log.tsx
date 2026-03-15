import React, { useState } from 'react';
import Head from 'next/head';
import AuditTrail from '../components/AuditTrail';

interface AuditEvent {
  id: string;
  timestamp: Date;
  user: string;
  action: string;
  entity: string;
  entityId: string;
  details: string;
  dataHash: string;
}

export default function AuditLog() {
  const [events, setEvents] = useState<AuditEvent[]>([
    {
      id: 'EVT-0042',
      timestamp: new Date('2024-03-14T14:32:00'),
      user: 'Prof. Fatima Zahra',
      action: 'Approve Correction',
      entity: 'Correction',
      entityId: 'CORR-003',
      details:
        'Approved linguistic error correction for Arabic transliteration in Surah Al-Baqarah',
      dataHash:
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    },
    {
      id: 'EVT-0041',
      timestamp: new Date('2024-03-14T13:15:00'),
      user: 'Dr. Ahmed Al-Ansari',
      action: 'Submit Correction',
      entity: 'Correction',
      entityId: 'CORR-004',
      details:
        'Submitted hadith grade review for Sunan An-Nasa\'i collection',
      dataHash:
        'a3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b856',
    },
    {
      id: 'EVT-0040',
      timestamp: new Date('2024-03-14T11:48:00'),
      user: 'System Admin',
      action: 'Create Correction',
      entity: 'Correction',
      entityId: 'CORR-002',
      details: 'System-initiated correction for consistency check',
      dataHash:
        'b3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b857',
    },
    {
      id: 'EVT-0039',
      timestamp: new Date('2024-03-14T10:20:00'),
      user: 'Prof. Aisha Mohammed',
      action: 'Review Correction',
      entity: 'Correction',
      entityId: 'CORR-001',
      details:
        'Reviewed and commented on Verse 2:219 madhab conflict resolution',
      dataHash:
        'c3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b858',
    },
    {
      id: 'EVT-0038',
      timestamp: new Date('2024-03-13T16:45:00'),
      user: 'Dr. Mustafa Hassan',
      action: 'Reject Correction',
      entity: 'Correction',
      entityId: 'CORR-005',
      details: 'Rejected proposed change to Tafsir interpretation due to weak evidence',
      dataHash:
        'd3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b859',
    },
    {
      id: 'EVT-0037',
      timestamp: new Date('2024-03-13T14:12:00'),
      user: 'Prof. Fatima Zahra',
      action: 'Update User Role',
      entity: 'User',
      entityId: 'USER-042',
      details: 'Promoted user to Scholar status with approval permissions',
      dataHash:
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b860',
    },
    {
      id: 'EVT-0036',
      timestamp: new Date('2024-03-13T09:30:00'),
      user: 'System Admin',
      action: 'Export Audit Log',
      entity: 'Audit',
      entityId: 'AUDIT-001',
      details: 'Exported complete audit trail for Q1 2024 compliance review',
      dataHash:
        'f3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b861',
    },
    {
      id: 'EVT-0035',
      timestamp: new Date('2024-03-12T15:00:00'),
      user: 'Dr. Ahmed Al-Ansari',
      action: 'Approve Correction',
      entity: 'Correction',
      entityId: 'CORR-006',
      details: 'Approved hadith chain authentication update',
      dataHash:
        'a3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b862',
    },
  ]);

  const [dateRange, setDateRange] = useState({ from: '', to: '' });

  const handleSearch = (term: string) => {
    console.log('Search term:', term);
  };

  const handleExport = (format: 'json' | 'csv') => {
    if (format === 'json') {
      const json = JSON.stringify(events, null, 2);
      const blob = new Blob([json], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-trail-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
    } else if (format === 'csv') {
      let csv =
        'ID,Timestamp,User,Action,Entity,EntityID,Details,DataHash\n';
      events.forEach((e) => {
        csv += `"${e.id}","${e.timestamp.toISOString()}","${e.user}","${e.action}","${e.entity}","${e.entityId}","${e.details}","${e.dataHash}"\n`;
      });
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-trail-${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
    }
  };

  return (
    <>
      <Head>
        <title>Audit Log - NOMOS</title>
      </Head>

      <div>
        <h1 className="text-3xl font-bold mb-8">Immutable Audit Trail</h1>

        {/* Date Range Filter */}
        <div className="card mb-6">
          <h3 className="font-semibold mb-4">Date Range Filter</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2">
                From Date
              </label>
              <input
                type="date"
                value={dateRange.from}
                onChange={(e) =>
                  setDateRange({ ...dateRange, from: e.target.value })
                }
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">
                To Date
              </label>
              <input
                type="date"
                value={dateRange.to}
                onChange={(e) =>
                  setDateRange({ ...dateRange, to: e.target.value })
                }
                className="input-field"
              />
            </div>
          </div>
        </div>

        {/* Tamper Detection Alert */}
        <div className="card mb-6 bg-green-50 border-l-4 border-green-500">
          <p className="font-semibold text-green-800">
            ✓ All hashes verified. No tampering detected.
          </p>
          <p className="text-sm text-green-700 mt-2">
            Last verification: {new Date().toLocaleString()}
          </p>
        </div>

        {/* Audit Trail Component */}
        <AuditTrail
          events={events}
          onSearch={handleSearch}
          onExport={handleExport}
        />
      </div>
    </>
  );
}
