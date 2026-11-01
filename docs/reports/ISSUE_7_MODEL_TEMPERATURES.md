# Turbo Tower temperature profile

[Deutsch](ISSUE_7_MODEL_TEMPERATURES.de.md) | [English](ISSUE_7_MODEL_TEMPERATURES.md)

On 2026-11-01 the owner supplied temperature ranges for CAF-DC111S-AEU. “Repeat” is interpreted as Reheat and “Proof” as the proofing program. The Dry range was supplied immediately beforehand. Only Proof's 1 °C increment was explicitly reported; no increment is inferred for other programs. These are owner-reported appliance limits, separate from successful transmission evidence and from duration bounds.

| Program | Owner-reported appliance range | Pinned adapter range | Supervised temperature intersection |
| --- | --- | --- | --- |
| Air Fry | 120–230 °C | 120–205 °C | 120–205 °C |
| Roast | 175–230 °C | 120–205 °C | 175–205 °C |
| Bake | 80–205 °C | 80–205 °C | 80–205 °C |
| Grill | 160–230 °C | 205–240 °C | 205–230 °C |
| Reheat | 40–205 °C | 40–205 °C | 40–205 °C |
| Dry | 35–95 °C | 34–95 °C | 35–95 °C |
| Proof | 30–45 °C, 1 °C increments | Missing | Blocked |

The pinned Airfryer Control 1.0.2-beta.1 revision [f43a9bf8](https://github.com/misterm2310/airfryer-control/tree/f43a9bf8ddb7cc65e27897dd92158cc06840bc08) was re-read: `const.py` lists only six IDs and TwinFry ranges; `services.py` requires these IDs and, with `streng:true`, calls `outside_limits` before sending. `senden.py` maps these programs to the prepared `multi_app` payload. Disabling strictness would silently clamp temperatures and would still not add Proof. The public safe service therefore cannot provide the complete owner ranges with the reviewed version. No change to the upstream repository was made.

Beta b10 stores all seven appliance ranges in an exact-model profile. Discovery exposes that static profile under `model_profile`, separately from adapter `programs`, without adding missing programs or changing capability provenance. Unknown models receive no profile. The panel's expandable temperature table shows owner and adapter ranges separately, including missing Proof and its 1 °C step. Display follows the HA °C/°F preference; stored bounds remain Celsius.

Backend settings validation additionally enforces the model temperature range. The reviewed contract and current fresh adapter report remain mandatory, so only the intersection can be prepared. In particular Roast below 175 °C and Grill above 230 °C are blocked. Model-valid values outside the pinned contract remain blocked too. No clamping, automatic fallback, raw commands, start, retry or Proof alias is introduced. Both recipe and manual sources share validation; saved recipes and the independent dry-run API remain unchanged.

The twelve-step guided list remains unchanged: its nominal settings already fit the intersection, including Dry 55 °C / 360 minutes on both zones. It does not claim endpoint acceptance. Program duration limits and non-Proof temperature increments remain unverified.

Passed locally: 150 Python tests, 38 frontend tests, compilation, documentation links and git diff --check. Tests cover rejection before device reads/control for model-invalid and adapter-invalid settings, all common temperature endpoints, blocked Proof, absent profiles for unknown models, preserved adapter programs/provenance and translated °C/°F range rendering. Frontend tests use VM/DOM stubs. No GitHub Actions, HACS/Hassfest, Python 3.14, native HA/Companion UI or new appliance endpoint tests.

Local check: install b10, restart HA and fully reopen the app. Open the device test preview, expand “Appliance temperature ranges” and compare the table with the appliance. The guided list still contains six adapter-reported programs. For real sends, physically cancel prior preparations and re-arm if required; remain beside the appliance and do not press Start. Do not infer time bounds or try unsupported Proof through another program. Full ranges and Proof require a model-aware upstream adapter change followed by contract review and explicit supervised acceptance.
