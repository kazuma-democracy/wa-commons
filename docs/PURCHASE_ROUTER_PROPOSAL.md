# WA Commons Purchase Route Router — Product Proposal v0.2

Status: **preregistered future-domain design; not current implementation authority**  
Date: 2026-08-31

## 1. Decision summary

WA Commons will treat purchasing as the first preregistered candidate for the second Peace Router domain, but **not** as a new general shopping destination, marketplace, price-comparison crawler, or universal ethical-product score.

The primary product strategy is now **distribution-first / integration-first**:

> **Do not ask users to abandon the shopping and comparison services they already use. Bring WA Commons to the point where the user is already deciding what to buy and where to buy it.**

The first hypothesis to test is:

> **When a user is already viewing or considering an exact item, can WA Commons expose alternative purchase routes and the relevant organization Evidence under that user's own Policy, with minimal extra friction?**

The staged experiment is:

1. **Books mechanism test first** — use strong book identity such as ISBN. The preferred entry is an existing discovery surface through a browser extension/sidebar, share-to-WA action, or pasted URL; direct ISBN entry remains a fallback.
2. **Electronics and PC-parts extension second** — only after the mechanism is useful, add products identified by JAN/GTIN/model number and bounded price/availability observations where rights and data quality permit.
3. **Standalone WA search later, only if justified** — a first-party product search page may become another client of the same Router core after the integration-first mechanism proves useful and suitable data rights exist. It is not the acquisition or MVP assumption.

Version 0 is **affiliate-free**. WA Commons will not receive routing commissions in the initial experiment.

This proposal does not move Phase 6 ahead of the current M2/M3 work. It records a future design hypothesis so later work does not have to reconstruct the product intent from conversation history.

## 2. Why distribution-first

The earlier purchasing concept assumed users might begin a shopping session inside WA Commons. That creates two independent adoption problems before the Evidence/Policy value can even be tested:

- users must discover a new shopping site;
- users must change a familiar search/comparison habit before WA Commons can help them.

Existing commerce and comparison surfaces already solve product discovery, catalog breadth, reviews, merchant relationships, search ranking, and habit formation at a scale WA Commons does not need to reproduce.

The integration-first design therefore follows this rule:

```text
existing user habit
(Amazon / Rakuten / price comparison / retailer / search / publisher / other)
                ↓
      explicit user action to invoke WA
                ↓
        exact product identity
                ↓
       WA alternative routes
                ↓
 organization Evidence + User Policy
                ↓
      explained route options
                ↓
     external retailer checkout
```

WA Commons should compete on the layer the incumbent surfaces normally do not provide: inspectable organization identity, user-owned Policy, provenance, uncertainty, and route alternatives.

This is both a product-distribution decision and a scope-control decision. WA Commons should not spend the first experiment rebuilding catalog search merely to reach the point where its differentiating logic begins.

## 3. What the Router owns and what it borrows

### Existing discovery surfaces own

Where permitted by their terms and the user's explicit action, existing services may supply the context that identifies what the user is already viewing or considering.

Examples of possible entry surfaces include:

- an online retailer product page;
- a marketplace listing;
- a price-comparison product page;
- a publisher page;
- a general web search result;
- a shared product URL from another app.

The fact that a surface is named as a product example does **not** mean WA Commons has adopted its data, terms, API, or extension behavior. Every integration requires a fresh source/rights review.

### WA Commons owns

WA Commons should own the durable, domain-reusable layer:

- conservative product identity handoff;
- alternative-route representation;
- seller / marketplace / fulfillment separation;
- legal-entity resolution;
- Evidence Graph and provenance;
- User Policy application;
- explainable route results;
- uncertainty/dispute handling;
- audit/outcome signals;
- privacy-minimizing integration contract.

### External retailers own checkout

WA Commons does not operate the transaction. The user chooses a route and completes the purchase on the external retailer's own service.

## 4. Preferred interaction surfaces

The same Router core should support multiple thin clients. The first clients should reuse existing user behavior instead of creating a new destination requirement.

### P1 — Browser extension / side panel

When the user explicitly invokes WA Commons on a supported product page, the extension should extract only the minimum identity context needed to resolve the item, subject to the site's current terms and browser-extension rules.

Conceptual experience:

```text
User is already viewing a book/product
        ↓
"Check with WA Commons"
        ↓
WA side panel
        ↓
Exact item identity
Alternative routes
Seller/platform/fulfillment Evidence
User Policy result
        ↓
Open chosen retailer
```

The extension must not require broad browsing-history collection. It should not continuously inspect unrelated pages or transmit page history merely because it has technical permission to do so.

### P2 — Share-to-WA / URL handoff

On mobile or unsupported browsers, the user can share the current product/book URL to WA Commons. The Router resolves the exact item if a permitted adapter can do so, then returns alternative routes.

This should be a first-class path, not merely an emergency fallback, because it avoids dependence on one browser or one page DOM.

### P3 — Direct identifier input

ISBN is the direct fallback for books; JAN/GTIN/model identifiers may serve later product domains.

### P4 — Standalone search — optional later client

A WA Commons search page may later support:

```text
search
  ↓
product candidates
  ↓
exact product identity
  ↓
purchase routes
  ↓
Evidence + Policy
```

But this should be added only after measured use shows that users want a first-party search surface and a lawful/reproducible catalog path exists. The Router core must not depend on WA Commons owning the search funnel.

## 5. Why route the purchase before deeply scoring the product

The earlier purchasing concept also considered helping users choose products based on domestic manufacture, domestic companies, supply-chain facts, price and peace-related Policy.

That direction may become valuable later, but it introduces a much larger new identity/data problem:

- millions of SKUs;
- product-to-brand-to-manufacturer resolution;
- OEM and private-label ambiguity;
- weak manufacturing-country coverage;
- volatile marketplace price, stock, shipping and point data;
- high risk of silently converting missing product facts into misleading labels.

A purchase-route experiment is materially narrower.

For the same already-chosen product, changing the seller or platform usually has a lower user cost than changing the product itself. The user does not need to accept different quality, specifications or brand characteristics merely to exercise a preference about the economic route.

This makes the first experiment a cleaner test:

```text
same wanted item
      ↓
multiple available purchase routes
      ↓
shared factual evidence about route entities
      ↓
user-owned policy
      ↓
explainable alternatives
      ↓
user chooses
```

The project does **not** claim that routing a purchase to any particular retailer automatically benefits Japan, peace, employment or another public objective. WA Commons exposes narrow facts and lets Policy remain user-controlled.

## 6. Stage P1 — Books mechanism test

Books are the first mechanism test because they provide a comparatively strong product identity boundary and allow the routing behavior itself to be tested before introducing a broad SKU ontology.

### Preferred entry order

1. browser extension / side panel from a supported book page;
2. share-to-WA or pasted book URL;
3. ISBN direct entry;
4. standalone title search only if later needed and supported by a reviewed data source.

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
- which discovery surfaces can legally/reliably expose enough identity context to WA Commons;
- which retailers expose searchable/deep-linkable book routes;
- whether browser extensions, page-context extraction, sharing, deep links or caching are allowed under each current service contract;
- whether availability or price data may be retrieved, stored and redisplayed;
- the legal/contractual meaning of any pricing assumptions used in the experiment.

A browser extension is not a loophole around a site's terms. If a service prohibits the needed automated extraction or reuse, WA Commons must use a narrower permitted handoff, an official interface, or omit that integration.

No legal or data-rights assumption from brainstorming is adopted merely because it sounds plausible.

## 7. Stage P2 — Electronics and PC parts

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

## 8. Entity model

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

## 9. Integration boundary

Integrations should be thin and replaceable.

Each discovery-surface adapter should answer only a narrow question such as:

> **What exact item is the user explicitly asking WA Commons to evaluate, and what source locator proves that handoff?**

The adapter should not become a hidden second catalog, crawler, browser-history collector, or policy engine.

Preferred architecture:

```text
Browser Extension ─┐
Share Target ──────┼──→ Product Identity Handoff ─→ Purchase Router Core
Direct ID Input ───┤
Future WA Search ──┘
```

If one external site changes its DOM, API, or policy, that adapter may fail without redefining the Router core.

## 10. Reuse from Peace Capital

The point of this experiment is to test whether the shared core really generalizes.

### Expected reuse

- Evidence Graph concepts and provenance;
- `CONFIRMED`, `DISPUTED`, `UNKNOWN`, `EXPIRED` semantics where applicable;
- conservative legal-entity resolution and parent relationships;
- source registry and terms/license discipline;
- user-owned versioned Policy;
- explainable rule/evidence trace;
- append-oriented corrections and challenge paths;
- audit/outcome logging.

### New domain-specific work

- book/product identity handoff;
- purchase-route representation;
- seller/platform/fulfillment separation;
- discovery-surface and retailer adapters;
- short-lived price/stock observations;
- browser/share interaction for route choice;
- optional later standalone search client.

Phase 5 must extract a domain-independent routing contract rather than silently copying investment-specific semantics into purchasing. Purchasing is a test of the abstraction, not permission to fork a second independent policy/evidence stack.

## 11. Policy behavior

WA Commons does not define one official "good retailer", "Japanese retailer" or "peaceful purchase" score.

User policies may eventually express factual preferences such as:

- prefer a seller that resolves to a Japanese legal entity;
- prefer manufacturer/direct retail where evidenced;
- prefer a retailer with physical stores where that fact is sourced;
- avoid or watch organizations that match the user's existing peace-policy rules;
- accept a route only within a user-selected cost/time constraint.

The exact purchasing Policy vocabulary will be designed only after Phase 5 establishes the reusable routing interface.

Missing evidence must remain missing. For example, failure to resolve a seller's parent does not imply independence, domestic ownership, safety or Policy compliance.

## 12. Affiliate-free v0 and conflicts of interest

The first experiment will use **no affiliate commissions**.

Reasons:

- keep the routing mechanism independent from monetization incentives;
- make experimental results easier to interpret;
- avoid a structural incentive to favor the retailer paying the highest commission;
- keep the initial open-source public-interest implementation simple.

No affiliate rate, sponsorship payment or commercial consideration is a routing input in v0.

A future monetization model is not prohibited forever, but introducing one would require a separate governance/design decision. Any future commercial incentive must be visibly disclosed and structurally isolated from deterministic Policy/routing output.

## 13. Privacy and authority

The first implementation should minimize user data.

- no autonomous purchase;
- no stored payment credentials;
- no automatic order submission;
- no broad browsing-history collection;
- integration clients should inspect only the page/item the user explicitly invokes;
- do not retain submitted URLs or identifiers longer than necessary unless the user explicitly chooses history/saved items;
- browser extensions/share targets receive only the minimum permissions needed for the explicit user action;
- do not transmit unrelated page content when a stable product identifier is sufficient.

The Router recommends or explains routes. The user remains the actor who chooses and completes the purchase.

## 14. Evidence and legal safety

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

- "this retailer helps Japan" without a defined user Policy and supporting narrow claims;
- "this company is a war company" as an unqualified product label;
- treating platform presence as proof of seller identity;
- using an ISBN/JAN prefix or marketplace name as a proxy for manufacturing origin;
- converting `UNKNOWN` into a favorable or unfavorable default;
- assuming that data visible in a browser may automatically be copied, cached, republished or scraped.

All new data sources and integration surfaces require exact terms/license review before ingestion, caching or redistribution.

## 15. Success measures

The first experiments should measure the mechanism and distribution advantage rather than ideology adoption.

Candidate measures include:

- exact item-identity resolution rate from each supported entry surface;
- percentage of explicit WA invocations that reach a resolved item;
- percentage of supported items with at least one alternative route;
- percentage with two or more independently resolved routes;
- legal-entity resolution coverage for displayed sellers/platforms;
- route evidence freshness/unknown/dispute counts;
- rate at which users open an alternative route;
- rate at which a user voluntarily chooses a different route after seeing alternatives;
- repeated-use intent or actual repeated use;
- friction from discovery page to WA result;
- non-ideological benefit such as easier availability discovery, direct-retailer discovery or lower decision friction.

A later outcome metric may record **Redirected Purchase Value**: the value of purchases where the user voluntarily chose a different route after using WA Commons. This is a routing signal only. It must not be presented as proof of equivalent economic benefit, domestic value added or peace impact.

## 16. Kill / pivot conditions

Do not proceed merely because the design is attractive.

Reconsider or stop the purchasing experiment if evidence shows that:

- permitted integration paths cannot reliably identify the item the user explicitly invokes;
- major useful surfaces prohibit or technically prevent the minimum integration needed and no share/URL fallback remains useful;
- permitted data paths cannot produce useful alternative routes;
- item identity cannot be kept sufficiently exact;
- retailer/legal-entity resolution is too weak for the intended claims;
- source terms prevent a reproducible open implementation;
- users do not find route comparison useful without ideological motivation;
- users rarely change routes even when the practical cost is negligible;
- maintaining the routing data requires building a full marketplace/price-comparison crawler;
- a standalone search catalog becomes necessary merely to compensate for a failed integration strategy.

If the experiment fails, Phase 6 returns to the other candidate domains instead of weakening Evidence rules to force a success.

## 17. Explicit non-goals

Version 0 will not:

- operate a marketplace;
- take payment or place orders;
- require users to begin shopping inside WA Commons;
- build a complete first-party book/product search engine before the Router mechanism is proven;
- guarantee the global cheapest price;
- build a complete Amazon/Rakuten/price-comparison clone;
- score retailers with a universal WA Commons morality or "Japan contribution" number;
- infer manufacturing country from retail channel;
- scrape or republish a service in violation of its terms;
- use affiliate commission to influence ranking;
- autonomously redirect or complete a user's purchase;
- displace the current M2/M3 execution order.

## 18. Preregistered sequence

```text
Current work
M2 / M3 / Utility proof
        ↓
Phase 5
Extract domain-independent Peace Router core
        ↓
Phase 6A
Books integration-first mechanism test
(browser/share/URL + ISBN fallback)
        ↓
Utility / evidence / rights / integration gate
        ↓
Phase 6B
Electronics + PC parts route extension
(JAN/GTIN/model + bounded price/stock observations)
        ↓
Optional later client
Standalone WA product search if demand + rights justify it
        ↓
Two-domain proof or explicit pivot
```

Preparatory source/rights/integration research and specification may happen earlier when explicitly assigned and when it cannot contaminate current work, but implementation of the second domain must respect the roadmap gates.