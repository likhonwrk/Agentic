# 🤝 Contributing to Agentic

Thank you for your interest in contributing to Agentic! This document provides guidelines and information for contributors.

## 🌟 Ways to Contribute

- **Bug Reports**: Report issues and bugs
- **Feature Requests**: Suggest new features and improvements
- **Code Contributions**: Submit pull requests with fixes and enhancements
- **Documentation**: Improve documentation and guides
- **Testing**: Help test new features and report feedback
- **Community**: Help other users in discussions and issues

## 🚀 Getting Started

### 1. Fork and Clone

\`\`\`bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/Agentic.git
cd Agentic
\`\`\`

### 2. Set Up Development Environment

\`\`\`bash
# Start development environment
./dev.sh up -d

# Install dependencies
cd frontend && npm install
cd ../backend && pip install -r requirements.txt
\`\`\`

### 3. Create a Branch

\`\`\`bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
\`\`\`

## 📝 Development Guidelines

### Code Style

**Python (Backend)**
- Follow PEP 8 style guide
- Use type hints for all functions
- Add docstrings for classes and functions
- Use `black` for code formatting
- Use `flake8` for linting

\`\`\`bash
# Format code
black backend/
flake8 backend/
\`\`\`

**TypeScript/Vue (Frontend)**
- Use Vue 3 Composition API
- Follow TypeScript strict mode
- Use Prettier for formatting
- Use ESLint for linting

\`\`\`bash
# Format code
cd frontend
npm run format
npm run lint
\`\`\`

**Docker**
- Use multi-stage builds for optimization
- Include health checks
- Use specific version tags
- Document environment variables

### Commit Messages

Use conventional commit format:

\`\`\`
type(scope): description

[optional body]

[optional footer]
\`\`\`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
\`\`\`
feat(backend): add session persistence with Redis
fix(frontend): resolve WebSocket connection issues
docs(readme): update installation instructions
\`\`\`

## 🧪 Testing

### Running Tests

\`\`\`bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm run test

# Integration tests
./dev.sh test
\`\`\`

### Writing Tests

**Backend Tests**
\`\`\`python
# tests/test_agent_manager.py
import pytest
from app.core.agent_manager import AgentManager

def test_create_agent():
    manager = AgentManager()
    agent = manager.create_agent("test", "chat")
    assert agent.name == "test"
    assert agent.type == "chat"
\`\`\`

**Frontend Tests**
\`\`\`typescript
// tests/components/ChatInput.test.ts
import { mount } from '@vue/test-utils'
import ChatInput from '@/components/ChatInput.vue'

describe('ChatInput', () => {
  it('emits message on send', async () => {
    const wrapper = mount(ChatInput)
    await wrapper.find('input').setValue('test message')
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('send')).toBeTruthy()
  })
})
\`\`\`

## 📋 Pull Request Process

### 1. Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main

### 2. Pull Request Template

\`\`\`markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass
- [ ] Manual testing completed
- [ ] Integration tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
\`\`\`

### 3. Review Process

1. **Automated Checks**: CI/CD pipeline runs tests
2. **Code Review**: Maintainers review code
3. **Feedback**: Address review comments
4. **Approval**: Get approval from maintainers
5. **Merge**: Maintainers merge the PR

## 🐛 Bug Reports

Use the bug report template:

\`\`\`markdown
**Describe the bug**
A clear description of the bug

**To Reproduce**
Steps to reproduce the behavior

**Expected behavior**
What you expected to happen

**Screenshots**
If applicable, add screenshots

**Environment:**
- OS: [e.g. Ubuntu 22.04]
- Docker version: [e.g. 20.10.21]
- Agentic version: [e.g. 2.0.1]

**Additional context**
Any other context about the problem
\`\`\`

## 💡 Feature Requests

Use the feature request template:

\`\`\`markdown
**Is your feature request related to a problem?**
A clear description of the problem

**Describe the solution you'd like**
A clear description of what you want to happen

**Describe alternatives you've considered**
Alternative solutions or features considered

**Additional context**
Any other context or screenshots
\`\`\`

## 🏗️ Architecture Guidelines

### Adding New Features

1. **Design Document**: Create design doc for major features
2. **API Design**: Design RESTful APIs with OpenAPI specs
3. **Database Schema**: Plan database changes carefully
4. **Security**: Consider security implications
5. **Performance**: Consider performance impact
6. **Documentation**: Update relevant documentation

### Code Organization

\`\`\`
backend/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Core business logic
│   ├── models/       # Data models
│   ├── services/     # External services
│   └── utils/        # Utility functions
├── tests/            # Test files
└── requirements.txt

frontend/
├── src/
│   ├── components/   # Vue components
│   ├── pages/        # Page components
│   ├── services/     # API services
│   ├── types/        # TypeScript types
│   └── utils/        # Utility functions
├── tests/            # Test files
└── package.json
\`\`\`

## 🔒 Security Guidelines

### Security Considerations

- **Input Validation**: Validate all user inputs
- **Authentication**: Secure API endpoints
- **Authorization**: Implement proper permissions
- **Secrets**: Never commit secrets to git
- **Dependencies**: Keep dependencies updated
- **Sandboxing**: Ensure proper isolation

### Reporting Security Issues

For security vulnerabilities, please email: [likhonwrk@gmail.com](mailto:likhonwrk@gmail.com)

Do not create public issues for security vulnerabilities.

## 📚 Documentation

### Documentation Types

- **API Documentation**: OpenAPI/Swagger specs
- **User Guides**: Step-by-step instructions
- **Developer Guides**: Technical documentation
- **Architecture Docs**: System design documents
- **Troubleshooting**: Common issues and solutions

### Writing Documentation

- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Keep content up-to-date
- Test all instructions

## 🎉 Recognition

Contributors are recognized in:

- **README.md**: Contributors section
- **CHANGELOG.md**: Release notes
- **GitHub**: Contributor graphs
- **Discord**: Community recognition

## 📞 Getting Help

- **GitHub Issues**: Technical questions
- **GitHub Discussions**: General discussions
- **Discord**: Real-time chat (coming soon)
- **Email**: [likhonwrk@gmail.com](mailto:likhonwrk@gmail.com)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Agentic! 🚀
