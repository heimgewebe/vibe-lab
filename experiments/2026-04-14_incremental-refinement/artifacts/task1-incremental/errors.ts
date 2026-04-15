// Step 4: Error handling — centralized error classes and middleware

import { Request, Response, NextFunction } from 'express';
import { ApiError } from './types';

export class AppError extends Error {
  constructor(
    public readonly statusCode: number,
    message: string,
    public readonly errors?: string[]
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(404, `${resource} with id '${id}' not found`);
    this.name = 'NotFoundError';
  }
}

export class ValidationError extends AppError {
  constructor(errors: string[]) {
    super(400, 'Validation failed', errors);
    this.name = 'ValidationError';
  }
}

export function errorHandler(
  err: Error,
  _req: Request,
  res: Response,
  _next: NextFunction
): void {
  if (err instanceof AppError) {
    const body: ApiError = {
      status: err.statusCode,
      message: err.message,
    };
    if (err.errors) body.errors = err.errors;
    res.status(err.statusCode).json(body);
    return;
  }

  console.error('Unexpected error:', err);
  res.status(500).json({
    status: 500,
    message: 'Internal Server Error',
  });
}
