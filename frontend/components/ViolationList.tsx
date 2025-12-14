import React, { useState } from 'react';
import { Violation, fixViolation } from '../services/complianceService';
import { Wrench, Loader2, Check, Eye, X } from 'lucide-react';

interface ViolationListProps {
    violations: Violation[];
    onFixApplied?: () => void;
}

const ViolationList: React.FC<ViolationListProps> = ({ violations, onFixApplied }) => {
    const [fixing, setFixing] = useState<string | null>(null);
    const [previewData, setPreviewData] = useState<{ diff: string, violation: Violation } | null>(null);
    const [loadingPreview, setLoadingPreview] = useState<string | null>(null);

    const handlePreview = async (violation: Violation) => {
        const violationKey = `${violation.file}-${violation.rule_id}`;
        setLoadingPreview(violationKey);
        try {
            // @ts-ignore - path might not be in the interface but is in API
            const fullPath = violation.path || "";
            const result = await fixViolation(fullPath, violation.rule_id, true); // dryRun = true
            if (result.success && result.diff) {
                setPreviewData({ diff: result.diff, violation });
            } else {
                alert(`No changes generated: ${result.message}`);
            }
        } catch (err) {
            alert(`Preview failed: ${err}`);
        } finally {
            setLoadingPreview(null);
        }
    };

    const confirmFix = async (violation: Violation) => {
        // Close preview
        setPreviewData(null);
        await handleFix(violation);
    }

    const handleFix = async (violation: Violation) => {
        // Unique ID for the row
        const violationKey = `${violation.file}-${violation.rule_id}`;
        setFixing(violationKey);

        try {
            // @ts-ignore - path might not be in the interface but is in API
            const fullPath = violation.path || "";
            if (!fullPath) {
                alert("Cannot fix: File path missing");
                return;
            }

            await fixViolation(fullPath, violation.rule_id, false); // dryRun = false
            if (onFixApplied) {
                onFixApplied(); // Refresh data
            }
        } catch (err) {
            alert(`Fix failed: ${err}`);
        } finally {
            setFixing(null);
        }
    };

    if (!violations || violations.length === 0) {
        return (
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-md text-slate-500 text-center">
                No violations found. Good job!
            </div>
        );
    }

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'critical': return 'text-red-600 bg-red-50';
            case 'high': return 'text-orange-600 bg-orange-50';
            case 'medium': return 'text-yellow-600 bg-yellow-50';
            case 'low': return 'text-blue-600 bg-blue-50';
            default: return 'text-slate-600 bg-slate-50';
        }
    };

    // Only some rules are auto-fixable in Phase 3
    const isFixable = (ruleId: string) => {
        return ['missing_required_field', 'invalid_status'].includes(ruleId);
    };

    return (
        <>
            {/* Modal for Preview */}
            {previewData && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                    <div className="bg-white rounded-xl shadow-2xl w-full max-w-3xl overflow-hidden flex flex-col max-h-[90vh] animate-in zoom-in-95 duration-200">
                        <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
                            <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                                <Eye size={18} className="text-blue-500" />
                                Confirm Fix: <span className="font-mono text-sm bg-slate-200 px-2 py-0.5 rounded text-slate-600">{previewData.violation.file}</span>
                            </h3>
                            <button onClick={() => setPreviewData(null)} className="text-slate-400 hover:text-slate-600">
                                <X size={20} />
                            </button>
                        </div>
                        <div className="p-0 overflow-auto bg-slate-900 flex-1">
                            <pre className="text-xs font-mono text-slate-300 p-4 whitespace-pre-wrap">
                                {previewData.diff}
                            </pre>
                        </div>
                        <div className="p-4 border-t border-slate-200 flex justify-end gap-2 bg-white">
                            <button
                                onClick={() => setPreviewData(null)}
                                className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg transition"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={() => confirmFix(previewData.violation)}
                                className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition shadow-sm flex items-center gap-2"
                            >
                                <Wrench size={14} />
                                Apply Fix
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className="overflow-x-auto shadow ring-1 ring-slate-900/5 sm:rounded-lg">
                <table className="min-w-full divide-y divide-slate-300">
                    <thead className="bg-slate-50">
                        <tr>
                            <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-slate-900 sm:pl-6">File</th>
                            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">Rule ID</th>
                            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">Severity</th>
                            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">Message</th>
                            <th scope="col" className="px-3 py-3.5 text-right text-sm font-semibold text-slate-900">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 bg-white">
                        {violations.map((violation, index) => {
                            const violationKey = `${violation.file}-${violation.rule_id}-${index}`;
                            const isProcessing = fixing === `${violation.file}-${violation.rule_id}`;
                            const isPreviewing = loadingPreview === `${violation.file}-${violation.rule_id}`;

                            return (
                                <tr key={violationKey}>
                                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-slate-900 sm:pl-6">
                                        {violation.file}
                                    </td>
                                    <td className="whitespace-nowrap px-3 py-4 text-sm text-slate-500">
                                        <code className="bg-slate-100 px-1 py-0.5 rounded text-xs">{violation.rule_id}</code>
                                    </td>
                                    <td className="whitespace-nowrap px-3 py-4 text-sm">
                                        <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ring-slate-500/10 ${getSeverityColor(violation.severity)}`}>
                                            {violation.severity}
                                        </span>
                                    </td>
                                    <td className="px-3 py-4 text-sm text-slate-500">
                                        {violation.message}
                                    </td>
                                    <td className="px-3 py-4 text-sm text-right">
                                        {isFixable(violation.rule_id) && (
                                            <div className="flex justify-end gap-2">
                                                <button
                                                    onClick={() => handlePreview(violation)}
                                                    disabled={isProcessing || isPreviewing}
                                                    className="inline-flex items-center px-2.5 py-1.5 border border-slate-300 shadow-sm text-xs font-medium rounded text-slate-700 bg-white hover:bg-slate-50 focus:outline-none disabled:opacity-50"
                                                    title="Dry Run / Preview"
                                                >
                                                    {isPreviewing ? <Loader2 className="w-3 h-3 animate-spin" /> : <Eye className="w-3 h-3" />}
                                                </button>
                                                <button
                                                    onClick={() => handleFix(violation)}
                                                    disabled={isProcessing || isPreviewing}
                                                    className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                                                >
                                                    {isProcessing ? (
                                                        <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                                                    ) : (
                                                        <Wrench className="w-3 h-3 mr-1" />
                                                    )}
                                                    Quick Fix
                                                </button>
                                            </div>
                                        )}
                                    </td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>
            </div>
        </>
    );
};

export default ViolationList;
