# interfaces/ — Data A cross-team integration

Data A's interface contract with the other Robo-Greeno tracks (Embedded, Data B,
Cloud) and the canonical AgCloud platform.

| File | Purpose |
|------|---------|
| **[INTEGRATION.md](INTEGRATION.md)** | The master contract — shared conventions + one section per team. **Start here.** |
| [pose_stamped.schema.json](pose_stamped.schema.json) | Canonical time-stamped robot-state message (JSON Schema, draft 2020-12). |
| [pose_stamped.example.json](pose_stamped.example.json) | A valid example message. |
| [servo_conventions.md](servo_conventions.md) | 18-channel servo map, joint ranges, command format, PWM template (for Embedded). |
| [hexapod.urdf](hexapod.urdf) | Robot description, generated from `config.py` (sim/firmware parity). |
| [gen_urdf.py](gen_urdf.py) | Regenerates `hexapod.urdf` from the single source-of-truth geometry. |

Built from investigation of the other teams' repos on 2026-06-22. The schema and
URDF are machine-validated (`jsonschema`, XML well-formedness, 18-joint count).
