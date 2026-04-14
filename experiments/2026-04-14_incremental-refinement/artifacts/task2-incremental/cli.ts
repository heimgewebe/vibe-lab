// Step 5: Input validation — CLI argument parsing and validation

import { CliOptions, TransformRule, FilterCriteria } from './types';
import { InvalidArgumentError } from './errors';

export function parseAndValidateArgs(argv: string[]): CliOptions {
  const args = argv.slice(2);
  const options: CliOptions = {
    inputPath: '',
    delimiter: ',',
    outputFormat: 'csv',
    transforms: [],
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    switch (arg) {
      case '--input':
      case '-i':
        options.inputPath = requireNextArg(args, i++, 'input');
        i++;
        break;

      case '--output':
      case '-o':
        options.outputPath = requireNextArg(args, i++, 'output');
        i++;
        break;

      case '--delimiter':
      case '-d': {
        const delim = requireNextArg(args, i++, 'delimiter');
        i++;
        if (delim.length !== 1) {
          throw new InvalidArgumentError('delimiter', 'must be a single character');
        }
        options.delimiter = delim;
        break;
      }

      case '--format':
      case '-f': {
        const format = requireNextArg(args, i++, 'format');
        i++;
        if (format !== 'csv' && format !== 'json') {
          throw new InvalidArgumentError('format', "must be 'csv' or 'json'");
        }
        options.outputFormat = format;
        break;
      }

      case '--transform':
      case '-t': {
        const spec = requireNextArg(args, i++, 'transform');
        i++;
        options.transforms.push(parseTransformSpec(spec));
        break;
      }

      case '--filter': {
        const spec = requireNextArg(args, i++, 'filter');
        i++;
        options.filter = parseFilterSpec(spec);
        break;
      }

      case '--columns':
      case '-c': {
        const cols = requireNextArg(args, i++, 'columns');
        i++;
        options.selectColumns = cols.split(',').map((c) => c.trim());
        break;
      }

      case '--help':
      case '-h':
        printHelp();
        process.exit(0);

      default:
        if (arg.startsWith('-')) {
          throw new InvalidArgumentError(arg, 'unknown option');
        }
        if (!options.inputPath) {
          options.inputPath = arg;
        }
    }
  }

  if (!options.inputPath) {
    throw new InvalidArgumentError('input', 'no input file specified');
  }

  return options;
}

function requireNextArg(args: string[], currentIdx: number, name: string): string {
  if (currentIdx + 1 >= args.length) {
    throw new InvalidArgumentError(name, 'value required');
  }
  return args[currentIdx + 1];
}

function parseTransformSpec(spec: string): TransformRule {
  const parts = spec.split(':');
  if (parts.length < 2) {
    throw new InvalidArgumentError('transform', "format: column:operation[:from→to]");
  }

  const validOps = ['uppercase', 'lowercase', 'trim', 'replace', 'remove', 'rename'];
  if (!validOps.includes(parts[1])) {
    throw new InvalidArgumentError('transform', `unknown operation '${parts[1]}'. Valid: ${validOps.join(', ')}`);
  }

  const rule: TransformRule = {
    column: parts[0],
    operation: parts[1] as TransformRule['operation'],
  };

  if (parts.length > 2 && parts[2].includes('→')) {
    const [from, to] = parts[2].split('→');
    rule.args = { from, to, newName: to };
  }

  return rule;
}

function parseFilterSpec(spec: string): FilterCriteria {
  // Supports: column=value, column^=value, column~=value
  const match = spec.match(/^([^=^~]+)([\^~]?=)(.*)$/);
  if (!match) {
    throw new InvalidArgumentError('filter', "format: column=value, column^=value (startsWith), column~=value (contains)");
  }

  const [, column, operator, value] = match;
  const mode: FilterCriteria['mode'] =
    operator === '^=' ? 'startsWith' :
    operator === '~=' ? 'contains' :
    'exact';

  return { column, value, mode };
}

function printHelp(): void {
  console.log(`csv-tool — Parse and transform CSV files

Usage:
  csv-tool <input> [options]

Options:
  -i, --input <file>        Input CSV file
  -o, --output <file>       Output file (stdout if omitted)
  -d, --delimiter <char>    CSV delimiter (default: ,)
  -f, --format csv|json     Output format (default: csv)
  -t, --transform <spec>    Transform: column:operation[:args]
  -c, --columns <list>      Select columns (comma-separated)
  --filter <spec>           Filter: column=value
  -h, --help                Show this help

Transform operations: uppercase, lowercase, trim, replace, remove, rename
`);
}
