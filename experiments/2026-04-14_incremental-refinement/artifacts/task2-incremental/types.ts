// Step 1: Types for CSV parsing and transformation

export interface CsvRow {
  [key: string]: string;
}

export interface ParsedCsv {
  headers: string[];
  rows: CsvRow[];
}

export type TransformOperation =
  | 'uppercase'
  | 'lowercase'
  | 'trim'
  | 'replace'
  | 'remove'
  | 'rename';

export interface TransformRule {
  column: string;
  operation: TransformOperation;
  args?: {
    from?: string;
    to?: string;
    newName?: string;
  };
}

export interface FilterCriteria {
  column: string;
  value: string;
  mode: 'contains' | 'exact' | 'startsWith';
}

export interface CliOptions {
  inputPath: string;
  outputPath?: string;
  delimiter: string;
  outputFormat: 'csv' | 'json';
  transforms: TransformRule[];
  filter?: FilterCriteria;
  selectColumns?: string[];
}

export interface CliResult {
  success: boolean;
  rowsProcessed: number;
  outputPath?: string;
  error?: string;
}
