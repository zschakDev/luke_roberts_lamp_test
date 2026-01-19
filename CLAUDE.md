# CLAUDE.md - AI Assistant Guide

**Last Updated:** 2026-01-19
**Repository:** luke_roberts_lamp_test
**Status:** Initial/Development Phase

---

## 🎯 Purpose

This document provides comprehensive guidance for AI assistants (like Claude) working with this codebase. It explains the project structure, development workflows, conventions, and best practices to follow.

---

## 📁 Repository Overview

### Current State

This repository is in its **initial development phase**. As of the last update, it contains:

- Basic repository structure
- README.md with project title
- Git workflow configured for AI-assisted development

### Project Context

**Project Name:** luke_roberts_lamp_test
**Suggested Focus:** LAMP stack testing/development (Linux, Apache, MySQL, PHP)
**Stage:** New/Template Repository

---

## 🏗️ Codebase Structure

### Current Directory Layout

```
luke_roberts_lamp_test/
├── README.md          # Project overview and documentation
├── CLAUDE.md          # This file - AI assistant guide
└── .git/              # Git repository data
```

### Expected Future Structure

As the project develops, expect the following structure:

```
luke_roberts_lamp_test/
├── src/               # Source code
├── tests/             # Test files
├── config/            # Configuration files
├── docs/              # Additional documentation
├── scripts/           # Build/utility scripts
├── public/            # Public assets (if web project)
├── .env.example       # Environment variable template
├── README.md          # Project documentation
├── CLAUDE.md          # AI assistant guide (this file)
└── [build configs]    # package.json, composer.json, etc.
```

---

## 🔧 Technology Stack

### Current Stack

**Status:** Not yet defined

### Potential Stack (Based on Project Name)

If this becomes a LAMP stack project:

- **L**inux - Operating system
- **A**pache - Web server
- **M**ySQL/MariaDB - Database
- **P**HP - Server-side scripting

### To Be Determined

- Build tools
- Testing frameworks
- Development dependencies
- CI/CD pipeline tools

---

## 🔄 Git Workflow

### Branch Strategy

**Development Branch:** `claude/claude-md-mkkgvl3xfllqnwo4-q6J4e`

### Important Git Rules

#### ✅ DO:
- Develop all changes on the designated Claude branch
- Use clear, descriptive commit messages
- Push to the specified branch when changes are complete
- Create the branch locally if it doesn't exist yet
- Use `git push -u origin <branch-name>` for pushing

#### ❌ DON'T:
- Never push to a different branch without explicit permission
- Never push to main/master without authorization
- Never use force push unless explicitly requested
- Never skip git hooks (--no-verify)

### Git Push Protocol

**Standard push command:**
```bash
git push -u origin claude/claude-md-mkkgvl3xfllqnwo4-q6J4e
```

**Critical Requirements:**
- Branch must start with 'claude/' and end with matching session ID
- Pushes to non-matching branches will fail with 403 HTTP code
- Retry on network errors up to 4 times with exponential backoff (2s, 4s, 8s, 16s)

### Git Fetch/Pull Protocol

**Prefer specific branches:**
```bash
git fetch origin <branch-name>
git pull origin <branch-name>
```

**Retry logic:** Same as push - up to 4 retries with exponential backoff on network failures

### Commit Message Guidelines

**Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style/formatting
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat: Add user authentication system

Implement JWT-based authentication with login/logout endpoints.
Includes password hashing and token validation.

Closes #123
```

---

## 📝 Development Conventions

### Code Style

**To Be Established** - Will be updated as project develops

When writing code:
- Follow language-specific best practices
- Maintain consistency with existing code
- Add comments only where logic isn't self-evident
- Avoid over-engineering - keep solutions simple

### File Naming

**To Be Established** - Will be updated as project develops

General guidelines:
- Use descriptive, meaningful names
- Follow language/framework conventions
- Be consistent with existing patterns

### Documentation Standards

**Code Documentation:**
- Document complex algorithms and business logic
- Don't document obvious code
- Keep comments up-to-date with code changes

**Project Documentation:**
- Keep README.md current with setup instructions
- Update CLAUDE.md as conventions are established
- Document API endpoints and interfaces

---

## 🧪 Testing Strategy

### Current Status

**No testing framework configured yet**

### Future Testing Approach

When testing is implemented, follow these principles:
- Write tests for new features
- Maintain existing tests when refactoring
- Run tests before committing
- Aim for meaningful test coverage, not just high percentages

### Expected Test Structure

```
tests/
├── unit/          # Unit tests
├── integration/   # Integration tests
├── e2e/           # End-to-end tests
└── fixtures/      # Test data
```

---

## 🚀 Build & Deployment

### Current Status

**No build system configured yet**

### Future Build Process

Will be documented here once established:
- Build commands
- Environment setup
- Deployment procedures
- Environment variables

---

## 🤖 AI Assistant Guidelines

### General Principles

1. **Read Before Modify:** Always read files before suggesting changes
2. **Minimal Changes:** Only make changes that are directly requested
3. **No Over-Engineering:** Keep solutions simple and focused
4. **Security First:** Watch for vulnerabilities (XSS, SQL injection, etc.)
5. **Context Awareness:** Use TodoWrite tool for complex, multi-step tasks

### Before Making Changes

✅ **Always:**
- Read the file you're about to modify
- Understand the existing code structure
- Check for existing patterns to follow
- Consider security implications
- Use TodoWrite for task planning when appropriate

❌ **Never:**
- Make changes to code you haven't read
- Add features beyond what was requested
- Refactor surrounding code unnecessarily
- Add error handling for impossible scenarios
- Create abstractions for one-time operations

### Task Execution Workflow

1. **Understand:** Read relevant files and context
2. **Plan:** Use TodoWrite for multi-step tasks
3. **Clarify:** Use AskUserQuestion if unclear
4. **Implement:** Make focused, minimal changes
5. **Verify:** Test changes work as expected
6. **Commit:** Follow git workflow (if requested)

### Code References

When referencing code, use the pattern: `file_path:line_number`

**Example:** "The initialization happens in src/index.js:42"

### Tool Usage

**Prefer specialized tools:**
- `Read` - for reading files (not `cat`)
- `Edit` - for modifying files (not `sed`)
- `Write` - for creating files (not `echo >`)
- `Grep` - for searching content (not `grep`)
- `Glob` - for finding files (not `find`)
- `Task` with Explore agent - for codebase exploration

**Parallel execution:**
- Use multiple tool calls in single message when operations are independent
- Use sequential calls only when there are dependencies

---

## 🔒 Security Considerations

### General Guidelines

- Never commit sensitive data (.env files, credentials, API keys)
- Validate user input at system boundaries
- Use parameterized queries for database operations
- Implement proper authentication and authorization
- Keep dependencies updated

### Common Vulnerabilities to Avoid

- SQL Injection
- Cross-Site Scripting (XSS)
- Cross-Site Request Forgery (CSRF)
- Command Injection
- Path Traversal
- Insecure Deserialization

---

## 📚 Additional Resources

### Project Documentation

- **README.md** - Main project documentation
- **CLAUDE.md** - This file (AI assistant guide)

### External Resources

*To be added as project develops*

---

## 🔄 Changelog

### 2026-01-19
- Initial CLAUDE.md creation
- Documented git workflow requirements
- Established AI assistant guidelines
- Created placeholder structure for future development

---

## 📮 Contributing

### For AI Assistants

Follow the guidelines in this document. When in doubt:
1. Ask for clarification
2. Make minimal changes
3. Prioritize security and simplicity
4. Document significant decisions

### For Human Developers

*To be established as team grows*

---

## ❓ Questions or Updates Needed?

This document should evolve with the project. If conventions change or new patterns emerge, update this file to reflect the current state of the codebase.

**Update Protocol:**
- Document new conventions as they're established
- Keep the technology stack section current
- Update directory structure when it changes
- Add examples of common patterns
- Note breaking changes or major refactors

---

**End of CLAUDE.md**
