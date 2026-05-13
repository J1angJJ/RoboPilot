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

export interface ScaffoldFileItem {
  path: string;
  purpose?: string;
  source_basis?: string;
  status?: string;
}

export interface MigrationScaffoldPreviewResult {
  plan_path: string;
  source_path: string;
  target: string;
  package_name: string;
  target_style: string;
  scaffold_files_to_create: ScaffoldFileItem[];
  placeholder_files: ScaffoldFileItem[];
  files_requiring_manual_migration: string[];
  interface_files_to_review: string[];
  dependency_items_to_review: string[];
  risks: string[];
  conflicts: string[];
  suggested_next_steps: string[];
  safety_note: string;
}

export interface MigrationScaffoldGenerationResult {
  plan_path: string;
  output_path: string;
  source_path: string;
  target: string;
  package_name: string;
  target_style: string;
  files_created: string[];
  conflicts: string[];
  skipped_files: string[];
  manual_migration_required: string[];
  risks: string[];
  suggested_next_steps: string[];
  safety_note: string;
}

export interface PlaceholderCheck {
  path: string;
  passed: boolean;
  missing_concepts: string[];
}

export interface MigrationScaffoldValidationResult {
  plan_path: string;
  scaffold_path: string;
  source_path: string;
  target: string;
  package_name: string;
  target_style: string;
  valid: boolean;
  missing_files: string[];
  unexpected_files: string[];
  placeholder_checks: PlaceholderCheck[];
  issues: string[];
  warnings: string[];
  suggested_next_steps: string[];
  safety_note: string;
}

export interface ProjectTreeState {
  workspacePath?: string;
  projectType?: string;
  packageName?: string;
  issuesCount?: number;
  warningsCount?: number;
  dependencyWarningsCount?: number;
  migrationPlanStatus?: string;
  scaffoldPreviewStatus?: string;
  scaffoldDirectoryStatus?: string;
  scaffoldValidationStatus?: string;
  scaffoldReportStatus?: string;
}
