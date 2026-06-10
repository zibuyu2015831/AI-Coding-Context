---
name: design-thinking
description: Use when a task is complex or ambiguous and the user wants structured 5-Why analysis, multi-option comparison, and risk analysis before deciding — or asks to "think it through" / "@think". Not for reviewing finished output (use mutual-review).
---

# AICC Design Thinking

A five-step structured design pass that ends in a self-contained decision
package. Run it BEFORE writing a plan or code for anything non-trivial.

## When to run

- The user asks (`@think`, "think this through", "compare approaches").
- `aicc.enforceDesignThinking` is true and the task is architecture-class.
- Auto-suggest when the task smells complex: cross-module impact, new
  technology, security/compliance surface, or genuinely competing
  approaches.

Variants: **standard** (all 5 steps) | **quick** (steps 1, 2, 5 only — for
time-boxed or well-understood problems) | **deep** (standard + a
perspective debate in step 4, see below). Skip entirely only on explicit
user instruction — record the skip.

## The five steps

Detailed question banks: [references/step-prompts.md](references/step-prompts.md).

1. **Problem essence (Why)** — 5-Why chain (3+ layers) to the real business
   motivation; target users, scenario, tentative success criteria.
   Gate: root motivation stated in one sentence; criteria measurable.
2. **Solution exploration (How)** — 2-3 genuinely different options, each
   with core idea, stack, pros/cons, cost; a recommendation with 3+
   reasons; explicit In/Out of scope lists.
   Gate: at least 2 substantive options; no deferred decisions.
3. **Risk & testing** — risk table (risk, impact H/M/L, concrete
   mitigation); test strategy (unit/integration/E2E scope); acceptance
   criteria refined into testable checklist items incl. boundary and error
   cases.
   Gate: every high-impact risk has a mitigation.
4. **Reflection & integration** — check the three lenses (product,
   architecture, testing) for conflicts and gaps. Verdict: READY |
   NEED_ITERATION (name what to redo) | NEED_USER_DECISION (present the
   disagreement, let the user arbitrate).
5. **Final decision** — the decision package (format in
   [references/step-prompts.md](references/step-prompts.md) section 5):
   background, chosen solution + rejected alternatives, scope, risks,
   acceptance criteria, test strategy, next actions. It must stand alone —
   readable without steps 1-4.

## Perspective parameter (replaces persona files)

In step 2 critique and step 4 (always in **deep** mode), challenge the
design from one or more named perspectives:

| perspective | values | signature challenges |
| --- | --- | --- |
| `pragmatist` | reality over theory; simplicity; never break users | "Is this a real problem or invented?" "What's the simpler way?" "Will this break anything?" "Do the data structures already solve this?" |
| `evolutionist` | incremental change; readability; tests as safety net | "What are the smells here?" "Can we get there in three small steps?" "Where's the test coverage that makes this safe?" |
| `purist` | SOLID; TDD; naming as design | "How many reasons does this class have to change?" "Where are the tests?" "Does this name reveal intent?" |

Default: `pragmatist`. The user may name any combination ("challenge this
as a purist"). Output each perspective's strongest objections and how the
design answers them — unanswered objections go to step 4 as conflicts.

## Output & handoffs

- Write the decision package to the conversation; for architecture-class
  decisions also record an ADR (/aicc:adr).
- Feed the package to planning/implementation as-is; if the user wants a
  second opinion on it, run /aicc:mutual-review.
- During /aicc:init, this skill serves as the optional deep-analysis step
  for complex projects.
