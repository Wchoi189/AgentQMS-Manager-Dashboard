import * as React from 'react';
import { useState, useEffect, useRef } from 'react';
import { ArrowLeft, Edit, Save, Trash2, Eye, Code, Loader2, FileText, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import remarkFrontmatter from 'remark-frontmatter';
import { remarkAlert } from 'remark-github-blockquote-alert';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';
import mermaid from 'mermaid';
import { bridgeService, Artifact } from '../services/bridgeService';

// Import KaTeX CSS
import 'katex/dist/katex.min.css';
// Import Highlight.js CSS
import 'highlight.js/styles/github-dark.css';
// Import custom styles for alerts if needed (or rely on inline/tailwind)
import 'remark-github-blockquote-alert/alert.css';

interface ArtifactViewerProps {
    artifactId: string;
    onBack: () => void;
}

const MermaidDiagram: React.FC<{ chart: string }> = ({ chart }) => {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (containerRef.current) {
            mermaid.init(undefined, containerRef.current);
        }
    }, [chart]);

    return (
        <div className="mermaid" ref={containerRef}>
            {chart}
        </div>
    );
};

const ArtifactViewer: React.FC<ArtifactViewerProps> = ({ artifactId, onBack }) => {
    const [artifact, setArtifact] = useState<Artifact | null>(null);
    const [content, setContent] = useState('');
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [deleting, setDeleting] = useState(false);
    const [mode, setMode] = useState<'preview' | 'source'>('preview');
    const [error, setError] = useState<string | null>(null);
    const [notification, setNotification] = useState<{ type: 'success' | 'error', message: string } | null>(null);

    useEffect(() => {
        mermaid.initialize({ startOnLoad: false, theme: 'dark' });
        loadArtifact();
    }, [artifactId]);

    const loadArtifact = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await bridgeService.getArtifact(artifactId);
            setArtifact(data);
            setContent(data.content || '');
            // Default to preview mode if content exists, otherwise source for new/empty
            setMode(data.content ? 'preview' : 'source');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load artifact');
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        if (!artifact) return;
        setSaving(true);
        setNotification(null);
        try {
            await bridgeService.updateArtifact(artifact.id, { content });
            setNotification({ type: 'success', message: 'Artifact saved successfully' });
            // Reload to ensure sync
            const updated = await bridgeService.getArtifact(artifact.id);
            setArtifact(updated);
        } catch (err) {
            setNotification({ type: 'error', message: err instanceof Error ? err.message : 'Failed to save' });
        } finally {
            setSaving(false);
            // Hide notification after 3s
            setTimeout(() => setNotification(null), 3000);
        }
    };

    const handleDelete = async () => {
        if (!artifact || !window.confirm('Are you sure you want to delete this artifact? This action cannot be undone.')) return;
        setDeleting(true);
        try {
            await bridgeService.deleteArtifact(artifact.id);
            onBack(); // Return to list
        } catch (err) {
            setNotification({ type: 'error', message: err instanceof Error ? err.message : 'Failed to delete' });
            setDeleting(false);
        }
    };

    if (loading) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-slate-400">
                <Loader2 className="animate-spin mb-4" size={32} />
                <p>Loading artifact...</p>
            </div>
        );
    }

    if (error || !artifact) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-red-400">
                <XCircle size={48} className="mb-4" />
                <p className="text-lg font-semibold">Error Loading Artifact</p>
                <p className="text-sm opacity-75 mb-6">{error || 'Artifact not found'}</p>
                <button
                    onClick={onBack}
                    className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors"
                >
                    <ArrowLeft size={16} /> Back to Library
                </button>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col bg-slate-900">
            {/* Header / Toolbar */}
            <div className="flex items-center justify-between p-4 border-b border-slate-700 bg-slate-800/50 backdrop-blur-sm sticky top-0 z-10">
                <div className="flex items-center gap-4">
                    <button
                        onClick={onBack}
                        className="p-2 hover:bg-slate-700 text-slate-400 hover:text-white rounded-full transition-colors"
                        title="Back to Library"
                    >
                        <ArrowLeft size={20} />
                    </button>
                    <div>
                        <h2 className="text-lg font-bold text-white leading-tight">{artifact.title}</h2>
                        <div className="flex items-center gap-2 text-xs text-slate-400">
                            <span className="font-mono bg-slate-950 px-1 rounded">{artifact.id}</span>
                            <span>•</span>
                            <span className="uppercase tracking-wider">{artifact.type.replace('_', ' ')}</span>
                            <span>•</span>
                            <span className={`capitalize ${artifact.status === 'active' ? 'text-green-400' : 'text-slate-500'}`}>
                                {artifact.status}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    {/* View Mode Toggle */}
                    <div className="flex bg-slate-950 rounded-lg p-1 border border-slate-700 mr-2">
                        <button
                            onClick={() => setMode('preview')}
                            className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-medium transition-all ${mode === 'preview' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
                                }`}
                        >
                            <Eye size={14} /> Preview
                        </button>
                        <button
                            onClick={() => setMode('source')}
                            className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-medium transition-all ${mode === 'source' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
                                }`}
                        >
                            <Code size={14} /> Source
                        </button>
                    </div>

                    <div className="h-6 w-px bg-slate-700 mx-2"></div>

                    {/* Actions */}
                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className="flex items-center gap-2 px-3 py-1.5 bg-green-600 hover:bg-green-500 disabled:opacity-50 text-white rounded text-xs font-medium transition-colors"
                    >
                        {saving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
                        Save
                    </button>
                    <button
                        onClick={handleDelete}
                        disabled={deleting}
                        className="flex items-center gap-2 px-3 py-1.5 bg-red-600/20 hover:bg-red-600/30 text-red-500 hover:text-red-400 disabled:opacity-50 rounded text-xs font-medium transition-colors border border-red-600/30"
                    >
                        {deleting ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
                        Delete
                    </button>
                </div>
            </div>

            {/* Notification Toast */}
            {notification && (
                <div className={`absolute top-20 right-8 px-4 py-2 rounded shadow-lg flex items-center gap-2 text-sm z-50 animate-in slide-in-from-right-10 fade-in ${notification.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
                    }`}>
                    {notification.type === 'success' ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
                    {notification.message}
                </div>
            )}

            {/* Content Area */}
            <div className="flex-1 overflow-hidden relative">
                {mode === 'preview' ? (
                    <div className="h-full overflow-y-auto p-8 custom-scrollbar bg-slate-900">
                        <div className="prose prose-invert max-w-4xl mx-auto prose-headings:font-bold prose-h1:text-3xl prose-h2:text-2xl prose-a:text-blue-400 prose-code:text-purple-300 prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800">
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm, remarkMath, remarkFrontmatter, remarkAlert]}
                                rehypePlugins={[rehypeKatex, rehypeHighlight]}
                                components={{
                                    code(props) {
                                        const { children, className, ...rest } = props;
                                        const match = /language-(\w+)/.exec(className || '');
                                        if (match && match[1] === 'mermaid') {
                                            return <MermaidDiagram chart={String(children).replace(/\n$/, '')} />;
                                        }
                                        return (
                                            <code className={className} {...rest}>
                                                {children}
                                            </code>
                                        );
                                    }
                                }}
                            >
                                {content}
                            </ReactMarkdown>
                        </div>
                    </div>
                ) : (
                    <div className="h-full p-0">
                        <textarea
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                            className="w-full h-full bg-slate-950 text-slate-300 font-mono text-sm p-6 resize-none focus:outline-none leading-relaxed"
                            placeholder="# Enter markdown content..."
                            spellCheck={false}
                        />
                    </div>
                )}
            </div>

            {/* Status Footer */}
            <div className="px-4 py-2 border-t border-slate-800 bg-slate-900/50 text-xs text-slate-500 flex justify-between">
                <span>Created: {artifact.created_at || 'Unknown'}</span>
                <span>{content.length} characters</span>
            </div>
        </div>
    );
};

export default ArtifactViewer;
