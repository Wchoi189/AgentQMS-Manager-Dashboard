import React, { useState } from 'react';
import {
    Activity,
    AlertTriangle,
    Box,
    Code,
    FileCode,
    Combine,
    GitCommit,
    Layers,
    LayoutGrid,
    Search,
    ChevronRight,
    ChevronDown,
    FileText
} from 'lucide-react';

interface ASTData {
    summary: {
        total_files: number;
        total_classes: number;
        total_functions: number;
        total_complexity: number;
        total_lines: number;
        avg_complexity_per_function: number;
        avg_lines_per_file: number;
    };
    code_smells: string[];
    high_complexity_functions: Array<{
        file: string;
        function: string;
        complexity: number;
    }>;
    files: Array<{
        file: string;
        classes: Array<{
            name: string;
            line: number;
            methods: string[];
            docstring: string | null;
        }>;
        functions: Array<{
            name: string;
            line: number;
            args: string[];
            complexity: number;
            docstring: string | null;
            returns: string | null;
        }>;
        imports: any[];
        total_complexity: number;
        line_count: number;
    }>;
}

interface ASTVisualizerProps {
    data: ASTData;
}

const MetricCard = ({ label, value, icon: Icon, color = "blue" }: { label: string; value: string | number; icon: any; color?: string }) => (
    <div className="bg-slate-900/50 border border-slate-700/50 rounded-xl p-4 flex items-center gap-4 hover:border-slate-600 transition-colors">
        <div className={`p-3 rounded-lg bg-${color}-500/10 text-${color}-400`}>
            <Icon size={24} />
        </div>
        <div>
            <div className="text-2xl font-bold text-white tracking-tight">{value}</div>
            <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">{label}</div>
        </div>
    </div>
);

const FileTreeItem = ({ file }: { file: ASTData['files'][0] }) => {
    const [isOpen, setIsOpen] = useState(false);

    // Determine file health color based on complexity
    const healthColor = file.total_complexity > 20 ? 'text-red-400' : file.total_complexity > 10 ? 'text-yellow-400' : 'text-slate-400';

    return (
        <div className="border border-slate-700/50 rounded-lg bg-slate-900/30 overflow-hidden">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between p-3 hover:bg-slate-800/50 transition-colors"
            >
                <div className="flex items-center gap-3">
                    <FileCode size={18} className="text-blue-400" />
                    <span className="font-mono text-sm text-slate-200">{file.file}</span>
                </div>
                <div className="flex items-center gap-4 text-xs">
                    <span className={`font-mono ${healthColor} flex items-center gap-1`}>
                        <Activity size={14} />
                        {file.total_complexity}
                    </span>
                    <span className="text-slate-500">{file.classes.length} classes</span>
                    <span className="text-slate-500">{file.functions.length} funcs</span>
                    {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                </div>
            </button>

            {isOpen && (
                <div className="p-3 bg-slate-950/30 border-t border-slate-700/50 space-y-3 animate-in slide-in-from-top-2">
                    {file.classes.length > 0 && (
                        <div>
                            <div className="text-xs font-semibold text-slate-500 uppercase mb-2 ml-1">Classes</div>
                            <div className="space-y-1">
                                {file.classes.map((cls, idx) => (
                                    <div key={idx} className="ml-2 flex items-start gap-2 text-sm text-slate-300">
                                        <Box size={14} className="mt-1 text-purple-400" />
                                        <div>
                                            <span className="font-semibold text-purple-200">{cls.name}</span>
                                            {cls.methods.length > 0 && (
                                                <div className="text-xs text-slate-500 mt-0.5">
                                                    Methods: {cls.methods.join(", ")}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {file.functions.length > 0 && (
                        <div>
                            <div className="text-xs font-semibold text-slate-500 uppercase mb-2 ml-1">Top Functions</div>
                            <div className="space-y-1">
                                {file.functions.map((func, idx) => (
                                    <div key={idx} className="ml-2 flex items-center justify-between text-sm text-slate-300 group">
                                        <div className="flex items-center gap-2">
                                            <Code size={14} className="text-green-400" />
                                            <span>{func.name}()</span>
                                            <span className="text-slate-600 text-xs">Line {func.line}</span>
                                        </div>
                                        <span className={`text-xs font-mono px-1.5 py-0.5 rounded ${func.complexity > 5 ? 'bg-red-500/20 text-red-400' : 'bg-slate-800 text-slate-500'
                                            }`}>
                                            CC: {func.complexity}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

const ASTVisualizer: React.FC<ASTVisualizerProps> = ({ data }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [view, setView] = useState<'files' | 'smells'>('files');

    const filteredFiles = data.files.filter(f =>
        f.file.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="h-full flex flex-col gap-6 animate-in fade-in duration-500">
            {/* Header Structure Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <MetricCard
                    label="Analyzed Files"
                    value={data.summary.total_files}
                    icon={FileText}
                    color="blue"
                />
                <MetricCard
                    label="Code Objects"
                    value={data.summary.total_classes + data.summary.total_functions}
                    icon={LayoutGrid}
                    color="purple"
                />
                <MetricCard
                    label="Avg Complexity"
                    value={data.summary.avg_complexity_per_function}
                    icon={Activity}
                    color={data.summary.avg_complexity_per_function > 10 ? 'red' : 'green'}
                />
                <MetricCard
                    label="Total LOC"
                    value={data.summary.total_lines.toLocaleString()}
                    icon={GitCommit}
                    color="slate"
                />
            </div>

            <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column: File Explorer */}
                <div className="lg:col-span-2 flex flex-col bg-slate-800/50 rounded-xl border border-slate-700/50 overflow-hidden">
                    <div className="p-4 border-b border-slate-700/50 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Layers className="text-slate-400" size={18} />
                            <h3 className="font-semibold text-white">Project Structure</h3>
                        </div>
                        <div className="relative">
                            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                            <input
                                type="text"
                                placeholder="Filter files..."
                                className="bg-slate-900 border border-slate-700 rounded-full pl-9 pr-4 py-1 text-sm text-slate-300 focus:outline-none focus:border-blue-500 w-48 transition-all"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
                        {filteredFiles.map((file, idx) => (
                            <FileTreeItem key={idx} file={file} />
                        ))}
                    </div>
                </div>

                {/* Right Column: Insights & Smells */}
                <div className="flex flex-col gap-4">
                    {/* High Complexity Warning */}
                    <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-4 flex-1 overflow-hidden flex flex-col">
                        <div className="flex items-center gap-2 mb-4">
                            <AlertTriangle className="text-yellow-500" size={18} />
                            <h3 className="font-semibold text-white">Complexity Hotspots</h3>
                        </div>

                        <div className="flex-1 overflow-y-auto space-y-3 custom-scrollbar pr-2">
                            {data.high_complexity_functions.length === 0 ? (
                                <div className="text-center py-8 text-slate-500 text-sm">
                                    <Activity size={32} className="mx-auto mb-2 opacity-50" />
                                    No high complexity functions found.
                                </div>
                            ) : (
                                data.high_complexity_functions.map((func, idx) => (
                                    <div key={idx} className="bg-red-500/5 border border-red-500/20 rounded-lg p-3">
                                        <div className="flex justify-between items-start mb-1">
                                            <span className="font-mono text-sm font-semibold text-red-200">{func.function}</span>
                                            <span className="text-xs font-bold text-red-400 bg-red-500/10 px-2 py-0.5 rounded-full">
                                                CC: {func.complexity}
                                            </span>
                                        </div>
                                        <div className="text-xs text-slate-500 truncate" title={func.file}>
                                            {func.file}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Code Smells */}
                    <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-4 h-1/3 flex flex-col">
                        <div className="flex items-center gap-2 mb-4">
                            <Combine className="text-orange-400" size={18} />
                            <h3 className="font-semibold text-white">Analysis Alerts</h3>
                        </div>
                        <div className="flex-1 overflow-y-auto">
                            {data.code_smells.length === 0 ? (
                                <p className="text-sm text-slate-500">No warnings generated.</p>
                            ) : (
                                <ul className="space-y-2">
                                    {data.code_smells.map((smell, idx) => (
                                        <li key={idx} className="text-sm text-orange-200 bg-orange-500/10 px-3 py-2 rounded border border-orange-500/20">
                                            {smell}
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ASTVisualizer;
