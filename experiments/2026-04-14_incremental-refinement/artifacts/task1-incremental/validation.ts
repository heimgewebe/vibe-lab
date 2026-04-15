// Step 5: Input validation for all endpoints

import { CreateBookmarkDto, UpdateBookmarkDto } from './types';
import { ValidationError } from './errors';

function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

function assertString(value: unknown, name: string, errors: string[]): void {
  if (typeof value !== 'string') {
    errors.push(`${name} must be a string`);
  }
}

function assertStringArray(value: unknown, name: string, errors: string[]): void {
  if (!Array.isArray(value)) {
    errors.push(`${name} must be an array`);
    return;
  }
  for (let i = 0; i < value.length; i++) {
    if (typeof value[i] !== 'string') {
      errors.push(`${name}[${i}] must be a string`);
    }
  }
}

export function validateCreateBookmark(body: unknown): CreateBookmarkDto {
  const errors: string[] = [];
  if (typeof body !== 'object' || body === null) {
    throw new ValidationError(['Request body must be a JSON object']);
  }
  const obj = body as Record<string, unknown>;

  // Required fields
  if (!obj.url || typeof obj.url !== 'string') {
    errors.push('url is required and must be a string');
  } else if (!isValidUrl(obj.url)) {
    errors.push('url must be a valid URL');
  }

  if (!obj.title || typeof obj.title !== 'string') {
    errors.push('title is required and must be a string');
  } else if (obj.title.trim().length === 0) {
    errors.push('title must not be empty');
  }

  // Optional fields
  if (obj.description !== undefined) {
    assertString(obj.description, 'description', errors);
  }

  if (obj.tags !== undefined) {
    assertStringArray(obj.tags, 'tags', errors);
  }

  if (errors.length > 0) throw new ValidationError(errors);

  return {
    url: obj.url as string,
    title: obj.title as string,
    description: obj.description as string | undefined,
    tags: obj.tags as string[] | undefined,
  };
}

export function validateUpdateBookmark(body: unknown): UpdateBookmarkDto {
  const errors: string[] = [];
  if (typeof body !== 'object' || body === null) {
    throw new ValidationError(['Request body must be a JSON object']);
  }
  const obj = body as Record<string, unknown>;

  if (obj.url !== undefined) {
    if (typeof obj.url !== 'string') {
      errors.push('url must be a string');
    } else if (!isValidUrl(obj.url)) {
      errors.push('url must be a valid URL');
    }
  }

  if (obj.title !== undefined) {
    assertString(obj.title, 'title', errors);
    if (typeof obj.title === 'string' && obj.title.trim().length === 0) {
      errors.push('title must not be empty');
    }
  }

  if (obj.description !== undefined) {
    assertString(obj.description, 'description', errors);
  }

  if (obj.tags !== undefined) {
    assertStringArray(obj.tags, 'tags', errors);
  }

  if (errors.length > 0) throw new ValidationError(errors);

  return {
    url: obj.url as string | undefined,
    title: obj.title as string | undefined,
    description: obj.description as string | undefined,
    tags: obj.tags as string[] | undefined,
  };
}
