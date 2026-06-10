# Design Thinking — Step Question Banks

The working questions for each step. Use them as prompts to yourself (or
to subagents in deep mode); skip questions that are plainly inapplicable,
never skip a gate.

## 1. Problem essence (Why)

- Why is this needed? Why does that matter? (repeat 3-5 layers until you
  hit business value or a user pain point — record the chain)
- Who exactly uses this, and in what scenario?
- How will we know it succeeded? (3-5 verifiable checkpoints, marked
  tentative — step 3 hardens them)
- Common chains worth recognizing: technical problem -> process issue ->
  organizational issue; feature request -> user experience -> commercial value.

## 2. Solution exploration (How)

Per option (2-3 options):

```text
Option <A/B/C>: <name>
Core idea: <one sentence>
Stack: <key tech and why>
Pros: <2-3, specific>
Cons: <2-3, honest>
Cost: <relative dev effort + operational burden>
```

- Are the options genuinely different (not one option in three coats)?
- Which fits the existing codebase and team skills — cite evidence?
- Scope: what is IN, what is OUT (with reason), what is future work?
- Recommendation: name the option and give 3+ reasons tied to constraints.

## 3. Risk & testing

- What can break technically? What existing behavior could this disturb?
- Which external dependencies can fail, and what happens then?
- Risk table: risk | impact (H/M/L) | concrete mitigation (no "be careful").
- Tests: what must unit tests cover? integration? E2E? Which acceptance
  criterion does each test verify?
- Boundary conditions (empty, max, concurrent) and error scenarios
  (network down, dependency unavailable) — each becomes a checklist item.

## 4. Reflection & integration

- One-sentence verdict from each lens: product (does it serve the Why?),
  architecture (is it sound and proportionate?), testing (is it verifiable?).
- Where do the lenses disagree? What knowledge is still missing?
- Any high-impact risk whose mitigation is hand-wavy?
- Verdict: READY / NEED_ITERATION (which step, what question) /
  NEED_USER_DECISION (state the trade-off cleanly, both sides' best case).

## 5. Final decision package

```markdown
## Decision: <title>
### Background & goals
<business value, core requirements, users/scenarios>
### Technical solution
Chosen: <name + one-line core idea>; key design points; stack choices.
Rejected: <option> — <why, one line each>
### Scope
In: ... / Out: <item — reason> / Future: ...
### Risks & mitigation
| risk | impact | mitigation |
### Acceptance criteria
Functional + boundary + error checklist; non-functional (perf, security).
### Test strategy
unit / integration / E2E scope.
### Next actions
3-5 concrete, ordered tasks.
```

Quality gate: self-contained; no unresolved conflicts; next actions
executable without re-reading the analysis.
