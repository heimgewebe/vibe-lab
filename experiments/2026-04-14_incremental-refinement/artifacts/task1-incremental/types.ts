// Step 1: TypeScript types for the Bookmark system

export interface Tag {
  name: string;
}

export interface Bookmark {
  id: string;
  url: string;
  title: string;
  description: string;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateBookmarkDto {
  url: string;
  title: string;
  description?: string;
  tags?: string[];
}

export interface UpdateBookmarkDto {
  url?: string;
  title?: string;
  description?: string;
  tags?: string[];
}

export interface BookmarkSearchParams {
  query?: string;
  tags?: string[];
  page?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface ApiError {
  status: number;
  message: string;
  errors?: string[];
}
