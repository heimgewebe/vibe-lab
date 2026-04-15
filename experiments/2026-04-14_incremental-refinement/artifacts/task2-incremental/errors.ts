// Step 4: Error handling — structured CLI errors

export class CliError extends Error {
  constructor(
    message: string,
    public readonly exitCode: number = 1
  ) {
    super(message);
    this.name = 'CliError';
  }
}

export class FileNotFoundError extends CliError {
  constructor(filePath: string) {
    super(`File not found: ${filePath}`);
    this.name = 'FileNotFoundError';
  }
}

export class InvalidArgumentError extends CliError {
  constructor(argument: string, reason: string) {
    super(`Invalid argument '${argument}': ${reason}`);
    this.name = 'InvalidArgumentError';
  }
}

export function handleCliError(err: unknown): never {
  if (err instanceof CliError) {
    console.error(`Error: ${err.message}`);
    process.exit(err.exitCode);
  }
  if (err instanceof Error) {
    console.error(`Unexpected error: ${err.message}`);
  } else {
    console.error('An unknown error occurred');
  }
  process.exit(1);
}
