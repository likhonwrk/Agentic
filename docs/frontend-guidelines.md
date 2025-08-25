---
applyTo: "{frontend/**/*.{ts,tsx,js,jsx}}"
---

# Frontend Development Guidelines

## Libraries and Frameworks

- React for component-based UI development
- Tailwind CSS for styling
- TypeScript for type safety

## Coding Standards

- Use semicolons at the end of each statement
- Use single quotes for strings
- Use function-based components in React
- Use arrow functions for callbacks

Example:

```tsx
const TaskComponent: React.FC<TaskProps> = ({ task }) => {
  const [isComplete, setIsComplete] = useState(false);
  
  const handleComplete = () => {
    setIsComplete(true);
  };
  
  return (
    <div className='p-4 border rounded'>
      <h3>{task.title}</h3>
      <button onClick={handleComplete}>Complete</button>
    </div>
  );
};
```
