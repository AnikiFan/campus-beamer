# Choose a diagram by its meaning

Read the rows relevant to the relationship supplied for drawing.

| Relationship to represent | Mermaid type | Mermaid semantics |
| --- | --- | --- |
| Steps, decisions, feedback, module dependencies | `flowchart` | A useful default for process or relation graphs; a module graph is not necessarily a native architecture diagram. |
| Messages and ordering across participants | `sequenceDiagram`; `zenuml` for nested calls | Distinguish synchronous calls, returns and asynchronous messages. ZenUML needs its external package. |
| Lifecycle and permitted transitions | `stateDiagram-v2` | Use states rather than turning each state into a procedural step. |
| Classes, methods, inheritance and composition | `classDiagram` | For software structure, not a general conceptual taxonomy. |
| Entities, attributes and cardinality | `erDiagram` | Preserve keys and cardinality semantics. |
| A central idea and its branches | `mindmap` | Topic decomposition; use flowchart for directed or labeled relationships. |
| Aligned modules or regular block layouts | `block-beta` | When placement matters more than automatic graph routing. |
| Services, infrastructure and deployment groups | `architecture-beta` | Native resource icons and groups; use flowchart for an abstract research method. |
| System context and software abstraction levels | `C4Context`, `C4Container`, related C4 types | Choose one abstraction level per view; C4 containers are not Docker-only. |
| Requirements and implementation/verification links | `requirementDiagram` | Traceability rather than a generic flow. |
| A process divided by responsible actor/team | `swimlane-beta` | Lanes encode responsibility. |
| Files, folders and directory hierarchy | `treeView-beta` | More suitable than a mindmap for a directory tree. |
| Tasks with dates, durations and dependencies | `gantt` | Tasks have start dates, durations and optional dependencies. |
| Stages or dated milestones | `timeline` | Simpler progression when duration is not the point. |
| Work items grouped by status | `kanban` | Columns represent statuses; cards represent work items. |
| Journey stages, actors and experience scores | `journey` | Each task has a score and participating actors. |
| Small numbers of part-to-whole categories | `pie` | Prefer bars for precise comparisons. |
| Category comparison or ordered numeric trends | `xychart-beta` with `bar` or `line` | Bars compare categories; lines connect an ordered series. |
| Multi-dimensional profiles | `radar-beta` | Requires comparable scales and explicit axis definitions. |
| Position along two dimensions | `quadrantChart` | Define both axes and point coordinates. |
| Quantified flow between sources and destinations | `sankey-beta` | Widths carry quantities; flowchart suits an unquantified process. |
| Hierarchical proportions | `treemap-beta` | Areas encode values; very small leaves can be unreadable. |
| Sets and overlaps | `venn-beta` | Preserve intersection semantics; use another form for many sets. |
| Commits, branches and merges | `gitGraph` | Commit order and branch/merge structure define the graph. |
| Protocol bit fields | `packet-beta` | Preserve bit positions, widths and ordering. |
| Causes grouped around a problem | `ishikawa-beta` | Indentation creates categories and nested causes. |
| Value-chain dependencies and component evolution | `wardley-beta` | Its visibility/evolution axes must fit the argument. |
| Problem contexts in the Cynefin framework | `cynefin-beta` | Not a generic quadrant chart; retain the framework's meanings. |
| UI, commands, events and read models | `eventmodeling` | Event-oriented system behavior. |
| Grammar sequence, choice and repetition | `railroad-ebnf-beta`, related railroad notations | Language rules rather than task flows. |

The repository style experiment used Mermaid **11.17.2** with Mermaid CLI
**11.12.0**. CLI and engine versions are separate. Some types are experimental;
check the installed engine and primary syntax documentation before using a less
familiar type. Online documentation may describe types absent locally.

Known behavior from that experiment:

- Sankey's CSV parser in that version accepts ASCII labels, not Chinese labels,
  even when quoted. Do not silently translate meaningful user labels: choose
  another local renderer/type or explain the limitation and preserve meaning.
- Quote non-ASCII strings in XY category lists and requirement `text`/`type`
  fields. Event modeling uses `rmo` or `readmodel` for a read model.
- C4, journey, timeline, radar, packet and native architecture need additional
  configuration/CSS beyond global theme variables; use the shared style helper.
- Shared typography and palette do not make all families geometrically identical.

Primary references: [diagram directory](https://mermaid.js.org/intro/syntax-reference.html),
[themes](https://mermaid.js.org/config/theming.html),
[configuration schema](https://mermaid.js.org/config/schema-docs/config.html).
