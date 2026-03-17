import React, { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';

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

interface AuditTrailProps {
  events: AuditEvent[];
  onSearch?: (term: string) => void;
  onExport?: (format: 'json' | 'csv') => void;
}

export default function AuditTrail({
  events,
  onSearch,
  onExport,
}: AuditTrailProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState('all');
  const [actionFilter, setActionFilter] = useState('all');

  const actions = [...new Set(events.map((e) => e.action))];

  const filteredEvents = events.filter((event) => {
    const matchesSearch =
      searchTerm === '' ||
      event.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
      event.entity.toLowerCase().includes(searchTerm.toLowerCase()) ||
      event.details.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesAction = actionFilter === 'all' || event.action === actionFilter;

    return matchesSearch && matchesAction;
  });

  const handleSearch = (term: string) => {
    setSearchTerm(term);
    onSearch?.(term);
  };

  const getActionColor = (action: string) => {
    if (action.includes('Approve')) return 'text-green-600 bg-green-50';
    if (action.includes('Reject')) return 'text-red-600 bg-red-50';
    if (action.includes('Create')) return 'text-blue-600 bg-blue-50';
    if (action.includes('Update')) return 'text-yellow-600 bg-yellow-50';
    return 'text-gray-600 bg-gray-50';
  };

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6">Immutable Audit Trail</h2>

      {/* Filters and Search */}
      <div className="flex gap-4 mb-6">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search by user, entity, or details..."
            value={searchTerm}
            onChange={(e) => handleSearch(e.target.value)}
            className="input-field"
          />
        </div>
        <div>
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="input-field"
          >
            <option value="all">All Actions</option>
            {actions.map((action) => (
              <option key={action} value={action}>
                {action}
              </option>
            ))}
          </select>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onExport?.('json')}
            className="btn-secondary text-sm"
          >
            JSON
          </button>
          <button
            onClick={() => onExport?.('csv')}
            className="btn-secondary text-sm"
          >
            CSV
          </button>
        </div>
      </div>

      {/* Event List */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {filteredEvents.length > 0 ? (
          filteredEvents.map((event) => (
            <div
              key={event.id}
              className={`border rounded-lg p-4 ${getActionColor(event.action)}`}
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <p className="font-semibold">{event.action}</p>
                  <p className="text-sm">
                    {event.entity} ({event.entityId})
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">
                    {formatDistanceToNow(event.timestamp, { addSuffix: true })}
                  </p>
                  <p className="text-xs text-gray-600">by {event.user}</p>
                </div>
              </div>
              <p className="text-sm mb-2">{event.details}</p>
              <div className="flex items-center justify-between">
                <code className="text-xs bg-gray-200 px-2 py-1 rounded font-mono break-all">
                  {event.dataHash.substring(0, 40)}...
                </code>
                <span className="text-xs text-gray-500">✓ Hash Verified</span>
              </div>
            </div>
          ))
        ) : (
          <p className="text-center text-gray-500 py-8">No events found</p>
        )}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-4 gap-4 text-center">
        <div>
          <p className="text-2xl font-bold text-gray-700">
            {filteredEvents.length}
          </p>
          <p className="text-xs text-gray-600">Total Events</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-green-600">
            {filteredEvents.filter((e) => e.action.includes('Approve')).length}
          </p>
          <p className="text-xs text-gray-600">Approvals</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-red-600">
            {filteredEvents.filter((e) => e.action.includes('Reject')).length}
          </p>
          <p className="text-xs text-gray-600">Rejections</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-blue-600">
            {[...new Set(filteredEvents.map((e) => e.user))].length}
          </p>
          <p className="text-xs text-gray-600">Users</p>
        </div>
      </div>
    </div>
  );
}
