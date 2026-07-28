# WardLog

WardLog is an AI-powered clinical activity logger for doctors. Instead of filling out
timesheet forms, a doctor logs their work and patient encounters through natural
conversation with an AI assistant — e.g. "I did a clinic block this morning from 8 to 12"
or "I saw a patient named Uma, 51, with knee pain." The assistant extracts the structured
details, confirms them with the doctor, and persists them.

---

## Working agreement (read first)

- Do only what I explicitly ask. Do not take initiative beyond the current instruction.
- Do not create, modify, or delete files, run commands, or refactor unless I ask for it.
- If something seems missing, wrong, or worth doing, **tell me and wait** — propose, don't act.
- Treat everything below as reference context, not a to-do list. It describes the intended
  design; it is not an instruction to build any of it on your own.
- When a request is ambiguous, ask before proceeding.

---

This is the **root context** for the whole microservice suite. Each service has its own
`CLAUDE.md` with service-specific details (stack, schema, endpoints). Keep suite-wide
facts here; keep service-local facts in the service files. Do not duplicate — if something
is true of one service only, it belongs in that service's file, not here.

---

## Architecture

Microservices suite, polyglot (Java/Spring + Python). Services communicate over **HTTP**.
Keep service interfaces contract-first and treat transport as a thin adapter over the
domain logic, so the boundaries stay clean.

### Service overview

| Service            | Language / Stack                          | Responsibility                                                        |
|--------------------|-------------------------------------------|-----------------------------------------------------------------------|
| Gateway            | Java, Spring Cloud Gateway                | Single entry point, routing                                            |
| Discovery (Eureka) | Java, Netflix Eureka                      | Service registration & discovery                                      |
| User Service       | Java, Spring Boot                         | Auth, JWT, per-user identity                                          |
| AI Service         | Python, LangGraph/LangChain, Neo4j, Redis | Conversation, extraction, confirmation, memory. Merged AI + Memory.   |
| Timesheet Service  | Java, Spring Boot, PostgreSQL             | Source of truth for logged activities                                |
| Report Service     | Java, Spring Boot                         | Reads from Timesheet via API; AI-queryable reports                    |

---

## Services

### Gateway
Single entry point for the suite. Routes incoming requests to the appropriate service.
Spring Cloud Gateway.

### Discovery (Eureka)
Service registration and discovery. Java services register here and reach each other
through discovery rather than hardcoded hosts.

### User Service
Authentication and identity. Issues and validates JWTs, owns per-user identity.

### AI Service
The conversational core (Python, LangGraph/LangChain). It is the merged AI + Memory
service and handles:
- **Activity extraction** — extracts structured clinical activities from natural
  conversation and confirms them with the doctor before they're logged.
- **AI memory management** — owns the Neo4j clinical knowledge graph; uses Redis for
  session state.
- **Document parsing** — ingests uploaded documents and extracts their content/metadata.
- **Report discussion** — lets the doctor query and discuss reports conversationally
  (reports come from the Report Service).

### Timesheet Service
Source of truth for logged activities (Java, Spring Boot, PostgreSQL). At a high level it
handles:
- **Activity logging** — recording logged activities.
- **Activity displaying** — showing an individual activity.
- **Timesheet closing** — closing a month, which locks it.
- **Listing all activities** — listing logged activities.
- **Activity details** — returning the full details for an activity.

### Report Service
Reads logged activities from the Timesheet Service's API to build reports. No separate
read store — it queries Timesheet directly.

---

## Shared conventions

- **Group / namespace:** `com.wardlog` for all Java services.
- **Java services:** Java 17, Spring Boot 3.x (3.5.x line). Maven build.
- **Python service:** snake_case for functions/modules, PascalCase for classes.
- **Service discovery:** all Java services register with Eureka; reach other services
  through discovery, not hardcoded hosts.
- **Config:** externalize environment-specific values (hosts, ports, credentials) via
  env vars with sensible local defaults.

---

## Domain glossary

- **Activity / ActivityBlock** — a logged unit of clinical work (a clinic block, a
  surgery, etc.). Every block produces a **Consultation** as its encounter node in the
  knowledge graph.
- **Consultation** — the universal encounter node for all activity types (the earlier
  surgery/clinic path split was collapsed into this).
- **Timesheet** — the doctor's collection of logged activities, viewable per month.
  Months can be **closed** (manual action), which locks them.
- **Knowledge graph** — Neo4j, owned by the AI Service. Ontology: Doctor, ActivityBlock,
  Consultation, Patient, Diagnosis, Drug, SurgeryType, ProgressNote, Report.

---

## Repository layout

```
wardlog/
  CLAUDE.md                 <- this file (suite-wide context)
  gateway/
  discovery/                <- Eureka
  user-service/
  ai-service/               <- Python, LangGraph, Neo4j
  timesheet-service/        <- Java, Spring Boot, Postgres
  report-service/           <- Java, Spring Boot
```