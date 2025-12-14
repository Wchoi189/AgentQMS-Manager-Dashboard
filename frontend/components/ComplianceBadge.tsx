import React from 'react';

interface ComplianceBadgeProps {
    score: number;
    isCompliant: boolean;
}

const ComplianceBadge: React.FC<ComplianceBadgeProps> = ({ score, isCompliant }) => {
    // Determine color based on score or generic compliant status
    const bgColor = isCompliant ? 'bg-green-100' : 'bg-red-100';
    const textColor = isCompliant ? 'text-green-800' : 'text-red-800';
    const borderColor = isCompliant ? 'border-green-200' : 'border-red-200';

    return (
        <div className={`inline-flex items-center px-4 py-2 border rounded-full ${bgColor} ${borderColor}`}>
            <div className={`w-3 h-3 rounded-full mr-2 ${isCompliant ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <div className="flex flex-col">
                <span className={`text-sm font-medium ${textColor}`}>
                    {isCompliant ? 'Compliant' : 'Non-Compliant'}
                </span>
                <span className="text-xs text-slate-500 font-mono">
                    Score: {score}%
                </span>
            </div>
        </div>
    );
};

export default ComplianceBadge;
