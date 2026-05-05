# Generate Conventional Commit Message

Analyze the staged changes and generate a commit message that strictly follows the Conventional Commits 1.0.0 specification.

## Steps

1. Run `git diff --staged` to inspect all staged changes.
2. Run `git diff --staged --stat` for a file-level summary.
3. Analyze the nature, scope, and impact of the changes.
4. Generate a commit message following the rules below.
5. Show the proposed message to the user for confirmation before committing.

## Conventional Commits Rules

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Type (required)

Choose the single most accurate type:

| Type | When to use |
|------|-------------|
| `feat` | Introduces a new feature (maps to SemVer MINOR) |
| `fix` | Patches a bug (maps to SemVer PATCH) |
| `docs` | Documentation changes only |
| `style` | Formatting, whitespace — no logic change |
| `refactor` | Code restructuring — no feature or bug change |
| `perf` | Performance improvement |
| `test` | Adding or correcting tests |
| `build` | Build system or dependency changes |
| `ci` | CI/CD configuration changes |
| `chore` | Maintenance tasks that don't fit other types |
| `revert` | Reverts a previous commit |

### Scope (optional)

- A noun in parentheses describing the part of the codebase changed.
- Use the module name, file name (without extension), or logical area: `fix(parser):`, `feat(auth):`.
- Omit if the change is truly cross-cutting.

### Description (required)

- Lowercase, imperative mood ("add feature" not "added feature").
- No period at the end.
- 72 characters or fewer on the subject line.
- Must immediately follow the `type[(scope)]: ` prefix.

### Body (optional)

- Separated from the subject by a blank line.
- Explain **what** and **why**, not how.
- Wrap at 100 characters per line.
- Use multiple paragraphs if needed.

### Footers (optional)

- Separated from the body (or subject if no body) by a blank line.
- Use git trailer format: `Token: value` where multi-word tokens use hyphens (`Reviewed-by:`).
- `BREAKING CHANGE:` must be uppercase and followed by a description of what breaks and how to migrate.

### Breaking Changes

Signal a breaking change in one or both of these ways:

1. Append `!` before the colon: `feat(api)!: remove deprecated endpoint`
2. Add a footer: `BREAKING CHANGE: <description>`

Breaking changes map to SemVer MAJOR regardless of type.

## Decision Rules

- If the diff touches multiple unrelated concerns, still produce **one** message — pick the dominant change as the type and summarize the rest in the body.
- If the diff is empty or nothing is staged, report that and stop.
- If a change removes or alters a public API, flag it as `BREAKING CHANGE`.
- Prefer a concise subject over an exhaustive one; use the body for detail.

## Output Format

Present the commit message in a fenced code block so it is easy to copy, then ask:

> Commit with this message? (yes / edit / cancel)

If the user confirms, run:

```bash
git commit -m "$(cat <<'EOF'
<message here>
EOF
)"
```

If they want to edit, ask what to change and regenerate. If they cancel, do nothing.
