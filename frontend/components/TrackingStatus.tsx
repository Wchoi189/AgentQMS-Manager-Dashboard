import React, { useEffect, useState } from 'react';
import { Activity, AlertCircle } from 'lucide-react';
import { bridgeService, TrackingStatus } from '../services/bridgeService';

const TrackingStatusComponent: React.FC = () => {
  const [tracking, setTracking] = useState<TrackingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedKind, setSelectedKind] = useState<string>('all');

  useEffect(() => {
    loadTrackingStatus();
  }, [selectedKind]);

  const loadTrackingStatus = async () => {
    try {
      setLoading(true);
      const response = await bridgeService.getTrackingStatus(selectedKind);
      setTracking(response);
    } catch (error) {
      console.error('Failed to load tracking status:', error);
      setTracking({
        kind: selectedKind,
        status: 'Error loading tracking status',
        success: false,
        error: String(error),
      });
    } finally {
      setLoading(false);
    }
  };

  const kinds = ['all', 'plan', 'experiment', 'debug', 'refactor'];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Activity className="w-5 h-5 text-blue-500" />
        <h3 className="font-semibold text-sm">Tracking Database Status</h3>
      </div>

      {/* Kind Selector */}
      <div className="flex gap-2 flex-wrap">
        {kinds.map((kind) => (
          <button
            key={kind}
            onClick={() => setSelectedKind(kind)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${selectedKind === kind
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
          >
            {kind.charAt(0).toUpperCase() + kind.slice(1)}
          </button>
        ))}
      </div>

      {/* Status Display */}
      {loading ? (
        <div className="text-sm text-gray-500">Loading tracking status...</div>
      ) : tracking?.success ? (
        !tracking.status || tracking.status.includes("No plans found") ? (
          <div className="bg-slate-50 border border-slate-200 rounded p-4 text-center text-slate-500 text-sm">
            No {selectedKind === 'all' ? 'active plans' : selectedKind} found in database.
          </div>
        ) : (
          <div className="bg-green-50 border border-green-200 rounded p-3">
            <div className="space-y-1">
              {tracking.status.split(';').map((statusPart, index) => {
                const cleanedPart = statusPart.trim();
                if (!cleanedPart) return null;
                const [label, ...rest] = cleanedPart.split(':');
                const value = rest.join(':').trim();

                return (
                  <div key={index} className="flex justify-between items-start text-sm border-b border-green-200/50 last:border-0 pb-1 last:pb-0">
                    <span className="font-semibold text-green-900 capitalize">{label.trim()}</span>
                    <span className="text-green-700 ml-2 text-right">{value || 'N/A'}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-3 flex gap-2">
          <AlertCircle className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-yellow-800 font-medium">
              {tracking?.error || 'Unable to fetch tracking status'}
            </p>
            {tracking?.status && (
              <p className="text-sm text-yellow-700 mt-1">{tracking.status}</p>
            )}
          </div>
        </div>
      )}

      {/* Refresh Button */}
      <button
        onClick={loadTrackingStatus}
        disabled={loading}
        className="w-full px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm font-medium disabled:opacity-50"
      >
        {loading ? 'Refreshing...' : 'Refresh Status'}
      </button>
    </div>
  );
};

export default TrackingStatusComponent;
