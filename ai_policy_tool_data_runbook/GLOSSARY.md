# Glossary — AI Policy Tool reporting

Every column, state value and term used by the reporting notebooks in this
directory, with what it means, where it comes from, and what it does *not* mean.

Read the "watch out" notes. Most of the errors in past reports came from a
column meaning something slightly different from what its name suggests.

- `01-policy-report-reproduction.md` — reproduce a past report
- `02-policy-report-current.md` — current figures, original method
- `03-policy-report-version-adjusted.md` — corrected metric, hand-run SQL
- `04-adjusted-report-end-to-end.md` — corrected metric, Run All

---

## 1. The report columns

The first 18 are the deliverable's original columns, in order. Ten come from
Canvas Data 2, eight from the AI Policy Tool.

| column | source | meaning |
|---|---|---|
| `course_id` | CD2 `courses.id` | Canvas' internal course id. The join key between the two databases. Stable for the life of the course. |
| `term_name` | CD2 `enrollment_terms.name` | Human-readable term, e.g. `2026-2027 Fall`. |
| `course_code` | CD2 `courses.course_code` | Short catalogue code, e.g. `ECON 970`. The registrar appends `[CROSSLISTED - NOT ACTIVE]` here when a course is folded into another. |
| `sis_source_id` | CD2 `courses.sis_source_id` | The registrar's own id for the course. Not the same as `course_id`. |
| `course_name` | CD2 `courses.name` | Full title. The registrar appends `[DELETED BY REGISTRAR]` here when a course is withdrawn. |
| `course_group` | CD2 `accounts.name` | The Canvas sub-account holding the course. **Not a department** — see §4. |
| `parent_account` | CD2 `accounts.name` (parent) | Always `Harvard College/GSAS` in this report; the filter is account id 39. |
| `workflow_state` | CD2 `courses.workflow_state`, remapped | Whether the *course* is published in Canvas. See §2. |
| `ai_policy_in_nav` | CD2 `courses.tab_configuration` | Whether the tool is visible in the course's left-hand navigation. See §2. |
| `ai_policy_created` | policy `created_at` | Date the instructor picked a template and clicked Publish. **Immutable** (`auto_now_add`), which is what makes historical reproduction possible at all. A new row, and so a new `created_at`, appears on every publish — not on every edit. |
| `ai_policy_updated` | policy `updated_at` | Set at creation just after `created_at`, then changes only when the faculty member edits the existing policy. `auto_now`, no history. Never exactly equal to `created_at`, and identical to it *as a date* for 91.8% of policies — see §3. |
| `ai_policy_template` | template `name` | Which template the instructor started from. |
| `ai_policy_body` | policy `body`, as plain text | The policy text as it stands now. A **snapshot** copied from the template at publish time, then owned by the course. |
| `ai_policy_template_body` | template `body`, as plain text | The template text **right now**, at the moment of the query. Not what the instructor was shown, unless the template has not been edited since. |
| `ai_policy_body_changed` | computed | Whether the instructor changed the text. **The definition differs between notebooks** — see §2, and read it carefully before quoting a number. |
| `ai_policy_exists` | computed | `Y` if the course has a published, active policy. |
| `head_instructors` | CD2 `users.name` | Comma-separated head instructors. Load-bearing in notebook 03: instructor spread is what separates a template version from one professor's reused wording. |
| `instructors` | CD2 `users.name` | Comma-separated instructors (the non-head role). |

Added by the adjustment. **Not every artifact carries all of them** — the
notebooks and the packaged scripts in `repro/` produce overlapping but different
sets, so the "from" column says where each one appears:

- **nb** = notebooks `03` and `04`
- **script** = `repro/build_adjusted_report.py` and `repro/pull_current_adjusted.py`,
  which produced `AIPolicyReport_adjusted_2026-08-25.xlsx` and
  `AIPolicyReport_adjusted_current_2026-09-21.xlsx`

| column | from | meaning |
|---|---|---|
| `ai_policy_edit_class` | both | What the policy actually is, in four buckets. See §2. More informative than the Y/N flag. |
| `ai_policy_template_version_matched` | both | Which template version(s) the body matches verbatim, e.g. `v3`. Blank means it matched none, i.e. the instructor edited it. |
| `ai_policy_similarity_to_nearest_version` | both | 0–1, `difflib` ratio against the closest known version. `1.0` = verbatim. |
| `ai_policy_template_body_compared` | both | The text actually used for the comparison, so the judgement can be checked by eye. |
| `ai_policy_nearest_version` | nb | Which version an edited policy is closest to — i.e. which one the instructor started from. Editing the current template and editing a two-versions-old one are different situations. |
| `ai_policy_body_changed_original_method` | nb | The old flag, kept beside the corrected one for comparison. Measures template churn, not faculty behaviour. |
| `ai_policy_template_version_at_publish` | script | The version that was live on the publish date. Usually the same as the matched one; a difference means the policy was published inside a changeover window. |
| `ai_policy_body_shared_courses` | script | How many courses hold this exact body. High = template text; 1 = unique to the course. |
| `ai_policy_body_shared_instructors` | script | How many distinct head instructors hold it. **1 across several courses = one professor reusing their own text**, which is an edit, not a template. |
| `ai_policy_adjustment_note` | script | Why the row was classified as it was, in words. |
| `ai_policy_body_changed_adjusted` | script | The corrected flag, where the script keeps the original in `ai_policy_body_changed`. Absent from the 2026-09-21 pull onward, where `ai_policy_body_changed` **is** the corrected value. |

Where an artifact puts the corrected value differs, and it matters:

| artifact | `ai_policy_body_changed` holds | corrected value also in |
|---|---|---|
| notebooks 03 / 04 | the **corrected** value | — (original is in `..._original_method`) |
| `AIPolicyReport_adjusted_2026-08-25.xlsx` | the **original** value, for comparison | `ai_policy_body_changed_adjusted` |
| `AIPolicyReport_adjusted_current_2026-09-21.xlsx` | the **corrected** value | — (original not computed) |

---

## 2. State values

### `workflow_state` — is the **course** published in Canvas

**These are states of the Canvas course itself, not of the AI policy.** Canvas'
raw values are renamed in the SQL purely for readability — the mapping changes
no meaning:

| raw Canvas value | reported as | what it means | in scope, Fall 2026 |
|---|---|---|---|
| `claimed` | `unpublished` | **A new course.** It exists, but the instructor has not published it, so students cannot see it. | 3,603 |
| `available` | `published` | **A published course** — live to students. | 1,413 |
| `completed` | `completed` | **The course is over.** The term has ended and the course is concluded and read-only. | 0 |
| `deleted` | `deleted` | Deleted in Canvas. | 0 |

`ELSE c.workflow_state::text` is a safety net that **never fires**: across all
173,000 courses in Canvas Data 2, `workflow_state` only ever holds those four
values. Only the first two occur in a current-term pull, because a Fall course
is not concluded yet, and deleted courses are excluded by the registrar filters
anyway.

Note that `claimed` counts here are larger than the report's row count — the
report applies further filters (course level, the excluded sub-account, the
registrar markers) after this one.

**Watch out:** this moves sharply when term starts (Fall 2026 began 2026-09-02)
as instructors publish their courses. A large change between two pulls is the
calendar, not a data problem, and it is not reproducible after the fact — CD2
holds current state only.

### `ai_policy_in_nav` — is the tool visible in course navigation

Derived from `courses.tab_configuration`, matching LTI external tool id
**111167**:

| value | when |
|---|---|
| `hidden` | the tool is explicitly marked hidden, **or** the tool does not appear in the configuration at all |
| `visible` | the tool appears and is not marked hidden |

**Watch out: in practice this column never reports a deliberate hide.**
Measured across the 1,654 courses in the 2026-09-22 report:

| branch | courses | reported as |
|---|---|---|
| tool listed in `tab_configuration`, not marked hidden | 1,645 | `visible` |
| tool not mentioned at all | 7 | `hidden` (via `ELSE`) |
| `tab_configuration` is NULL | 2 | `hidden` (via `ELSE`) |
| **explicitly `"hidden":true`** | **0** | `hidden` |

The first `WHEN` — the elaborate `"hidden":true` pattern — **matches nothing**.
Every `hidden` in the report comes from the fallback, and means "the tool is
not mentioned in this course's navigation configuration", not "somebody hid
it".

That is probably the wrong answer for at least the NULL cases. Canvas writes
`tab_configuration` only once a course customises its navigation; until then
every enabled tool shows in its default position. So a course with no
`tab_configuration` almost certainly *is* showing the tool, while this column
calls it hidden. Worth confirming by opening one of those courses in Canvas.

Practical consequence: **do not quote `nav_hidden` as "instructors who hid the
tool".** It is 9 courses out of 1,654, and the likeliest reading of all 9 is
"navigation was never customised". A hidden tool would not prevent a policy
from existing in any case.

### One row per publish, not per edit

Every row in `policy_wizard_policies` belongs to exactly one course — there are
no rows without a `course_id`. But a course can own several rows, because the
two actions behave differently:

| the instructor... | what happens | new row? |
|---|---|---|
| picks a template and clicks **Publish** | `Policies.objects.create(...)`, and the course's previous active row is flipped to `is_active = 0` | **yes** |
| **edits** the policy already in force | `policy_to_edit.save()` on the existing row | no |

So the row count is a count of *publishes*, not of edits. As of 2026-09-22
there are 5,356 rows across 4,947 courses:

| rows for one course | courses |
|---|---|
| 1 | 4,651 |
| 2 | 239 |
| 3 to 5 | 52 |
| 7 to 17 | 5 |

The course with 17 rows was republished 17 times; 16 of those rows are now
`is_active = 0`. This is the closest thing to history the schema has, and it is
a poor one: it records that a policy was replaced, never when, because
deactivation writes no timestamp.

### `created_at` vs `updated_at`

| column | Django | set when |
|---|---|---|
| `created_at` | `auto_now_add` | the instructor picked a template and clicked Publish. **Immutable** — the one date in the system that can be trusted. |
| `updated_at` | `auto_now` | **set at creation, a fraction of a second after `created_at`, and changes only when the faculty member edits the existing policy.** Nothing else moves it. |

#### What actually moves `updated_at`

Exactly one thing: **an instructor editing the policy already in force and
saving it.** There are only three write paths to a policy row in the whole
application, and only one of them stamps the column.

| code | action | `updated_at` |
|---|---|---|
| `views.py:192` `Policies.objects.create(...)` | publish — writes a **new** row | set at insert |
| `views.py:235` `policy_to_edit.save()` | instructor edits the policy in force | **moves** — `auto_now` fires |
| `utils.py:76` `.update(is_active=False)` | deactivate | **not touched** — a queryset update never calls `save()` |

So the two instructor actions diverge:

| the instructor... | row | `created_at` | `updated_at` |
|---|---|---|---|
| edits the policy in force | the same row, `body` overwritten | unchanged | **moves to the edit** |
| starts over from templates and publishes | a **new** row | new | new; the old row's is frozen |

Nothing else moves it. Publishing a replacement leaves the old row alone.
Direct SQL sets only the columns it names, which is why Jeremy's recovery
(`SET is_active = 1`) left `updated_at` reading its pre-incident value.
Template edits touch a different table. `Policies` is registered in Django
admin, so a save there *would* fire `auto_now`, but `django_admin_log` holds
two entries, both from 2020 — it has effectively never been used.

Measured on the current term, with a one-second threshold to discount the
insert gap:

| | policies | |
|---|---|---|
| never edited after publishing | 419 | 80.3% |
| edited after publishing | 103 | **19.7%** |

About one instructor in five comes back and edits a policy they had already
published.

**This is not the same question as `ai_policy_body_changed`.** `updated_at`
catches edits made *after* publishing. The adjusted flag catches text that
differs from the template, including text customised in the editor *before*
clicking Publish — which never touches `updated_at` at all. That is why 19.7%
here sits beside 56% there without contradiction.

⚠️ The edit path is also where the cross-course bug lives. Before saving, it
calls `inactivate_active_policies(request)`, which deactivates by the
**session's** course rather than the edited policy's course. An instructor
editing one course's policy with another course's tab open can switch off the
other course's policy — and because that goes through `.update()`, nothing
records it. See §8.

#### Three things to know before using these columns

**They are never exactly equal.** Django evaluates `auto_now_add` and `auto_now`
as separate `now()` calls during the same insert, so every row is born with a
gap — the smallest in the current scope is 17 microseconds. Never test
`updated_at = created_at` to mean "never edited". Compare the dates, or allow a
tolerance.

**In the report both are formatted as dates**, so an edit made later the same
day is invisible. Of the current-scope policies:

| | policies | |
|---|---|---|
| same day, later time | 479 | 91.8% — look identical in the report |
| a later day | 43 | 8.2% — visibly edited after publishing |

So `ai_policy_updated > ai_policy_created` in the report means "edited on a
later day", not "edited". The `ai_policy_body_changed` column, not the dates,
is what answers whether the text was changed.

**`updated_at` does not move when a policy is deactivated.**
`inactivate_active_policies` uses a queryset `.update()`, which bypasses
`auto_now` entirely. A policy switched off months ago still carries the
`updated_at` of its last text edit. This is why a disappeared policy cannot be
dated, and why a past report cannot be fully reproduced — see §8.

**There is no history.** An edit overwrites `body` in place. The previous text
is not kept anywhere, so a policy's wording on an earlier date is recoverable
only if some other course published the identical text and still holds it —
which is exactly the trick the version recovery in notebooks 03 and 04 relies
on.

### `is_published` vs `is_active` vs `workflow_state` — three different things

In one line:

- **`is_published` — did the course select a policy at all?**
- **`is_active` — is that policy the one students can see?**
- **`workflow_state` — is the *course* live in Canvas?** Nothing to do with policies.

Both flags sit on the **policy row** and both are set when the policy is
created. Neither says anything about whether the *tool* is visible — that is
`ai_policy_in_nav`, which comes from Canvas, not from this database.

| flag | on | set | values |
|---|---|---|---|
| `is_published` | the policy row | at creation | `1` = this course selected a policy |
| `is_active` | the policy row | at creation | `1` = visible to students, `0` = not visible |
| `workflow_state` | the Canvas course | — | `published` / `unpublished` / `completed` / `deleted` |

Because a row only ever comes into existence by being published, every row the
current tool has written carries `is_published = 1`. The flag earns its keep at
the *course* level rather than the row level: it is what lets you ask "did this
course ever choose a policy", independently of whether one is showing now.

`is_active` is the visibility switch, and the whole rule is one line of code:

```python
# student_active_policy_view
active_policy = Policies.objects.get(course_id=..., is_active=True)
```

Flip `is_active` to `0` and students get the "no policy" page even though the
row, and its full text, are still in the database. Flip it back to `1` and the
policy reappears. That is exactly the disappearing-policy incident: row 5202
sat at `is_published = 1`, `is_active = 0` — the course had selected a policy,
but nothing was visible — and the recovery was a single flag flip,
`UPDATE policy_wizard_policies SET is_active = 1 WHERE id = 5202;`.
`is_published` was never touched.

**Nothing in the application reads `is_published`.** Outside tests it appears
exactly twice: the field definition in `models.py`, and `views.py` where it is
set to `True` at creation. No view, query or template filters on it.

**`is_published` is still worth keeping.** It is not read at runtime, but it is
the only marker that a course *ever* had a policy, which makes it the one way
to find courses that have been stranded by the bug — published once, nothing
active now:

```sql
HAVING sum(is_active) = 0
   AND bool_or(is_published = 1)
```

Because both flags are written in the same statement, they only ever disagree
when something later changes `is_active` — which is why **no row exists with
`is_published = 0` and `is_active = 1`**.

**For a student to actually see a policy, three separate things must hold:**

1. the **course** is published in Canvas (`workflow_state`) — otherwise the
   student is not in the course at all
2. the **tool** appears in the course navigation (`ai_policy_in_nav`) — if it
   is hidden there is no link to reach it
3. an **active** policy exists — otherwise the student gets the "no policy"
   page

Only the third is about the policy record. The report's `ai_policy_exists`
reflects the third; the other two are carried in their own columns.

**What the combinations actually mean**, with counts from the full table as of
2026-09-22:

| `is_published` | `is_active` | policies | courses | what it is |
|---|---|---|---|---|
| 1 | 1 | 4,968 | 4,853 | the live policy. **This is what the report counts.** |
| 1 | 0 | 289 | 209 | published once, then superseded or deactivated |
| 0 | 0 | 99 | 94 | never published. Every one was created between 2014 and 2020-12-07 — drafts from the old tool. Nothing since 2021 has ever been left unpublished. |
| 0 | 1 | 0 | 0 | does not occur, and would be meaningless |

Two facts in that table matter more than they look:

- **4,968 active policies across 4,853 courses.** That is 115 too many.
  **88 courses currently hold more than one active policy**, which the
  application assumes cannot happen and the database does not prevent — there
  is no unique constraint on `(course_id) WHERE is_active = 1`. A duplicate
  fans out the left join and inflates every count downstream, which is why
  notebooks 03 and 04 assert on it before joining. All 88 predate 2026, so the
  current term's pull is clean, but the assertion is not decoration.
- **20 courses are stranded**: they have published policies and no active one,
  so the tool shows the instructor nothing and the report counts them as having
  no policy. Some are ordinary (the instructor deliberately removed a policy);
  others are the disappearing-policy bug. You cannot tell which from the data,
  because deactivation writes no timestamp — see §8.

**When `is_active` flips to 0, nothing records it.** `inactivate_active_policies`
uses a queryset `.update()`, which bypasses Django's `auto_now`, so
`updated_at` still reads whenever the policy was last *edited*. A policy that
was live on the date of an earlier report and is inactive now leaves no trace
of having changed. This is the single biggest limit on reproducing a past
report, and it is why the 2026-08-25 reproduction tops out at 94% recall.

### `ai_policy_exists` — does the course have a policy

`Y` when `ai_policy_created` is not null, i.e. a row survived the policy query's
`is_published = 1 AND is_active = 1` filter.

**Watch out:** `N` does not prove no policy was ever published. A deactivated
policy (`is_active = 0`) disappears from the query with no timestamp recording
when, so a course can go from `Y` to `N` between pulls and leave no trace.

### `ai_policy_body_changed` — did the instructor change the text

**Two different definitions carry this name.** Always check which notebook
produced a file.

| definition | where | what it compares | what it measures |
|---|---|---|---|
| original | the original runbook, notebook 02 | policy body vs the template's **current** text | how recently the template was edited relative to the policy — **not** faculty behaviour |
| adjusted | notebook 03, the adjusted workbooks | policy body vs the template version the policy was **published under** | whether the instructor changed what they were given |

On the 2026-08-25 data the two gave 178 of 216 changed (82.4%) and 108 of 216
(50.0%) respectively. The difference is 70 courses holding verbatim text from a
superseded template version.

The adjusted definition can only ever move a row from `Y` to `N`, never the
reverse, because the current template text is one of the versions it checks
against. An `N → Y` reclassification means something is wrong with the
candidate set.

### `ai_policy_edit_class` — what the policy actually is

| value | rule | reading |
|---|---|---|
| `unedited — verbatim template text` | body matches some known version exactly, after folding whitespace and case | the instructor accepted the template |
| `trivial edit` | similarity ≥ 0.99 to the nearest version | a few characters differ (`we` → `I`, a stray word) |
| `reworded template text` | similarity 0.50–0.99 | recognisably the template, substantively reworded |
| `instructor's own text` | similarity < 0.50 | they wrote their own policy |
| `not assessed` | no version history for that template | e.g. `Custom Policy`; the original flag is carried through unchanged |

### Template version `status` and dating `basis`

| value | meaning |
|---|---|
| `CURRENT` | matches what the template says now |
| `superseded` | a real earlier version, recovered from published policies |
| `(custom text, not a version)` | a cluster that failed the 3-instructor / 3-course test |
| basis `exact` | the edit itself appears in the Splunk access log, timestamped to the second |
| basis `estimated` | bounded only by publish dates — either no edit was logged in the window, or it predates log retention (from 2026-08-19) |
| basis `indeterminate` | the previous version was still being published after this one first appeared, so no window exists. For Maximally Restrictive v2/v3 the cause is benign: same wording, different stored markup |
| basis `first version observed` | the earliest version recoverable; nothing bounds it from below |

---

## 3. AI Policy Tool database

Database `academic_integrity_tool_v2` on `tlt-prod-postgres`. Credentials in
SSM Parameter Store under `/prod/academic_integrity_tool_v2/*`, account
`363687077708` (tlt-prod).

### `policy_wizard_policies` — one row per publish

The application assumes one *active* policy per course. The database does not
enforce it, and 88 courses currently hold more than one.

| field | notes |
|---|---|
| `id` | The policy's own primary key, assigned by the database. **A new `id` every time a course publishes** — each publish inserts a row, so a course that has published four times owns four ids, three of them now `is_active = 0`. Editing an existing policy reuses its id; it does not mint a new one. This is the id you quote when fixing a row by hand, as in `UPDATE policy_wizard_policies SET is_active = 1 WHERE id = 5202`. |
| `course_id` | Canvas course id — which course the policy belongs to. Never null. **No unique constraint**, even though the code assumes one active policy per course, and 88 courses currently break that assumption. |
| `related_template_id` | FK to `policy_wizard_policytemplates.id` — which template the instructor started from. The template table holds 7 rows: ids 1–4 are the retired 2018 set plus `Custom Policy`, and **ids 6, 7 and 8 are the three OUE templates** (Maximally Restrictive, Mixed, Fully-Encouraging). There is no id 5. The FK records only *which* template was chosen; the text itself was copied into `body` at publish time and does not follow the template afterwards. |
| `context_id` | The LTI context identifier from the launch. Recorded alongside `course_id`; the report joins on `course_id`. |
| `body` | The policy text. Quill Delta JSON or legacy HTML — see §5. |
| `is_published` | Set at creation. Presently not read by the code; it does not control visibility. Its one use is finding courses stranded with no active policy — see "published vs active" below. |
| `is_active` | Set at creation. `1` = visible to students, `0` = not visible. The policy the instructor selected as the course policy. Set to `0` when superseded — or, in the known bug, when another course's policy is saved in the same browser session. |
| `published_by` | The LTI `lis_person_sourcedid` of whoever published it. The only user attribution anywhere in the schema. |
| `created_at` | `auto_now_add`. Immutable, and therefore the one trustworthy date in the system. |
| `updated_at` | `auto_now`. Overwritten on every save, with no history table. |

### `policy_wizard_policytemplates` — the templates

| id | name | notes |
|---|---|---|
| 1–3 | `Collaboration Permitted: Written Work`, `Collaboration Permitted: Problem Sets`, `Collaboration Prohibited` | The 2018 set, retired and commented out of the view code. |
| 4 | `Custom Policy` | A blank starting point, not a policy. No version history to recover. |
| 6 | `Maximally Restrictive Policy` | OUE template. Rewritten repeatedly 2026-08-19 to 08-28. |
| 7 | `Mixed Policy` | OUE template. Rewritten 2026-08-28 12:10:08. |
| 8 | `Fully-Encouraging Policy` | OUE template. Rewritten 2026-08-28 12:10:53. |

There is no id 5. Template ids matter because the Splunk log identifies an edit
only by id.

**`updated_at` on this table is declared `auto_now_add`, not `auto_now`.** It is
a copy of `created_at` (2018 or 2025) and has never moved, no matter how many
times a template has been rewritten. This is why template edit times have to
come from Splunk.

### Terms from the application

| term | meaning |
|---|---|
| copy-on-publish | Publishing copies the template `body` into the policy row. The policy is a snapshot; the template keeps moving. This single behaviour is what makes version recovery possible and what makes the original metric wrong. |
| `auto_now_add` | Django: set once, on insert. Correct for `created_at`; a bug on `PolicyTemplates.updated_at`. |
| `auto_now` | Django: overwritten on every `.save()`. **Bypassed by a queryset `.update()`** — which is how deactivation is performed, so deactivation writes no timestamp. |
| Administrator role | An LTI launch role. Required to reach the template edit screens. The only thing the logs narrow a template edit down to. |
| `lis_person_sourcedid` | The user identifier supplied by Canvas on LTI launch. Stored on policies as `published_by`; never stored for template edits. |

---

## 4. Canvas Data 2

Database `residential` on `uw-canvas-data-2-prod`, user `academictech`.
Credentials in Secrets Manager, `uw-cd2-db-user-prod-academictech`.

**The secret's own `dbname` says `postgres`, which is not where the data is.**
A client will show four databases on this cluster: `residential` (Harvard
College/GSAS, what this report needs), `exed` (the other Canvas instance),
`postgres` (empty of Canvas data) and `rdsadmin` (RDS-internal, returns
`permission denied`). Anything that trusts the secret's `dbname` lands in
`postgres` — the wrong one.

#### Connecting with DataGrip, pgAdmin or any GUI client

`academictech@uw-canvas-data-2-prod` is **user@host** — it names neither a
database nor a schema. Two settings have to be right, and getting either wrong
produces the same unhelpful error, `relation "courses" does not exist`:

| | set it to | why |
|---|---|---|
| database | **`residential`** | the connection defaults to `postgres`, which has no Canvas tables. In DataGrip, pick it from the database dropdown in the console toolbar. |
| schema | **`canvas`** | `courses`, `accounts` and `enrollment_terms` all live there. Either select it in the schema dropdown, or qualify every table as `canvas.courses` and so on. |

`SET search_path TO academictech,canvas,public;` also works, **but only if it
runs in the same session as the query**. DataGrip executes the statement under
the caret, so running the `SELECT` on its own silently skips the `SET` and the
query fails. Schema-qualifying the table names avoids the problem entirely and
is the safer thing to paste into a client.

One more client-side trap, this one specific to DataGrip and other JDBC tools:
the `ai_policy_in_nav` pattern contains `:"context_external_tool_111167"` and
`:true`, and a colon followed by a word is how these clients mark a **named
parameter**. The tool tries to bind them instead of sending them. Either turn
off parameter detection, or build the pattern without a literal colon:

```sql
c.tab_configuration LIKE '%{"id"' || chr(58) || '"context_external_tool_111167","hidden"' || chr(58) || 'true}%'
```

Verified to classify identically to the original: 33 hidden, 4,983 visible.

| term | meaning |
|---|---|
| Course Group | The Canvas sub-account a course belongs to, e.g. `Anthropology`. **Not a department.** Departments map to course groups one-to-many, and that mapping is not in CD2, so departments cannot be derived from this data alone. |
| account id 39 | `Harvard College/GSAS` — a school account directly under `Harvard University` (id 1), with 544 sub-accounts beneath it (the course groups). The AI Policy Tool is installed at this account, which is why the whole report is scoped to courses under it. |
| term `sis_source_id` | `2026-1` (Fall), `2026-6` (Fall 1), `2026-7` (Fall 2) — all three are Fall 2026 and all three are included. |
| external tool id 111167 | The AI Policy Tool's LTI registration, matched inside `tab_configuration`. |
| `\D3\d{2,3}` | The course-code filter that excludes 300- and 3000-level (graduate) courses. |
| `[CROSSLISTED - NOT ACTIVE]` | Appended by the registrar to `course_code`. The report's SQL then excludes the course. It often reappears under a new `course_id`. |
| `[DELETED BY REGISTRAR]` | Appended by the registrar to `name`. Same effect. |
| Head Instructor / Instructor | Canvas roles. Both are pulled; head instructors are the ones used to validate template versions. |
| no as-of dimension | CD2 exposes current state only. There is no way to ask what a course looked like on a past date, so the ten Canvas columns are always "as of the pull" and are not reproducible later. |

---

## 5. Policy and template text

| term | meaning |
|---|---|
| Quill Delta | The JSON format written by the current editor, e.g. `{"ops":[{"insert":"..."}]}`. Stored bodies are full-document deltas, so every op is a plain insert. |
| legacy HTML | What the old TinyMCE editor wrote. Still present in bodies not edited since the migration. |
| `to_plain_text` | Converts either format to plain text. Everything downstream compares plain text, never markup. |
| normalisation | Before comparing, whitespace is collapsed and case folded. Without it, 19 of the 2026-08-25 "edits" were a trailing newline. |
| control characters | A few stored bodies contain them (legacy paste artefacts). XLSX rejects them, so they are stripped when writing a workbook. Excel strips them silently on its own way out, which is why a delivered workbook has none and a fresh database pull does. |
| CRLF folding | Excel drops `\r` when it stores cell text. Comparing a fresh pull against a delivered `.xlsx` must fold `\r\n` to `\n` or ~10 rows differ on line endings alone. |

---

## 6. Template versions and dating

| term | meaning |
|---|---|
| version | A distinct wording of a template that at least one instructor published under. Recovered as a cluster of identical policy bodies, numbered `v1`, `v2`, … in order of first use. |
| the 3-and-3 rule | A cluster counts as a version only if ≥ 3 distinct head instructors across ≥ 3 distinct courses hold it. Below that it cannot be distinguished from one professor reusing their own wording. Makes the adjusted figure a conservative floor. |
| `first_seen` / `last_seen` | First and last **publish** date observed for that text. Not edit dates. A version stays live after the last instructor happens to use it. |
| window | The interval in which an edit must have happened: after the previous version's `last_seen`, before this version's `first_seen`. |
| `written` | Best available answer for when a version was created: a timestamp when the log confirms it, otherwise the window. |
| confirmed edit | A `POST /lti/launch/template/<id>/edit/` returning `302` in the application log. `302` means the save took effect. |
| editing session | A run of POSTs seconds apart. Each save overwrites the last, so the final POST in a window is the version that survived. |
| storage change | Two versions with identical wording but different stored markup — legacy HTML vs Quill Delta. Not a policy change. Maximally Restrictive v1/v2/v3 are one wording stored three ways. |
| Splunk source | `index=soc-isites sourcetype=djangoapp`, `attrs.product=academicintegritytoolv2`, `environment=prod`. Django runserver-style access lines: timestamp, method, path, status, size. **No user, no client IP.** Retention roughly 35 days. |

---

## 7. Method vocabulary

| term | meaning |
|---|---|
| original method | `body_changed` computed against the template's current text. What the original runbook does. |
| adjusted method | Computed against the version the policy was published under. What notebook 03 does. |
| re-query vs replay | Re-running the SQL later does **not** reproduce an earlier report, because bodies, `updated_at` and `is_active` are overwritten in place and CD2 has no as-of dimension. The only reliable reproduction is replaying archived input CSVs. Archive them on every run. |
| precision / recall | Used in notebook 01. Precision: of the rows a reproduction returns, how many match the original exactly. Recall: what share of the original's rows it can return at all. The 2026-08-25 reproduction reached 100% precision on 94% recall. |
| reproduction ceiling | An `as_of` bound applied to `created_at`, and optionally to `updated_at`, to exclude anything that happened after a target date. |

---

## 8. Known defects, in shorthand

These come up constantly in discussion of the data. Each is an application
defect, not a reporting choice.

| shorthand | defect | reporting consequence |
|---|---|---|
| the `auto_now_add` bug | `PolicyTemplates.updated_at` never moves | template edit times must come from Splunk |
| no version table | template edits overwrite `body` in place | versions must be reconstructed from published policies |
| the churn metric | `body_changed` diffs a snapshot against live text | reported faculty edits that never happened; 82% vs a real 50% |
| the stampless deactivate | `is_active = 0` written by queryset `.update()`, bypassing `auto_now` | a policy can leave the report with nothing recording that it was ever active |
| no `updated_by` | neither table records who changed anything | no template edit is attributable to a person |
| no unique constraint | nothing enforces one active policy per course | the join could silently fan out; notebook 03 asserts against it |
| the shared-session bug | saving one course's policy can deactivate another's (`edit_active_policy` uses the session's course, not the edited policy's) | courses disappear from the report between pulls |
