import React, { useState } from 'react';
import { ShieldCheck, AlertTriangle, CheckCircle, Loader2, ArrowRight, Terminal, Wand2, ClipboardPaste, Eye } from 'lucide-react';
import { auditDocumentation } from '../services/aiService';
import { AuditResponse, AuditToolConfig } from '../types';
import ASTVisualizer from './ASTVisualizer';

// Mock Tool Definitions based on 'AgentQMS/agent_tools/audit/*.py'
const AUDIT_TOOLS: AuditToolConfig[] = [
    {
        id: 'validate_frontmatter',
        name: 'Frontmatter Validator',
        description: 'Checks for mandatory fields (branch_name, timestamp) in YAML header.',
        command: 'python AgentQMS/agent_tools/audit/validate_frontmatter.py',
        scriptPath: 'agent_tools/audit/validate_frontmatter.py',
        args: [{ name: 'Target File', flag: '--file', type: 'text', placeholder: 'e.g., docs/architecture/README.md' }]
    },
    {
        id: 'check_links',
        name: 'Dead Link Checker',
        description: 'Scans markdown files for broken internal and external links.',
        command: 'python AgentQMS/agent_tools/audit/check_links.py',
        scriptPath: 'agent_tools/audit/check_links.py',
        args: [{ name: 'Directory', flag: '--dir', type: 'text', placeholder: 'e.g., docs/' }]
    },
    {
        id: 'structure_audit',
        name: 'Structural Integrity',
        description: 'Verifies that the folder structure matches the .agentqms/config.json rules.',
        command: 'python AgentQMS/agent_tools/audit/structure_check.py',
        scriptPath: 'agent_tools/audit/structure_check.py',
        args: []
    },
    {
        id: 'ast_analyzer',
        name: 'AST Analyzer',
        description: 'Analyzes Python code structure, complexity, and code smells.',
        command: 'python AgentQMS/scripts/ast_analysis_cli.py check-quality',
        scriptPath: 'scripts/ast_analysis_cli.py',
        args: [{ name: 'Target Path', flag: '', type: 'text', placeholder: 'e.g., AgentQMS/' }]
    }
];

const FrameworkAuditor: React.FC = () => {
    const [mode, setMode] = useState<'ai' | 'tool'>('tool');
    const [activeTab, setActiveTab] = useState<'config' | 'visualize'>('config');

    // AI State
    const [inputContent, setInputContent] = useState('');
    const [isAuditing, setIsAuditing] = useState(false);
    const [result, setResult] = useState<AuditResponse | null>(null);

    // Tool State
    const [selectedTool, setSelectedTool] = useState<AuditToolConfig>(AUDIT_TOOLS[0]);
    const [toolArgs, setToolArgs] = useState<Record<string, string>>({});
    const [generatedCommand, setGeneratedCommand] = useState('');

    // Visualization State
    const [pastedJson, setPastedJson] = useState('');
    const [parsedData, setParsedData] = useState<any>(null);

    const handleAiAudit = async () => {
        if (!inputContent.trim()) return;
        setIsAuditing(true);
        setResult(null);

        try {
            const data = await auditDocumentation(inputContent, 'Generic');
            setResult(data);
        } catch (e) {
            console.error(e);
            setResult({
                score: 0,
                issues: ["Audit Process Failed", e instanceof Error ? e.message : "Unknown Error"],
                recommendations: ["Check Settings > API Key"],
                rawAnalysis: "System encountered an error."
            });
        } finally {
            setIsAuditing(false);
        }
    };

    const updateToolCommand = (tool: AuditToolConfig, args: Record<string, string>) => {
        let cmd = tool.command;
        // Handle positional args (empty flag) separate from flagged args if needed, 
        // but for now simple appending checks
        tool.args.forEach(arg => {
            const val = args[arg.name];
            if (val) {
                if (arg.flag === '') {
                    cmd += ` ${val}`;
                } else {
                    cmd += ` ${arg.flag} "${val}"`;
                }
            }
        });

        // Special case for AST Analyzer to ensure JSON output
        if (tool.id === 'ast_analyzer') {
            cmd += ' --json';
        }

        setGeneratedCommand(cmd);
    };

    const handleArgChange = (name: string, value: string) => {
        const newArgs = { ...toolArgs, [name]: value };
        setToolArgs(newArgs);
        updateToolCommand(selectedTool, newArgs);
    };

    const handleJsonPaste = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const json = e.target.value;
        setPastedJson(json);
        try {
            const data = JSON.parse(json);
            setParsedData(data);
        } catch (err) {
            setParsedData(null);
        }
    };

    return (
        <div className="h-full flex flex-col relative overflow-hidden">
            <div className="mb-6 flex justify-between items-end shrink-0">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-2">Framework Auditor</h2>
                    <p className="text-slate-400">Validate artifacts using AI Intelligence or Local Python Tools.</p>
                </div>
                <div className="flex bg-slate-800 rounded-lg p-1 border border-slate-700">
                    <button
                        onClick={() => setMode('ai')}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm transition-all ${mode === 'ai' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
                    >
                        <Wand2 size={16} /> AI Analysis
                    </button>
                    <button
                        onClick={() => setMode('tool')}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm transition-all ${mode === 'tool' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
                    >
                        <Terminal size={16} /> Tool Runner
                    </button>
                </div>
            </div>

            {mode === 'ai' ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full min-h-0 animate-in fade-in overflow-hidden">
                    {/* Input Area */}
                    <div className="flex flex-col h-full overflow-hidden">
                        <textarea
                            className="flex-1 w-full bg-slate-900 border border-slate-700 rounded-xl p-4 text-slate-300 font-mono text-sm focus:outline-none focus:border-blue-500 resize-none mb-4 custom-scrollbar"
                            placeholder="Paste document content here (including Frontmatter)..."
                            value={inputContent}
                            onChange={(e) => setInputContent(e.target.value)}
                        />
                        <button
                            onClick={handleAiAudit}
                            disabled={isAuditing || !inputContent}
                            className={`w-full py-3 rounded-lg flex items-center justify-center gap-2 font-semibold transition-all shrink-0 ${isAuditing || !inputContent
                                ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
                                : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/20'
                                }`}
                        >
                            {isAuditing ? <Loader2 className="animate-spin" /> : <ShieldCheck />}
                            {isAuditing ? 'Auditing...' : 'Run Compliance Audit'}
                        </button>
                    </div>

                    {/* Results Area */}
                    <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 overflow-y-auto custom-scrollbar">
                        {!result ? (
                            <div className="h-full flex flex-col items-center justify-center text-slate-500 opacity-50">
                                <ShieldCheck size={64} className="mb-4" />
                                <p>Awaiting input for analysis...</p>
                            </div>
                        ) : (
                            <div className="animate-in slide-in-from-bottom-4 duration-500">
                                <div className="flex items-center justify-between mb-6">
                                    <h3 className="text-lg font-semibold text-white">Audit Report</h3>
                                    <div className={`px-4 py-1.5 rounded-full font-bold text-sm ${result.score >= 90 ? 'bg-green-500/20 text-green-400 border border-green-500/50' :
                                        result.score >= 70 ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50' :
                                            'bg-red-500/20 text-red-400 border border-red-500/50'
                                        }`}>
                                        Score: {result.score}/100
                                    </div>
                                </div>

                                <div className="mb-6 p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                                    <h4 className="text-sm font-semibold text-slate-300 mb-2">Analysis Summary</h4>
                                    <p className="text-slate-400 text-sm">{result.rawAnalysis}</p>
                                </div>

                                <div className="mb-6">
                                    <h4 className="text-sm font-semibold text-red-400 mb-3 flex items-center gap-2">
                                        <AlertTriangle size={16} /> Issues Detected
                                    </h4>
                                    {result.issues.length === 0 ? (
                                        <p className="text-slate-500 text-sm italic">No critical issues found.</p>
                                    ) : (
                                        <ul className="space-y-2">
                                            {result.issues.map((issue, idx) => (
                                                <li key={idx} className="flex items-start gap-2 text-sm text-slate-300 bg-red-500/5 p-2 rounded">
                                                    <span className="mt-1 block min-w-[6px] h-1.5 rounded-full bg-red-500"></span>
                                                    {issue}
                                                </li>
                                            ))}
                                        </ul>
                                    )}
                                </div>

                                <div>
                                    <h4 className="text-sm font-semibold text-green-400 mb-3 flex items-center gap-2">
                                        <CheckCircle size={16} /> Recommended Actions
                                    </h4>
                                    <ul className="space-y-2">
                                        {result.recommendations.map((rec, idx) => (
                                            <li key={idx} className="flex items-start gap-2 text-sm text-slate-300 bg-green-500/5 p-2 rounded">
                                                <ArrowRight size={14} className="mt-1 text-green-500" />
                                                {rec}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            ) : (
                <div className="h-full flex flex-col animate-in fade-in overflow-hidden">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-full min-h-0">
                        {/* Tool Selection */}
                        <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 overflow-y-auto custom-scrollbar min-h-0">
                            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Available Tools</h3>
                            <div className="space-y-2">
                                {AUDIT_TOOLS.map(tool => (
                                    <button
                                        key={tool.id}
                                        onClick={() => {
                                            setSelectedTool(tool);
                                            setToolArgs({});
                                            setGeneratedCommand(tool.command + (tool.id === 'ast_analyzer' ? ' --json' : ''));
                                            setActiveTab('config');
                                            setPastedJson('');
                                            setParsedData(null);
                                        }}
                                        className={`w-full text-left p-3 rounded-lg border transition-all ${selectedTool.id === tool.id
                                            ? 'bg-blue-600/20 border-blue-500 text-white'
                                            : 'bg-slate-900 border-slate-800 text-slate-400 hover:bg-slate-800'
                                            }`}
                                    >
                                        <div className="font-semibold text-sm">{tool.name}</div>
                                        <div className="text-xs opacity-70 mt-1 truncate">{tool.description}</div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Configuration & Output */}
                        <div className="md:col-span-2 bg-slate-800 rounded-xl border border-slate-700 flex flex-col overflow-hidden min-h-0">
                            {/* Tabs */}
                            <div className="flex border-b border-slate-700">
                                <button
                                    onClick={() => setActiveTab('config')}
                                    className={`px-6 py-3 text-sm font-medium transition-colors ${activeTab === 'config' ? 'bg-slate-800 text-blue-400 border-b-2 border-blue-500' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'}`}
                                >
                                    Configuration & Run
                                </button>
                                {selectedTool.id === 'ast_analyzer' && (
                                    <button
                                        onClick={() => setActiveTab('visualize')}
                                        className={`px-6 py-3 text-sm font-medium transition-colors flex items-center gap-2 ${activeTab === 'visualize' ? 'bg-slate-800 text-purple-400 border-b-2 border-purple-500' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'}`}
                                    >
                                        <Eye size={16} /> Results Visualizer
                                    </button>
                                )}
                            </div>

                            <div className="p-6 flex-1 overflow-y-auto custom-scrollbar flex flex-col">
                                {activeTab === 'config' ? (
                                    <>
                                        <div className="mb-6 shrink-0">
                                            <h3 className="text-lg font-bold text-white mb-2">{selectedTool.name}</h3>
                                            <p className="text-slate-400 text-sm">{selectedTool.description}</p>
                                        </div>

                                        <div className="bg-slate-900 rounded-lg p-4 border border-slate-700 mb-6 shrink-0">
                                            <h4 className="text-xs font-semibold text-slate-500 uppercase mb-3">Configuration Arguments</h4>
                                            {selectedTool.args.length === 0 ? (
                                                <p className="text-sm text-slate-600 italic">No arguments required for this tool.</p>
                                            ) : (
                                                <div className="space-y-3">
                                                    {selectedTool.args.map((arg, idx) => (
                                                        <div key={idx}>
                                                            <label className="block text-xs font-medium text-slate-300 mb-1">
                                                                {arg.name} <span className="text-slate-600">({arg.flag || 'positional'})</span>
                                                            </label>
                                                            <input
                                                                type="text"
                                                                className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none placeholder:text-slate-700"
                                                                placeholder={arg.placeholder || `Enter ${arg.name}...`}
                                                                onChange={(e) => handleArgChange(arg.name, e.target.value)}
                                                            />
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>

                                        <div className="mt-auto shrink-0">
                                            <label className="block text-xs font-semibold text-slate-500 uppercase mb-2">Generated Execution Command</label>
                                            <div className="flex gap-2">
                                                <code className="flex-1 bg-black rounded-lg p-4 font-mono text-green-400 text-sm border border-slate-800 overflow-x-auto whitespace-nowrap">
                                                    {generatedCommand}
                                                </code>
                                                <button
                                                    onClick={() => {
                                                        navigator.clipboard.writeText(generatedCommand);
                                                        alert('Command copied! Run this in your terminal.');
                                                    }}
                                                    className="bg-slate-700 hover:bg-slate-600 text-white px-4 rounded-lg flex flex-col items-center justify-center gap-1 transition-colors shrink-0"
                                                >
                                                    <Terminal size={18} />
                                                    <span className="text-xs">Copy</span>
                                                </button>
                                            </div>
                                            <p className="text-xs text-yellow-500/80 mt-2 flex items-center gap-1">
                                                <AlertTriangle size={12} />
                                                Browser cannot execute Python directly. Copy command to run locally.
                                            </p>
                                        </div>
                                    </>
                                ) : (
                                    <div className="h-full flex flex-col">
                                        {!parsedData ? (
                                            <div className="flex-1 flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-700 rounded-xl p-8 transition-all hover:border-slate-600 bg-slate-900/30">
                                                <ClipboardPaste size={48} className="mb-4 opacity-50" />
                                                <h4 className="text-lg font-semibold text-slate-400 mb-2">Paste Analysis Output</h4>
                                                <p className="text-sm text-center max-w-md mb-6 opacity-70">
                                                    Run the command in your terminal with the <code className="bg-slate-800 px-1 py-0.5 rounded text-slate-300">--json</code> flag, then copy and paste the output here to visualize results.
                                                </p>
                                                <textarea
                                                    className="w-full max-w-2xl h-48 bg-slate-950 border border-slate-700 rounded-lg p-4 font-mono text-xs text-slate-300 focus:outline-none focus:border-purple-500"
                                                    placeholder='Paste JSON output here...'
                                                    value={pastedJson}
                                                    onChange={handleJsonPaste}
                                                />
                                                {pastedJson && !parsedData && (
                                                    <p className="text-red-400 text-xs mt-2">Invalid JSON format</p>
                                                )}
                                            </div>
                                        ) : (
                                            <div className="h-full flex flex-col">
                                                <div className="flex justify-between items-center mb-4 pb-4 border-b border-slate-700/50">
                                                    <h3 className="font-semibold text-white flex items-center gap-2">
                                                        <Eye className="text-purple-400" size={18} />
                                                        Analysis Results
                                                    </h3>
                                                    <button
                                                        onClick={() => {
                                                            setPastedJson('');
                                                            setParsedData(null);
                                                        }}
                                                        className="text-xs text-slate-400 hover:text-white"
                                                    >
                                                        Clear Data
                                                    </button>
                                                </div>
                                                <div className="flex-1 min-h-0">
                                                    <ASTVisualizer data={parsedData} />
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FrameworkAuditor;
