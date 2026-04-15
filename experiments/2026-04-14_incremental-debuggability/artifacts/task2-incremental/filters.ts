// Step 3 (part 2): Filtering and column selection

import { CsvRow, FilterCriteria } from './types';

export function filterRows(
  rows: CsvRow[],
  headers: string[],
  criteria: FilterCriteria
): CsvRow[] {
  if (!headers.includes(criteria.column)) {
    console.warn(`Warning: filter column '${criteria.column}' not found`);
    return rows;
  }

  return rows.filter((row) => {
    const cellValue = row[criteria.column] ?? '';
    switch (criteria.mode) {
      case 'exact':
        return cellValue === criteria.value;
      case 'contains':
        return cellValue.includes(criteria.value);
      case 'startsWith':
        return cellValue.startsWith(criteria.value);
    }
  });
}

export function selectColumns(
  rows: CsvRow[],
  headers: string[],
  columns: string[]
): { rows: CsvRow[]; headers: string[] } {
  const valid = columns.filter((c) => headers.includes(c));
  const invalid = columns.filter((c) => !headers.includes(c));

  if (invalid.length > 0) {
    console.warn(`Warning: columns not found: ${invalid.join(', ')}`);
  }

  const newRows = rows.map((row) => {
    const newRow: CsvRow = {};
    for (const col of valid) {
      newRow[col] = row[col] ?? '';
    }
    return newRow;
  });

  return { rows: newRows, headers: valid };
}
