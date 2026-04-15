// Step 6: Main entry point — wiring all components together

import * as fs from 'fs';
import * as path from 'path';
import { parseAndValidateArgs } from './cli';
import { CsvParser } from './parser';
import { TransformEngine } from './transformer';
import { filterRows, selectColumns } from './filters';
import { handleCliError, FileNotFoundError } from './errors';

function main(): void {
  try {
    const options = parseAndValidateArgs(process.argv);

    // Read input file
    const resolvedPath = path.resolve(options.inputPath);
    if (!fs.existsSync(resolvedPath)) {
      throw new FileNotFoundError(resolvedPath);
    }
    const content = fs.readFileSync(resolvedPath, 'utf-8');

    // Parse CSV
    const parser = new CsvParser(options.delimiter);
    let { headers, rows } = parser.parse(content);

    // Apply filter
    if (options.filter) {
      rows = filterRows(rows, headers, options.filter);
    }

    // Apply transforms
    if (options.transforms.length > 0) {
      const engine = new TransformEngine();
      const result = engine.applyAll(rows, headers, options.transforms);
      rows = result.rows;
      headers = result.headers;
    }

    // Select columns
    if (options.selectColumns) {
      const result = selectColumns(rows, headers, options.selectColumns);
      rows = result.rows;
      headers = result.headers;
    }

    // Format output
    let output: string;
    if (options.outputFormat === 'json') {
      output = JSON.stringify(rows, null, 2);
    } else {
      output = parser.serialize(headers, rows);
    }

    // Write output
    if (options.outputPath) {
      fs.writeFileSync(path.resolve(options.outputPath), output, 'utf-8');
      console.log(`Output written to ${options.outputPath} (${rows.length} rows)`);
    } else {
      console.log(output);
    }
  } catch (err) {
    handleCliError(err);
  }
}

main();
