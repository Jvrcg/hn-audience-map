# Where Does the AI Infrastructure Buyer Actually Live? A Hacker News Audience Map

![HN Audience Overlap Map](hn_audience_map.png)

Baseten's job description mentioned Reddit as a channel they're exploring to reach their audience. I wanted to understand the channel's audience makeup (traffic between subreddits) before discussing it during the interviews, so I was going to build a Reddit audience overlap analysis. Unfortunately, Reddit's API restrictions made it impossible without enterprise access, which is why I pivoted to the closest high-signal channel for a technical/infra focused audience, Hacker News.

I pulled 12 months (tried 6 months, but it was not enough) of HN stories across 31 companies in the AI/data stack. The group is made up of Baseten, its direct competitors, the foundation-model providers, and the broader infra layer, then mapped which companies share commenters to get as close as possible to the idea of "subreddit traffic flow". If the same people show up discussing two companies, those companies are competing for (or sharing) the same attention, which, depending on the channel, is how I would start building one of the targeting audiences.

## What I found

**HuggingFace is the gravitational center of the AI-infra audience.** Nearly every infra company that has an HN presence, such as Modal, Replicate, Together, and LangChain, connects through it. If you're trying to reach this audience, HuggingFace adjacent conversation is the room they're already in.

**The foundation-model giants (OpenAI, Anthropic, Microsoft, AWS) dominate raw volume but cluster separately.** Around 19,700 unique commenters total, and OpenAI + Anthropic alone account for the bulk. That's the "AI conversation," but it's a different room than the infra-buyer conversation.

**Baseten doesn't appear on its own audience map.** One story, zero comments, no measurable overlap with any peer in 12 months. Its closest competitors, Modal, Replicate, and Together.AI, each have real, active HN communities. This is an opportunity for brand expansion and engagement.

## Why it matters

As AI adoption matures and intelligence becomes native to products rather than a bolt-on API call, the inference layer migrates (as Tuhin mentioned throughout his interviews) from "closed intelligence" (renting someone else's hosted model) to "owned intelligence" (running your own on dedicated infra). That audience will need to realize the capabilities or availability of Baseten beforehand or during research. The people having technical infrastructure conversations on HN today are the buyers whose needs hyperscale as that shift accelerates.

## The AI-search angle (AEO / GEO)

There's a second reason this matters more now than it would have a few years ago. HN discussions are represented in the data that trains LLMs and in the sources that answer engines cite. Showing up on HN isn't just about reaching people; it's about being present in the inputs that determine which names AI tools recommend. While outside a paid media manager role, this would be low-hanging fruit that would support paid media efforts with social proof.

## What I'd do about it

1. **Show up where the audience already is.** The infra cluster routes conversations through HuggingFace, Modal, and Replicate, not Baseten's own. Earned presence (technical content, Show HN launches, founder/engineer participation) in that adjacency is the cheapest and easiest way in.
2. **Treat HN as a channel-fit test, not a guarantee.** Modal posts ~2x/month and gets traction. Cadence and content type matter more than channel choice; the audience is there, but the consistent presence isn't.
3. **Map before you buy.** This same overlap method works as a pre-spend audit for any channel (Reddit, paid social interest targeting, podcast/newsletter sponsorships), to find where the buyer already clusters before allocating budget.

## Things to note

Shared commenters approximate shared audience, not causal influence (and some of them are probably the companies themselves). The 12 month window matters, as a 6 month cut missed slower posting companies entirely. And HN skews toward a specific technical persona; it's one signal, not the whole market. This is a directional map, not an attribution model.

---

*Built with Python (HN Algolia API + NetworkX).*
