# Meeting Minutes: Monroe St NE 9

- Source audio: `/Users/mschwar/Downloads/Monroe St NE 9.m4a`
- Duration: `00:23:04`
- Generated: `2026-05-10`
- Attendees: Lee Biby, Matt Schwartz, Thomas Gentry
- Note: These minutes were generated from an AI transcript. Review against the audio before treating wording as exact.

## Purpose

Clarify why the current White Rabbit lead-search workflow is returning too few results, align expectations between the demo path and the live product path, and decide what needs to happen before the upcoming Scotty demo.

## Key Context

Lee tested several lead-search queries in White Rabbit, including broad and narrower versions around HR directors in Tampa and HR directors for hospitals in Tampa. The searches returned only a few usable results, with many failed/noisy outcomes.

Matt explained that the issue is probably not the search intent itself, but that the pipeline is over-validating and filtering too aggressively. The system may be finding many possible leads, then repeatedly narrowing them down until only a few survive.

The group revisited the original strategy: a controlled demo with pre-populated or curated lists was lower risk, while building a live self-serve product before the customer confirms the exact need is much higher risk.

## Decisions

- The current lead-search validation should be loosened so more results come through.
- The product should show a wide-net search result and then clearly explain validation quality, rather than silently filtering most results away.
- It is acceptable for the output to include weaker leads if those leads are labeled with why they are weak or unlikely.
- The safest demo path is still a controlled, pre-populated experience that guarantees a strong list in the 100 to 1,000 range.
- The team should pursue both paths if possible: continue pushing toward the live tool while preserving a reliable controlled demo path.
- If the self-serve workflow is not ready, the team can still sell the value by offering to generate qualified lists for the customer while the self-serve interface matures.

## Action Items

- Matt: Loosen the current validation pipeline so it returns more candidate leads instead of filtering too aggressively.
- Matt: Preserve validation context in the output so users can see why leads are strong, weak, or unlikely.
- Matt: Continue working toward the closest live version possible by end of night.
- Matt: Make the tool usable enough for Lee and Thomas to test tomorrow if possible.
- Lee: Use the GitHub/White Rabbit repository with an agent to ask high-level questions about what has been built and how it works.
- Lee: Help translate the technical state into customer/demo language for Thomas.
- Thomas: Build a 4 to 5 slide deck for the demo and send it to Matt and Lee for approval.
- Team: Prepare a controlled demo path with pre-populated search examples in case the live tool is not ready or does not behave predictably.

## Open Questions

- How close can the live workflow get by the end of the night?
- Which exact searches should be pre-populated for the Scotty demo?
- What result count is good enough for the demo: 100, 500, 1,000, or another range?
- How should the product show weaker leads without making the output feel low quality?
- Is the upcoming customer interaction best framed as a demo, proof of concept, concierge list-building service, or some hybrid?
- How much of the technical development timeline should be exposed to Thomas or the customer?

## Discussion Notes

Lee described testing multiple query variants and repeatedly getting only a handful of returned leads. Matt explained that the pipeline appears to be doing too much vetting before showing results.

Matt reframed the desired behavior: cast a wide net, return a larger set, and show the validation process. The differentiator is not avoiding bad leads entirely; it is showing which leads are weak and why, so the customer is not forced to discover that manually.

Lee clarified the gap between Thomas's sales expectations and the current product reality. Thomas saw the earlier manually assisted list and believed the product was closer to self-serve than it actually is.

Matt acknowledged that he got excited and jumped from the controlled demo concept into trying to build the live app. That live path may work, but it creates risk because the team does not yet know exactly what Scotty will want.

Thomas joined later and confirmed the sales goal: get into the Tuesday demo with enough clarity to bring capital in the door. He asked whether the inputs could be lightened so users can get closer to 1,000 leads when kicking the tires.

Thomas emphasized the product's differentiator: compared with traditional lead-generation tools that require many filters, White Rabbit can connect the dots from simpler natural-language inputs.

The meeting ended with Thomas taking ownership of a short demo deck and Matt committing to keep pushing the live tool so Lee and Thomas can test it the next day.
