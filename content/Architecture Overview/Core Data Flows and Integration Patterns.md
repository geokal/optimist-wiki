# Core Data Flows and Integration Patterns

<cite>
**Referenced Files in This Document**
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/CSAR_DISTRIBUTION_AND_LIFECYCLE_ARCHITECTURE.md`
- `docs/VIM_CONFIGURATION_AND_INSTANTIATION_FLOW.md`
- `docs/ONBOARDING_AND_LIFECYCLE_ARCHITECTURE_REVIEW.md`
- `src/Meao/Program.cs`
- `src/Meao/Workflows/CreateAppInstWF.cs`
- `src/Meao/Workflows/InstantiateAppInstWF.cs`
- `src/Meao/Workflows/TerminateAppinstWF.cs`
- `src/Meao/Workflows/OnboardAppPkgWF.cs`
- `src/Meao/Validators/GrantRequestValidator.cs`
- `src/Meao/Domain/Placement/PlacementEngine.cs`
- `src/PlatformManager/PlatformManager/Program.cs`
- `src/PlatformManager/PlatformManager/Services/LcmWorkerService.cs`
- `src/VimAdapter/main.py`
- `src/VimAdapter/src/server/lcm_grpc_server.py`
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
This document explains the core data flows and integration patterns in Optimist.Orchestrator, focusing on:

- CSAR onboarding from upload through validation, parsing, distribution, and cataloging.
- Application lifecycle flow: grant request → placement decision → instantiation → operation → termination.
- The Temporal workflow saga pattern used by Meao for durable orchestration and compensation.
- VIM configuration and instantiation flow across PlatformManager and VimAdapter.
- Sequence diagrams for deployment, status synchronization, and error recovery.
- Data consistency, eventual consistency, and state synchronization mechanisms.

The system implements ETSI GS MEC 010-2 roles: Meao (MEO), ApmApi (package management inside MEO), Catalogue (internal census), PlatformManager (MEPM), and VimAdapter (VIM adapter). External operators interact with Meao and ApmApi through an API gateway; Meao calls PlatformManager directly over the management plane.

**Section sources**
- `README.md#L1-L120`
- `docs/ARCHITECTURE.md#L1-L120`

## Project Structure
Optimist.Orchestrator is a modular multi-service system:

| Service | Role | Runtime | Primary Ports | Main Responsibility |
|---|---|---|---:|---|
| Meao | MEO orchestrator engine | .NET 8 | 5154 | Temporal workflows, placement engine, grants, MEPM coordination |
| ApmApi | App package management | .NET 8 | 5184 | CSAR upload, AppD descriptor extraction, validation, finalization |
| Catalogue | Internal MEO inventory | .NET 8 | 5165 | Edge hosts, MEPM registry, capacity headroom, app instance census |
| PlatformManager | MEPM LCM execution | .NET 8 | 5155 | `/app_lcm/v1`, background VIM provisioning, gRPC bridge to VimAdapter |
| VimAdapter | VIM adapter | Python 3.11 | 50051 | Kubernetes Helm or OpenStack provisioning via gRPC |

```mermaid
graph TB
    Operator["Operator"]
    Gateway["APISIX Gateway :9080"]
    Meao["Meao :5154<br/>Temporal + PlacementEngine"]
    ApmApi["ApmApi :5184<br/>CSAR + AppD processing"]
    Catalogue["Catalogue :5165<br/>Census + Inventory"]
    PlatformManager["PlatformManager :5155<br/>/app_lcm/v1"]
    VimAdapter["VimAdapter :50051<br/>Python gRPC"]
    K8s["Kubernetes Cluster"]
    OpenStack["OpenStack Cloud"]

    Operator --> Gateway
    Gateway --> Meao
    Gateway --> ApmApi
    Gateway --> Catalogue
    Meao --> PlatformManager
    PlatformManager --> VimAdapter
    VimAdapter --> K8s
    VimAdapter --> OpenStack
```

**Diagram sources**
- `README.md#L40-L120`
- `docs/ARCHITECTURE.md#L40-L120`

**Section sources**
- `README.md#L1-L120`
- `docs/ARCHITECTURE.md#L1-L120`

## Core Components
Meao is the central orchestrator. It registers Temporal workflows, activities, HTTP clients, service discovery, authentication handlers, and hosted workers.

Key responsibilities:

- Register Temporal client and worker task queue.
- Register `CreateAppInstWF`, `InstantiateAppInstWF`, `TerminateAppinstWF`, and `OnboardAppPkgWF`.
- Register activities for catalogue, APM, auth, MEPM, app instance, grants, and placement.
- Configure Keycloak-based JWT authentication and internal service tokens.
- Configure named HTTP clients backed by Consul service discovery and resilience handlers.
- Provide dedicated activity-level HTTP clients with controlled timeouts.

```mermaid
flowchart TD
    Start["Meao Program Startup"] --> Telemetry["Add Shared Telemetry"]
    Telemetry --> Db["Register MeaoDBContext"]
    Db --> Auth["Configure Keycloak Authentication"]
    Auth --> TemporalClient["Create Temporal Client"]
    TemporalClient --> Discovery["Register Consul Service Discovery"]
    Discovery --> HttpClients["Register Named HttpClient Factories"]
    HttpClients --> Activities["Register Activities"]
    Activities --> Workflows["Register Temporal Workflows"]
    Workflows --> Workers["Add Hosted Temporal Worker"]
```

**Diagram sources**
- `src/Meao/Program.cs#L1-L200`

**Section sources**
- `src/Meao/Program.cs#L1-L200`

## Architecture Overview
At a high level, the system separates concerns across four layers:

1. **Northbound API layer:** APISIX routes operator requests to Meao, ApmApi, and Catalogue.
2. **System-level orchestration:** Meao owns workflow state, placement decisions, grants, and MEPM coordination.
3. **Host-level execution:** PlatformManager owns `/app_lcm/v1` and drives VIM provisioning asynchronously.
4. **Infrastructure layer:** VimAdapter translates lifecycle commands into Kubernetes or OpenStack operations.

```mermaid
sequenceDiagram
    participant Op as "Operator"
    participant GW as "APISIX"
    participant MEO as "Meao"
    participant APM as "ApmApi"
    participant CAT as "Catalogue"
    participant PM as "PlatformManager"
    participant VIM as "VimAdapter"

    Op->>GW: "Onboard CSAR"
    GW->>APM: "POST /app_pkgm/v1/onboarded_app_packages"
    Op->>GW: "PUT package content"
    APM-->>Op: "202 Accepted"

    Op->>GW: "Create AppInstance"
    GW->>MEO: "Launch CreateAppInstWF"
    MEO->>CAT: "Query hosts"
    MEO->>MEO: "Placement decision"
    MEO->>PM: "Create MEPM instance record"
    MEO-->>Op: "AppInstanceId"

    Op->>GW: "Instantiate"
    GW->>MEO: "Launch InstantiateAppInstWF"
    MEO->>PM: "Start LCM operation"
    PM->>VIM: "gRPC provision"
    VIM-->>PM: "Provision result"
    PM-->>MEO: "State signal"
    MEO-->>Op: "Deployment complete"
```

**Diagram sources**
- `docs/ONBOARDING_AND_LIFECYCLE_ARCHITECTURE_REVIEW.md#L120-L220`
- `docs/CSAR_DISTRIBUTION_AND_LIFECYCLE_ARCHITECTURE.md#L1-L120`

**Section sources**
- `docs/ARCHITECTURE.md#L1-L120`
- `docs/ONBOARDING_AND_LIFECYCLE_ARCHITECTURE_REVIEW.md#L1-L120`

## Detailed Component Analysis

### CSAR Onboarding Flow
The CSAR onboarding flow moves from ApmApi through Meao’s Temporal saga into Catalogue and OCI distribution paths.

#### End-to-End Onboarding Sequence
```mermaid
sequenceDiagram
    participant Op as "Operator"
    participant APM as "ApmApi"
    participant MEO as "Meao"
    participant WF as "OnboardAppPkgWF"
    participant ACT as "Activities"
    participant CAT as "Catalogue"
    participant ZOT as "OCI Registry"

    Op->>APM: "Create package"
    APM-->>Op: "AppPkgId"
    Op->>APM: "Upload CSAR"
    APM->>WF: "Signal parse completion"
    WF->>ACT: "Validate AppD / resolve reference"
    ACT->>CAT: "Register package inventory"
    ACT->>ZOT: "Resolve/publish OCI reference"
    ACT->>CAT: "Mark package onboarded"
    WF-->>Op: "ONBOARDED"
```

**Diagram sources**
- `src/Meao/Workflows/OnboardAppPkgWF.cs#L1-L200`
- `src/Meao/Workflows/OnboardAppPkgWF.cs#L200-L367`
- `docs/CSAR_DISTRIBUTION_AND_LIFECYCLE_ARCHITECTURE.md#L1-L120`

#### Key Behaviors
- **Claim Check Pattern:** The workflow receives a staging claim rather than raw CSAR bytes, keeping Temporal history small and replay-safe.
- **Async AppD Parsing:** New executions kick asynchronous parsing in ApmApi and wait via a signal-fast path plus bounded polling fallback.
- **Legacy and Patched Paths:** Pre-Phase-48 histories use legacy registration; patched runs register a package inventory record and mark it onboarded only after ApmApi finalization.
- **Compensation:** Failures trigger rollback and package-inventory compensation without deleting records.

**Section sources**
- `src/Meao/Workflows/OnboardAppPkgWF.cs#L1-L200`
- `src/Meao/Workflows/OnboardAppPkgWF.cs#L200-L367`
- `docs/CSAR_DISTRIBUTION_AND_LIFECYCLE_ARCHITECTURE.md#L1-L120`

### Application Lifecycle Data Flow
The application lifecycle spans grant request, placement, instantiation, operation, and termination.

#### Lifecycle State Model
```mermaid
stateDiagram-v2
    [*] --> NOT_INSTANTIATED
    NOT_INSTANTIATED --> INSTANTIATING : "instantiate"
    INSTANTIATING --> INSTANTIATED : "completed"
    INSTANTIATING --> FAILED_TEMP : "failed_temp"
    INSTANTIATING --> FAILED : "failed"
    INSTANTIATED --> TERMINATING : "terminate"
    TERMINATING --> NOT_INSTANTIATED : "completed"
    TERMINATING --> FAILED : "failed"
    FAILED --> [*]
```

**Diagram sources**
- `src/Meao/Workflows/InstantiateAppInstWF.cs#L1-L200`
- `src/Meao/Workflows/TerminateAppinstWF.cs#L1-L180`

#### Grant Request Validation
Grant requests are validated before being accepted by the granting API.

Validation rules include:

- `AppInstanceId` must be present and a valid GUID.
- `AppLcmOpOccId` must be present.
- `AppDId` must be present.
- `Operation` must be one of `INSTANTIATE`, `OPERATE`, or `TERMINATE`.
- `_links` must contain required `appInstance` and `appLcmOpOcc` hrefs.
- For `INSTANTIATE`, `AddResources` must be present and non-empty.
- Resource definitions must have a valid resource type.

```mermaid
flowchart TD
    Start["Grant Request Received"] --> ValidateGuid["Validate AppInstanceId is GUID"]
    ValidateGuid --> ValidateOpOcc["Validate AppLcmOpOccId"]
    ValidateOpOcc --> ValidateAppD["Validate AppDId"]
    ValidateAppD --> ValidateOp["Validate Operation ∈ {INSTANTIATE, OPERATE, TERMINATE}"]
    ValidateOp --> ValidateLinks{"_links present?"}
    ValidateLinks -->|No| Reject["Reject request"]
    ValidateLinks -->|Yes| ValidateHref["Validate hrefs"]
    ValidateHref --> ValidateResources{"Operation == INSTANTIATE?"}
    ValidateResources -->|Yes| ValidateAdd["Validate AddResources not empty"]
    ValidateAdd --> ValidateResourceTypes["Validate resource types"]
    ValidateResources -->|No| Accept["Accept validated grant"]
    ValidateResourceTypes --> Accept
```

**Diagram sources**
- `src/Meao/Validators/GrantRequestValidator.cs#L1-L84`

**Section sources**
- `src/Meao/Validators/GrantRequestValidator.cs#L1-L84`

#### Placement Decision
When no host IP is supplied, Meao performs dynamic placement.

Placement behavior:

1. Fetches edge hosts from Catalogue.
2. Applies hard constraints: ONLINE status, VIM type, CPU, RAM, storage, required services, and latency.
3. Evaluates placement policies in registered order.
4. Scores eligible candidates using optional services and policy adjustments.
5. Selects the highest-scoring host and returns a placement decision with allocated resources.

```mermaid
flowchart TD
    Start["SelectHostAsync"] --> Query["GET /catalogue/v1/edge_hosts"]
    Query --> Filter["Apply hard constraints"]
    Filter --> NoCandidates{"Any candidate?"}
    NoCandidates -->|No| ThrowNoHost["Throw 'No edge host satisfies constraints'"]
    NoCandidates -->|Yes| Policies["Evaluate IPlacementPolicy list"]
    Policies --> Eligible{"Any eligible host?"}
    Eligible -->|No| ThrowPolicy["Throw 'No edge host satisfies policies'"]
    Eligible --> Score["Score candidates"]
    Score --> Select["Select best host"]
    Select --> Return["Return PlacementDecision"]
```

**Diagram sources**
- `src/Meao/Domain/Placement/PlacementEngine.cs#L1-L200`

**Section sources**
- `src/Meao/Domain/Placement/PlacementEngine.cs#L1-L200`

#### Instantiation Workflow
`InstantiateAppInstWF` coordinates grant creation, MEPM invocation, hybrid signal/poll waiting, and cleanup.

Critical steps:

1. Load existing `AppInstanceInfo`.
2. Resolve compute requirements from `VirtualComputeDescriptor`.
3. Perform dynamic placement if no host IP is provided, otherwise reserve capacity for the explicit host.
4. Resolve MEPM base URL from Catalogue.
5. Ensure MEPM instance record exists.
6. Create a grant.
7. Trigger MEPM instantiate operation.
8. Wait for terminal state using signals and polling.
9. Update local state, register deployed app in Catalogue, and mark grant consumed.

```mermaid
sequenceDiagram
    participant WF as "InstantiateAppInstWF"
    participant DB as "Meao DB"
    participant PL as "PlacementActivities"
    participant CAT as "CatalogueActivities"
    participant GR as "GrantActivities"
    participant PM as "MepmActivities"
    participant POLL as "HybridSignalPollHelper"

    WF->>DB: "GetAppInstanceDB"
    alt "No HostIp"
        WF->>PL: "SelectAndReserveHostAsync"
    else "HostIp provided"
        WF->>PL: "ReserveHostCapacityAsync"
    end
    WF->>CAT: "GetMepmBaseUrlForHostAsync"
    WF->>PM: "CreateAppInstanceAsync"
    WF->>GR: "CreateGrantAsync"
    WF->>PM: "InstantiateAppInstanceAsync"
    loop "Until completed, failed, or timeout"
        WF->>POLL: "PollNextStateAsync"
        POLL-->>WF: "Operation state"
    end
    WF->>GR: "MarkGrantConsumedAsync"
    WF->>CAT: "AddMecApp"
    WF-->>Caller: "SUCCESS"
```

**Diagram sources**
- `src/Meao/Workflows/InstantiateAppInstWF.cs#L1-L200`
- `src/Meao/Workflows/InstantiateAppInstWF.cs#L200-L353`

**Section sources**
- `src/Meao/Workflows/InstantiateAppInstWF.cs#L1-L353`

#### Termination Workflow
`TerminateAppinstWF` terminates the remote workload, releases capacity, removes the app from Catalogue, and updates local state.

Termination compensation includes:

- Mark grant failed if not yet consumed.
- Release host capacity.
- Remove MEC app from Catalogue.
- Update `InstantiationState`, `OperationalState`, `HostIp`, and `MepmInstanceId`.

```mermaid
sequenceDiagram
    participant WF as "TerminateAppinstWF"
    participant DB as "Meao DB"
    participant GR as "GrantActivities"
    participant PM as "MepmActivities"
    participant PL as "PlacementActivities"
    participant CAT as "CatalogueActivities"

    WF->>DB: "GetAppInstanceDB"
    WF->>GR: "CreateGrantAsync"
    WF->>PM: "TerminateAppInstanceAsync"
    loop "Wait for terminal state"
        WF->>PM: "Poll LcmOpOcc state"
    end
    WF->>PL: "ReleaseHostCapacityAsync"
    WF->>CAT: "RemoveMecApp"
    WF->>DB: "UpdateAppInstanceDB"
    WF-->>Caller: "SUCCESS or CleanupFailed"
```

**Diagram sources**
- `src/Meao/Workflows/TerminateAppinstWF.cs#L1-L180`
- `src/Meao/Workflows/TerminateAppinstWF.cs#L180-L272`

**Section sources**
- `src/Meao/Workflows/TerminateAppinstWF.cs#L1-L272`

### Temporal Workflow Saga Pattern and Compensation
Meao uses Temporal workflows as durable sagas. Each workflow tracks its current stage, persists intermediate state, and compensates on failure.

Saga characteristics:

- **Deterministic Task Queue:** All workflows share `meao-task-queue`.
- **Stage Tracking:** Workflows update `_currentStage` so compensation can identify where failure occurred.
- **Activity Policies:** Standard, long-running, best-effort, and compensation policies control retry and timeout behavior.
- **Compensation Path:** Rollback activities run after failures, including ApmApi rollback and Catalogue package-inventory compensation.
- **Cancellation Handling:** Cancellation triggers cleanup and rethrows cancellation exceptions instead of masking them.

```mermaid
flowchart TD
    Start["Workflow Run"] --> Stage["Execute Stage N"]
    Stage --> Success{"Success?"}
    Success -->|Yes| Next["Proceed to Stage N+1"]
    Success -->|No| Compensate["Run Compensation Activities"]
    Compensate --> Rollback["Rollback ApmApi"]
    Rollback --> Inventory["Compensate Package Inventory"]
    Inventory --> ReThrow["Re-throw or surface cleanup failure"]
    Next --> End["Terminal State"]
```

**Diagram sources**
- `src/Meao/Workflows/OnboardAppPkgWF.cs#L1-L200`
- `src/Meao/Workflows/OnboardAppPkgWF.cs#L200-L367`

**Section sources**
- `src/Meao/Workflows/OnboardAppPkgWF.cs#L1-L367`

### VIM Configuration and Instantiation Flow
VIM configuration is separated into three conceptual layers: infrastructure access configuration, platform rules, and application workload configuration.

#### Configuration Layers
```mermaid
flowchart TD
    Layer1["Layer 1: VimConnectionInfo<br/>kubeconfig / clouds.yaml"] --> Layer2["Layer 2: Platform Rules<br/>traffic/DNS/service config"]
    Layer2 --> Layer3["Layer 3: CSAR / AppD<br/>Helm values, images, topologies"]
```

**Diagram sources**
- `docs/VIM_CONFIGURATION_AND_INSTANTIATION_FLOW.md#L1-L60`

#### Bootstrap and End-to-End Instantiation
```mermaid
sequenceDiagram
    participant Op as "Operator"
    participant PM as "PlatformManager"
    participant VA as "VimAdapter"
    participant Store as "ConfigStore"
    participant Target as "K8s / OpenStack"

    Op->>PM: "POST /app_lcm/v1/configs"
    PM->>VA: "gRPC uploadConfig"
    VA->>Store: "Persist kubeconfig or clouds.yaml"
    Store-->>VA: "OK"

    Op->>PM: "POST /app_lcm/v1/app_instances/{id}/instantiate"
    PM->>VA: "gRPC Instantiate"
    VA->>Store: "Load host config"
    Store-->>VA: "Raw config bytes"
    VA->>Target: "Deploy workload"
    Target-->>VA: "Workload active"
    VA-->>PM: "Success"
```

**Diagram sources**
- `docs/VIM_CONFIGURATION_AND_INSTANTIATION_FLOW.md#L60-L134`

**Section sources**
- `docs/VIM_CONFIGURATION_AND_INSTANTIATION_FLOW.md#L1-L134`

### PlatformManager Lifecycle Execution
PlatformManager exposes the MEPM LCM API and runs background work to process VIM provisioning.

Startup and service registration include:

- EF Core database context for `mepm_db`.
- Problem Details exception handling.
- Keycloak authentication.
- LCM work queue and hosted worker.
- OCI distribution client.
- Notification dispatcher.
- Health endpoints and migration entrypoints.

```mermaid
flowchart TD
    Start["PlatformManager Program Startup"] --> Db["Register LcmDbContext"]
    Db --> Auth["Enable Keycloak Authentication"]
    Auth --> Services["Register LCM Services"]
    Services --> Queue["Register LcmWorkQueue"]
    Queue --> Worker["Register LcmWorkerService"]
    Worker --> Endpoints["Map LCM Endpoints"]
```

**Diagram sources**
- `src/PlatformManager/PlatformManager/Program.cs#L1-L200`

**Section sources**
- `src/PlatformManager/PlatformManager/Program.cs#L1-L200`

### VimAdapter gRPC Server
VimAdapter is a thin Python gRPC server that selects a VIM adapter at startup and validates inputs.

Key behaviors:

- Default VIM type is `k8s`.
- Config upload enforces host IP validation, payload size limits, and optional validation mode.
- Package upload enforces UUID validation, host IP validation, and streaming size limits.
- Errors map to gRPC status codes such as `INVALID_ARGUMENT`, `RESOURCE_EXHAUSTED`, `NOT_FOUND`, and `INTERNAL`.

```mermaid
classDiagram
    class LcmService {
        +string vim_adapter
        +uploadConfig(request_iterator, context)
        +removeConfig(request, context)
        +uploadPackage(request_iterator, context)
        +deletePackage(request, context)
    }
```

**Diagram sources**
- `src/VimAdapter/main.py#L1-L24`
- `src/VimAdapter/src/server/lcm_grpc_server.py#L1-L200`

**Section sources**
- `src/VimAdapter/main.py#L1-L24`
- `src/VimAdapter/src/server/lcm_grpc_server.py#L1-L200`

## Dependency Analysis
The main dependency relationships are:

- Meao depends on Catalogue, ApmApi, and PlatformManager.
- PlatformManager depends on VimAdapter via gRPC and on Catalogue for MEPM discovery.
- VimAdapter depends on Kubernetes or OpenStack infrastructure.
- Workflows depend on activities for external side effects.
- Placement decisions depend on Catalogue host inventory.

```mermaid
graph TB
    Meao["Meao"]
    ApmApi["ApmApi"]
    Catalogue["Catalogue"]
    PlatformManager["PlatformManager"]
    VimAdapter["VimAdapter"]
    Infrastructure["Kubernetes / OpenStack"]

    Meao --> Catalogue
    Meao --> ApmApi
    Meao --> PlatformManager
    PlatformManager --> VimAdapter
    VimAdapter --> Infrastructure
```

**Diagram sources**
- `docs/ARCHITECTURE.md#L40-L120`
- `README.md#L40-L120`

**Section sources**
- `docs/ARCHITECTURE.md#L40-L120`
- `README.md#L40-L120`

## Performance Considerations
- **Background Processing:** PlatformManager offloads long-running VIM provisioning to `LcmWorkerService`, avoiding blocking HTTP responses.
- **Timeout Enforcement:** Vim operation timeouts are configurable; defaults protect against hung VIM calls.
- **Crash Recovery:** On startup, PlatformManager replays `PROCESSING` operation occurrences created before process boot.
- **Eventual Consistency:** Catalogue and MEAO census states are updated after successful lifecycle operations; temporary inconsistency is tolerated until reconciliation completes.
- **OCI Distribution:** Modern CSAR distribution uses content-addressed OCI artifacts and pre-staging caches, reducing cold-start download costs.
- **Placement Cost:** Placement queries Catalogue hosts and evaluates policies; large host inventories increase selection time.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and their likely causes:

| Symptom | Likely Cause | Recovery |
|---|---|---|
| Onboarding fails during AppD parsing | Invalid CSAR or missing descriptor | Inspect ApmApi parse logs; check staging claim fields |
| Instantiation times out | MEPM or VimAdapter unavailable | Verify MEPM health, VimAdapter gRPC, and target cluster/cloud connectivity |
| Capacity reservation succeeds but deployment fails | VIM provisioning error | Check `LcmWorkerService` logs and operation occurrence state |
| Termination leaves instance in inconsistent state | Compensation failure | Review Catalogue removal and capacity release logs; manually reconcile if needed |
| Grant request rejected | Missing or invalid fields | Validate `AppInstanceId`, `Operation`, `_links`, and resource definitions |
| No host selected | Constraints or policies reject all hosts | Adjust resource requirements, service requirements, latency constraints, or placement policies |

**Section sources**
- `src/Meao/Validators/GrantRequestValidator.cs#L1-L84`
- `src/Meao/Domain/Placement/PlacementEngine.cs#L1-L200`
- `src/PlatformManager/PlatformManager/Services/LcmWorkerService.cs#L1-L200`

## Conclusion
Optimist.Orchestrator implements a durable, event-driven MEC orchestration stack:

- ApmApi handles CSAR ingestion and descriptor parsing.
- Meao coordinates the full lifecycle through Temporal workflows, placing applications using Catalogue-backed constraints and policies.
- PlatformManager executes lifecycle operations asynchronously and bridges REST to VimAdapter gRPC.
- VimAdapter provisions workloads onto Kubernetes or OpenStack.
- Compensation mechanisms, crash recovery, and hybrid signal/poll synchronization provide resilience while accepting eventual consistency between MEAO, Catalogue, MEPM, and VIM states.