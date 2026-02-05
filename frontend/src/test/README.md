# Frontend Testing

## Test Framework

- **Vitest**: 测试运行器
- **Testing Library**: React 组件测试
- **jsdom**: DOM 环境

## Run Tests

```bash
# Run tests
npm test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

## Test Structure

```
src/
├── components/common/
│   ├── Button.test.tsx
│   └── Input.test.tsx
├── stores/
│   ├── auth.test.ts
│   └── ppt.test.ts
├── utils/
│   └── index.test.ts
└── test/
    └── setup.ts
```

## Coverage

目标覆盖率:
- Components: 80%+
- Stores: 80%+
- Utils: 90%+
