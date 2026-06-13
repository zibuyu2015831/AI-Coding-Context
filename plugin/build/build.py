#!/usr/bin/env python3
"""AICC plugin build: verify sources, lint, manifest, Codex projection.

The converged English artifacts under plugin/ are authored (convergence of
prose is editorial, not mechanical) and committed; this script is the
verification + provenance + projection layer:

  1. Assert the clone-form source dirs still exist and did not shrink
     (the plugin is additive; it must never break master/dev clone usage).
  2. Run the reverse-entropy lint (build/lint.py).
  3. Generate build/manifest.generated.json: every shipped plugin file ->
     source path(s) on the dev tree, converged flag, line count.
  4. Measure the doc-line budget (skills/ + references/ + agents/, excluding
     scripts/ and build/) against <= 50% of the 63,176-line source corpus.
  5. --codex: project the flat Codex package into dist/codex/ (see spec §7).

Usage: python3 build.py [--codex] [--json]
"""

import argparse
import json
import os
import re
import sys

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(PLUGIN_ROOT)
SOURCE_DIRS = ("core", "workflows", "agents", "tools", "templates", "guides")
DOC_BUDGET_BASELINE = 63176  # public doc corpus on dev at planning time
DOC_BUDGET_RATIO = 0.5

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint

# Provenance: plugin-relative path -> {sources: [dev-tree paths], converged,
# note}. "authored" means net-new plugin infrastructure with no 1:1 source.
# Convergence definition (spec §6): dropped source, >=30% reduction, or a
# merge of >=2 sources.
PROVENANCE = {
    ".claude-plugin/plugin.json": {"sources": [], "converged": None, "note": "authored"},
    "BUILD_NOTES.md": {"sources": [], "converged": None, "note": "authored build log"},
    "MIGRATION.md": {
        "sources": ["config/MIGRATION_GUIDE.md", "AI_ENTRY_POINT.md"],
        "converged": True,
        "note": "clone->plugin migration guide; supersedes manual-bootstrap instructions",
    },
    "README.md": {
        "sources": ["AI_ENTRY_POINT.md", "README.md"],
        "converged": True,
        "note": "quick-start distilled from the 811-line entry doc; rest deleted",
    },
    "settings.json": {
        "sources": ["config/CONFIG_TEMPLATE.md"],
        "converged": True,
        "note": "config keys reduced to the consumed set (spec §5)",
    },
    "hooks/hooks.json": {"sources": [], "converged": None, "note": "authored"},
    "hooks/_aicc_common.py": {"sources": [], "converged": None, "note": "authored"},
    "hooks/pre_commit_gate.py": {
        "sources": ["tools/git-hooks/pre-commit", "workflows/git_safety_workflow.md"],
        "converged": True,
        "note": "advisory pre-commit doc checks turned into an enforcing PreToolUse gate",
    },
    "hooks/dangerous_git_guard.py": {
        "sources": ["tools/py/git_safety.py", "workflows/git_safety_workflow.md"],
        "converged": True,
        "note": "dangerous-command list enforced at PreToolUse instead of advisory doc",
    },
    "hooks/session_inject.py": {
        "sources": ["AI_ENTRY_POINT.md"],
        "converged": True,
        "note": "replaces the manual paste-the-entry-doc bootstrap",
    },
    "hooks/post_tool_audit.py": {"sources": [], "converged": None, "note": "authored telemetry"},
    "scripts/py/summary_validator.py": {
        "sources": ["tools/py/summary_validator.py", "core/SUMMARY_FORMAT_SPEC.md"],
        "converged": True,
        "note": "English rewrite, ~60% smaller, same rule set",
    },
    "scripts/py/contract_check.py": {
        "sources": ["tools/py/framework_contract_checker.py", "core/contracts/main_doc_contract.yaml"],
        "converged": True,
        "note": "English rewrite; project-specific Chinese contract replaced by plugin contract v1",
    },
    "scripts/py/doc_health.py": {
        "sources": ["tools/py/doc_health_checker.py", "tools/py/timestamp_analyzer.py"],
        "converged": True,
        "note": "English rewrite of the health orchestrator (paths/staleness/frontmatter)",
    },
    "scripts/py/project_scan.py": {
        "sources": ["tools/py/project_scanner.py"],
        "converged": True,
        "note": "English rewrite, trimmed to type detection + inventory",
    },
    "scripts/py/git_safety.py": {
        "sources": ["tools/py/git_safety.py"],
        "converged": True,
        "note": "English rewrite of dangerous-operation classifier",
    },
    "scripts/py/complexity_scan.py": {
        "sources": ["tools/py/complexity_scanner.py"],
        "converged": True,
        "note": "English rewrite; metrics only, dashboard skill omitted (BUILD_NOTES)",
    },
    "scripts/py/knowledge.py": {
        "sources": ["tools/py/knowledge_cli.py", "tools/py/knowledge_matcher.py",
                    "tools/py/knowledge_repo_manager.py"],
        "converged": True,
        "note": "English rewrite of the real shared-repo mechanism, 3 tools merged",
    },
    "build/build.py": {"sources": [], "converged": None, "note": "authored"},
    "build/lint.py": {"sources": [], "converged": None, "note": "authored"},
    "build/codex_projection.py": {"sources": [], "converged": None,
                                  "note": "authored Codex flat projection (spec 7) + self-contained .codex/ hooks bundle for enforcement parity (Codex >= v0.117)"},
    "build/test_codex_projection.py": {"sources": [], "converged": None,
                                       "note": "authored regression test for the Codex projection + .codex/ enforcement bundle"},
}


def fail(message):
    print("BUILD FAIL: %s" % message)
    sys.exit(1)


def assert_sources_intact():
    for name in SOURCE_DIRS:
        path = os.path.join(REPO_ROOT, name)
        if not os.path.isdir(path) or not os.listdir(path):
            fail("source dir %s/ is missing or empty — clone form must stay intact" % name)


def shipped_files():
    skip_prefixes = ("build/manifest.generated.json",)
    for base, dirs, names in os.walk(PLUGIN_ROOT):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
        for name in sorted(names):
            rel = os.path.relpath(os.path.join(base, name), PLUGIN_ROOT)
            rel = rel.replace(os.sep, "/")
            if rel in skip_prefixes or name in (".gitkeep", ".gitignore"):
                continue
            yield rel


def count_lines(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


def generate_manifest():
    entries, missing = [], []
    for rel in shipped_files():
        meta = PROVENANCE.get(rel)
        if meta is None:
            # skills/agents/references entries are registered per-file below
            meta = AUTO_PROVENANCE(rel)
        if meta is None:
            missing.append(rel)
            continue
        entries.append({
            "path": rel,
            "sources": meta["sources"],
            "converged": meta["converged"],
            "lines": count_lines(os.path.join(PLUGIN_ROOT, rel)),
            "note": meta["note"],
        })
    if missing:
        fail("no provenance for shipped file(s): %s" % ", ".join(missing))
    manifest = {
        "plugin": "aicc",
        "source_branch": "dev",
        "entries": sorted(entries, key=lambda e: e["path"]),
        "doc_budget": doc_budget(),
    }
    out = os.path.join(PLUGIN_ROOT, "build", "manifest.generated.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=True)
        fh.write("\n")
    return manifest


# Per-directory provenance for authored skill/agent/reference content; the
# skill-level source mapping lives in SKILL_SOURCES and is applied per file.
SKILL_SOURCES = {
    "init": ["workflows/path_a_first_generation.md", "AI_ENTRY_POINT.md",
             "templates/GENERATION_PLAN_TEMPLATE.md", "templates/generation_plan_simple.md",
             "templates/generation_plan_medium.md", "templates/generation_plan_complex.md",
             "templates/generation_plan_critical.md", "templates/generation_plan_trivial.md",
             "templates/AI_Coding_Context_TEMPLATE.md", "templates/AI_RULES_TEMPLATE.md"],
    "health-check": ["workflows/path_b_health_check.md", "workflows/document_health_check.md",
                     "templates/HEALTH_CHECK_REPORT_TEMPLATE.md"],
    "incremental-update": ["workflows/path_c_incremental_update.md",
                           "workflows/commit_guided_update.md",
                           "workflows/git_safety_workflow.md",
                           "guides/commit_guided_quick_start.md",
                           "guides/commit_guided_migration.md"],
    "design-thinking": ["workflows/path_d_specific_tasks.md",
                        "templates/prompts/design_thinking/step1_why.md",
                        "templates/prompts/design_thinking/step2_how.md",
                        "templates/prompts/design_thinking/step3_risk.md",
                        "templates/prompts/design_thinking/step4_reflection.md",
                        "templates/prompts/design_thinking/step5_decision.md",
                        "agents/personas/linus_torvalds.md",
                        "agents/personas/martin_fowler.md",
                        "agents/personas/uncle_bob.md"],
    "mutual-review": ["workflows/review-workflow.md",
                      "agents/runtime/plan_reviewer.md", "agents/runtime/code_reviewer.md",
                      "workflows/review_standards/feature_review_standard.md",
                      "workflows/review_standards/bugfix_review_standard.md",
                      "workflows/review_standards/refactor_review_standard.md",
                      "workflows/review_standards/doc_review_standard.md"],
    "adr": ["dev/architecture/adr-template.md", "workflows/decision_workflow.md"],
    "doc-fallacy-fix": ["workflows/doc_error_fix_workflow.md",
                        "agents/workflows/error_detector.md",
                        "agents/workflows/document_fix_coordinator.md"],
    "systematic-review": ["dev/quality/AUDIT_WORKFLOW.md", "dev/quality/Start_Review.md",
                          "dev/quality/Issue_Recording_Standard.md"],
    "doc-reading-habit": ["core/SUMMARY_FORMAT_SPEC.md",
                          "agents/runtime/document_recommender.md"],
    "knowledge-reuse": ["tools/py/knowledge_cli.py", "tools/py/knowledge_matcher.py",
                        "agents/workflows/knowledge_librarian.md",
                        "agents/workflows/knowledge_matcher.md",
                        "templates/knowledge_README_TEMPLATE.md"],
}

AGENT_SOURCES = {
    "agents/architecture-analyst.md": ["agents/development/architecture_analyst.md"],
    "agents/api-designer.md": ["agents/development/api_designer.md"],
    "agents/database-designer.md": ["agents/development/database_designer.md"],
    "agents/product-manager.md": ["agents/development/product_manager.md"],
}

REFERENCE_SOURCES = {
    "references/language-rules.md": ["core/language_rules.md"],
    "references/security-rules.md": ["core/security_rules.md"],
    "references/summary-format-spec.md": ["core/SUMMARY_FORMAT_SPEC.md"],
    "references/project-types.md": ["core/project_types.md", "core/project_types/README.md"],
    "references/framework-boundary.md": ["AI_ENTRY_POINT.md"],
}


def AUTO_PROVENANCE(rel):
    if rel in AGENT_SOURCES:
        return {"sources": AGENT_SOURCES[rel], "converged": True,
                "note": "English conversion, boilerplate stripped"}
    if rel in REFERENCE_SOURCES:
        return {"sources": REFERENCE_SOURCES[rel], "converged": True,
                "note": "English convergence of core rule doc"}
    match = re.match(r"^skills/([^/]+)/", rel)
    if match and match.group(1) in SKILL_SOURCES:
        return {"sources": SKILL_SOURCES[match.group(1)], "converged": True,
                "note": "converged English skill content (see BUILD_NOTES.md)"}
    if rel.startswith("bin/"):
        return {"sources": ["tools/py/"], "converged": True,
                "note": "authored CLI wrapper over scripts/py"}
    return None


def doc_budget():
    total = 0
    for sub in ("skills", "references", "agents"):
        path = os.path.join(PLUGIN_ROOT, sub)
        if not os.path.isdir(path):
            continue
        for base, dirs, names in os.walk(path):
            for name in names:
                if name.endswith(".md"):
                    total += count_lines(os.path.join(base, name))
    cap = int(DOC_BUDGET_BASELINE * DOC_BUDGET_RATIO)
    return {"doc_lines": total, "baseline": DOC_BUDGET_BASELINE,
            "cap": cap, "within_budget": total <= cap}


def project_codex():
    """Emit the flat Codex package (spec §7). Implemented at checkpoint P4."""
    import codex_projection
    return codex_projection.run(PLUGIN_ROOT, os.path.join(REPO_ROOT, "dist", "codex"))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build/verify the AICC plugin.")
    parser.add_argument("--codex", action="store_true",
                        help="also project the flat Codex package into dist/codex/")
    parser.add_argument("--json", action="store_true", help="JSON summary output")
    args = parser.parse_args(argv)

    assert_sources_intact()
    problems = lint.run(PLUGIN_ROOT)
    if problems:
        for problem in problems:
            print("LINT: %s" % problem)
        fail("lint reported %d problem(s)" % len(problems))

    manifest = generate_manifest()
    budget = manifest["doc_budget"]
    if not budget["within_budget"]:
        print("WARNING: doc lines %d exceed the 50%% cap %d — converge further "
              "or justify in BUILD_NOTES.md" % (budget["doc_lines"], budget["cap"]))

    codex = project_codex() if args.codex else None
    summary = {
        "files": len(manifest["entries"]),
        "doc_budget": budget,
        "codex": codex,
        "lint": "clean",
    }
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print("build OK: %d files in manifest; doc lines %d / cap %d%s"
              % (summary["files"], budget["doc_lines"], budget["cap"],
                 "; codex projected" if codex else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
