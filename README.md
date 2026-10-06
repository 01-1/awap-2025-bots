# AWAP 2025 bots

My competition bots for AWAP 2025 (CMU ACM's annual programming competition), a turn-based
strategy game with units, buildings, terrain and a turn limit.

Note: this description was written with LLMs. The bots' own provenance is described below and is
recorded in the header comment of each file, written at the time.

## Layout

| Path | |
|---|---|
| [`main/`](https://github.com/01-1/awap-2025-bots/tree/main/main) | The bots that mattered. `c2 → c3 → c4 → c5` is one lineage grown over the competition (361 → 473 → 534 → 538 lines); `wh-farm.py` (645 lines) is the other. |
| [`variants/`](https://github.com/01-1/awap-2025-bots/tree/main/variants) | 43 experiments — catapult rushes, warrior/healer ratio sweeps (`21-`, `42-`, `64-`, `82-`, `91-`), engineer and explorer builds, bridge play. Most were dead ends. |
| [`llm-baselines/`](https://github.com/01-1/awap-2025-bots/tree/main/llm-baselines) | Single-prompt bots generated from DeepSeek and GPT-4o, one strategy each. |

The game engine is not mine — it's
[`acm-cmu/awap-engine-2025-public`](https://github.com/acm-cmu/awap-engine-2025-public), provided
by the organizers. Only the bots are here. To run these you'd drop them into that engine's `bots/`
directory.

## On provenance, and what the baselines are doing here

Every bot in `main/` carries a header I wrote at the time:

```python
# written with help from chatgpt, deepseek, claude          (c2–c5)
# Written mostly using DeepSeek, with human modifications   (wh-farm.py)
```

So these are LLM-assisted, not hand-written, and I'm not claiming otherwise.

What's more interesting is the comparison sitting next to them. Early on I generated a spread of
single-strategy bots straight from DeepSeek and GPT-4o — one prompt, one strategy, no iteration.
They lost. In the original working tree those two directories were named `sucky-deepseek-bots` and
`these bots suck (chatGPT-4o)`, which is a fair summary of how they performed.

The size difference is most of the story: the generated bots average roughly 23 lines (GPT-4o) and
48 lines (DeepSeek), while the ones that actually competed run 361 to 645. A one-shot generated bot
commits to a single strategy and has no answer when the opponent adapts. The entries that placed
were LLM-drafted and then iterated by hand across many versions against real opponents — which is
what `variants/` is a record of.

That's the takeaway I'd draw from this repo: in February 2025, model output was a good first draft
and a bad final answer, and essentially all of the value was in the iteration loop on top of it.
