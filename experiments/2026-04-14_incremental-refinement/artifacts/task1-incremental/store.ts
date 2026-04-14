// Step 3: Core logic — BookmarkStore with CRUD + search

import { Bookmark, CreateBookmarkDto, UpdateBookmarkDto, BookmarkSearchParams, PaginatedResponse } from './types';

export class BookmarkStore {
  private bookmarks: Map<string, Bookmark> = new Map();
  private idCounter = 0;

  private generateId(): string {
    return (++this.idCounter).toString();
  }

  create(dto: CreateBookmarkDto): Bookmark {
    const id = this.generateId();
    const now = new Date();
    const bookmark: Bookmark = {
      id,
      url: dto.url,
      title: dto.title,
      description: dto.description ?? '',
      tags: dto.tags ?? [],
      createdAt: now,
      updatedAt: now,
    };
    this.bookmarks.set(id, bookmark);
    return bookmark;
  }

  getById(id: string): Bookmark | undefined {
    return this.bookmarks.get(id);
  }

  update(id: string, dto: UpdateBookmarkDto): Bookmark | undefined {
    const bookmark = this.bookmarks.get(id);
    if (!bookmark) return undefined;

    if (dto.url !== undefined) bookmark.url = dto.url;
    if (dto.title !== undefined) bookmark.title = dto.title;
    if (dto.description !== undefined) bookmark.description = dto.description;
    if (dto.tags !== undefined) bookmark.tags = dto.tags;
    bookmark.updatedAt = new Date();

    return bookmark;
  }

  delete(id: string): boolean {
    return this.bookmarks.delete(id);
  }

  search(params: BookmarkSearchParams): PaginatedResponse<Bookmark> {
    let results = Array.from(this.bookmarks.values());

    // Full-text search over title and description
    if (params.query) {
      const q = params.query.toLowerCase();
      results = results.filter(
        (b) =>
          b.title.toLowerCase().includes(q) ||
          b.description.toLowerCase().includes(q)
      );
    }

    // Tag-based filtering (all specified tags must be present)
    if (params.tags && params.tags.length > 0) {
      results = results.filter((b) =>
        params.tags!.every((tag) => b.tags.includes(tag))
      );
    }

    const total = results.length;
    const page = params.page ?? 1;
    const limit = params.limit ?? 20;
    const totalPages = Math.ceil(total / limit);
    const start = (page - 1) * limit;
    const data = results.slice(start, start + limit);

    return { data, total, page, limit, totalPages };
  }
}
