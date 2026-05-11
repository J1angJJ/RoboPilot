export interface CommandResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

export interface DetectResult {
  project_path: string;
  exists: boolean;
  project_type: string;
  confidence: string;
  detected_signals: string[];
  missing_common_files: string[];
  notes: string[];
  suggested_next_steps: string[];
}

export interface Ros1InspectionResult {
  project_path: string;
  exists: boolean;
  package_name: string;
  package_format: string;
  detected_project_type: string;
  issues: string[];
  suggested_next_steps: string[];
}

export interface DependencyAnalysisResult {
  project_path: string;
  exists: boolean;
  project_type: string;
  declared_dependencies: Record<string, string[]>;
  detected_usage: Record<string, string[]>;
  possibly_missing: string[];
  possibly_unused: string[];
  warnings: string[];
  suggested_next_steps: string[];
}

export interface MigrationPlanResult {
  source_path: string;
  target: string;
  source_project_type: string;
  package_name: string;
  confidence: string;
  summary: string;
  risks: string[];
  suggested_next_steps: string[];
}

export interface MigrationPreviewResult {
  plan_path: string;
  project_path: string;
  target: string;
  package_name: string;
  files_to_create: string[];
  files_requiring_manual_migration: string[];
  interface_files_to_review: string[];
  dependency_items_to_review: string[];
  conflicts: string[];
  risks: string[];
  suggested_next_steps: string[];
}

export interface ProjectTreeState {
  projectType?: string;
  packageName?: string;
  issuesCount?: number;
  dependencyWarningsCount?: number;
  migrationPlanStatus?: string;
}
