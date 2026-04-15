// Step 2: Express routing for CRUD operations

import { Router } from 'express';
import { BookmarkController } from './controller';

const router = Router();
const controller = new BookmarkController();

router.post('/', controller.create);
router.get('/', controller.list);
router.get('/:id', controller.getById);
router.put('/:id', controller.update);
router.delete('/:id', controller.delete);

export { router as bookmarkRouter };
