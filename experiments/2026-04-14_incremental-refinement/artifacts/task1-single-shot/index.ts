// Task 1 — Single-Shot: Complete Bookmark REST API
// Generated as a single, comprehensive response to one prompt

import express, { Request, Response, NextFunction } from 'express';

// ---- Types ----
interface Bookmark {
  id: string;
  url: string;
  title: string;
  description: string;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
}

interface CreateBookmarkInput {
  url: string;
  title: string;
  description?: string;
  tags?: string[];
}

interface UpdateBookmarkInput {
  url?: string;
  title?: string;
  description?: string;
  tags?: string[];
}

interface SearchParams {
  q?: string;
  tags?: string[];
  page?: number;
  limit?: number;
}

// ---- In-memory store ----
const bookmarks: Map<string, Bookmark> = new Map();
let idCounter = 0;
function generateId(): string { return (++idCounter).toString(); }

// ---- Validation helpers ----
function isValidUrl(url: string): boolean {
  try { new URL(url); return true; } catch { return false; }
}

function validateCreateInput(body: any): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  if (!body.url || typeof body.url !== 'string') errors.push('url is required and must be a string');
  else if (!isValidUrl(body.url)) errors.push('url must be a valid URL');
  if (!body.title || typeof body.title !== 'string') errors.push('title is required and must be a string');
  if (body.description !== undefined && typeof body.description !== 'string') errors.push('description must be a string');
  if (body.tags !== undefined) {
    if (!Array.isArray(body.tags)) errors.push('tags must be an array');
    else if (body.tags.some((t: any) => typeof t !== 'string')) errors.push('all tags must be strings');
  }
  return { valid: errors.length === 0, errors };
}

function validateUpdateInput(body: any): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  if (body.url !== undefined) {
    if (typeof body.url !== 'string') errors.push('url must be a string');
    else if (!isValidUrl(body.url)) errors.push('url must be a valid URL');
  }
  if (body.title !== undefined && typeof body.title !== 'string') errors.push('title must be a string');
  if (body.description !== undefined && typeof body.description !== 'string') errors.push('description must be a string');
  if (body.tags !== undefined) {
    if (!Array.isArray(body.tags)) errors.push('tags must be an array');
    else if (body.tags.some((t: any) => typeof t !== 'string')) errors.push('all tags must be strings');
  }
  return { valid: errors.length === 0, errors };
}

// ---- Express setup ----
const app = express();
app.use(express.json());

// Error handling middleware
function errorHandler(err: Error, _req: Request, res: Response, _next: NextFunction): void {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal Server Error' });
}

// ---- Routes ----

// Create bookmark
app.post('/bookmarks', (req: Request, res: Response) => {
  const validation = validateCreateInput(req.body);
  if (!validation.valid) {
    res.status(400).json({ errors: validation.errors });
    return;
  }
  const id = generateId();
  const bookmark: Bookmark = {
    id,
    url: req.body.url,
    title: req.body.title,
    description: req.body.description || '',
    tags: req.body.tags || [],
    createdAt: new Date(),
    updatedAt: new Date(),
  };
  bookmarks.set(id, bookmark);
  res.status(201).json(bookmark);
});

// List/search bookmarks
app.get('/bookmarks', (req: Request, res: Response) => {
  let results = Array.from(bookmarks.values());
  const q = req.query.q as string | undefined;
  const tags = req.query.tags as string | string[] | undefined;
  const page = Math.max(parseInt(req.query.page as string) || 1, 1);
  const limit = Math.max(parseInt(req.query.limit as string) || 20, 1);

  // Full-text search
  if (q) {
    const lower = q.toLowerCase();
    results = results.filter(b =>
      b.title.toLowerCase().includes(lower) ||
      b.description.toLowerCase().includes(lower)
    );
  }

  // Tag filtering
  if (tags) {
    const tagList = Array.isArray(tags) ? tags : [tags];
    results = results.filter(b => tagList.every(t => b.tags.includes(t)));
  }

  // Pagination
  const total = results.length;
  const start = (page - 1) * limit;
  results = results.slice(start, start + limit);

  res.json({ data: results, total, page, limit });
});

// Get single bookmark
app.get('/bookmarks/:id', (req: Request, res: Response) => {
  const bookmark = bookmarks.get(req.params.id);
  if (!bookmark) {
    res.status(404).json({ error: 'Bookmark not found' });
    return;
  }
  res.json(bookmark);
});

// Update bookmark
app.put('/bookmarks/:id', (req: Request, res: Response) => {
  const bookmark = bookmarks.get(req.params.id);
  if (!bookmark) {
    res.status(404).json({ error: 'Bookmark not found' });
    return;
  }
  const validation = validateUpdateInput(req.body);
  if (!validation.valid) {
    res.status(400).json({ errors: validation.errors });
    return;
  }
  if (req.body.url !== undefined) bookmark.url = req.body.url;
  if (req.body.title !== undefined) bookmark.title = req.body.title;
  if (req.body.description !== undefined) bookmark.description = req.body.description;
  if (req.body.tags !== undefined) bookmark.tags = req.body.tags;
  bookmark.updatedAt = new Date();
  res.json(bookmark);
});

// Delete bookmark
app.delete('/bookmarks/:id', (req: Request, res: Response) => {
  if (!bookmarks.has(req.params.id)) {
    res.status(404).json({ error: 'Bookmark not found' });
    return;
  }
  bookmarks.delete(req.params.id);
  res.status(204).send();
});

app.use(errorHandler);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

export { app, Bookmark, CreateBookmarkInput, UpdateBookmarkInput, SearchParams };
