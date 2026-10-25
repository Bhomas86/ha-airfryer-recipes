# Draft: Supported interface for safe single-attempt preparation

[Deutsch](UPSTREAM_SAFE_SEND_PROPOSAL.de.md) | [English](UPSTREAM_SAFE_SEND_PROPOSAL.md)

**Status: unpublished.** At the owner's request, the message to the developer will be German only. This English companion is for internal project documentation only.

**Proposed title:** Recipe management for Airfryer Control – integration and required interfaces

---

Hello,

we have already been in contact about two issues. I would like to briefly describe what I am planning on top of your integration and which interfaces would help.

With Codex's support, I am developing an additional Home Assistant integration called [Airfryer Recipes](https://github.com/Bhomas86/ha-airfryer-recipes). It will manage simple recipes with a program, temperature and cooking time locally. The recipe library with categories, personal favorites and JSON import/export already works and I have tested it in Home Assistant.

Next, I plan a dashboard card: select an air fryer and zone, load a recipe or enter settings manually, then deliberately transmit them. Device communication and VeSync login should remain entirely within **Airfryer Control**. Recipe management should also work without a connected appliance.

My first target is the **Cosori Turbo Tower Pro Smart CAF-DC111S-AEU**. Cooking should still be started manually on the appliance. SYNC and MATCH are planned for later.

Reviewing your source at `5a3c530` / version 1.0.1 raised four integration points:

1. **One fixed send attempt without automatic retry.** Through `async_send`, `programm_senden` tries several command variants after rejection. Additionally, `bypass_v2` can repeat the same request through `_with_relogin` after logging in again. For our controls, we would like a mode that sends exactly the fixed variant at most once. After an uncertain result, the user should decide whether to try again. Any required login before the actual send would of course be possible.

2. **Reliably current states per device and zone.** The last successful device-report time and an explicit error/connectivity state would help. An unreported zone must be distinguishable from a zone actually reported idle. Currently the zone sensor also returns idle when the zone report is absent. Old data or an overall successful coordinator refresh should not grant transmission permission. A state revision would additionally help detect changes between preview and confirmation.

3. **Confirmed programs and limits per model and zone.** The UI should offer only supported programs and appropriate temperature/time ranges. Which are already confirmed for CAF-DC111S-AEU? We do not want to adopt general TwinFry values for other models without verification. Values should not be silently clamped during sending either.

4. **A supported preparation interface without heater start.** Ideally this would be a clearly defined action or Python interface accepting device, zone, program, temperature and minutes. Our integration should neither call private methods nor manage its own cloud credentials. Where ascertainable, distinguishing between command acceptance, settings confirmed on the device and unknown outcome would be helpful.

Would such additions be feasible for you, or is there already a planned approach? My main aim is to coordinate the integration with you rather than build around your integration.

Until this is clarified, our live transmission remains disabled. We have read-only discovery and a test preview without control commands. Changes during an active cooking cycle also remain blocked for now. These are requirements for our planned integration; I do not mean to claim a confirmed security defect in your integration.

Thank you for your support so far!
