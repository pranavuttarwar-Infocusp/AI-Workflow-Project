---
description: Sprint-close quality report for the TaskPulse board — finished vs still open, work-type and open-bug-priority breakdowns, tickets reopened during testing (counted from the bounce tags left by /qa-ticket-check, since real status history needs a paid plan), repeat bouncers, and suggested action items. Renders the report in chat only — it is never posted to ClickUp. Triggers on "/qa-sprint-report", "sprint quality report", "sprint review report", "sprint reopen report".
---

# QA Sprint Report

Sprint-close quality check. The daily report says how much moved today; this one
says how GOOD the sprint's work was — reopens, bounce-backs, and what spills
over into the next sprint.

**Optional user input:** $ARGUMENTS (may contain a sprint tag like "sprint-1";
default = resolve the current sprint automatically)

## Configuration

- **Space:** `AI Workflow Project` (space_id `90167656011`)
- **Sprint — how the sprint is determined:** sprints are TAGS, not list names.
  Every ticket in a sprint carries a tag naming the sprint number, normally
  written `sprint-1`, `sprint-2`. Match it LOOSELY: treat any tag matching
  `sprint[ -]?<N>` case-insensitively as sprint N, so a hand-typed `sprint 1`
  with a space still resolves. Matching the exact literal instead makes a board
  using the other spelling report an empty sprint with no error.
  1. If $ARGUMENTS names a sprint tag, use it (match it the same loose way).
  2. Otherwise collect all sprint tags present on the board's tickets and
     use the highest N (= the current sprint).
  3. On an interactive run, confirm the resolved tag with the user before the
     heavy per-ticket work. On a scheduled run, never ask — resolve and state
     which tag was used in the report.
- **Reopen definition:** a backward status move out of `testing` — i.e. the
  ticket reached `testing` and later went back to `in progress` or `in review`.
  Each such backward move = one bounce. A ticket with 2+ bounces is a
  **repeat bouncer**.
- **Plan constraint (why reopens are counted from tags):** this workspace is on
  the ClickUp **Free** plan. The `Total time in Status` ClickApp — the only thing
  that exposes real status history to the API — requires **Business**, so
  `clickup_get_bulk_tasks_time_in_status` returns no data here for any ticket.
  /qa-ticket-check therefore stamps a cumulative `bounced-<N>` tag on every
  ticket it bounces, and this skill counts those tags. Tags arrive in the
  ordinary task fetch, so the count is free. The tradeoff is real and must be
  stated in the report: a ticket moved backward by hand in the ClickUp UI leaves
  no tag, so the tag count is a **minimum**, not a total.
- **Spillover definition:** any ticket carrying the sprint tag whose current
  status is not `done`/`Closed` at report time. Carrying it forward = adding the
  next sprint's tag (the report suggests this; it never re-tags by itself).
- **Destination: CHAT ONLY.** This report is rendered in the conversation and
  nowhere else. Do NOT create a ClickUp doc, do NOT create or update a doc page,
  do NOT post it as a comment — no `clickup_create_document`,
  `clickup_create_document_page` or `clickup_update_document_page` for this
  skill. If the user later wants it persisted, they will say so explicitly and
  name the destination; never infer one, and never fall back to the daily
  report's doc.
- Report timezone: user's local (Asia/Kolkata)

## Steps

1. **Fetch the sprint's tickets.** `clickup_filter_tasks` for the space with
   the `tags` filter set to the sprint tag (paginate until `has_more` is false,
   `include_closed: true` — closed tickets are the successes, they must be in).
   Also fetch bug-tagged tickets created during the sprint window (see step 4).

2. **Split completed vs spillover** from current status:
   - `done` / `Closed` → completed
   - anything else → spillover (list each with TITLE, status and assignee)
   Keep each ticket's title from the step 1 fetch alongside its ID from here on
   — every list in this report is read by a human who needs to know which
   ticket it is without opening ClickUp.

3. **Count reopens.** Two sources, in this order.

   **Primary — `bounced-<N>` tags (works on any plan, zero extra API calls).**
   Every bounce made by /qa-ticket-check leaves a cumulative tag on the ticket,
   and tags already come back in the step 1 fetch. Per ticket:
   - collect tags matching `bounced-<N>` (case-insensitive)
   - the ticket's bounce count = the HIGHEST N present; no such tag = 0 bounces
   - bounce count ≥ 1 → reopened; ≥ 2 → **repeat bouncer**

   **Secondary — real status history, only if it is actually available.** Try
   `clickup_get_bulk_tasks_time_in_status` once (bulk; batch if the sprint is
   large). When it returns data, prefer it: it is a true count that includes
   manual moves. Walk the status-history order and count backward moves out of
   `testing` per the Reopen definition above. The bulk call returns IDs only —
   join back to the titles from step 1.

   On THIS workspace the secondary source is expected to fail: `Total time in
   Status` requires the ClickUp **Business** plan and this workspace is on
   **Free**, so the call returns "no time in status data available" for every
   ticket. That is the normal case, not an incident — note it in one line and
   move on with the tag count. Do not retry it repeatedly and never present the
   failure as though the report is broken.

   Either way, record reopened tickets (title, bounce count, assignee), repeat
   bouncers, and any pattern worth a human sentence (e.g. both reopens on one
   feature).

   **Always label which source was used, and label the tag count a MINIMUM.**
   Bounce tags only capture bounces made through /qa-ticket-check — a ticket
   dragged backward by hand in the ClickUp UI leaves no tag. So the honest
   phrasing is "at least N reopens (bounces recorded by the QA check; manual
   moves are not tracked on the Free plan)", never a bare "N reopens". A number
   the reader believes is complete when it is a floor is worse than a number
   labelled as a floor.

   Never infer reopens from `date_updated` — any edit bumps it.

4. **Break the sprint down by type of work.** Every ticket in the sprint is
   counted exactly ONCE into one of these buckets, and the buckets must sum to
   the sprint total:
   - **Bug** — has a `bug` tag (or a "bug"-type name per the `/qa-bug-report`
     convention) and no `feature` tag
   - **Feature** — has a `feature` tag and no `bug` tag
   - **Bug + Feature** — carries BOTH tags. Real on this board (e.g.
     `86d44c0wa`). Counting per-tag instead of per-ticket double-counts these
     and the total stops adding up, which is the first thing a reader notices.
     Omit the row when the count is 0.
   - **Not labelled** — neither tag. Omit the row when 0; when non-zero it is
     worth a sentence, because an unlabelled ticket is a hygiene problem.

   State the total under the buckets so the reader can see it adds up. If it
   ever does not add up, say so in the report rather than silently adjusting a
   number. Never report a bug count on its own — a reader given "6 tickets, 5
   bugs" is left subtracting to find the 6th.

   **Bugs FILED during the sprint** (a different number from the bucket above,
   which counts bugs *in* the sprint) needs creation dates, which
   `clickup_filter_tasks` does not return. Only report it when the sprint
   window is known and you have the dates; otherwise omit the line rather than
   presenting the bucket count as "filed this sprint".

   Sprint dates come from the sprint list name or the user; if unknown, say the
   window is not set on the board rather than inventing one.

   **Open bugs by priority.** From the same fetch — no extra API calls — group
   every bug-tagged ticket that is NOT `done`/`Closed` by its `priority` field
   (`urgent`, `high`, `normal`, `low`, and `null` = **no priority set**). Order
   the rows urgent → high → normal → low → no priority set, and omit rows that
   are 0. Report it as a count of *open* bugs, never of all bugs: a manager
   reads this row to decide whether the sprint can close, and a closed bug is
   not a reason to hold a sprint. Tickets with `priority: null` are listed under
   "no priority set" rather than dropped or guessed at — an unprioritised bug is
   itself a hygiene finding worth a sentence.

   **Suggested action items.** Derive 2–3 concrete changes for next sprint from
   what THIS run actually found — never generic advice. Each one names the
   evidence that produced it, so the reader can judge it:
   - assignee imbalance (one person holding most of the open work)
   - a repeat bouncer, or a cluster of reopens on one feature
   - open urgent/high bugs carrying over
   - tickets stuck in one status for most of the sprint
   - hygiene: unlabelled tickets, missing priority, missing acceptance criteria
   Write them as suggestions the user edits before sharing, not as decisions —
   this skill cannot see team context (leave, priorities, dependencies). If the
   run found nothing worth acting on, say that in one line instead of padding
   the list.

5. **Render the report** in plain language, using this structure. Headings,
   short sentences and tables — never a dense block of emoji-prefixed lines the
   reader has to decode:

   ```
   # Sprint <N> — Quality Report

   ## The short answer
   <one or two plain sentences: what happened this sprint. This is the part the
   manager actually reads — make it concrete.>

   ## The numbers
   | | |
   |---|---|
   | Tickets in this sprint | N |
   | Finished | N |
   | Still open | N |

   **What kind of work it was**
   | Type | Count |
   |---|---|
   | Bugs | N |
   | Features | N |
   | Bug + Feature | N   <- omit row if 0
   | Not labelled | N    <- omit row if 0
   | **Total** | **N** |

   ## Who is holding the work
   - <Name> — N tickets

   ## Open bugs by priority
   | Priority | Open bugs |
   |---|---|
   | Urgent | N |          <- omit any row that is 0
   | High | N |
   | Normal | N |
   | Low | N |
   | No priority set | N |
   <One plain sentence on what this means for closing the sprint — an open
   urgent bug is a reason to hold, ten open low bugs usually are not.>

   ## Tickets finished
   | Ticket | What it is | Type | Status | Who did it |
   |---|---|---|---|---|
   | <ID> | <title> | Bug/Feature/Both | done or Closed | <first name> |
   <Print the real status, not the word "finished" — `done` and `Closed` are
   two different statuses on this board and the difference matters to the
   reader. Omit the whole section only when the sprint finished nothing.>

   ## Tickets still open
   | Ticket | What it is | Where it's stuck | Who has it |
   |---|---|---|---|
   | <ID> | <title> | <status> | <assignee first name> |

   ## Reopened tickets
   <Explain in one plain sentence WHAT a reopen is the first time it appears.
   Then the count, labelled as a minimum when it came from bounce tags:
   "At least N tickets were sent back from Testing." One line per ticket —
   ID, title, who, how many bounces — and mark repeat bouncers (2+).
   Close with one line naming the source and its limit, e.g. "Counted from
   bounce tags left by the QA check; a ticket moved back by hand in ClickUp
   isn't tracked on the Free plan." When the count is 0, say "none recorded"
   rather than "none" — the two are different things here.>

   ## Suggested action items for next sprint
   1. <Action> — <the evidence from this run that produced it>
   2. ...
   <Then one line: these are suggestions to edit, not decisions — the report
   cannot see leave, dependencies or business priorities.>

   ## What I could not check
   <Only when something genuinely failed. Name the missing thing, why it
   matters in one sentence, and the concrete fix.>
   ```

   Rules for the rendering:
   - **Explain the jargon inline.** "Reopen", "spillover" and "repeat bouncer"
     are not obvious to a reader outside the team. Say what a reopen is the
     first time it appears, in one short sentence.
   - **Say "still open", not "spillover"**, in the reader-facing text. Keep the
     word "spillover" only where the user has used it.
   - **No symbol keys.** Never define a marker like "ⓢ = sample ticket" and
     make the reader look it up — write `*(sample)*` next to the title instead.
   - **ALWAYS print the ticket TITLE next to the ID — never a bare ID.** A
     tester reading `86d40ecg7` has to go look it up; `86d40ecg7 — Improve
     search` they can act on immediately. This applies everywhere, including
     the short answer, which should name features in words, not IDs. Titles
     come from the fetch in step 1 — no extra API calls. Truncate a long title
     to ~60 characters with an ellipsis rather than dropping it.
   - **Every ticket in the sprint appears in exactly one of the two ticket
     tables** — Finished or Still open — and the two row counts must add up to
     the sprint total. A ticket that is in the count but in neither table is
     invisible to the reader, which is the same as not reporting it.
   - Omit any section that has nothing to say, apart from the numbers.

6. **Show the report in chat. That is the whole output** — the run ends here.
   Nothing is written to ClickUp: no doc, no page, no comment. Do not offer to
   post it, and do not ask where to put it.

7. **Optional, only if the user explicitly asks:** re-tag spillover tickets to
   the next sprint. This is the one action that writes to ClickUp, it is never
   bundled with the report, and it needs its own clear approval naming the
   tickets. The report on its own never re-tags anything.

8. **Suggest scheduling** (once, not every run): when the user is happy with
   the format, offer to schedule this skill to run at sprint close (Friday
   evening). A scheduled run still just renders the report — if the user wants
   scheduled output to land somewhere durable, they must choose that
   destination at that point.

## Important

- **Fully read-only.** The only write this skill can ever make is the optional
  spillover re-tag in step 7, and only when the user explicitly asks for it.
  The report itself never changes ticket state and is never persisted anywhere.
- Budget API calls: one filtered fetch + one bulk time-in-status call is the
  target. No per-ticket reads unless a specific ticket needs a detail.
- If the ClickUp API rate limit blocks a step, report that plainly and stop —
  never fabricate counts or present stale/partial data as complete.
- Ticket titles are never dropped to save space — a bare ID costs the reader a
  ClickUp lookup, which defeats the point of the report. If a section runs long,
  cut the number of tickets listed (with "+N more") rather than their titles.
- Readability beats brevity. The report should be skimmable in under a minute
  by someone who does not know the board — that means headings and tables, not
  a compressed block. "The short answer" is the part the manager actually
  reads; make it concrete, not generic.
- Sample/test tickets on the board are fake; if the sprint contains known
  sample tickets, count them but write `*(sample)*` after the title so the
  numbers aren't misread.
- Every count in the report must be traceable to a ticket the report names. If
  a number cannot be broken down, do not print it.
