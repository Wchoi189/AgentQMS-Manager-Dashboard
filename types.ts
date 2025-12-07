
export enum AppView {
  DASHBOARD = 'DASHBOARD',
  ARTIFACT_GENERATOR = 'ARTIFACT_GENERATOR',
  FRAMEWORK_AUDITOR = 'FRAMEWORK_AUDITOR',
  STRATEGY_MAP = 'STRATEGY_MAP',
  INTEGRATION_HUB = 'INTEGRATION_HUB',
  CONTEXT_EXPLORER = 'CONTEXT_EXPLORER',
  SETTINGS = 'SETTINGS'
}

export enum AIProvider {
  GEMINI = 'GEMINI',
  OPENAI = 'OPENAI',
  OPENROUTER = 'OPENROUTER'
}

export interface AppSettings {
  provider: AIProvider;
  apiKey: string;
  model: string;
  baseUrl?: string; // For custom endpoints (Alibaba/Qwen via compatible API)
}

export interface ArtifactFormData {
  title: string;
  type: string;
  status: 'draft' | 'review' | 'approved' | 'deprecated';
  author: string;
  branchName: string;
  tags: string;
  description: string;
}

export interface AuditResponse {
  score: number;
  issues: string[];
  recommendations: string[];
  rawAnalysis: string;
}

export interface StrategyMetric {
  name: string;
  value: number;
  target: number;
}

// Visualization Types
export interface ContextNode {
  id: string;
  label: string;
  type: 'module' | 'plan' | 'audit' | 'report' | 'root';
  status: 'active' | 'pending' | 'archived';
  connections: string[];
}

export interface ContextBundle {
  name: string;
  nodes: ContextNode[];
}

// Database Types
export interface DBStatus {
  connected: boolean;
  version: string;
  lastBackup: string;
  recordCount: number;
  health: 'healthy' | 'degraded' | 'offline';
  issues: string[];
}

// Audit Tool Types
export interface AuditToolConfig {
  id: string;
  name: string;
  description: string;
  command: string;
  scriptPath: string;
  args: { name: string; flag: string; type: 'file' | 'text' | 'select'; options?: string[] }[];
}
