# Spec: Turn the eShop into a conference sponsor merch shop

## Problem Statement

Conference sponsors want branded giveaways (mugs, socks, keep cups, stickers and the like) printed with their logo and waiting at their booth on the day. Today that is arranged by email: the organiser sends a PDF price list, sponsors reply with quantities, someone chases payment, proofs go back and forth as attachments, and nobody can see where an order is. Sponsors don't know what's on offer or when they have to order by; organisers and the supplier lose track of who has paid and who has approved what.

The eShop as it stands is a generic consumer storefront: anonymous browsing, personal accounts, a hard-coded shipping address and an order that is "done" the moment checkout completes. None of that matches how sponsor merch actually works.

## Solution

The eShop becomes the sponsor merch shop. Each conference curates its own catalogue of logo-printed, one-size items with its own prices. A sponsorship (a sponsor company at a particular conference) has a shared basket and places orders for delivery to its booth. Orders are a one-way commitment, paid in advance and invoiced outside the app; before production the sponsor approves a proof image for every line. The organiser and the supplier work through API-only roles (no admin UI) to record payment, post proofs and move orders through to "delivered to booth". Nothing is public: every account is created by the organiser and everything sits behind sign-in.

## User Stories

### Sponsor reps

1. As a sponsor rep, I want to sign in with an account the organiser created for me, so that I can order on behalf of my company without registering.
2. As a sponsor rep, I want to change my password after first sign-in, so that the organiser-issued one is not the one I keep using.
3. As a sponsor rep whose company sponsors several conferences, I want to pick which conference I'm ordering for, so that the right catalogue and booth are used.
4. As a sponsor rep whose company sponsors exactly one conference, I want to land straight on that conference's catalogue, so that I'm not asked a question with one answer.
5. As a sponsor rep, I want to browse the conference's catalogue of merch, so that I can see what giveaways are available and at what price.
6. As a sponsor rep, I want to filter the catalogue by item type (mugs, socks, stickers…), so that I can find what I want quickly.
7. As a sponsor rep, I want to see the conference's expected attendee count on the catalogue, so that I can size my order sensibly.
8. As a sponsor rep, I want to see the order cut-off date on the catalogue, so that I know how long I have.
9. As a sponsor rep, I want to see that every item will carry my company's logo, so that I know what I'm buying.
10. As a sponsor rep, I want to add an item to the basket in a quantity, so that I can build up an order.
11. As a sponsor rep, I want the basket to be shared with my colleagues at the same sponsorship, so that two of us don't both order 500 mugs.
12. As a sponsor rep, I want to change line quantities and remove lines from the basket, so that I can correct the order before committing.
13. As a sponsor rep, I want to be told at checkout if a line is below 500, above 10,000 or not a multiple of 500, so that I can fix it before the order is placed.
14. As a sponsor rep, I want to be refused at checkout after the cut-off with a clear message, so that I don't believe an order was placed when it wasn't.
15. As a sponsor rep, I want checkout to confirm that delivery is to our booth and that an invoice will follow, so that I'm not asked for an address or a card.
16. As a sponsor rep, I want to see a confirmation after placing an order, so that I know it went through.
17. As a sponsor rep, I want to see every order my sponsorship has placed, including ones placed by colleagues, so that we have one view of what's been ordered.
18. As a sponsor rep, I want to see an order's status (placed, in production, delivered to booth) and whether it is paid, so that I know where it is.
19. As a sponsor rep, I want to see the proof image for each line of an order, so that I can check the logo and placement.
20. As a sponsor rep, I want to approve a line's proof, so that production can go ahead.
21. As a sponsor rep, I want to reject a line's proof with a comment, so that the supplier knows what to fix.
22. As a sponsor rep, I want to see a new proof on a line I rejected, so that I can approve the corrected version.
23. As a sponsor rep, I want to see "waiting on payment", "waiting on proofs" or "ready for production" on an order, so that I understand what is holding it up.
24. As a sponsor rep, I want to know that orders can't be changed in the app and that changes go by email, so that I don't look for an edit button.
25. As a sponsor rep, I want to be blocked from seeing other sponsorships' baskets, orders and proofs, so that competitors can't see what we're giving away.

### Organiser

26. As an organiser, I want to create a conference with its name, start and end dates and expected attendee count, so that sponsors can order for it.
27. As an organiser, I want to update a conference's dates and attendee count, so that the cut-off and sizing hint stay right.
28. As an organiser, I want to add items to a conference's catalogue with a name, description, type, picture and price, so that each conference offers what suits it.
29. As an organiser, I want to update and remove catalogue items, so that the list and prices stay current.
30. As an organiser, I want to create a sponsor with a name and logo, so that it can sponsor conferences.
31. As an organiser, I want to create a sponsorship linking a sponsor to a conference with a booth, so that it can order.
32. As an organiser, I want to create a rep account (email, initial password) attached to a sponsorship, so that the sponsor's people can sign in.
33. As an organiser, I want to create organiser and supplier accounts, so that colleagues and the supplier can do their part.
34. As an organiser, I want to list the orders for a conference with their payment and proof status, so that I can chase sponsors and invoice.
35. As an organiser, I want to mark an order as paid, so that it can move to production once proofs are approved.
36. As an organiser, I want to be refused when I try to act outside the organiser role, so that roles are enforced in one place.

### Supplier

37. As the supplier, I want to list placed orders across all conferences with their sponsor logo, booth and lines, so that I know what to make.
38. As the supplier, I want to upload a proof image for an order line, so that the sponsor can approve it.
39. As the supplier, I want to see which lines have been rejected and the sponsor's comment, so that I can fix and re-upload.
40. As the supplier, I want to mark an order as in production, and be refused until it is paid and every line is approved, so that nothing is made for an unpaid or unapproved order.
41. As the supplier, I want to mark an order as delivered to booth, so that the sponsor can see it has arrived.
42. As the supplier, I want to see no more about a sponsor than its name, logo and booth, so that sponsor contact details stay private.

### Everyone

43. As any user, I want to be sent to sign-in when I'm not signed in, so that nothing in the shop is public.
44. As any user, I want to be refused when I sign in with a bad or expired token, so that there is no anonymous fallback.
45. As the organiser standing up a new environment, I want the seed to create the first organiser, the supplier and DDD Perth 2027 as a test conference, so that there is something to sign in to.

## Implementation Decisions

### Domain model

- **Conference**: name, start date, end date, expected attendee count. The **order cut-off is derived**: six weeks before the start date, never stored.
- **Catalogue item** belongs to one conference: name, description, item type, picture, price. Items are one-size; there are no variants. The old brand concept is dropped; the type concept stays as the catalogue filter (mug, sticker, socks, keep cup, water bottle, USB drive, battery pack). No t-shirts.
- **Sponsor**: name, logo image. A company, independent of any conference.
- **Sponsorship**: sponsor × conference, plus booth label. It owns the basket and the orders and is the invoiced party.
- **User**: email, password hash, role (`rep`, `organiser`, `supplier`). A rep is attached to one or more sponsorships. Organiser and supplier users are attached to nothing: one supplier role spans all conferences.
- **Basket**: keyed by sponsorship, shared by its reps. Anonymous (UUID-keyed) baskets and the merge-on-login behaviour are removed.
- **Order**: belongs to a sponsorship; carries placed-at (timezone-aware UTC), a status (`placed` → `in_production` → `delivered_to_booth`), a paid flag with paid-at, and lines. Shipping address fields are removed; delivery is implicitly the sponsorship's booth.
- **Order line**: copied product name, picture, unit price and quantity (as today), plus a **proof** sub-state: `awaiting_proof` → `proof_uploaded` → `approved`, or `rejected` with a comment, which returns to `awaiting_proof` when a new proof is uploaded. Each upload replaces the current proof image; history is not kept.

### Rules (live in the services layer)

- Quantity per line: minimum 500, maximum 10,000, must be a multiple of 500. Enforced at checkout, not when adding or editing lines, so a basket can be built up incrementally. The same rule applies to every item.
- Checkout is refused once the current time is past the cut-off, with a message naming the cut-off date.
- Checkout requires a non-empty basket belonging to the caller's chosen sponsorship, and empties it in the same transaction as placing the order.
- Orders cannot be edited or cancelled in the app.
- "Ready for production" is a derived label: paid and every line approved.
- Transition to `in_production` is refused unless ready for production; to `delivered_to_booth` only from `in_production`.
- Proofs can only be uploaded and approved/rejected while the order is `placed`.
- Proof upload is refused on a line that is already approved.

### Authentication and authorisation

- Existing JWT sign-in stays; the token identifies the user, and the role comes from the user record.
- No register endpoint or page. Accounts are created only through the organiser API. A change-password endpoint is available to every signed-in user.
- There is no anonymous access of any kind; the basket-id header path is removed.
- Reps choose an active sponsorship by sending its id with basket and order requests (or in a header); the API refuses a sponsorship the rep isn't attached to. Reps with one sponsorship get it as the default.
- Role checks are a single dependency used by every organiser and supplier route; a wrong role is a 403.

### API shape (contracts, not paths)

- Conference list for the signed-in rep (the ones their sponsorships cover), and conference detail including attendee count and derived cut-off.
- Catalogue types and paged catalogue items, scoped to a conference.
- Basket get / add line / set quantities, scoped to the active sponsorship.
- Place order; list orders; order detail, scoped to the active sponsorship. Detail includes status, paid, ready-for-production, and each line's proof state, proof image and rejection comment.
- Approve / reject a line's proof (rep).
- Organiser: create/update conference; create/update/delete catalogue item; create sponsor (with logo upload); create sponsorship; create user (any role; reps need at least one sponsorship); list a conference's orders; mark order paid.
- Supplier: list placed orders across conferences; upload a line proof; mark in production; mark delivered to booth.
- Health endpoint stays.
- Logos and proofs are stored as static image files and served the same way product pictures are today.

### Seed

- Startup seed creates, only if absent: one organiser account, one supplier account, and the conference "DDD Perth 2027" with placeholder dates and attendee count, a sample catalogue of the seven item types, one sample sponsor with a placeholder logo, its sponsorship with a booth, and one rep account. The organiser corrects real dates and numbers through the API. Credentials are documented in the README, as the demo user's are today.
- The existing product/brand/demo-user seed and the "Sheet → Pin" migration are removed.

### Frontend

- Screens: sign-in → conference picker (only shown when the rep has more than one sponsorship) → catalogue (shows attendee count and cut-off, type filter, pagination) → basket → checkout (confirms booth delivery and invoice-to-follow; shows quantity-rule and cut-off errors from the API) → success → orders list → order detail (status, paid, hold-up label, per-line proof image with approve / reject-with-comment) → change password.
- Register page, anonymous basket id in local storage and the brand filter are removed. Organiser and supplier have no screens.

## Testing Decisions

- A good test drives the HTTP API and asserts on responses and on later observable state through the API, never on tables, SQL or service internals. One scenario per test, named for the behaviour.
- **One seam**: the existing `client` TestClient fixture, which boots the real app against a throwaway seeded SQLite database. No new seams.
- Tests create their own conferences, catalogue items, sponsors, sponsorships and reps through the organiser API in a fixture or helper, signing in as the seeded organiser. Only the seeded organiser and supplier accounts are assumed from the seed, the same way tests use the demo user today. A helper that signs in and returns a bearer header already exists and is reused per role.
- Behaviours that must each have a test: role enforcement (403s) for every organiser and supplier route; no anonymous access; rep cannot touch another sponsorship's basket, orders or proofs; shared basket across two reps; 500/10,000/multiple-of-500 rule at checkout and *not* on add; cut-off refusal (freeze time or seed a conference with a past start); order belongs to sponsorship and appears for every rep; mark-paid only by organiser; proof upload, approve, reject-with-comment, re-upload after reject, upload refused on approved line; in-production refused until paid and all approved, allowed after; delivered only from in-production; conference picker data for reps with one vs several sponsorships; derived cut-off and attendee count in conference detail; order timestamps timezone-aware UTC.
- Prior art: the existing tests for basket identity, checkout, input limits, order timestamps and product images; the input-limits test is the model for the quantity rule, the basket-identity test for sponsorship isolation.
- The repo convention holds: every behaviour change lands with a backend test, and test output is pasted as evidence.

## Out of Scope

- Payment gateway, invoicing, or any money movement; "paid" is a flag the organiser sets.
- Admin, organiser or supplier UI; those roles are API-only.
- Editing or cancelling orders in the app; changes go by email.
- Public registration, self-service sign-up, password reset by email, or any public page.
- Real shipping addresses; delivery is always to the booth.
- Sizes or variants; every item is one size. T-shirts.
- Per-item minimums; the 500-step rule is global.
- Proof history (only the latest proof per line is kept).
- Attendee accounts or any attendee interaction.
- Multiple suppliers or per-conference suppliers.
- Notifications (email, push) on status changes.
- Stock or inventory.

## Further Notes

- Decisions were settled in a grilling session; the chosen answers are recorded here rather than the alternatives.
- Payment and proof approval are deliberately parallel gates: sponsors can approve designs before finance pays, and vice versa; production needs both.
- DDD Perth 2027's real dates and attendance weren't confirmed; the seed uses placeholders and the organiser API is the way to set the truth.
- Suggested order of work: schema and seed first, then auth/roles, then organiser API (it's what tests need to set up everything else), then basket and checkout rules, then order lifecycle and proofs, then frontend.
