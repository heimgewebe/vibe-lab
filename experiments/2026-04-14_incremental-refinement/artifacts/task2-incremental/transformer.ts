// Step 3: Transformation engine — applying rules to CSV data

import { CsvRow, TransformRule } from './types';

export class TransformEngine {
  applyAll(
    rows: CsvRow[],
    headers: string[],
    rules: TransformRule[]
  ): { rows: CsvRow[]; headers: string[] } {
    let currentHeaders = [...headers];

    for (const rule of rules) {
      const result = this.applyRule(rows, currentHeaders, rule);
      currentHeaders = result.headers;
    }

    return { rows, headers: currentHeaders };
  }

  private applyRule(
    rows: CsvRow[],
    headers: string[],
    rule: TransformRule
  ): { headers: string[] } {
    if (rule.operation !== 'rename' && !headers.includes(rule.column)) {
      console.warn(`Warning: column '${rule.column}' not found — skipping`);
      return { headers };
    }

    switch (rule.operation) {
      case 'uppercase':
        for (const row of rows) {
          if (row[rule.column] !== undefined) {
            row[rule.column] = row[rule.column].toUpperCase();
          }
        }
        return { headers };

      case 'lowercase':
        for (const row of rows) {
          if (row[rule.column] !== undefined) {
            row[rule.column] = row[rule.column].toLowerCase();
          }
        }
        return { headers };

      case 'trim':
        for (const row of rows) {
          if (row[rule.column] !== undefined) {
            row[rule.column] = row[rule.column].trim();
          }
        }
        return { headers };

      case 'replace':
        if (rule.args?.from !== undefined && rule.args?.to !== undefined) {
          const pattern = new RegExp(this.escapeRegex(rule.args.from), 'g');
          for (const row of rows) {
            if (row[rule.column] !== undefined) {
              row[rule.column] = row[rule.column].replace(pattern, rule.args.to);
            }
          }
        }
        return { headers };

      case 'remove': {
        const newHeaders = headers.filter((h) => h !== rule.column);
        for (const row of rows) {
          delete row[rule.column];
        }
        return { headers: newHeaders };
      }

      case 'rename': {
        if (!rule.args?.newName) {
          console.warn('Rename requires args.newName — skipping');
          return { headers };
        }
        const idx = headers.indexOf(rule.column);
        if (idx < 0) {
          console.warn(`Warning: column '${rule.column}' not found — skipping rename`);
          return { headers };
        }
        const newHeaders = [...headers];
        newHeaders[idx] = rule.args.newName;
        for (const row of rows) {
          row[rule.args.newName] = row[rule.column] ?? '';
          delete row[rule.column];
        }
        return { headers: newHeaders };
      }
    }
  }

  private escapeRegex(str: string): string {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
}
