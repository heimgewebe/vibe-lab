// Step 2: CSV parser — reading and parsing CSV content

import { ParsedCsv, CsvRow } from './types';

export class CsvParser {
  constructor(private readonly delimiter: string = ',') {}

  parse(content: string): ParsedCsv {
    const lines = content.split(/\r?\n/).filter((line) => line.trim() !== '');

    if (lines.length === 0) {
      throw new CsvParseError('CSV content is empty');
    }

    const headers = this.parseLine(lines[0]);

    if (headers.length === 0) {
      throw new CsvParseError('CSV header row is empty');
    }

    const rows: CsvRow[] = [];
    for (let i = 1; i < lines.length; i++) {
      const values = this.parseLine(lines[i]);
      const row: CsvRow = {};
      for (let j = 0; j < headers.length; j++) {
        row[headers[j]] = values[j] ?? '';
      }
      rows.push(row);
    }

    return { headers, rows };
  }

  private parseLine(line: string): string[] {
    // Simple split — handles basic CSV (no quoted fields with delimiters)
    return line.split(this.delimiter).map((field) => field.trim());
  }

  serialize(headers: string[], rows: CsvRow[]): string {
    const headerLine = headers.join(this.delimiter);
    const dataLines = rows.map((row) =>
      headers.map((h) => row[h] ?? '').join(this.delimiter)
    );
    return [headerLine, ...dataLines].join('\n');
  }
}

export class CsvParseError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'CsvParseError';
  }
}
