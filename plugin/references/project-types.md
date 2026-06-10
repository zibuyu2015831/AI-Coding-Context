# Project Types

AICC recognizes these project types. The type drives which sub-docs the
generation plan proposes; detection signals come from `aicc-scan`.

| type | detection signals | characteristic sub-docs |
| --- | --- | --- |
| web frontend | package.json + react/vue/angular deps | component_guide, state_management, routing_guide |
| fullstack | frontend deps + server framework or monorepo | architecture_overview, api_layer, + frontend set |
| backend API | express/fastapi/spring/gin, no UI deps | api_layer, database_schema, deployment_guide |
| microservices | multiple service dirs, compose/k8s manifests | per-service overview, service_boundaries, deployment_guide |
| mobile app | pubspec.yaml, android/ + ios/, react-native | screen_flow, state_management, release_guide |
| desktop app | electron/tauri deps, .xcodeproj | architecture_overview, packaging_guide |
| CLI tool | bin entry, console_scripts, cobra/clap | command_reference, architecture_overview |
| library / SDK | exports + no app entry, publish config | api_reference, usage_guide, versioning_policy |
| script / toy | < ~10 files, no package structure | main doc only |
| data science | notebooks, pandas/sklearn deps | data_pipeline, experiment_guide |
| AI / LLM app | llm sdk deps (anthropic/openai), prompt dirs | prompt_catalog, model_config, eval_guide |
| serverless | serverless.yml, sam/cdk templates | function_map, deployment_guide |
| containerized | Dockerfile/compose as primary delivery | deployment_guide, service_topology |

Rules:

- Detect from marker files and dependencies, not directory names alone.
- A project can match 2+ types (e.g. containerized backend API): union the
  sub-doc sets, then prune to what the code actually contains.
- When signals conflict or none match, ask the user instead of guessing.
