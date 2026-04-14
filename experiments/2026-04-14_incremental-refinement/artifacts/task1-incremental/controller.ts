// Step 3+4+5 combined: Controller using store, validation, and error handling

import { Request, Response, NextFunction } from 'express';
import { BookmarkStore } from './store';
import { NotFoundError } from './errors';
import { validateCreateBookmark, validateUpdateBookmark } from './validation';

const store = new BookmarkStore();

export class BookmarkController {
  create = (req: Request, res: Response, next: NextFunction): void => {
    try {
      const dto = validateCreateBookmark(req.body);
      const bookmark = store.create(dto);
      res.status(201).json(bookmark);
    } catch (err) {
      next(err);
    }
  };

  list = (req: Request, res: Response, _next: NextFunction): void => {
    const query = req.query.q as string | undefined;
    const tagsParam = req.query.tags;
    const tags = tagsParam
      ? Array.isArray(tagsParam)
        ? (tagsParam as string[])
        : [tagsParam as string]
      : undefined;
    const page = req.query.page ? parseInt(req.query.page as string, 10) : undefined;
    const limit = req.query.limit ? parseInt(req.query.limit as string, 10) : undefined;

    const result = store.search({ query, tags, page, limit });
    res.json(result);
  };

  getById = (req: Request, res: Response, next: NextFunction): void => {
    try {
      const bookmark = store.getById(req.params.id);
      if (!bookmark) throw new NotFoundError('Bookmark', req.params.id);
      res.json(bookmark);
    } catch (err) {
      next(err);
    }
  };

  update = (req: Request, res: Response, next: NextFunction): void => {
    try {
      const dto = validateUpdateBookmark(req.body);
      const bookmark = store.update(req.params.id, dto);
      if (!bookmark) throw new NotFoundError('Bookmark', req.params.id);
      res.json(bookmark);
    } catch (err) {
      next(err);
    }
  };

  delete = (req: Request, res: Response, next: NextFunction): void => {
    try {
      const deleted = store.delete(req.params.id);
      if (!deleted) throw new NotFoundError('Bookmark', req.params.id);
      res.status(204).send();
    } catch (err) {
      next(err);
    }
  };
}
