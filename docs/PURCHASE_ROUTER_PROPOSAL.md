# WA Commons Purchase Route Router — Product Proposal v0.1

Status: **preregistered future-domain design; not current implementation authority**  
Date: 2026-08-31

## 1. Decision summary

WA Commons will treat purchasing as the first preregistered candidate for the second Peace Router domain, but **not** as a general shopping search engine, marketplace, price-comparison crawler, or ethical-product score.

The first hypothesis to test is narrower:

> **When a user already knows what they want to buy, can WA Commons make it easier to choose *where to buy it* according to that user's own policy, while preserving ordinary utility and showing the trade-off honestly?**

The staged experiment is:

1. **Books mechanism test first** — use strong book identity such as ISBN and a shared/book URL as the entry point, then show alternative purchase routes.
2. **Electronics and PC-parts extension second** — only after the mechanism is useful, add products identified by JAN/GTIN/model number and introduce price/availability observations where rights and data quality permit.

Version 0 is **affiliate-free**. WA Commons will not receive routing commissions in the initial experiment.

This proposal does not move Phase 6 ahead of the current M2/M3 work. It records a future design hypothesis so later work does not have to reconstruct the product intent from conversation history.

## 2. Why route the purchase instead of choosing the product

The earlier purchasing concept considered helping users choose products based on domestic manufacture, domestic companies, supply-chain facts, price and peace-related policy.

That direction has real value, but it introduces a very large new identity/data problem:

- millions of SKUs;
- product-to-brand-to-manufacturer resolution;
- OEM and private-label ambiguity;
- weak manufacturing-country coverage;
- volatile marketplace price, stock, shipping and point data;
- high risk of silently converting missing product facts into misleading labels.

A purchase-route experiment is materially narrower.

For the same already-chosen product, changing the seller or platform usually has a lower user cost than changing the product itself. The user does not need to accept different quality, specifications or brand characteristics merely to exercise a preference about the economic route.

This makes the experiment a cleaner test of the WA Commons hypothesis:

```text
same wanted item
      ↓
multiple available purchase routes
      ↓
shared factual evidence about the route entities
      ↓
user-owned policy
      ↓
explainable alternatives
      ↓
user chooses
```

The project does **not** claim that routing a purchase to any particular retailer automatically benefits Japan, peace, employment or another public objective. WA Commons exposes narrow facts and lets policy remain user-controlled.

## 3. Product position

The Purchase Route Router is a **decision layer**, not a commerce destination.

It should not require users to abandon the shopping/search services they already use. A supported flow may begin from:

- a product/book URL the user is already viewing;
- an ISBN;
- later, a JAN/GTIN or manufacturer model number.

The Router then returns a bounded set of alternative purchase routes and their evidence state. The transaction still happens at the external retailer.

```text
Existing discovery channel
(Amazon / search / publisher / retailer / other)
                ↓
        Product identity
                ↓
       Alternative routes
                ↓
Seller / marketplace / fulfillment identities
                ↓
         WA Evidence Graph
                ↓
          User Policy
                ↓
      Explained route options
                ↓
     External retailer checkout
```

The core product question is not "Which company is morally best?" It is:

> **"For this exact item, which available purchase routes satisfy the conditions I chose, and what do I give up by choosing them?"**

## 4. Stage P1 — Books mechanism test

Books are the first mechanism test because they provide a comparatively strong product identity boundary and allow the routing behavior itself to be tested before introducing a broad SKU ontology.

### Entry

Preferred entry paths:

1. share/paste a URL for a book the user is already considering;
2. enter an ISBN directly.

Title search may be added only if it is needed for the mechanism test. WA Commons should not begin by building another general book-search catalog.

### Required behavior

For one resolved edition/item, the Router should be able to show zero or more supported purchase routes with explicit state for:

- seller;
- marketplace/platform, if any;
- fulfillment actor when known and materially distinct;
- direct retailer URL;
- availability state when a permitted source supports it;
- relevant organization identity/evidence;
- user-policy result and explanation;
- `UNKNOWN` / `DISPUTED` / unavailable-route states rather than forced conclusions.

A route with insufficient evidence is not converted into a negative or positive label.

### Book-specific research gate

Before implementation, an exact source/rights review must verify:

- permitted ISBN/title metadata sources;
- which retailers expose searchable/deep-linkable book routes;
- whether availability or price data may be retrieved, stored and redisplayed;
- exact retailer terms for automation, deep links and caching;
- the legal/contractual meaning of any pricing assumptions used in the experiment.

No legal or data-rights assumption from brainstorming is adopted merely because it sounds plausible.

## 5. Stage P2 — Electronics and PC parts

Only after the Books Router demonstrates useful routing behavior should the same mechanism expand to electronics and PC parts.

Identity becomes stricter and more complex:

```text
JAN / GTIN exact
    ↓
manufacturer model number exact
    ↓
brand + normalized model
    ↓
manual user confirmation when exact identity is not proven
```

Name similarity alone must not silently route a user to a different product, bundle, revision, capacity, color, regional version, parallel-import version or accessory set.

This stage may add timestamped observations such as:

- displayed item price;
- stock/availability;
- shipping status;
- delivery estimate;
- visible points or other retailer-provided terms.

These are **observations that decay quickly**, not stable company Evidence Claims. They must retain source and observation time and must never be presented as a guaranteed checkout total unless the source contract actually supports that claim.

Where supported, the UI may show the trade-off between an unconstrained route and a policy-compatible route, for example:

```text
lowest observed route         ¥42,800
policy-compatible route       ¥43,000
observed difference              +¥200
```

The Router must not call a route "cheapest" or "best" beyond what the actual data coverage and timestamp justify.

## 6. Entity model

The purchase domain must not collapse distinct actors into one company.

Minimum conceptual entities:

```text
ProductIdentity
PurchaseRoute / Offer
Seller
MarketplaceOperator
FulfillmentProvider
LegalEntity
CorporateGroup / Parent relation
```

A route might therefore mean:

```text
Product X
  SOLD_BY       → Local Retailer A
  MARKETPLACE   → Platform B
  FULFILLED_BY  → Logistics Actor C
```

Each organization may resolve independently to the existing WA Commons legal-entity layer when strong identifiers and the current conservative entity-resolution rules support the match.

`Seller`, `MarketplaceOperator` and `FulfillmentProvider` must not be treated as interchangeable merely because the user experiences them on one web page.

## 7. Reuse from Peace Capital

The point of this experiment is to test whether the shared core really generalizes.

### Expected reuse

- Evidence Graph concepts and provenance;
- `CONFIRMED`, `DISPUTED`, `UNKNOWN`, `EXPIRED` semantics where applicable;
- conservative legal-entity resolution and parent relationships;
- source registry and terms/license discipline;
- user-owned versioned policy;
- explainable rule/evidence trace;
- append-oriented corrections and challenge paths;
- audit/outcome logging.

### New domain-specific work

- book/product identity;
- purchase-route representation;
- seller/platform/fulfillment separation;
- retailer/source adapters;
- short-lived price/stock observations;
- UI/interaction for route choice.

Phase 5 must extract a domain-independent routing contract rather than silently copying investment-specific semantics into purchasing. Purchasing is a test of the abstraction, not permission to fork a second independent policy/evidence stack.

## 8. Policy behavior

WA Commons does not define one official "good retailer", "Japanese retailer" or "peaceful purchase" score.

User policies may eventually express factual preferences such as:

- prefer a seller that resolves to a Japanese legal entity;
- prefer manufacturer/direct retail where evidenced;
- prefer a retailer with physical stores where that fact is sourced;
- avoid or watch organizations that match the user's existing peace-policy rules;
- accept a route only within a user-selected cost/time constraint.

The exact purchasing policy vocabulary will be designed only after Phase 5 establishes the reusable routing interface.

Missing evidence must remain missing. For example, failure to resolve a seller's parent does not imply independence, domestic ownership, safety or policy compliance.

## 9. Affiliate-free v0 and conflicts of interest

The first experiment will use **no affiliate commissions**.

Reasons:

- keep the routing mechanism independent from monetization incentives;
- make experimental results easier to interpret;
- avoid a structural incentive to favor the retailer paying the highest commission;
- keep the initial open-source public-interest implementation simple.

No affiliate rate, sponsorship payment or commercial consideration is a routing input in v0.

A future monetization model is not prohibited forever, but introducing one would require a separate governance/design decision. Any future commercial incentive must be visibly disclosed and structurally isolated from deterministic policy/routing output.

## 10. Privacy and authority

The first implementation should minimize user data.

- no autonomous purchase;
- no stored payment credentials;
- no automatic order submission;
- no broad browsing-history collection;
- do not retain submitted URLs or identifiers longer than necessary unless the user explicitly chooses history/saved items;
- browser extensions/share targets, if later added, receive only the minimum permissions needed for the explicit user action.

The Router recommends or explains routes. The user remains the actor who chooses and completes the purchase.

## 11. Evidence and legal safety

The existing WA Commons separation remains mandatory:

```text
Observation
   ↓
Evidence Claim
   ↓
Adjudication
   ↓
User Policy
   ↓
Route explanation
   ↓
User action
   ↓
Outcome
```

Examples of safe factual statements include a verified legal entity, parent relationship, disclosed marketplace operator or timestamped availability observation.

Unsafe shortcuts include:

- "this retailer helps Japan" without a defined user policy and supporting narrow claims;
- "this company is a war company" as an unqualified product label;
- treating platform presence as proof of seller identity;
- using an ISBN/JAN prefix or marketplace name as a proxy for manufacturing origin;
- converting `UNKNOWN` into a favorable or unfavorable default.

All new data sources require exact terms/license review before ingestion or redistribution.

## 12. Success measures

The first experiments should measure the mechanism rather than ideology adoption.

Candidate measures include:

- exact item-identity resolution rate;
- percentage of supported queries with at least one alternative route;
- percentage with two or more independently resolved routes;
- legal-entity resolution coverage for displayed sellers/platforms;
- route evidence freshness/unknown/dispute counts;
- rate at which users open an alternative route;
- rate at which a user voluntarily chooses a different route after seeing alternatives;
- repeated-use intent or actual repeated use;
- non-ideological benefit such as easier availability discovery, direct-retailer discovery or lower decision friction.

A later outcome metric may record **Redirected Purchase Value**: the value of purchases where the user voluntarily chose a different route after using WA Commons. This is a routing signal only. It must not be presented as proof of equivalent economic benefit, domestic value added or peace impact.

## 13. Kill / pivot conditions

Do not proceed merely because the design is attractive.

Reconsider or stop the purchasing experiment if evidence shows that:

- permitted data paths cannot produce useful alternative routes;
- item identity cannot be kept sufficiently exact;
- retailer/legal-entity resolution is too weak for the intended claims;
- source terms prevent a reproducible open implementation;
- users do not find route comparison useful without ideological motivation;
- users rarely change routes even when the practical cost is negligible;
- maintaining the routing data requires building a full marketplace/price-comparison crawler.

If the experiment fails, Phase 6 returns to the other candidate domains instead of weakening evidence rules to force a success.

## 14. Explicit non-goals

Version 0 will not:

- operate a marketplace;
- take payment or place orders;
- guarantee the global cheapest price;
- build a complete Amazon/Rakuten/price-comparison clone;
- score retailers with a universal WA Commons morality or "Japan contribution" number;
- infer manufacturing country from retail channel;
- scrape a service in violation of its terms;
- use affiliate commission to influence ranking;
- autonomously redirect or complete a user's purchase;
- displace the current M2/M3 execution order.

## 15. Preregistered sequence

```text
Current work
M2 / M3 / Utility proof
        ↓
Phase 5
Extract domain-independent Peace Router core
        ↓
Phase 6A
Books Purchase Route mechanism test
(URL share + ISBN)
        ↓
Utility / evidence / rights gate
        ↓
Phase 6B
Electronics + PC parts route extension
(JAN/GTIN/model + bounded price/stock observations)
        ↓
Two-domain proof or explicit pivot
```

Preparatory source/rights research and specification may happen earlier when explicitly assigned and when it cannot contaminate current work, but implementation of the second domain must respect the roadmap gates.