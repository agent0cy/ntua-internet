# PlantUML diagrams

Formal UML versions of the diagrams in [`../uml-diagrams.md`](../uml-diagrams.md)
(which uses Mermaid). Use these when you want textbook UML notation —
stick-figure actors, ovals, `«stereotypes»`, proper activity swimlanes.

| File | Contents |
|------|----------|
| `use-case.puml` | Use case diagram (1) |
| `sequence.puml` | Sequence diagrams (5: search, average, add, rate, recommendations) |
| `activity.puml` | Activity diagrams (2: user session, recommendation algorithm) |
| `class.puml` | Class diagram + backend module/component dependency view |

Files with several `@startuml ... @enduml` blocks render to **one image per block**,
named by the title right after `@startuml` (e.g. `sequence-recommendations`).

## How to view

**Option A — online, no install (fastest):**
Open <https://www.plantuml.com/plantuml>, paste the contents of one `@startuml`
block, and it renders instantly.

**Option B — VS Code:**
Install the *PlantUML* extension (`jebbs.plantuml`), open a `.puml` file, and
press `Alt+D` to preview. It can use the public render server, so no local
Graphviz is needed.

**Option C — local CLI:**
```bash
# needs Java (present) + Graphviz for class/activity/use-case/component diagrams
sudo apt install graphviz
# get the jar once:
curl -L -o plantuml.jar https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar
# render every diagram to PNG (sequence diagrams don't need Graphviz):
java -jar plantuml.jar docs/plantuml/*.puml
```

> Note: sequence diagrams render without Graphviz; the other types need `dot`
> (Graphviz) installed.
