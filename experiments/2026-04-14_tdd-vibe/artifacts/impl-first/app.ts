import express, { Request, Response, NextFunction } from "express";
import { usersRouter } from "./users";

const app = express();

app.use(express.json());

// Mount router
app.use("/users", usersRouter);

// 404 catch-all
app.use((_req: Request, res: Response) => {
  res.status(404).json({ success: false, error: { message: "Route not found" } });
});

// 500 global error handler
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error(err);
  res.status(500).json({ success: false, error: { message: "Internal server error" } });
});

export default app;

if (require.main === module) {
  const PORT = process.env.PORT ?? 3000;
  app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
}
