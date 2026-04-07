# 🤖 Strengthen hook review guidance with state schema and parity rules

## Job Story

**When** a developer adds Python implementations of hooks that already exist as shell scripts, **wants to** verify that both implementations remain in sync and consume state identically, **so** they can **catch divergence early before silent failures** in production.

## Summary

This PR adds two new rule files to strengthen code review for hook-related changes:

1. **`.claude/rules/hook-state-schema.md`** — Formal documentation and validation pattern for JSON state written by hooks for consumption by other hooks (e.g., session state persistence)

2. **`.claude/rules/hook-patterns.md`** — Verification guidance for maintaining multiple language implementations of the same hook (Python and shell)

Both rules are derived from gaps identified in PR #751 (Enable SessionStop hooks via dev10x hook session) through post-merge lessons learned analysis.

## Changes Applied

### High Priority Item: Hook State Schema Documentation

**File**: `.claude/rules/hook-state-schema.md` (new)

When a hook writes JSON state for future consumption, reviewers need a structured checklist to prevent divergence. PR #751 added `session_persist()` which writes session state that `session_reload()` consumes, but no formal documentation existed for this pattern.

**Includes**:
- Definition of when pattern applies
- Five-point schema documentation requirements
- Example reviewer checklist
- Anti-patterns to avoid
- References to related guidance

**Impact**: Prevents schema divergence in future hooks that write state (e.g., session_migrate_permissions, future audit trail hooks)

### High Priority Item: Python-Shell Equivalence Verification

**File**: `.claude/rules/hook-patterns.md` (new)

PR #751 demonstrated the pattern: both `session_persist()` and `session_goodbye()` have Python implementations that mirror existing shell scripts. Without formalized verification, future ports could diverge silently.

**Includes**:
- Definition of when pattern applies (parallel implementations)
- Five-point verification checklist (schemas, error handling, fallbacks, types, testing)
- Example test pattern for interop validation
- Anti-patterns to avoid
- References to related guidance

**Impact**: Catches divergence between language implementations early; applicable to any hook ported to/from Python

## Filtered Items (Skipped)

**Item 1: Elevate hook guidance item 9b in reviewer-generic.md**
- **Reason**: SKIPPED — Insufficient recurrence. Item 9b already exists in code but wasn't applied in PR #751. This appears to be one-off enforcement miss, not a pattern across 2+ PRs.
- **Evidence**: Only PR #751 shown as evidence of non-enforcement

## References

Based on lessons learned analysis of PR #751:  
https://github.com/Dev10x-Guru/dev10x-claude/pull/751

Lessons learned report generated: 2026-04-07

## Testing

No functional tests required (documentation/guidance only). Changes are additive to review process.

---

## File Contents

### .claude/rules/hook-state-schema.md

```markdown
# Hook State Schemas

Pattern for documenting and validating JSON state written by hooks for
consumption by other hooks (same session or future sessions).

## When This Pattern Applies

When a hook writes a JSON state object that is intended to be read by:
- Other hooks in the same session (e.g., SessionStart reads what SessionStop writes)
- The same hook in a future session (e.g., session state persistence)
- CLI tools that parse persisted state

Examples:
- `session_persist()` writes session state that `session_reload()` consumes
- Any hook writing data to `~/.claude/projects/_session_state/`

## Schema Documentation Requirements

When a hook writes JSON state:

1. **Schema definition** — Document all fields in the state object:
   - Field name and type (`str`, `bool`, `list`, etc.)
   - Whether field is optional or required
   - Default value if field is missing
   - Example value

2. **Reader validation** — Grep for all consumers of the schema:
   - Identify every function/hook that reads this state
   - Verify each reader handles all defined fields
   - Verify each reader provides appropriate fallbacks for missing fields

3. **Fallback consistency** — For fields with defaults:
   - Document which fields have fallbacks
   - Verify all readers use identical defaults (no silent mismatches)
   - Test behavior when field is missing/null in JSON

4. **Type compatibility** — For hooks implemented in multiple languages:
   - Verify Python `bool` serializes to JSON `true`/`false` (not string `"true"`)
   - Verify shell scripts parse booleans consistently
   - Test type coercion at language boundaries

5. **Test interop** — When both Python and shell implementations exist:
   - Write at least one test that parses output from each language
   - Compare output schemas between implementations
   - Verify identical error handling for missing fields

## Example Checklist

For a new hook that writes session state:

- [ ] Create schema table in hook docstring or `.claude/rules/` reference
- [ ] Document each field: name, type, default, example value
- [ ] Grep for all readers of this state (test by searching state dict keys)
- [ ] For each reader, verify fallback handling with `state.get("field", default)`
- [ ] If both Python and shell versions exist, add test comparing output
- [ ] Verify type representation matches across implementations (JSON bool vs string)

## Anti-Patterns

- ❌ Adding new fields to state without updating readers — causes silent failures
- ❌ Different fallback values in different readers — inconsistent behavior
- ❌ Type mismatches between writer and reader (e.g., Python `True` vs shell `"true"`) — parsing errors
- ❌ Testing only the writer, not the reader — divergence not caught until runtime

## Reference

See `.claude/rules/INDEX.md` for hook-related review guidance and agent
routing. Related: `.claude/rules/hook-input-patterns.md` (input validation).
```

### .claude/rules/hook-patterns.md

```markdown
# Hook Implementation Patterns

Guidance for maintaining consistent implementations when hooks exist in
multiple languages (Python and shell).

## When This Pattern Applies

When a PR adds a Python implementation of a hook that already exists as a
shell script (or vice versa), both implementations should be functionally
equivalent and use identical schemas.

Examples:
- `session_persist()` (Python) mirrors `session-stop-persist.sh` (shell)
- `session_goodbye()` (Python) mirrors `session-stop-goodbye.sh` (shell)

## Verification Checklist

### 1. Input/Output Schema Equivalence

- [ ] Both implementations read from identical stdin format (JSON structure)
- [ ] Both implementations write to identical stdout/file format
- [ ] Field names are identical across implementations (no renaming)
- [ ] Field types are compatible (JSON `true`/`false` vs shell `"true"`/`"false"`)

### 2. Error Handling Parity

- [ ] Both implementations handle missing stdin identically
- [ ] Both implementations handle malformed JSON identically
- [ ] Both implementations use same exit codes for error conditions
- [ ] Both implementations produce same error messages (or equivalent)

### 3. Fallback Value Consistency

- [ ] For optional fields, both implementations use identical defaults
- [ ] Missing/null values are handled the same way
- [ ] No silent failures due to different default handling
- [ ] Documented which fields have fallbacks and what the defaults are

### 4. Data Type Representation

- [ ] Booleans: JSON `true`/`false` vs shell string `"true"`/`"false"` — aligned
- [ ] Integers: JSON `123` vs shell `"123"` — explicitly tested
- [ ] Lists: JSON array `[...]` vs shell multiline/CSV — conversion verified
- [ ] Timestamps: identical format (ISO8601, UTC, etc.)

### 5. Cross-Language Testing

- [ ] At least one test invokes shell implementation and parses output
- [ ] At least one test invokes Python implementation and parses output
- [ ] Both outputs are compared for schema equivalence
- [ ] Test covers at least one error condition with missing/null data

## Example Test Pattern

```python
# Test that both implementations produce compatible output
def test_session_persist_matches_shell_implementation():
    # Invoke Python function
    python_output = session_persist()  # returns dict
    python_json = json.dumps(python_output)
    
    # Invoke shell script
    shell_proc = subprocess.run(
        ["bash", "hooks/scripts/session-stop-persist.sh"],
        input=json.dumps(stdin_data),
        capture_output=True,
        text=True
    )
    shell_output = json.loads(shell_proc.stdout)
    
    # Compare schemas
    assert set(python_output.keys()) == set(shell_output.keys())
    assert python_output["branch"] == shell_output["branch"]
    # ... verify all fields
```

## Anti-Patterns

- ❌ Implementing Python version without testing against shell version
- ❌ Renaming fields during port (field name divergence)
- ❌ Different type representations (bool vs string) not caught by tests
- ❌ Different error handling (one throws, other returns null) — silent divergence
- ❌ Different fallback values in readers (one uses `""`, other uses `"unknown"`)

## Reference

See `.claude/rules/hook-state-schema.md` for documenting state schemas.
See `.claude/rules/hook-input-patterns.md` for input validation patterns.
```
