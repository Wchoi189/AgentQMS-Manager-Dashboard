
import { GoogleGenAI } from "@google/genai";
import { AuditResponse, AIProvider, AppSettings } from "../types";
import { APP_CONFIG } from "../config/constants";

export const getSettings = (): AppSettings => {
  const saved = localStorage.getItem(APP_CONFIG.STORAGE.SETTINGS);
  if (saved) {
    return JSON.parse(saved);
  }
  return {
    provider: AIProvider.GEMINI,
    apiKey: process.env.API_KEY || '',
    model: APP_CONFIG.DEFAULTS.MODEL
  };
};

export const saveSettings = (settings: AppSettings) => {
  localStorage.setItem(APP_CONFIG.STORAGE.SETTINGS, JSON.stringify(settings));
};

// Generic Interface for AI Generation
interface AIRequestConfig {
  systemInstruction?: string;
  jsonMode?: boolean;
}

export const generateContent = async (prompt: string, config: AIRequestConfig = {}): Promise<string> => {
  const settings = getSettings();

  if (!settings.apiKey) {
    throw new Error("API Key is missing. Please configure it in Settings.");
  }

  // 1. Google Gemini Strategy
  if (settings.provider === AIProvider.GEMINI) {
    const ai = new GoogleGenAI({ apiKey: settings.apiKey });
    try {
      const response = await ai.models.generateContent({
        model: settings.model || APP_CONFIG.DEFAULTS.MODEL,
        contents: prompt,
        config: {
          systemInstruction: config.systemInstruction,
          responseMimeType: config.jsonMode ? "application/json" : "text/plain",
        }
      });
      return response.text || "";
    } catch (error) {
      console.error("Gemini API Error:", error);
      throw error;
    }
  }

  // 2. OpenAI / OpenRouter Strategy (Fetch-based)
  if (settings.provider === AIProvider.OPENAI || settings.provider === AIProvider.OPENROUTER) {
    const baseUrl = settings.provider === AIProvider.OPENROUTER 
      ? "https://openrouter.ai/api/v1" 
      : (settings.baseUrl || "https://api.openai.com/v1");
    
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${settings.apiKey}`
    };

    if (settings.provider === AIProvider.OPENROUTER) {
      headers["HTTP-Referer"] = window.location.origin;
      headers["X-Title"] = "AgentQMS";
    }

    try {
      const response = await fetch(`${baseUrl}/chat/completions`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          model: settings.model || "gpt-4-turbo",
          messages: [
            { role: "system", content: config.systemInstruction || "You are a helpful assistant." },
            { role: "user", content: prompt }
          ],
          response_format: config.jsonMode ? { type: "json_object" } : undefined
        })
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(`AI Provider Error: ${err.error?.message || response.statusText}`);
      }

      const data = await response.json();
      return data.choices[0]?.message?.content || "";
    } catch (error) {
      console.error(`${settings.provider} API Error:`, error);
      throw error;
    }
  }

  throw new Error("Unsupported AI Provider selected.");
};

export const auditDocumentation = async (content: string, type: string): Promise<AuditResponse> => {
  const systemInstruction = `
    You are AgentQMS, a Documentation Organization Efficiency Auditor.
    Your goal is to assess the organizational efficiency, consistency, and maintainability of documentation.
    
    Focus your assessment on:
    1. Organizational Efficiency: How well is the documentation structured? Are architectural documents separated from session notes?
    2. Consistency: Are naming conventions followed consistently? Is the structure predictable?
    3. Entry Points: Can users easily find what they need? Is navigation clear?
    4. Maintainability: Are there pain points that make maintenance difficult? Is there clutter?
    5. Opportunities: What specific improvements would enhance organization?
    
    DO NOT focus on frontmatter validation (that's handled by tools). Instead, assess:
    - How consistently conventions are followed
    - Whether architectural documents are separated from session notes
    - Clarity of entry points and navigation
    - Pain points in maintainability
    - Opportunities for organizational improvements
    
    Return a structured JSON assessment with keys: score (number 0-100), issues (string array), recommendations (string array), rawAnalysis (string).
    Score should reflect organizational efficiency (higher = better organized).
  `;

  const prompt = `Assess the organizational efficiency of this ${type} documentation:\n\n${content}\n\nProvide an organizational assessment focusing on structure, consistency, maintainability, and opportunities for improvement.`;
  
  try {
    const jsonStr = await generateContent(prompt, { 
      systemInstruction, 
      jsonMode: true 
    });
    return JSON.parse(jsonStr) as AuditResponse;
  } catch (error) {
    return {
      score: 0,
      issues: ["AI Audit Failed: " + (error instanceof Error ? error.message : "Unknown error")],
      recommendations: ["Check API Key in Settings", "Verify Model Availability"],
      rawAnalysis: "System error during audit."
    };
  }
};

interface DirectoryTree {
  name: string;
  path: string;
  type: string;
  file_count: number;
  children: DirectoryTree[];
}

export const generateArchitectureAdvice = async (
  topic: string, 
  directoryStructure?: DirectoryTree
): Promise<string> => {
  try {
    let prompt = `Based on the actual directory structure shown below, provide recommendations for improving documentation organization for: ${topic}.\n\n`;
    
    if (directoryStructure) {
      // Format directory tree as text
      const formatTree = (node: DirectoryTree, indent: string = ""): string => {
        let result = `${indent}${node.name}/ (${node.file_count} files)\n`;
        for (const child of node.children) {
          result += formatTree(child, indent + "  ");
        }
        return result;
      };
      
      prompt += `Current Directory Structure:\n${formatTree(directoryStructure)}\n\n`;
      prompt += `Focus your advice on:\n`;
      prompt += `- How to improve documentation organization and maintainability\n`;
      prompt += `- Separating architectural documents from session notes\n`;
      prompt += `- Consistency in naming conventions and folder structure\n`;
      prompt += `- Entry points and navigation clarity\n`;
      prompt += `- Opportunities for reducing clutter\n`;
      prompt += `- Specific recommendations based on the actual structure shown above\n\n`;
      prompt += `Provide 3-5 specific, actionable recommendations.`;
    } else {
      prompt += `Provide 3 strategic bullet points for implementing ${topic} in a documentation quality management framework (AgentQMS). Focus on documentation organization, not generic scalability.`;
    }
    
    return await generateContent(prompt, {
      systemInstruction: "You are a Senior Documentation Architect specializing in organizing technical documentation, maintaining consistency, and improving maintainability. Provide specific, actionable advice based on actual directory structures."
    });
  } catch (error) {
    return "Unable to generate advice. Please check your API settings.";
  }
};

export const generateAgentSystemPrompt = async (projectContext: string): Promise<string> => {
  try {
    const prompt = `Create a "Master System Prompt" for an AI Agent working on the following project: "${projectContext}".
      The goal of this prompt is to FORCE the AI agent to strictly follow the AgentQMS framework rules.
      
      The generated prompt must include:
      1. A "Role Definition" (You are an AgentQMS-compliant engineer).
      2. The "Prime Directive": Do not write code without an approved artifact.
      3. "Schema Enforcement": Include the YAML frontmatter schema (specifically branch_name and timestamp rules).
      4. "Folder Structure Awareness": Explicitly state that tools and scripts are located in '${APP_CONFIG.PATHS.TOOLS}/' and artifacts in '${APP_CONFIG.PATHS.MODULES}/<project>/'.
      
      Output the result as a raw, copy-pasteable Markdown block.`;
      
    return await generateContent(prompt, {
      systemInstruction: "You are a Meta-Prompt Engineer. You create system instructions for other AI models."
    });
  } catch (error) {
    return "Error generating protocol. Please check your API settings.";
  }
};

export const analyzeLinkRelevance = async (linkText: string, targetContent: string): Promise<string> => {
  try {
    const prompt = `
      Link Text: "${linkText}"
      Target Document Content Snippet: "${targetContent}"
      
      Does the link text accurately reflect the content of the target document? 
      Provide a 1 sentence verification. If it's vague, suggest a better link text.
    `;

    return await generateContent(prompt, {
      systemInstruction: "You are a documentation quality auditor verifying hyperlinks."
    });
  } catch (error) {
    console.error("Analysis Error:", error);
    return "AI Analysis unavailable.";
  }
};
