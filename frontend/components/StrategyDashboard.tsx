
import React, { useState, useEffect } from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Database, Layers, GitBranch, Search, Lightbulb, Loader2 } from 'lucide-react';
import { generateArchitectureAdvice } from '../services/aiService';

interface DirectoryTree {
    name: string;
    path: string;
    type: string;
    file_count: number;
    children: DirectoryTree[];
}

const StrategyDashboard: React.FC = () => {
    const [advice, setAdvice] = useState<string>("");
    const [loadingAdvice, setLoadingAdvice] = useState(false);
    const [directoryTree, setDirectoryTree] = useState<DirectoryTree | null>(null);
    const [loadingDirectory, setLoadingDirectory] = useState(true);
    const [metrics, setMetrics] = useState([
        { name: 'Schema Compliance', current: 0, target: 100 },
        { name: 'Branch Integration', current: 0, target: 100 },
        { name: 'Timestamp Accuracy', current: 0, target: 100 },
        { name: 'Index Coverage', current: 0, target: 100 },
    ]);
    const [loadingMetrics, setLoadingMetrics] = useState(true);

    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                const response = await fetch('/api/v1/compliance/metrics');
                if (response.ok) {
                    const data = await response.json();
                    console.log('Compliance metrics received:', data);
                    setMetrics([
                        { name: 'Schema Compliance', current: data.schema_compliance || 0, target: 100 },
                        { name: 'Branch Integration', current: data.branch_integration || 0, target: 100 },
                        { name: 'Timestamp Accuracy', current: data.timestamp_accuracy || 0, target: 100 },
                        { name: 'Index Coverage', current: data.index_coverage || 0, target: 100 },
                    ]);
                } else {
                    console.error('Failed to fetch compliance metrics:', response.status, response.statusText);
                    const errorText = await response.text();
                    console.error('Error response:', errorText);
                }
            } catch (error) {
                console.error('Failed to fetch compliance metrics:', error);
            } finally {
                setLoadingMetrics(false);
            }
        };
        fetchMetrics();
    }, []);

    useEffect(() => {
        const fetchDirectoryStructure = async () => {
            setLoadingDirectory(true);
            try {
                const response = await fetch('/api/v1/system/directory-structure');
                if (response.ok) {
                    const data = await response.json();
                    setDirectoryTree(data.tree);
                }
            } catch (error) {
                console.error('Failed to fetch directory structure:', error);
            } finally {
                setLoadingDirectory(false);
            }
        };
        fetchDirectoryStructure();
    }, []);

    const askAdvice = async (topic: string) => {
        setLoadingAdvice(true);
        try {
            const result = await generateArchitectureAdvice(topic, directoryTree || undefined);
            setAdvice(result);
        } catch (error) {
            setAdvice("Unable to generate advice. Please check your API settings.");
        } finally {
            setLoadingAdvice(false);
        }
    }

    const formatDirectoryTree = (node: DirectoryTree, indent: string = ""): string => {
        let result = `${indent}${node.name}/`;
        if (node.file_count > 0) {
            result += ` # ${node.file_count} file${node.file_count !== 1 ? 's' : ''}`;
        }
        result += "\n";
        for (const child of node.children) {
            result += formatDirectoryTree(child, indent + "├── ");
        }
        return result;
    }

  return (
    <div className="h-full overflow-y-auto pr-2">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-2">Strategy & Architecture</h2>
        <p className="text-slate-400">Framework health, indexing strategy, and containerization roadmap.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Metric Cards */}
        <div className="bg-slate-800 p-5 rounded-xl border border-slate-700">
            <div className="flex items-center gap-3 mb-2 text-blue-400">
                <Database size={24} />
                <h3 className="font-semibold text-lg">Indexing Status</h3>
            </div>
            <div className="flex items-center gap-2 mb-2">
                <span className="px-3 py-1 bg-slate-700/50 text-slate-400 text-xs font-medium rounded-full border border-slate-600">Coming Soon</span>
            </div>
            <p className="text-sm text-slate-500 mt-1">Advanced indexing analysis will be available in a future release.</p>
        </div>

        <div className="bg-slate-800 p-5 rounded-xl border border-slate-700">
            <div className="flex items-center gap-3 mb-2 text-purple-400">
                <Layers size={24} />
                <h3 className="font-semibold text-lg">Containerization</h3>
            </div>
            <div className="flex items-center gap-2 mb-2">
                <span className="px-3 py-1 bg-slate-700/50 text-slate-400 text-xs font-medium rounded-full border border-slate-600">Coming Soon</span>
            </div>
            <p className="text-sm text-slate-500 mt-1">Containerization status tracking will be available in a future release.</p>
        </div>

        <div className="bg-slate-800 p-5 rounded-xl border border-slate-700">
            <div className="flex items-center gap-3 mb-2 text-green-400">
                <GitBranch size={24} />
                <h3 className="font-semibold text-lg">Traceability</h3>
            </div>
            <div className="flex items-center gap-2 mb-2">
                <span className="px-3 py-1 bg-green-500/20 text-green-400 text-xs font-medium rounded-full border border-green-500/30">Active</span>
            </div>
            <p className="text-sm text-slate-500 mt-1">New `branch_name` enforcement active. Timestamp accuracy standardized.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Chart */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700" style={{ minHeight: '320px' }}>
          <h3 className="text-lg font-semibold text-white mb-4">Framework Health Audit</h3>
          <div style={{ width: '100%', height: '280px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metrics} layout="vertical" margin={{ top: 5, right: 30, left: 120, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" />
                <YAxis dataKey="name" type="category" stroke="#94a3b8" width={110} tick={{fontSize: 12}} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569', color: '#fff' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Legend />
                <Bar dataKey="current" name="Current State" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                <Bar dataKey="target" name="Target" fill="#1e293b" stroke="#3b82f6" strokeDasharray="4 4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Architect */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 flex flex-col">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Lightbulb className="text-yellow-400" /> AI Architect Advisor
            </h3>
            <div className="flex gap-2 mb-4 flex-wrap">
                <button 
                    onClick={() => askAdvice('Professional Indexing System')} 
                    disabled={true}
                    className="bg-slate-800 text-slate-500 px-3 py-1.5 rounded text-xs cursor-not-allowed border border-slate-700 relative group"
                    title="Advanced feature - Coming in future release"
                >
                    Indexing
                </button>
                <button 
                    onClick={() => askAdvice('Containerized Design')} 
                    className="bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded text-xs text-white transition"
                    title="Get advice on containerizing documentation structure"
                >
                    Containerization
                </button>
                <button 
                    onClick={() => askAdvice('Self-Auditing Framework')} 
                    className="bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded text-xs text-white transition"
                    title="Get advice on implementing self-auditing capabilities"
                >
                    Self-Audit
                </button>
            </div>
            <div className="flex-1 bg-slate-900 rounded p-4 overflow-y-auto border border-slate-700/50">
                {loadingAdvice ? (
                    <div className="text-slate-500 text-sm animate-pulse">Consulting knowledge base...</div>
                ) : advice ? (
                    <div className="prose prose-invert prose-sm">
                        <p className="whitespace-pre-wrap text-slate-300 text-sm">{advice}</p>
                    </div>
                ) : (
                    <div className="text-slate-600 text-sm italic">Select a topic above to receive strategic architectural recommendations.</div>
                )}
            </div>
        </div>
      </div>

       <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Search className="text-teal-400" /> Current Directory Structure
            </h3>
            {loadingDirectory ? (
                <div className="flex items-center justify-center py-8">
                    <Loader2 className="animate-spin text-teal-400" size={24} />
                    <span className="ml-3 text-slate-400 text-sm">Scanning directory structure...</span>
                </div>
            ) : directoryTree ? (
                <div className="font-mono text-sm text-slate-400 whitespace-pre bg-slate-950 p-4 rounded border border-slate-800 overflow-x-auto">
                    {formatDirectoryTree(directoryTree)}
                </div>
            ) : (
                <div className="text-slate-500 text-sm italic py-4">
                    Unable to load directory structure. Please check backend connection.
                </div>
            )}
       </div>
    </div>
  );
};

export default StrategyDashboard;
