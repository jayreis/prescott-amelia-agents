# Ecommerce CRO Standards

Check every email against this list before delivering. These apply regardless of client, platform, or campaign type.

---

**Lead with the offer or the value, not the brand.**
"Save 20% on your restock" beats "A note from our founder." Give it to them in the first line of the hero.

**Discount or offer lives in the hero or eyebrow — never buried in body copy.**
If there is an offer, it must be visible above the fold. Mirror it in the subject line.

**Headline-led, not paragraph-led.**
Body copy under any headline maxes at ~2 sentences before a CTA. The eye should scan the email in 3 seconds and know exactly what to do.

**Scarcity and urgency: stated plainly, once, near the closing CTA.**
One honest deadline or quantity limit. Do not stack urgency across every section — it reads as desperation. No fake countdowns. Real scarcity only.

**Risk reversal near the final CTA when relevant.**
One line — free shipping threshold, money-back guarantee, easy returns, or satisfaction guarantee. Placed directly under or beside the closing CTA button. Not a paragraph; one line.

**Social proof: one specific quote with a real name, OR one hard number.**
"4.8★ from 12,000 reviews" works. A wall of star ratings or a vague "customers love us" line does not. If the brief has no confirmed social proof, omit the section entirely.

**Numbered or icon-led lists for structured content.**
Any "how it works," "what's inside," or "benefits" section must use numbered lists or icon-led rows. Unformatted bullet paragraphs in this context are not acceptable.

**Subject line and preheader are part of the design — always propose both.**
- Subject line: ≤ 50 characters. Clear, benefit-forward, no clickbait.
- Preheader: 40–90 characters. Extends the subject — never repeats it.
- Both must be drafted before the email HTML is considered complete.

**Personalization is mandatory in every email — minimum standard:**
1. First name in the hero — worked naturally into the headline or subhead. Not bolted on as a greeting line.
2. First name in at least one body section.

**Seasonal/location personalization when the brief calls for it:**
> *"As the summer heats up in {{ person.city | default: 'your city' }}..."*
> *"{{ person.city | default: 'Mornings' }} mornings are getting warmer — here's your breakfast upgrade."*

The city token goes into the hero subhead or opening body line — never dropped in isolation, always paired with the seasonal theme, always with a fallback.

**Never invent personalization data.** If a token's source is not confirmed in the client's ESP, flag it to Prescott.
