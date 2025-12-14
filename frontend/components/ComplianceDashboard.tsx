import React, { useEffect, useState } from 'react';
import { validateCompliance, ValidationResult } from '../services/complianceService';
import ComplianceBadge from './ComplianceBadge';
import ViolationList from './ViolationList';
import { RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react';

const ComplianceDashboard: React.FC = () => {
    const [data, setData] = useState<ValidationResult | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const result = await validateCompliance();
            setData(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown error occurred');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <RefreshCw className="animate-spin text-blue-500 w-8 h-8" />
                <span className="ml-2 text-slate-400">Running compliance checks...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center text-red-700 mb-2">
                    <AlertTriangle className="w-5 h-5 mr-2" />
                    <h3 className="font-semibold">Error Loading Compliance Data</h3>
                </div>
                <p className="text-red-600">{error}</p>
                <button
                    onClick={fetchData}
                    className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
                >
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header / Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                    <h3 className="text-slate-500 text-sm font-medium uppercase tracking-wide mb-2">System Health</h3>
                    <div className="flex items-center justify-between">
                        <span className="text-3xl font-bold text-slate-900">{data?.score}%</span>
                        <ComplianceBadge score={data?.score || 0} isCompliant={data?.is_compliant || false} />
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                    <h3 className="text-slate-500 text-sm font-medium uppercase tracking-wide mb-2">Files Scanned</h3>
                    <div className="flex items-center">
                        <span className="text-3xl font-bold text-slate-900">{data?.total_files}</span>
                        <span className="ml-2 text-sm text-slate-500">docs checked</span>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                    <h3 className="text-slate-500 text-sm font-medium uppercase tracking-wide mb-2">Compliance Status</h3>
                    <div className="flex items-center">
                        <CheckCircle className={`w-8 h-8 ${data?.is_compliant ? 'text-green-500' : 'text-orange-500'} mr-3`} />
                        <div>
                            <p className="font-medium text-slate-900">{data?.is_compliant ? 'All Checks Passed' : 'Violations Found'}</p>
                            <p className="text-sm text-slate-500">{data?.violations.length} active violations</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="p-6 border-b border-slate-200 flex justify-between items-center">
                    <h2 className="text-lg font-semibold text-slate-900">Compliance Violations</h2>
                    <button onClick={fetchData} className="flex items-center text-sm text-blue-600 hover:text-blue-800">
                        <RefreshCw className="w-4 h-4 mr-1" /> Refresh
                    </button>
                </div>
                <div className="p-0">
                    <ViolationList violations={data?.violations || []} onFixApplied={fetchData} />
                </div>
            </div>
        </div>
    );
};

export default ComplianceDashboard;
