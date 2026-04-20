import os
import re

def check_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if not lines or lines[0].strip() != '---':
            return False, "Missing opening ---"
            
        closing_idx = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                closing_idx = i
                break
        
        if closing_idx == -1:
            return False, "Missing closing ---"
            
        frontmatter_lines = lines[1:closing_idx]
        has_summary = False
        has_importance = False
        
        for line in frontmatter_lines:
            line = line.strip()
            if line.startswith('summary:'):
                has_summary = True
            if line.startswith('importance:'):
                has_importance = True
                
        missing = []
        if not has_summary:
            missing.append('summary')
        if not has_importance:
            missing.append('importance')
            
        if missing:
            return False, f"Missing fields: {', '.join(missing)}"
            
        return True, None
            
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

files = [
    "./tools/CHANGELOG.md",
    "./tools/fallback/commands_win.md",
    "./tools/fallback/commands_unix.md",
    "./tools/README.md",
    "./tools/ROADMAP.md",
    "./core/project_types.md",
    "./core/language_rules.md",
    "./core/security_rules.md",
    "./core/project_types/backend_api.md",
    "./core/project_types/data_science.md",
    "./core/project_types/containerized.md",
    "./core/project_types/fullstack.md",
    "./core/project_types/script.md",
    "./core/project_types/library_sdk.md",
    "./core/project_types/README.md",
    "./core/project_types/microservices.md",
    "./core/project_types/mobile_app.md",
    "./core/project_types/desktop_app.md",
    "./core/project_types/serverless.md",
    "./core/project_types/web_frontend.md",
    "./core/project_types/ai_llm_app.md",
    "./core/project_types/cli_tool.md",
    "./core/update_triggers.md",
    "./quality/AUDIT_WORKFLOW.md",
    "./quality/contexts/_template.md",
    "./quality/HOW_TO_GENERATE_CONTEXTS.md",
    "./quality/README.md",
    "./quality/standards/COMMON_STANDARDS.md",
    "./quality/standards/QUALITY_CHECKLIST.md",
    "./config/CONFIG_TEMPLATE.md",
    "./config/README.md",
    "./config/MIGRATION_GUIDE.md",
    "./workflows/incremental_update_workflow.md",
    "./workflows/review-workflow.md",
    "./workflows/document_health_check.md",
    "./workflows/path_a_first_generation.md",
    "./workflows/path_d_specific_tasks.md",
    "./workflows/progress_tracking.md",
    "./workflows/doc_error_fix_workflow.md",
    "./workflows/generation_workflow.md",
    "./workflows/maintenance_workflow.md",
    "./workflows/shared/failure_handling.md",
    "./workflows/shared/special_scenarios.md",
    "./workflows/shared/ai_checklist.md",
    "./workflows/create_custom_agent_workflow.md",
    "./workflows/detection_workflow.md",
    "./workflows/path_c_incremental_update.md",
    "./workflows/path_b_health_check.md",
    "./workflows/monorepo_workflow.md",
    "./workflows/decision_workflow.md",
    "./workflows/create_custom_tool_workflow.md",
    "./workflows/git_safety_workflow.md",
    "./workflows/review_standards/feature_review_standard.md",
    "./workflows/review_standards/doc_review_standard.md",
    "./workflows/review_standards/refactor_review_standard.md",
    "./workflows/review_standards/bugfix_review_standard.md",
    "./workflows/commit_guided_update.md",
    "./agents/development/database_designer.md",
    "./agents/development/architecture_analyst.md",
    "./agents/development/product_manager.md",
    "./agents/development/api_designer.md",
    "./agents/_templates/agent_template.md",
    "./agents/_templates/quality_checklist.md",
    "./agents/_progress/implementation_progress.md",
    "./agents/_progress/issues_and_feedback.md",
    "./agents/_progress/role_conversion_log.md",
    "./agents/runtime/plan_reviewer.md",
    "./agents/runtime/design_facilitator.md",
    "./agents/runtime/performance_optimizer.md",
    "./agents/runtime/commit_analyst.md",
    "./agents/runtime/security_auditor.md",
    "./agents/runtime/document_recommender.md",
    "./agents/runtime/understanding_guardian.md",
    "./agents/runtime/code_reviewer.md",
    "./agents/runtime/test_engineer.md",
    "./agents/runtime/summary_generator.md",
    "./agents/workflows/create_custom_agent_workflow.md",
    "./agents/workflows/README.md",
    "./agents/README.md",
    "./agents/personas/uncle_bob.md",
    "./agents/personas/martin_fowler.md",
    "./agents/personas/README.md",
    "./agents/personas/linus_torvalds.md",
    "./agents/language_specific/python/python_expert.md",
    "./agents/language_specific/typescript/typescript_expert.md",
    "./agents/language_specific/vue3_expert.md",
    "./agents/language_specific/java/java_expert.md",
    "./agents/language_specific/vue3_state_manager.md",
    "./agents/language_specific/base/backend_engineer.md",
    "./agents/language_specific/base/frontend_engineer.md",
    "./agents/examples/typescript_expert_examples.md",
    "./agents/examples/plan_reviewer_examples.md",
    "./agents/examples/python_expert_examples.md",
    "./agents/examples/design_thinking/user_login_flow.md",
    "./agents/examples/vue3_expert_examples.md",
    "./agents/examples/performance_optimizer_examples.md",
    "./agents/examples/code_reviewer_examples.md",
    "./agents/examples/test_engineer_examples.md",
    "./agents/examples/README.md",
    "./agents/examples/api_designer_examples.md",
    "./agents/examples/vue3_state_manager_examples.md",
    "./agents/examples/backend_engineer_examples.md",
    "./agents/examples/database_designer_examples.md",
    "./agents/examples/java_expert_examples.md",
    "./agents/examples/security_auditor_examples.md",
    "./agents/examples/architecture_analyst_examples.md",
    "./agents/custom/_template.md",
    "./agents/custom/README.md",
    "./docs/README.md",
    "./docs/guides/commit_guided_migration.md",
    "./docs/guides/commit_guided_quick_start.md",
    "./README.md",
    "./guides/ai_rules_maintenance.md",
    "./guides/project_types.md",
    "./guides/generation_workflow.md",
    "./guides/configuration_management.md",
    "./guides/faq.md",
    "./guides/documentation_maintenance.md",
    "./guides/language_support.md",
    "./guides/quick_start.md",
    "./CONTRIBUTING.md",
    "./AI_ENTRY_POINT.md",
    "./templates/PROGRESS_TRACKING_TEMPLATE.md",
    "./templates/deployment_guide_TEMPLATE.md",
    "./templates/PLAN_TEMPLATE.md",
    "./templates/PROGRESS_TEMPLATE.md",
    "./templates/generation_plan_medium.md",
    "./templates/PROJECT_ANALYSIS_REPORT_TEMPLATE.md",
    "./templates/AI_RULES_TEMPLATE.md",
    "./templates/rules_README_TEMPLATE.md",
    "./templates/generation_plan_critical.md",
    "./templates/generation_plan_complex.md",
    "./templates/HEALTH_CHECK_REPORT_TEMPLATE.md",
    "./templates/RULE_TEMPLATE.md",
    "./templates/knowledge_README_TEMPLATE.md",
    "./templates/review/review_plan_TEMPLATE.md",
    "./templates/review/review_principles_TEMPLATE.md",
    "./templates/generation_plan_trivial.md",
    "./templates/generation_plan_simple.md",
    "./templates/rules/core/api_calling_EXAMPLE.md",
    "./templates/rules/triggers/document_reading_EXAMPLE.md",
    "./templates/rules/AI_RULES_STANDARD_TEMPLATE.md",
    "./templates/prompts/design_thinking/step5_decision.md",
    "./templates/prompts/design_thinking/step3_risk.md",
    "./templates/prompts/design_thinking/step4_reflection.md",
    "./templates/prompts/design_thinking/step2_how.md",
    "./templates/prompts/design_thinking/step1_why.md",
    "./templates/AI_Coding_Context_TEMPLATE.md",
    "./templates/testing_guide_TEMPLATE.md",
    "./templates/plans_README_TEMPLATE.md",
    "./templates/GENERATION_PLAN_TEMPLATE.md",
    "./.kiro/specs/js-cli-tools-implementation/requirements.md",
    "./.kiro/specs/js-cli-tools-implementation/tasks.md",
    "./.kiro/specs/js-cli-tools-implementation/design.md",
    "./.kiro/specs/post-generation-audit/requirements.md",
    "./.kiro/specs/post-generation-audit/QUICK_START.md",
    "./dev_docs/architecture/decisions/002-layered-documentation.md",
    "./dev_docs/architecture/decisions/001-markdown-as-first-class-doc.md",
    "./dev_docs/architecture/adr-template.md",
    "./dev_docs/architecture/evolution.md",
    "./reference/design_decisions.md",
    "./reference/SUMMARY_FORMAT_SPEC.md",
    "./reference/README.md",
    "./reference/framework_spec.md",
    "./reference/examples/summary_examples/tool_doc_example.md",
    "./reference/examples/summary_examples/config_doc_example.md",
    "./reference/examples/summary_examples/architecture_doc_example.md",
    "./reference/examples/summary_examples/workflow_doc_example.md",
    "./reference/examples/summary_examples/api_doc_example.md"
]

missing_list = []
for f in files:
    if os.path.isfile(f):
        is_ok, reason = check_file(f)
        if not is_ok:
            missing_list.append((f, reason))

for f, reason in missing_list:
    print(f"{f}: {reason}")
