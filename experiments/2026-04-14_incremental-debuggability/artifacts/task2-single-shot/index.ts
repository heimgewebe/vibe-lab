// Task 2 — Single-Shot: Complete CSV Parser and Transformer CLI
// Generated as a single, comprehensive response to one prompt

import * as fs from 'fs';
import * as path from 'path';

// ---- Types ----
interface CsvRow {
  [key: string]: string;
}

interface TransformRule {
  column: string;
  operation: 'uppercase' | 'lowercase' | 'trim' | 'replace' | 'remove' | 'rename';
  args?: { from?: string; to?: string; newName?: string };
}

interface CliOptions {
  input: string;
  output?: string;
  delimiter: string;
  transforms: TransformRule[];
  filterColumn?: string;
  filterValue?: string;
  columns?: string[];
  format: 'csv' | 'json';
}

// ---- CSV Parser ----
function parseCsv(content: string, delimiter: string): { headers: string[]; rows: CsvRow[] } {
  const lines = content.split('\n').filter(l => l.trim() !== '');
  if (lines.length === 0) throw new Error('CSV file is empty');

  const headers = lines[0].split(delimiter).map(h => h.trim());
  const rows: CsvRow[] = [];

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(delimiter);
    const row: CsvRow = {};
    headers.forEach((header, idx) => {
      row[header] = (values[idx] || '').trim();
    });
    rows.push(row);
  }

  return { headers, rows };
}

// ---- Transformations ----
function applyTransforms(rows: CsvRow[], headers: string[], transforms: TransformRule[]): { rows: CsvRow[]; headers: string[] } {
  let currentHeaders = [...headers];

  for (const rule of transforms) {
    if (!currentHeaders.includes(rule.column) && rule.operation !== 'rename') {
      console.warn(`Warning: Column '${rule.column}' not found, skipping transform`);
      continue;
    }

    switch (rule.operation) {
      case 'uppercase':
        rows.forEach(r => { if (r[rule.column]) r[rule.column] = r[rule.column].toUpperCase(); });
        break;
      case 'lowercase':
        rows.forEach(r => { if (r[rule.column]) r[rule.column] = r[rule.column].toLowerCase(); });
        break;
      case 'trim':
        rows.forEach(r => { if (r[rule.column]) r[rule.column] = r[rule.column].trim(); });
        break;
      case 'replace':
        if (rule.args?.from !== undefined && rule.args?.to !== undefined) {
          rows.forEach(r => {
            if (r[rule.column]) r[rule.column] = r[rule.column].replace(new RegExp(rule.args!.from!, 'g'), rule.args!.to!);
          });
        }
        break;
      case 'remove':
        currentHeaders = currentHeaders.filter(h => h !== rule.column);
        rows.forEach(r => { delete r[rule.column]; });
        break;
      case 'rename':
        if (rule.args?.newName) {
          const idx = currentHeaders.indexOf(rule.column);
          if (idx >= 0) {
            if (currentHeaders.includes(rule.args.newName)) {
              console.warn(`Warning: column '${rule.args.newName}' already exists — skipping rename`);
              break;
            }
            currentHeaders[idx] = rule.args.newName;
            rows.forEach(r => {
              r[rule.args!.newName!] = r[rule.column];
              delete r[rule.column];
            });
          }
        }
        break;
    }
  }

  return { rows, headers: currentHeaders };
}

// ---- Filtering ----
function filterRows(rows: CsvRow[], column: string, value: string): CsvRow[] {
  return rows.filter(r => r[column]?.includes(value));
}

// ---- Column Selection ----
function selectColumns(rows: CsvRow[], headers: string[], columns: string[]): { rows: CsvRow[]; headers: string[] } {
  const validColumns = columns.filter(c => headers.includes(c));
  const invalidColumns = columns.filter(c => !headers.includes(c));
  if (invalidColumns.length > 0) {
    console.warn(`Warning: Columns not found: ${invalidColumns.join(', ')}`);
  }
  const newRows = rows.map(r => {
    const newRow: CsvRow = {};
    validColumns.forEach(c => { newRow[c] = r[c]; });
    return newRow;
  });
  return { rows: newRows, headers: validColumns };
}

// ---- Output ----
function toCsv(rows: CsvRow[], headers: string[], delimiter: string): string {
  const lines = [headers.join(delimiter)];
  rows.forEach(r => {
    lines.push(headers.map(h => r[h] || '').join(delimiter));
  });
  return lines.join('\n');
}

function toJson(rows: CsvRow[]): string {
  return JSON.stringify(rows, null, 2);
}

// ---- CLI Argument Parser ----
function parseArgs(argv: string[]): CliOptions {
  const args = argv.slice(2);
  const options: CliOptions = {
    input: '',
    delimiter: ',',
    transforms: [],
    format: 'csv',
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--input': case '-i': options.input = args[++i]; break;
      case '--output': case '-o': options.output = args[++i]; break;
      case '--delimiter': case '-d': options.delimiter = args[++i]; break;
      case '--format': case '-f': options.format = args[++i] as 'csv' | 'json'; break;
      case '--filter': {
        const [col, val] = args[++i].split('=');
        options.filterColumn = col;
        options.filterValue = val;
        break;
      }
      case '--columns': case '-c': options.columns = args[++i].split(','); break;
      case '--transform': case '-t': {
        const parts = args[++i].split(':');
        const rule: TransformRule = { column: parts[0], operation: parts[1] as TransformRule['operation'] };
        if (parts.length > 2) {
          const [from, to] = parts[2].split('→');
          rule.args = { from, to, newName: to };
        }
        options.transforms.push(rule);
        break;
      }
      default:
        if (!options.input) options.input = args[i];
    }
  }

  if (!options.input) {
    console.error('Error: No input file specified');
    console.error('Usage: csv-tool <input> [--output <file>] [--delimiter <char>] [--format csv|json] [--transform col:op] [--filter col=val] [--columns col1,col2]');
    process.exit(1);
  }

  return options;
}

// ---- Main ----
function main(): void {
  const options = parseArgs(process.argv);

  // Read input
  let content: string;
  try {
    content = fs.readFileSync(path.resolve(options.input), 'utf-8');
  } catch (err) {
    console.error(`Error reading file: ${options.input}`);
    process.exit(1);
  }

  // Parse
  let { headers, rows } = parseCsv(content, options.delimiter);

  // Filter
  if (options.filterColumn && options.filterValue) {
    rows = filterRows(rows, options.filterColumn, options.filterValue);
  }

  // Transform
  if (options.transforms.length > 0) {
    const result = applyTransforms(rows, headers, options.transforms);
    rows = result.rows;
    headers = result.headers;
  }

  // Select columns
  if (options.columns) {
    const result = selectColumns(rows, headers, options.columns);
    rows = result.rows;
    headers = result.headers;
  }

  // Output
  const output = options.format === 'json' ? toJson(rows) : toCsv(rows, headers, options.delimiter);

  if (options.output) {
    fs.writeFileSync(path.resolve(options.output), output, 'utf-8');
    console.log(`Output written to ${options.output}`);
  } else {
    console.log(output);
  }
}

main();

export { parseCsv, applyTransforms, filterRows, selectColumns, toCsv, toJson, CsvRow, TransformRule, CliOptions };
