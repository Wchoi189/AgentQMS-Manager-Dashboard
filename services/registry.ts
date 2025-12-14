import { DocEntry } from '../types';
import { bridgeService } from './bridgeService';

export interface SystemStats {
  totalDocs: number;
  docGrowth: number;
  referenceHealth: number;
  brokenLinks: number;
  pendingMigrations: number;
  distribution: { name: string; valid: number; issues: number }[];
}

/**
 * Registry Service
 * Adapts the backend Bridge API for UI consumption.
 */

export const getRegistry = async (): Promise<DocEntry[]> => {
  try {
    const response = await bridgeService.getRegistry();
    // Backend returns { items: ArtifactResponse[], total: number }
    const items = response.items || [];

    return items.map((item: any) => ({
      path: item.path,
      udi: item.id, // Use ID as UDI for now
      title: item.title,
      lastModified: item.created_at || new Date().toISOString(),
      contentSnippet: "" // List view doesn't provide content
    }));
  } catch (e) {
    console.warn("Bridge unconnected. Returning empty registry.", e);
    return [];
  }
};

export const resolveUDI = async (udi: string): Promise<DocEntry | undefined> => {
  const registry = await getRegistry();
  return registry.find(doc => doc.udi === udi);
};

export const resolvePath = async (path: string): Promise<DocEntry | undefined> => {
  const registry = await getRegistry();
  // Simple fuzzy match
  return registry.find(doc => doc.path.includes(path) || path.includes(doc.path));
};

export const generateUDI = (): string => {
  return `udi://doc-${Math.floor(Math.random() * 100000).toString().padStart(6, '0')}`;
};

export const getSystemStats = async (): Promise<SystemStats> => {
  try {
    const stats = await bridgeService.getSystemStats();
    return stats;
  } catch (error) {
    console.warn("Failed to fetch system stats, using fallback", error);
    // Fallback if backend offline
    return {
      totalDocs: 0,
      docGrowth: 0,
      referenceHealth: 0,
      brokenLinks: 0,
      pendingMigrations: 0,
      distribution: []
    };
  }
};

export const commitMigration = async (filePath: string, content: string): Promise<{ success: boolean; message: string }> => {
  try {
    const result = await bridgeService.writeFile(filePath, content);
    return {
      success: result.success,
      message: `Successfully wrote ${result.bytes_written} bytes to disk.`
    };
  } catch (error) {
    console.error("Migration failed:", error);
    return {
      success: false,
      message: error instanceof Error ? error.message : "Failed to write to disk via Bridge."
    };
  }
};