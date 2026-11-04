# Optimist.Orchestrator Wiki

> Public technical documentation for the Optimist.Orchestrator ETSI MEC edge-orchestration platform.
> The documentation was generated from the repository wiki export and organized into browsable chapters.

## Browse the wiki

Once GitHub Pages is enabled, its deployed site provides the full sidebar, search, and Mermaid diagram rendering; the repository tree below remains directly browsable on GitHub.
See the [publishing and update guide](PUBLISHING.md) to enable GitHub Pages and refresh the wiki.
You can also browse every Markdown page directly from the repository tree below.

- [Getting Started](content/Getting%20Started.md)
- [Architecture Overview](content/Architecture%20Overview/Architecture%20Overview.md)
  - [System Overview and ETSI MEC Compliance](content/Architecture%20Overview/System%20Overview%20and%20ETSI%20MEC%20Compliance.md)
  - [Service Boundaries and Bounded Contexts](content/Architecture%20Overview/Service%20Boundaries%20and%20Bounded%20Contexts.md)
  - [Core Data Flows and Integration Patterns](content/Architecture%20Overview/Core%20Data%20Flows%20and%20Integration%20Patterns.md)
  - [Technology Stack and Infrastructure Dependencies](content/Architecture%20Overview/Technology%20Stack%20and%20Infrastructure%20Dependencies.md)
- [Core Services](content/Core%20Services/Core%20Services.md)
  - [Meao (MEO Orchestration Service)](content/Core%20Services/Meao%20%28MEO%20Orchestration%20Service%29/Meao%20%28MEO%20Orchestration%20Service%29.md)
    - [Temporal Workflows and Orchestration](content/Core%20Services/Meao%20%28MEO%20Orchestration%20Service%29/Temporal%20Workflows%20and%20Orchestration.md)
    - [Dynamic Placement Engine](content/Core%20Services/Meao%20%28MEO%20Orchestration%20Service%29/Dynamic%20Placement%20Engine.md)
    - [REST API Endpoints](content/Core%20Services/Meao%20%28MEO%20Orchestration%20Service%29/REST%20API%20Endpoints.md)
    - [Temporal Activities and Side Effects](content/Core%20Services/Meao%20%28MEO%20Orchestration%20Service%29/Temporal%20Activities%20and%20Side%20Effects.md)
    - [Service Configuration and Health](content/Core%20Services/Meao%20%28MEO%20Orchestration%20Service%29/Service%20Configuration%20and%20Health.md)
  - [ApmApi (Application Package Management Service)](content/Core%20Services/ApmApi%20%28Application%20Package%20Management%20Service%29/ApmApi%20%28Application%20Package%20Management%20Service%29.md)
    - [REST API Endpoints (/app_pkgm/v1)](content/Core%20Services/ApmApi%20%28Application%20Package%20Management%20Service%29/REST%20API%20Endpoints%20%28_app_pkgm_v1%29.md)
    - [CSAR Validation and Integrity Checking](content/Core%20Services/ApmApi%20%28Application%20Package%20Management%20Service%29/CSAR%20Validation%20and%20Integrity%20Checking.md)
    - [AppD Descriptor Parsing and Processing](content/Core%20Services/ApmApi%20%28Application%20Package%20Management%20Service%29/AppD%20Descriptor%20Parsing%20and%20Processing.md)
    - [Package Distribution and Storage](content/Core%20Services/ApmApi%20%28Application%20Package%20Management%20Service%29/Package%20Distribution%20and%20Storage.md)
    - [Subscription and Notification Management](content/Core%20Services/ApmApi%20%28Application%20Package%20Management%20Service%29/Subscription%20and%20Notification%20Management.md)
  - [Catalogue (Inventory Management Service)](content/Core%20Services/Catalogue%20%28Inventory%20Management%20Service%29.md)
  - [PlatformManager (MEPM Execution Service)](content/Core%20Services/PlatformManager%20%28MEPM%20Execution%20Service%29/PlatformManager%20%28MEPM%20Execution%20Service%29.md)
    - [LCM REST Endpoints](content/Core%20Services/PlatformManager%20%28MEPM%20Execution%20Service%29/LCM%20REST%20Endpoints.md)
    - [Background LCM Worker Service](content/Core%20Services/PlatformManager%20%28MEPM%20Execution%20Service%29/Background%20LCM%20Worker%20Service.md)
    - [VIM gRPC Client Service](content/Core%20Services/PlatformManager%20%28MEPM%20Execution%20Service%29/VIM%20gRPC%20Client%20Service.md)
    - [Package Distribution and CSAR Pre-Staging](content/Core%20Services/PlatformManager%20%28MEPM%20Execution%20Service%29/Package%20Distribution%20and%20CSAR%20Pre-Staging.md)
    - [Platform Configuration Service](content/Core%20Services/PlatformManager%20%28MEPM%20Execution%20Service%29/Platform%20Configuration%20Service.md)
  - [VimAdapter (VIM Adapter Service)](content/Core%20Services/VimAdapter%20%28VIM%20Adapter%20Service%29/VimAdapter%20%28VIM%20Adapter%20Service%29.md)
    - [Adapter Architecture and gRPC Interface](content/Core%20Services/VimAdapter%20%28VIM%20Adapter%20Service%29/Adapter%20Architecture%20and%20gRPC%20Interface.md)
    - [Kubernetes/Helm Adapter Implementation](content/Core%20Services/VimAdapter%20%28VIM%20Adapter%20Service%29/Kubernetes_Helm%20Adapter%20Implementation.md)
    - [OpenStack Cloud Adapter Implementation](content/Core%20Services/VimAdapter%20%28VIM%20Adapter%20Service%29/OpenStack%20Cloud%20Adapter%20Implementation.md)
    - [Custom Adapter Development Guide](content/Core%20Services/VimAdapter%20%28VIM%20Adapter%20Service%29/Custom%20Adapter%20Development%20Guide.md)
    - [Native Async OCI Distribution Client](content/Core%20Services/VimAdapter%20%28VIM%20Adapter%20Service%29/Native%20Async%20OCI%20Distribution%20Client.md)
    - [Registry Authority Validation and Mirror Endpoints](content/Core%20Services/VimAdapter%20%28VIM%20Adapter%20Service%29/Registry%20Authority%20Validation%20and%20Mirror%20Endpoints.md)
- [API Reference](content/API%20Reference/API%20Reference.md)
  - [ETSI App Lifecycle Management API](content/API%20Reference/ETSI%20App%20Lifecycle%20Management%20API.md)
  - [ETSI App Package Management API](content/API%20Reference/ETSI%20App%20Package%20Management%20API.md)
  - [ETSI Granting API](content/API%20Reference/ETSI%20Granting%20API.md)
  - [Internal Services API](content/API%20Reference/Internal%20Services%20API.md)
- [Workflow Orchestration](content/Workflow%20Orchestration/Workflow%20Orchestration.md)
  - [Temporal Workflow Definitions](content/Workflow%20Orchestration/Temporal%20Workflow%20Definitions.md)
  - [Workflow Activities](content/Workflow%20Orchestration/Workflow%20Activities.md)
  - [Saga Compensation Pattern](content/Workflow%20Orchestration/Saga%20Compensation%20Pattern.md)
  - [Hybrid Signal Polling](content/Workflow%20Orchestration/Hybrid%20Signal%20Polling.md)
- [Placement Engine](content/Placement%20Engine.md)
- [Data Models](content/Data%20Models/Data%20Models.md)
  - [Shared Domain Models](content/Data%20Models/Shared%20Domain%20Models.md)
  - [MEO Domain Models](content/Data%20Models/MEO%20Domain%20Models.md)
  - [APM API Domain Models](content/Data%20Models/APM%20API%20Domain%20Models.md)
  - [Catalogue Domain Models](content/Data%20Models/Catalogue%20Domain%20Models.md)
  - [Platform Manager Domain Models](content/Data%20Models/Platform%20Manager%20Domain%20Models.md)
- [Security & Authentication](content/Security%20%26%20Authentication.md)
- [Deployment & Operations](content/Deployment%20%26%20Operations.md)
- [Testing Strategy](content/Testing%20Strategy.md)
- [Monitoring & Observability](content/Monitoring%20%26%20Observability.md)
- [Development Guide](content/Development%20Guide.md)
- [Architecture Decision Records](content/Architecture%20Decision%20Records.md)
- [Troubleshooting & FAQ](content/Troubleshooting%20%26%20FAQ.md)

## Documentation scope

The chapters cover the system architecture, bounded contexts, core services, ETSI APIs, Temporal workflows, placement, data models, security, deployment, testing, observability, development guidance, architecture decisions, and troubleshooting.

> Source-code references in the generated pages are shown as paths because this repository contains the documentation showcase rather than the original source tree.

## Local preview

Run `uv run --no-project python -m http.server 8000` from the repository root, then open `http://localhost:8000`.
