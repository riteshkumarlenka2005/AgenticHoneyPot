# Contributing to Agentic HoneyPot

Thank you for your interest in contributing to the Agentic HoneyPot project! This document provides guidelines and information for contributors.

## 🎯 Project Vision

The Agentic HoneyPot aims to be a production-grade autonomous AI system for:
- Detecting and engaging scammers
- Extracting intelligence safely and ethically
- Wasting scammer time to protect potential victims
- Providing insights into scam patterns and tactics

## 🤝 How to Contribute

### Reporting Issues

- Check existing issues before creating a new one
- Use clear, descriptive titles
- Include steps to reproduce bugs
- Provide system information (OS, Python/Node version, etc.)
- Add relevant logs or screenshots

### Suggesting Features

- Explain the use case and benefit
- Consider safety and ethical implications
- Describe the expected behavior
- Suggest implementation approach if possible

### Submitting Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: brief description"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request**

## 📝 Code Guidelines

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints for all functions
- Add docstrings to classes and functions
- Keep functions focused and single-purpose
- Write unit tests for new features

Example:
```python
def detect_scam(message: str, history: Optional[list[dict]] = None) -> dict:
    """
    Detect if a message is a scam.
    
    Args:
        message: The message to analyze
        history: Optional conversation history
        
    Returns:
        Detection results with confidence and scam type
    """
    # Implementation
    pass
```

### TypeScript (Frontend)

- Use TypeScript strict mode
- Create reusable components
- Follow React best practices
- Use meaningful variable names
- Add JSDoc comments for complex logic

Example:
```typescript
interface ConversationProps {
  id: string
  onUpdate?: (conversation: Conversation) => void
}

export function ConversationView({ id, onUpdate }: ConversationProps) {
  // Implementation
}
```

### General Guidelines

- Keep code DRY (Don't Repeat Yourself)
- Write self-documenting code
- Add comments for complex logic
- Handle errors gracefully
- Validate user input

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest app/tests/
```

### Frontend Tests

```bash
cd frontend
npm test
```

### End-to-End Testing

1. Start the system with Docker Compose
2. Test the mock scammer workflow
3. Verify intelligence extraction
4. Check all dashboard pages

## 🔒 Security Considerations

When contributing, always consider:

1. **Safety Guardrails**: Never bypass safety limits
2. **Data Privacy**: Handle extracted data responsibly
3. **Input Validation**: Sanitize all user inputs
4. **Authentication**: Secure sensitive endpoints
5. **Rate Limiting**: Prevent abuse

## 🎨 Design Principles

### Backend

- **Modularity**: Keep services independent
- **Scalability**: Design for horizontal scaling
- **Testability**: Write testable code
- **Documentation**: Document APIs and complex logic
- **Error Handling**: Fail gracefully with helpful messages

### Frontend

- **Accessibility**: Follow WCAG guidelines
- **Responsiveness**: Support mobile, tablet, desktop
- **Performance**: Optimize bundle size and loading
- **User Experience**: Intuitive navigation and feedback
- **Consistency**: Use design system components

## 📚 Areas for Contribution

### High Priority

- [ ] WebSocket real-time updates
- [ ] Database persistence (currently in-memory)
- [ ] Advanced persona customization
- [ ] More scam detection patterns
- [ ] Multi-language support

### Medium Priority

- [ ] Conversation export/import
- [ ] Scammer profile tracking
- [ ] Advanced analytics and reporting
- [ ] API authentication and authorization
- [ ] Automated testing suite

### Documentation

- [ ] Video tutorials
- [ ] Architecture deep-dives
- [ ] Deployment guides (AWS, GCP, Azure)
- [ ] API client libraries (Python, JavaScript)
- [ ] Case studies and examples

## 🐛 Bug Triage Process

1. **Confirm**: Verify the bug is reproducible
2. **Classify**: Assign severity (critical, high, medium, low)
3. **Investigate**: Identify root cause
4. **Fix**: Implement solution with tests
5. **Verify**: Confirm fix resolves issue

## 📋 Pull Request Checklist

Before submitting:

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New code has tests
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] Safety guardrails are respected
- [ ] Changes are backward compatible (or migration path provided)

## 🔍 Code Review Process

Pull requests will be reviewed for:

- **Functionality**: Does it work as intended?
- **Code Quality**: Is it maintainable and clean?
- **Testing**: Are there adequate tests?
- **Documentation**: Is it well-documented?
- **Safety**: Does it respect safety guardrails?
- **Performance**: Is it efficient?

## 📞 Getting Help

- Open a GitHub issue for questions
- Join discussions in pull requests
- Review existing code and documentation

## 🎉 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Thanked in the community

## ⚖️ Legal

By contributing, you agree that:
- Your contributions will be licensed under the MIT License
- You have the right to submit the contribution
- Your contribution is your original work

## 🌟 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing private information
- Unethical use of the system

### Enforcement

Violations may result in:
1. Warning
2. Temporary ban
3. Permanent ban

## 📜 License

This project is licensed under the MIT License. See LICENSE file for details.

---

Thank you for contributing to making the internet safer! 🛡️
