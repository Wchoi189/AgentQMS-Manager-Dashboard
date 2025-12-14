
export interface Violation {
    file: string;
    rule_id: string;
    message: string;
    severity: "critical" | "high" | "medium" | "low";
}

export interface ValidationResult {
    is_compliant: boolean; // Computed on frontend or mismatch
    compliance_rate: number;
    violations: Violation[];
    total_files: number;
    valid_files: number; // Backend sends valid_files
    score?: number; // Optional alias for compatibility
}

const API_BASE_URL = "/api/v1";

export const validateCompliance = async (): Promise<ValidationResult> => {
    try {
        const response = await fetch(`${API_BASE_URL}/compliance/validate`);
        if (!response.ok) {
            throw new Error(`Compliance validation failed: ${response.statusText}`);
        }
        const data = await response.json();
        // Compute frontend-specific fields if missing
        return {
            ...data,
            is_compliant: data.compliance_rate === 100,
            score: data.compliance_rate,
            compliant_files: data.valid_files
        };
    } catch (error) {
        console.error("Error fetching compliance data:", error);
        // Return a default error state or rethrow
        throw error;
    }
};

export const fixViolation = async (filePath: string, ruleId: string, dryRun: boolean = false): Promise<{ success: boolean; message: string; diff?: string; new_content?: string }> => {
    try {
        const response = await fetch(`${API_BASE_URL}/compliance/fix`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ file_path: filePath, rule_id: ruleId, dry_run: dryRun }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Fix failed: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error applying fix:", error);
        throw error;
    }
};
