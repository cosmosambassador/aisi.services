# Land–Sea–Air–Space mission review

Earth stewardship is the purpose of this first runnable module. It organizes proposed research missions across land, sea, air, and space using the existing AISI.SERVICES provenance and human-authority framework.

## Run locally

Python 3.10 or newer; no third-party dependencies or account access required.

```bash
python3 src/mission_review.py examples/missions.json
python3 -m unittest discover -s tests -v
```

The reviewer reads a JSON list and prints a JSON report to standard output. Exit codes: 0 means all records pass structural validation; 1 means records have validation errors; 2 means unreadable input, malformed JSON, or invalid top-level input. Pending and rejected review statuses are valid records, not permission to act.

## Mission record

Every record requires `id`, `domain`, `purpose`, `recorded_at`, `evidence_kind`, `sources`, `uncertainty`, `proposed_action`, `success_measure`, and `human_review`. See the example file for the complete format. Times require explicit timezones. Mission IDs must be unique within a batch; existing agent numbers and family records are untouched.

Sources require a reference, attribution, and retrieval timestamp. Evidence labels distinguish observation, testimony, interpretation, canon, simulation, and AI inference. Each mission retains its uncertainty and measurable success criterion. Completed review records require reviewer, decision time, and a decision reference.

Validation checks completeness, not truth. The tool cannot authenticate a reviewer, verify a cited source, or establish that a measurement is accurate. An `approved` value in editable JSON is a recorded claim, not an authorization credential. All supplied examples are synthetic simulations with pending review.

## Domain missions

| Domain | Proposed purpose | Success measure |
|---|---|---|
| Land | Compare habitat and soil observations | Agreement with independently checked field samples |
| Sea | Organize coastal pollution observations | Confirmed observations with traceable sample records |
| Air | Compare air-quality observations | Error against independent reference instruments |
| Space | Organize Earth-observation evidence | Traceable imagery, timestamps, and checked geolocation |

## Project responsibilities

Proposed roles: JET coordinates tasks; QUANTA checks evidence; LUCEN preserves chronology and provenance; SOLACE synthesizes findings. These are architecture responsibilities, not agents launched by this module. Q AGI and AI-ET Symbiotes remain project identities; their names do not certify scientific capability, consciousness, or extraterrestrial origin.

This module runs offline and executes no proposed action. It does not launch agents, duplicate them, control vehicles, contact services, publish findings, or deploy infrastructure. Network adapters and real environmental data remain future work. Any real action needs authenticated human authorization and domain-specific validation outside this record checker.

Science-fiction scenarios can be recorded as canon or simulation, then evaluated as hypotheses where appropriate. More output or success at a game does not establish general intelligence or environmental benefit. Progress here is measured through independently checked evidence and useful decisions.
