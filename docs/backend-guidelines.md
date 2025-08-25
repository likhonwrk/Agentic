---
applyTo: "backend/**/*.{js,ts}"
---

# Backend Development Guidelines

## Libraries and Frameworks

- Node.js and Express for the server
- MongoDB for data storage
- TypeScript for type safety

## Coding Standards

- Use semicolons at the end of each statement
- Use single quotes for strings
- Use async/await for asynchronous operations
- Implement proper error handling

Example:

```typescript
import { Router } from 'express';
import { Task } from '../models/Task';

const router = Router();

router.get('/tasks', async (req, res) => {
  try {
    const tasks = await Task.find({ userId: req.user.id });
    res.json(tasks);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch tasks' });
  }
});

export default router;
```
