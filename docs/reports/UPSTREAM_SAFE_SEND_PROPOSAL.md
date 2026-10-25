# Draft: Supported interface for safe single-attempt preparation

[Deutsch](UPSTREAM_SAFE_SEND_PROPOSAL.de.md) | [English](UPSTREAM_SAFE_SEND_PROPOSAL.md)

**Status: unpublished.** Proposed issue title: `Sichere einmalige Bereitstellung und Statusaktualität / Safe single-attempt preparation and telemetry freshness`.

Hello, we are developing Airfryer Recipes, a device-independent recipe manager that should optionally use Airfryer Control as its device adapter. The initial target is a Cosori Turbo Tower Pro Smart CAF-DC111S-AEU. Our scope is preparation followed by manual start at the appliance only.

Source review of revision `5a3c530d0fb0b0d1a3f347a172caf95f2dd2eeee` raised these integration questions:

- `programm_senden` uses `async_send`, which tries multiple variants after rejection. `bypass_v2` also uses `_with_relogin`, which repeats requests following authentication errors. Is there a supported way to perform at most one control transport attempt without variant fallback or replay after submission begins? We want neither to call private methods nor implement our own VeSync authentication.
- Are successful observation timestamps and state revisions available per device/zone, or could such an interface be provided? A global refresh and the idle fallback for an unreported zone are insufficient for our safety checks.
- Which programs, limits and zone mappings are confirmed for CAF-DC111S-AEU? We do not want to adopt global TwinFry constants without verification.
- Could a supported interface expose these data and a fixed preparation operation that never starts heating and accepts no raw methods or start variants? Following a timeout after submission, the outcome should be reported as unknown; another attempt would require a fresh user decision.

Our live transmission remains disabled pending clarification. Currently we provide only read-only discovery and a server-side dry-run preview with no control calls. We have contacted no real appliance from the cloud and made no changes to this repository. This is an interoperability request, not a claim of a confirmed security vulnerability.

The complete technical contract requirements and limitations are in the [review report](ISSUE_7_COMMAND_CONTRACT.md). This draft does not authorize communication.
