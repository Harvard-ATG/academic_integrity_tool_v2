---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.2
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Report AI Policies Published for Fall 2026 — Version-Adjusted

## Overview

This notebook describes the process for obtaining data on AI Policies published via the AI Policy Tool for Fall 2026 courses, **corrected for the fact that the OUE policy templates have been edited several times during the year**.

It is a revision of `ai-policy-tool/reporting/policy-report.md`, and it produces the same report with the same columns. The only measure that changes is `ai_policy_body_changed`.

To generate a complete report:
- You will export data from the [AI Policy Tool](https://github.com/Harvard-ATG/academic_integrity_tool_v2) database.
- You will join it with course information extracted from [Canvas Data 2 (CD2)](https://harvardwiki.atlassian.net/wiki/spaces/k459/pages/38637832/Canvas+Data+2).
- You will **reconstruct the history of each policy template** from the published policies themselves, because the database keeps no version history.
- You will **read the template edit times out of Splunk**, because the database keeps no timestamp for them either.
- You will then compare each policy against the template version it was published under, rather than against the template's current text.

Everything here runs from four CSV exports and one Splunk export. No access to this repository is required.

**Why this matters, in one line:** the original method reported that 178 of 216 faculty (82%) had edited their AI policy as of 2026-08-25. The real figure was 108 of 216 (50%). The other 70 were holding verbatim template text from an earlier version of the template.


## Context

### Office of Undergraduate Education (OUE)

The primary stakeholder for the AI Policy Tool is the [Office of Undergraduate Education (OUE)](https://oue.fas.harvard.edu/) as they provide guidance on the use of generative AI and [policies for use in the classroom](https://oue.fas.harvard.edu/faculty-resources/generative-ai-guidance/). These policies are the same ones that we have setup as "templates" in the AI Policy Tool.

AI Policy Tool data is often requested by OUE prior to the start of term. Communication is typically coordinated by Jeff Emanuel (Associate Director, Academic Technology).

There are three OUE templates. A fourth, `Custom Policy`, is a blank starting point and is not a template in the sense used here:

- `Mixed Policy`
- `Maximally Restrictive Policy`
- `Fully-Encouraging Policy`

### AI Policy Tool

**Installation**: The *AI Policy Tool* is installed in the [Harvard College/GSAS](https://canvas.harvard.edu/accounts/39) Canvas account, which enables it for all courses by default.

**Visibility of tool**: Instructors can choose to hide the tool from their course navigation (see [tab_configuration](https://developerdocs.instructure.com/services/dap/dataset/dataset-additional-notes)). The tool can also be hidden if a course is imported from a previous term and that previous course the tool was hidden.

**Publishing a policy**: To understand how faculty use the tool to publish a policy in their Canvas course, refer to the [AI Policy Wizard Tool (PDF)](https://drive.google.com/file/d/1LACxLBuBJFDaXkscFHt8xQVsNRQqYRSZ/view?usp=drive_link). When faculty initially select a template and publish a policy, **the database copies the text from the template into the policy row**, so any subsequent changes are localized to that course.

**Editing a template**: Separately, an administrator can edit a template itself, through the tool's own administrator screens (`POST /lti/launch/template/<id>/edit/`). This overwrites `policy_wizard_policytemplates.body` in place. Policies already published keep their copy; policies published afterwards get the new text.

<!-- #region -->
### Why the original `body_changed` flag needs adjusting

The original runbook computes:

```python
aipolicies['body_changed'] = (aipolicies['policy_body'] != aipolicies['template_body'])
```

`policy_body` is a **snapshot**, frozen at publish time. `template_body` is **live**, whatever the template says at the moment of the query. So the comparison asks "does this policy match what we ship today", when the question OUE is asking is "did this instructor change what they were given".

Those are the same question only if the templates never move. They move:

| template | distinct wordings during 2026 | rewritten |
|---|---|---|
| Mixed Policy | 2 | 2026-08-28 |
| Maximally Restrictive Policy | 3 | around 2026-08-21, then 2026-08-28 |
| Fully-Encouraging Policy | 2 | 2026-08-28 |

All three were rewritten within 93 seconds of each other on 2026-08-28. Every policy published before that date therefore fails the comparison, whatever the instructor did. The flag decays toward 100% "changed" as time passes since the last template edit, and resets whenever a template is rewritten.

This notebook compares each policy against the template text **as it stood when that policy was published**.
<!-- #endregion -->

The original runbook already warned that formatting-only differences make a simple textual comparison unreliable, and recommended parsing the text before comparing. That warning stands and is handled here (`to_plain_text` in Step 7, plus whitespace and case folding in Step 10). The version problem is a second, larger effect on top of it.

### Template versions, and how they are recovered

There is no version table. `PolicyTemplates.updated_at` is declared `auto_now_add` rather than `auto_now`, so it holds the creation date and has never moved. `django_admin_log` is empty of these edits, because they go through the tool's own screens rather than Django admin.

Recovery is possible because **publishing takes a copy.**

Two different things happen in this system, and only one of them keeps anything:

- **An admin edits a template.** `admin_level_template_edit_view` sets
  `template_to_update.body` and calls `.save()`. This **overwrites** the
  template. The previous wording is not stored anywhere — it is simply gone.
- **A faculty member publishes a policy.** `instructor_level_policy_edit_view`
  calls `Policies.objects.create(body=...)`, which **copies the template's
  words, as they read that day**, into that course's own row. Nothing later
  changes that copy unless the instructor edits it.

So every published policy is a photocopy of the template on the day it was
published. The template gets overwritten; the photocopies do not. Old wordings
survive only because instructors took copies before the change.

About half the time a faculty member simply accepts the template as offered,
which copies its text word for word. Those untouched copies are the raw
material.

Two sources, each supplying half the answer:

- **Splunk says *when* the template changed.** It logs the edit as an HTTP
  request and nothing more — no text. Template 6, for instance, was saved at
  `2026-08-21 15:13:44` and again at `2026-08-28 12:09:20`.
- **The policies say *what* it said.** Any policy published *between* two
  change dates holds a copy of whatever the template read during that window.

So the method is: take the window between two changes, look at the policies
created inside it, and find text that several faculty hold identically. That
text is the version.

**Several** is the whole safeguard. One professor pasting the same paragraph
into two of their own courses would also produce identical text, so a wording
only counts as a version when **at least 3 different head instructors across 3
different courses** hold it. A real template version is shared by dozens of
unrelated people; one person's own writing collapses to one name. Anything too
thin to meet that bar is treated as a faculty edit, which means the adjusted
figure errs low rather than flattering itself.

Where Splunk has nothing — anything older than about 35 days — the publish
dates alone bracket the window instead, which is looser but still works. Step 9
labels every version with which of the two it relied on.

#### Has the 3-faculty rule thrown away a real version?

The obvious objection to the rule is that a version adopted by only one or two
faculty would be rejected, and those policies would then be counted as edited
when they were not. Two checks, both run against the live data on 2026-09-22.

**Check 1 — the window test.** Of the 171 rejected clusters, only 6 sit in a
*closed* window between two logged template saves, and only 2 of those are
even the right length to be template text. Both turn out to be a single
course's own writing, held by no other course anywhere:

| policy | course | published | chars | opens with |
|---|---|---|---|---|
| 5202 | 174223 | 8/19 16:26 | 628 | *"Use of generative AI for the study of works of art…"* |
| 5207 | 174262 | 8/21 13:34 | 1149 | *"All submitted work should be your own. AI tools are powerful…"* |

Neither resembles the Maximally Restrictive wording they would have to match.
They were published between two saves by coincidence. (5202 is Peter Burgard's
policy from the disappearing-policy incident — the test rediscovered it, and
its art-history wording confirms the custom body described in that report.)

So within the period Splunk covers, **the rule is not hiding a version.**
Before 2026-08-19 there are no logged save times and the test cannot be run;
that is where any residual doubt lives.

**Check 2 — similarity.** For every rejected cluster, compare its text against
the versions that were accepted. Only two come back near-identical — 0.9976 and
0.9864, a character or two apart — and both are already reported as
`trivial edit` with their score in
`ai_policy_similarity_to_nearest_version`. Nothing near-template is buried.

**Where the line is drawn, and how to move it.** `ai_policy_body_changed` flips
to `N` only on an *exact* match to a known version, which is the conservative
choice. Similarity is reported rather than applied, so anyone can redraw the
line without re-running the pull:

| line | changed | share |
|---|---|---|
| exact match only (what the report does) | 179 | 56.0% |
| also treat similarity >= 0.99 as unchanged | 172 | 53.8% |

#### A wording nobody published under is not a version

Splunk logs far more saves than there are versions, because an admin
frequently saves several times in one sitting. Template 6 is the clearest case:
**12 logged saves between 2026-08-19 and 2026-08-28, but only 2 wordings
anybody actually published under** in that period.

The other 10 left no copy in any policy row, so their text is unrecoverable —
and that does not matter. A wording nobody published under never reached a
single course, so no instructor was ever given it, and it cannot affect whether
any policy counts as edited. It is not a gap in the data; it is a version that
never existed as far as the report is concerned.

This is why the two sources count different things, and why neither is wrong:

| | counts | current term |
|---|---|---|
| Splunk saves | every time somebody clicked save | 14 |
| recovered versions | wordings at least 3 faculty published under | 9 |

Quote the first when asking "how often is the template edited". Quote the
second when asking "how many different policies did faculty actually receive".

### What this method cannot recover

- **Who edited a template.** `PolicyTemplates` has no `updated_by` column, the edit view writes no log line, and the Splunk access log records the request but carries no user and no client IP. It narrows to "someone holding an Administrator role in the tool" and no further.
- **A template version nobody published under.** If a template was edited and then edited again before any instructor published, the intermediate text left no copy anywhere and is gone.
- **Template text from before the reporting window.** Recovery depends on a policy having been published under the version.
- **Canvas state as of a past date.** CD2 exposes current state only, with no as-of dimension. The ten Canvas columns in this report are always "as of the pull".

### Canvas Data 2

Canvas Data 2 provides comprehensive data about Canvas courses, enrollments, and more in the form of a SQL database. For reporting purposes, the following tables are of immediate interest:

- `accounts` - stores the hierarchy for courses (e.g. `Harvard University > Harvard College/GSAS > {Course Group}`)
- `context_external_tools` - stores LTI tool registrations; use to find external tool ID
- `courses` - stores attributes for courses, and associated with an account
- `enrollments` - represents a user's enrollment with a specific course and section
- `enrollment_terms` - describes the term or semester associated with courses
- `roles` - describes role in course, which grants permissions (e.g. `Instructor`, `Enrollee`, etc)
- `users` - stores attributes for users such as their `name`

Note that every course is associated with a "Course Group" account which is not the same as a "Department", even though sometimes there is overlap. There is a department ➔ course group mapping (one-to-many), so it is technically possible to derive departments from the data, but not from Canvas Data 2 alone.

See `GLOSSARY.md` in this directory for every column and state value used below.


## Step 1: Prepare environment

Create a data directory to hold input and output CSV files.

```python
!mkdir -p data
```

<!-- #region -->
## Step 2: Export Policies from the AI Policy Tool database

Connect to the database `academic_integrity_tool_v2@tlt-prod-postgres` and run the following query. This is unchanged from the original runbook.

```sql
SELECT p.course_id,
       TO_CHAR(p.created_at, 'YYYY-MM-DD')                created,
       TO_CHAR(p.updated_at, 'YYYY-MM-DD')                updated,
       t.name                                          AS template_name,
       p.body                                          AS policy_body,
       t.body                                          AS template_body
FROM policy_wizard_policies p
         JOIN policy_wizard_policytemplates t ON p.related_template_id = t.id
WHERE p.is_published = 1        -- the course selected a policy (set when created)
  AND p.is_active = 1           -- and it is the one visible to students
  AND p.created_at > DATE '2026-01-01'
ORDER BY p.created_at DESC
```

Save the query results to a file named `data/aipolicies.csv` for later use.

Note: `policy_body`/`template_body` may be either legacy HTML (from the old WYSIWYG editor) or [Quill Delta](https://quilljs.com/docs/delta/) JSON, depending on when the policy/template was created or last edited. These are converted to plain text in Step 7, below.

Two things to know about this query:

- `created_at > DATE '2026-01-01'` does not affect the output. Every policy it excludes belongs to a course outside the Fall 2026 term filter, so the left join in Step 7 discards it anyway. Keep it as a performance guard; do not expect changing it to change anything.
- `is_active = 1` silently drops policies that were deactivated. Deactivation is untimestamped (see Step 5), so a policy that was live when a previous report ran can vanish from this one with nothing in the data to show it was ever there.
<!-- #endregion -->

<!-- #region -->
## Step 3: Export Courses from Canvas Data 2 (CD2)

Connect to the database `academictech@uw-canvas-data-2-prod`. To obtain credentials:

```bash
aws secretsmanager get-secret-value --secret-id uw-cd2-db-user-prod-academictech --query SecretString --output text
```

⚠️ The secret's own `dbname` is `postgres`, which is not where the data is. That cluster hosts two Canvas instances: **`residential`** (Harvard College/GSAS — what this report needs) and `exed`. Connect to `residential`.

Then connect. **Three settings have to be right, and getting any of them wrong
produces the same unhelpful error — `relation "courses" does not exist`:**

| | set it to | why |
|---|---|---|
| host | the `host` field from the secret | `academictech@uw-canvas-data-2-prod` is *user@host*. It names neither a database nor a schema. |
| **database** | **`residential`** | the cluster holds `residential` (Harvard College/GSAS — what this report needs), `exed` (the other Canvas instance), `postgres` and `rdsadmin`. The secret's own `dbname` field says `postgres`, which contains no Canvas data. In DataGrip, pick `residential` from the database dropdown. |
| **schema** | **`canvas`** | `courses`, `accounts` and `enrollment_terms` all live there. |

For the schema you can either select it in the client, or run this **in the
same session** as the query:

```sql
SET search_path TO academictech,canvas,public;
```

⚠️ In DataGrip and most GUI clients, "execute" runs only the statement under
the caret. Running the `SELECT` on its own silently skips the `SET`, and the
query fails. The reliable alternative is to qualify every table —
`canvas.courses`, `canvas.accounts`, `canvas.enrollment_terms` — and skip the
`SET` entirely.

⚠️ One more client-side trap. The `ai_policy_in_nav` pattern below contains
`:"context_external_tool_111167"` and `:true`, and a colon followed by a word
is how DataGrip and other JDBC clients mark a **named parameter** — the client
tries to bind them rather than sending them. Either turn off parameter
detection in the client, or build the pattern without a literal colon:

```sql
c.tab_configuration LIKE '%{"id"' || chr(58) || '"context_external_tool_111167","hidden"' || chr(58) || 'true}%'
```

Verified to classify identically to the literal pattern: 33 hidden, 4,983 visible.

Then run the following query to extract course data. This is unchanged from the original runbook.

```sql
SELECT c.id                AS course_id,
       et.name             AS term_name,
       c.course_code       AS course_code,
       c.sis_source_id     AS sis_source_id,
       c.name              AS course_name,
       account.name        AS course_group,
       parent_account.name AS parent_account,
       CASE c.workflow_state                  -- Canvas' own course states, renamed for the report
           WHEN 'claimed' THEN 'unpublished'  -- a new course, not yet published to students
           WHEN 'available' THEN 'published'  -- a published course, live to students
           WHEN 'completed' THEN 'completed'  -- the course is over; term ended, read-only
           WHEN 'deleted' THEN 'deleted'      -- course deleted in Canvas
           ELSE c.workflow_state::text        -- never fires: Canvas only ever uses the four above
           END             AS workflow_state,
       CASE
           WHEN tab_configuration LIKE '%{"id":"context_external_tool_111167","hidden":true}%' THEN 'hidden'
           WHEN tab_configuration LIKE '%context_external_tool_111167%' THEN 'visible'
           ELSE 'hidden'
           END             AS ai_policy_in_nav
FROM courses c
         JOIN enrollment_terms et ON (et.id = c.enrollment_term_id)
         JOIN accounts account ON (account.id = c.account_id)
         JOIN accounts parent_account ON (parent_account.id = account.parent_account_id)
WHERE parent_account.id = 39  -- Harvard College/GSAS, the school account under Harvard
                              -- University (id 1). Its 544 sub-accounts are the
                              -- 'course groups'; the AI Policy Tool is installed here,
                              -- so every course it covers sits under this account.
  AND et.sis_source_id IN ('2026-1', '2026-6', '2026-7')
  AND account.name <> 'Informal Learning Experiences'
  AND c.course_code !~ '\D3\d{2,3}'   -- drop graduate 300/3000-level: a non-digit, a 3,
                                     -- then 2-3 digits. Keeps 2000-level (the digit
                                     -- before the 3 blocks the match). 2,630 courses.
  AND c.course_code NOT LIKE '%[CROSSLISTED - NOT ACTIVE]%'
  AND c.name NOT LIKE '%[DELETED BY REGISTRAR]%'
ORDER BY c.course_code
```

Save the query results to a file named: `data/cd2courses.csv`.

In DataGrip that is the export icon above the result grid → *Export Data* →
format **CSV**, with the header row included. From the command line the
equivalent is:

```bash
psql "$CD2_DSN" -c "\copy (<the query, on one line, no trailing semicolon>) TO 'data/cd2courses.csv' CSV HEADER"
```

Expect roughly 1,650 rows for a Fall term. If you get zero, you are almost
certainly in the wrong database — see the table above.

Note the last two filters: the registrar marks a course by appending `[CROSSLISTED - NOT ACTIVE]` to `course_code` or `[DELETED BY REGISTRAR]` to `name`, and this query then drops it. A course can therefore leave the report between two pulls without anything being deleted in Canvas, and several reappear immediately under a new `course_id`.
<!-- #endregion -->

<!-- #region -->
## Step 4. Pull Instructor data

In addition to retrieving the course data, we would also like to pull the list of Head Instructor(s) associated with each course. Note that we are not applying the same comprehensive filters to this query as the courses query other than restricting to the [Harvard College/GSAS sub-account](https://canvas.harvard.edu/accounts/39?) and the desired term since we will ultimately be joining this against the course data.

Unchanged from the original runbook. **This export is now load-bearing for more than display**: the head instructor names are what distinguish a genuine template version from one professor's reused wording in Step 8.

```sql
SELECT c.id          AS course_id,
       et.name       AS term_name,
       c.course_code AS course_code,
       c.name        AS course_name,
       u.name        AS user_name,
       r.name        AS role_name
FROM courses c
         JOIN accounts account ON (account.id = c.account_id)
         JOIN accounts parent_account ON (parent_account.id = account.parent_account_id)
         JOIN enrollment_terms et ON (et.id = c.enrollment_term_id)
         JOIN enrollments e ON (e.course_id = c.id)
         JOIN users u ON (e.user_id = u.id)
         JOIN roles r ON (e.role_id = r.id)
WHERE parent_account.id = 39  -- Harvard College/GSAS (see the courses query)
  AND r.name in ('Head Instructor', 'Instructor')
  AND et.sis_source_id IN ('2026-1', '2026-6', '2026-7')
ORDER BY c.course_code, r.name, u.name
```

Save the query results to a file named `data/cd2people.csv`
<!-- #endregion -->

<!-- #region -->
## Step 5: Export the template list and the policy history

Two more exports from `academic_integrity_tool_v2@tlt-prod-postgres`.

**5a. The template list.** Needed to match the numeric template ids in the Splunk log (Step 6) to template names.

```sql
SELECT id,
       name,
       TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at,
       TO_CHAR(updated_at, 'YYYY-MM-DD HH24:MI:SS') AS updated_at,
       LENGTH(body)                                 AS body_chars
FROM policy_wizard_policytemplates
ORDER BY id
```

Save as `data/templates.csv`.

Read `updated_at` here with suspicion. The column is declared `auto_now_add` in the model, so it is a copy of `created_at` and has never moved, no matter how many times a template has been rewritten. It is exported only so the notebook can show that.

**5b. The policy history, for version recovery.**

For a **current** report, `data/aipolicies.csv` from Step 2 already is the history — it has no upper date bound, so every version that anyone has ever published under is in it. Skip to Step 6.

For a report **as of a past date**, Step 2's query is bounded and will not contain the clusters you need. Export the unbounded set separately:

```sql
SELECT p.course_id,
       TO_CHAR(p.created_at, 'YYYY-MM-DD')                created,
       TO_CHAR(p.updated_at, 'YYYY-MM-DD')                updated,
       t.name                                          AS template_name,
       p.body                                          AS policy_body,
       t.body                                          AS template_body
FROM policy_wizard_policies p
         JOIN policy_wizard_policytemplates t ON p.related_template_id = t.id
WHERE p.is_published = 1        -- the course selected a policy (set when created)
  AND p.is_active = 1           -- and it is the one visible to students
ORDER BY p.created_at DESC
```

Save as `data/aipolicies_history.csv`, and point `HISTORY_CSV` at it in Step 7.

Two things this table cannot tell you. They are separate problems:

**What a policy used to say.** Editing a policy overwrites its text in place,
and there is no history table. Only the current wording exists. Whatever it
said on an earlier date is gone.

**When a policy was switched off.** Deactivating sets `is_active = 0` through a
queryset `.update()`, which skips Django's `auto_now`, so `updated_at` is never
touched. A policy that was live in August and is off today still shows the
timestamp of its last text edit. Nothing anywhere records the switch-off, or
when it happened.

Neither can be worked around in reporting; both need a change in the
application. See the defect table at the end of this notebook.
<!-- #endregion -->

<!-- #region -->
## Step 6: Pull template edit times from Splunk

The database cannot tell you when a template was edited, because `updated_at` never moves. The application's own access log can: template edits are HTTP POSTs, and the path carries the template id.

Run this in Splunk and export the results as `data/template_edits.csv`:

```
index=soc-isites sourcetype=djangoapp
  "POST /lti/launch/" ("template/" AND "/edit/")
| rex field=_raw "POST /lti/launch/(?<view>[a-z_]+)/(?<template_id>\d+)/edit/ HTTP[^\"]*\" (?<status>\d+)"
| search status=302
| eval edited_at=strftime(_time, "%Y-%m-%d %H:%M:%S")
| table edited_at, template_id, view, status
| sort edited_at
```

#### Doing it by hand in the Splunk UI

1. Open **https://harvard.splunkcloud.com** and sign in (Harvard SAML), then go
   to the **Search & Reporting** app.
2. Paste the search above into the search bar. The leading `search` command is
   implicit in the UI, so the query starts at `index=soc-isites`. (The notebook
   and the REST API *do* need the explicit `search` keyword — that is the only
   difference between the two forms.)
3. Set the **time range picker** as wide as it will go — *All time*, or at
   least *Last 30 days*. The default is *Last 24 hours*, which returns nothing.
4. Run it and wait for the job to finish.
5. Above the results table, click the **export icon** (the downward arrow) →
   **Format: CSV** → **Export**.
6. Save it as `data/template_edits.csv`.

You should get **14 rows** with the header `edited_at,template_id,view,status`
— 12 saves against template 6, one each against 7 and 8. Those column names are
what Step 9 reads, and they come straight from the `| table` command, so do not
rename them.

⚠️ **This data is expiring.** The index holds roughly 35 days, and the oldest
rows here are from **2026-08-19**, already 34 days old when last checked on
2026-09-22. Once they age out, the exact date for Maximally Restrictive v4
(`2026-08-21 15:13:44`) is gone for good and that version falls back to an
estimated window. A snapshot taken 2026-09-22 is committed alongside this
runbook as `data/template_edits_captured_2026-09-22.csv` — if your own export
comes back short, use that file instead. Archive every future export the same
way; Splunk is not a system of record here.

What you get: the timestamp to the second, the template id, and the status. A `302` means the save took effect (the view redirects on success). A run of several POSTs seconds apart is one editing session — each save overwrites the last, so the final one in a window is the version that survived.

What you do **not** get: any identity. The log line is Django's runserver-style access log — timestamp, method, path, status, size. No user, no client IP. Only an Administrator-role launch can reach the view, and that is as far as the log narrows it.

If Splunk is unavailable, or the edit you care about predates retention, the notebook falls back to bounding each edit between publish dates. Step 9 labels which basis was used for every version, so a reader can see which dates are exact and which are inferred.
<!-- #endregion -->

## Step 7: Merge data

Now, merge the datasets from the AI Policy Tool and Canvas Data 2 (CD2) using [pandas.merge()](https://pandas.pydata.org/docs/reference/api/pandas.merge.html).

The goal is to create a combined dataset that:
- List all courses for Fall 2026 that are NOT 300/3000 level
- Indicates whether each course is published, and of those, which ones have published an AI Policy.

We want to ensure that even courses without a policy appear in the results (left join starting from the full course list).

This step is unchanged from the original runbook, except that the `body_changed` flag it computes is now labelled `ai_policy_body_changed_original_method` — Step 10 computes the one to report.

```python
import json
import hashlib
import re
import difflib

import pandas as pd
from bs4 import BeautifulSoup

DATA_DIR = './data'
HISTORY_CSV = f'{DATA_DIR}/aipolicies.csv'   # see Step 5b for a past-date report
EDITS_CSV = f'{DATA_DIR}/template_edits.csv'

OUE_TEMPLATES = ('Mixed Policy', 'Maximally Restrictive Policy', 'Fully-Encouraging Policy')

# A cluster of identical policy bodies is a template version only if this many
# distinct head instructors, across this many distinct courses, hold it.
MIN_INSTRUCTORS = 3
MIN_COURSES = 3

# Similarity to the nearest known version, used to classify edits.
TRIVIAL_EDIT = 0.99     # at or above this, a few characters differ
OWN_TEXT = 0.50         # below this, the instructor wrote their own policy

pd.set_option('display.width', 200, 'display.max_columns', 50)
```

```python
aipolicies = pd.read_csv(f'{DATA_DIR}/aipolicies.csv')
cd2courses = pd.read_csv(f'{DATA_DIR}/cd2courses.csv')
cd2people = pd.read_csv(f'{DATA_DIR}/cd2people.csv')
```

`policy_body` and `template_body` are either legacy HTML or Quill Delta JSON. Convert both to plain text (requires `beautifulsoup4`: `pip install beautifulsoup4`):

```python
def to_plain_text(body):
    if pd.isnull(body):
        return body
    body = str(body).strip()
    if body.startswith('{'):
        try:
            delta = json.loads(body)
            # Stored bodies are full-document deltas (https://github.com/slab/delta), spot-checked
            # against the data, so every op is a plain insert -- no retain/delete ops here.
            return ''.join(
                op['insert'] for op in delta.get('ops', [])
                if isinstance(op.get('insert'), str)
            )
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass
    return BeautifulSoup(body, 'html.parser').get_text()
```

```python
aipolicies['policy_body'] = aipolicies['policy_body'].apply(to_plain_text)
aipolicies['template_body'] = aipolicies['template_body'].apply(to_plain_text)
```

The original flag, kept under a name that says what it actually measures:

```python
aipolicies['body_changed_original_method'] = (
    (aipolicies['policy_body'] != aipolicies['template_body']).map({True: 'Y', False: 'N'})
)
aipolicies['body_changed_original_method'].value_counts()
```

Before joining, check the assumption the join relies on. The database has no unique constraint on one active policy per course, and a duplicate `course_id` would fan out the left join and inflate every count that follows:

```python
dupes = int(aipolicies['course_id'].duplicated().sum())
orphans = len(set(aipolicies['course_id'].dropna()) - set(cd2courses['course_id']))
print(f'policies: {len(aipolicies)}')
print(f'duplicate course_id: {dupes}   (must be 0, or the join below fans out)')
print(f'policies pointing at out-of-scope courses: {orphans}   (dropped by the left join)')
assert dupes == 0, 'duplicate active policies for one course -- investigate before reporting'
```

### Step 7.1 Merge Courses with Policies

```python
course_policies_df = pd.merge(cd2courses, aipolicies, on='course_id', how='left')
assert len(course_policies_df) == len(cd2courses), 'left join changed the row count'
```

```python
course_policies_df = course_policies_df.rename(columns={
    'template_name': 'ai_policy_template',
    'created': 'ai_policy_created',
    'updated': 'ai_policy_updated',
    'body_changed_original_method': 'ai_policy_body_changed_original_method',
    'policy_body': 'ai_policy_body',
    'template_body': 'ai_policy_template_body',
})
course_policies_df['ai_policy_exists'] = course_policies_df['ai_policy_created'].notnull().replace({False: "N", True: "Y"})
```

### Step 7.2 Merge Courses with People

```python
groups = cd2people.columns.drop('user_name').to_list()
cd2people_grouped_df = cd2people.groupby(by=groups, as_index=False).agg(lambda x: ",".join(sorted(set(x))))
cd2people_pivoted_df = cd2people_grouped_df.pivot(index="course_id", columns="role_name", values="user_name").fillna('')
```

```python
merged_df = pd.merge(course_policies_df, cd2people_pivoted_df, on='course_id', how='left')
merged_df = merged_df.rename(columns={
    'Head Instructor': 'head_instructors',
    'Instructor': 'instructors',
})
merged_df = merged_df.sort_values(by=['course_code', 'sis_source_id'])
merged_df.head()
```

## Step 8: Recover the template version history

Cluster the published policies on their normalised body text. Each cluster of identical text is a candidate template version; the instructor and course spread decides whether it really is one.

```python
def norm_text(s):
    """Collapse whitespace and fold case. The grouping key.

    Deliberately does NOT fold curly quotes into straight ones. Two of the
    Maximally Restrictive versions differ only in apostrophe style, and folding
    them together merges two separate saves into one version. It changes no
    count -- both are recognised versions, so a policy matching either is
    unedited either way -- but it keeps the version numbering here identical to
    template_versions.csv and to the reference workbooks.
    """
    s = '' if pd.isnull(s) else str(s)
    return re.sub(r'\s+', ' ', s).strip().lower()


def text_key(s):
    return hashlib.md5(norm_text(s).encode()).hexdigest()
```

```python
history = pd.read_csv(HISTORY_CSV)
history['policy_body'] = history['policy_body'].apply(to_plain_text)
history['template_body'] = history['template_body'].apply(to_plain_text)
history = history[history['template_name'].isin(OUE_TEMPLATES)].copy()
history['key'] = history['policy_body'].map(text_key)

# Attach the head instructor for each course, which is what tells a template
# version apart from one professor's reused wording.
who = (merged_df[['course_id', 'course_code', 'head_instructors']]
       .dropna(subset=['course_id'])
       .drop_duplicates('course_id')
       .set_index('course_id'))
history = history[history['course_id'].isin(who.index)].join(who, on='course_id')
history['head_instructors'] = history['head_instructors'].fillna('')
print(f'{len(history)} published policies on the three OUE templates')
```

```python
# What each template says right now, so the current version can be marked.
current_key = {t: text_key(g['template_body'].iloc[0]) for t, g in history.groupby('template_name')}

rows = []
for (template, key), g in history.groupby(['template_name', 'key']):
    names = sorted({n.strip() for s in g['head_instructors'] for n in str(s).split(',') if n.strip()})
    text = g['policy_body'].iloc[0]
    rows.append({
        'template_name': template,
        'key': key,
        'n_courses': g['course_id'].nunique(),
        'n_instructors': len(names),
        'first_seen': g['created'].min(),
        'last_seen': g['created'].max(),
        'chars': len(text),
        'is_current': key == current_key.get(template),
        'text': text,
    })

versions = pd.DataFrame(rows)
versions['is_version'] = (
    versions['is_current']
    | ((versions['n_instructors'] >= MIN_INSTRUCTORS) & (versions['n_courses'] >= MIN_COURSES))
)
versions = versions.sort_values(['template_name', 'first_seen']).reset_index(drop=True)

versions['version'] = '(custom text, not a version)'
for template, g in versions[versions.is_version].groupby('template_name'):
    for n, idx in enumerate(g.index, start=1):
        versions.at[idx, 'version'] = f'v{n}'

versions[versions.is_version][
    ['template_name', 'version', 'is_current', 'first_seen', 'last_seen',
     'n_courses', 'n_instructors', 'chars']
]
```

The clusters that did **not** qualify are worth a look. Each is either one instructor's own wording, or a template version too rarely used to tell apart from one:

```python
rejected = versions[~versions.is_version]
print(f'{len(rejected)} clusters rejected as versions')
rejected[rejected.n_courses > 1][
    ['template_name', 'n_courses', 'n_instructors', 'first_seen', 'chars']
].head(10)
```

## Step 9: Date each version

The clusters bound each edit to a window: after the previous version was last published under, before this one first was. The Splunk export pins the edit itself. Where both exist, the window usually collapses to a single timestamp.

```python
try:
    edits = pd.read_csv(EDITS_CSV, dtype={'template_id': str})
    templates = pd.read_csv(f'{DATA_DIR}/templates.csv', dtype={'id': str})
    id_to_name = dict(zip(templates['id'], templates['name']))
    edits['template_name'] = edits['template_id'].map(id_to_name)
    print(f'{len(edits)} template edits from the log, '
          f'{edits.edited_at.min()} to {edits.edited_at.max()}')
except FileNotFoundError:
    edits = pd.DataFrame(columns=['edited_at', 'template_id', 'template_name'])
    print('no Splunk export found -- dating from publish clusters alone')
```

```python
def date_versions(versions, edits):
    """Say when each version was written, and on what evidence."""
    out = []
    for template, g in versions[versions.is_version].groupby('template_name'):
        g = g.sort_values('first_seen')
        logged = sorted(edits[edits['template_name'] == template]['edited_at'].astype(str))
        prev = None
        for _, v in g.iterrows():
            rec = dict(v)
            if prev is None:
                rec.update(written=f'on or before {v.first_seen}',
                           basis='first version observed -- no earlier boundary',
                           confirmed='')
            elif prev.last_seen > v.first_seen:
                # Both were still being published at once, so no window exists.
                same = norm_text(prev.text) == norm_text(v.text)
                rec.update(
                    written='indeterminate',
                    basis=(f'observed use overlaps {prev.version} '
                           f'({v.first_seen} to {prev.last_seen})'
                           + (' -- and the text is word-for-word identical, so this is a '
                              'storage change (legacy HTML vs Quill Delta), not an edit'
                              if same else '')),
                    confirmed='')
            else:
                hits = [t for t in logged if prev.last_seen <= t[:10] <= v.first_seen]
                if hits:
                    rec.update(written=hits[-1], confirmed='; '.join(hits),
                               basis=('exact -- from the application log'
                                      + (f' (last of {len(hits)} saves in the window)'
                                         if len(hits) > 1 else '')))
                else:
                    rec.update(written=f'between {prev.last_seen} and {v.first_seen}',
                               confirmed='',
                               basis='estimated from publish clusters; no edit logged in this window')
            out.append(rec)
            prev = v
    return pd.DataFrame(out)


dated = date_versions(versions, edits)
dated[['template_name', 'version', 'written', 'basis', 'chars']]
```

For the record, what the database itself claims about template edit times:

```python
try:
    t = pd.read_csv(f'{DATA_DIR}/templates.csv')
    print(t[['id', 'name', 'created_at', 'updated_at', 'body_chars']].to_string(index=False))
    print('\nupdated_at == created_at for every row above, because the column is declared')
    print('auto_now_add. This is why Step 6 exists.')
except FileNotFoundError:
    pass
```

## Step 10: Compute the adjusted flag

For each policy, compare its body against every known version of its template — plus the template's current text, which is authoritative for anything published since the last edit. A verbatim match to any of them is not a faculty edit.

```python
version_texts = {}
for _, v in dated.iterrows():
    version_texts.setdefault(v.template_name, []).append((v.version, v.text))
for template, g in history.groupby('template_name'):
    version_texts.setdefault(template, []).append(
        ('(current template text)', g['template_body'].iloc[0])
    )
{t: [v for v, _ in vs] for t, vs in version_texts.items()}
```

```python
def classify(row):
    """-> (flag, edit_class, matched_versions, nearest, similarity, text_compared)"""
    if pd.isnull(row.get('ai_policy_created')):
        return (None, None, None, None, None, None)

    body = row['ai_policy_body']
    candidates = version_texts.get(row['ai_policy_template'], [])
    if not candidates:
        # No version history for this template (e.g. Custom Policy). Fall back
        # to the original comparison rather than guessing.
        return (row['ai_policy_body_changed_original_method'], 'not assessed', '', '',
                None, row['ai_policy_template_body'])

    exact = [name for name, text in candidates if norm_text(text) == norm_text(body)]
    best_name, best_score, best_text = '', 0.0, ''
    for name, text in candidates:
        score = difflib.SequenceMatcher(None, norm_text(body), norm_text(text),
                                        autojunk=False).ratio()
        if score > best_score:
            best_name, best_score, best_text = name, score, text

    if exact:
        return ('N', 'unedited -- verbatim template text', ', '.join(exact),
                exact[0], 1.0, dict(candidates)[exact[0]])
    # best_name says WHICH version an edited policy started from, which is what
    # makes the edit interpretable: editing the current template and editing a
    # two-versions-old one are different situations.
    if best_score >= TRIVIAL_EDIT:
        return ('Y', 'trivial edit', '', best_name, round(best_score, 4), best_text)
    if best_score >= OWN_TEXT:
        return ('Y', 'reworded template text', '', best_name, round(best_score, 4), best_text)
    return ('Y', "instructor's own text", '', best_name, round(best_score, 4), best_text)
```

```python
applied = merged_df.apply(classify, axis=1, result_type='expand')
applied.columns = ['ai_policy_body_changed', 'ai_policy_edit_class',
                   'ai_policy_template_version_matched',
                   'ai_policy_nearest_version',
                   'ai_policy_similarity_to_nearest_version',
                   'ai_policy_template_body_compared']
merged_df = pd.concat([merged_df.drop(columns=applied.columns, errors='ignore'), applied], axis=1)
```

`ai_policy_body_changed` now holds the adjusted value, in the column the original report uses. Compare the two methods:

```python
with_policy_df = merged_df[merged_df['ai_policy_exists'] == 'Y']
comparison = pd.DataFrame({
    'original method': with_policy_df['ai_policy_body_changed_original_method'].value_counts(),
    'adjusted': with_policy_df['ai_policy_body_changed'].value_counts(),
})
comparison['difference'] = comparison['adjusted'] - comparison['original method']
print(comparison.to_string())
print(f"\npolicies: {len(with_policy_df)}")
print(f"reclassified Y -> N: "
      f"{len(with_policy_df[(with_policy_df.ai_policy_body_changed_original_method == 'Y') & (with_policy_df.ai_policy_body_changed == 'N')])}")
print(f"reclassified N -> Y: "
      f"{len(with_policy_df[(with_policy_df.ai_policy_body_changed_original_method == 'N') & (with_policy_df.ai_policy_body_changed == 'Y')])}")
```

`N -> Y` should always be zero. The current template text is one of the candidates, so anything the original method called unchanged is still unchanged. If it is not zero, something is wrong with the candidate set.

```python
with_policy_df['ai_policy_edit_class'].value_counts()
```

The courses that moved, and what they matched — this is the table that explains the difference to a stakeholder:

```python
moved = with_policy_df[
    (with_policy_df.ai_policy_body_changed_original_method == 'Y')
    & (with_policy_df.ai_policy_body_changed == 'N')
]
moved[['course_code', 'course_name', 'head_instructors', 'ai_policy_created',
       'ai_policy_template', 'ai_policy_template_version_matched']].head(20)
```

## Step 11: Save merged data

```python
REPORT_COLUMNS = [
    'course_id', 'term_name', 'course_code', 'sis_source_id', 'course_name',
    'course_group', 'parent_account', 'workflow_state', 'ai_policy_in_nav',
    'ai_policy_created', 'ai_policy_updated', 'ai_policy_template',
    'ai_policy_body', 'ai_policy_template_body', 'ai_policy_body_changed',
    'ai_policy_exists', 'head_instructors', 'instructors',
    # added by this notebook
    'ai_policy_edit_class', 'ai_policy_template_version_matched',
    'ai_policy_nearest_version', 'ai_policy_similarity_to_nearest_version',
    'ai_policy_template_body_compared', 'ai_policy_body_changed_original_method',
]
out_df = merged_df[[c for c in REPORT_COLUMNS if c in merged_df.columns]]
out_df.to_csv(f'{DATA_DIR}/merged_adjusted.csv', index=None)
dated[['template_name', 'version', 'written', 'basis', 'confirmed', 'first_seen',
       'last_seen', 'n_courses', 'n_instructors', 'chars', 'text']].to_csv(
    f'{DATA_DIR}/template_versions.csv', index=None)
print(f'wrote {len(out_df)} rows')
```

The first 18 columns are the original report, in the original order, so this file drops into anything built for it. Note that `ai_policy_body_changed` **means something different** here than in a report produced by the original runbook: same name, corrected definition. Say so when you hand the file over.

Excel will refuse a few stored policy bodies that contain control characters (paste artefacts from the legacy editor). Strip them when writing a workbook:

```python
ILLEGAL_XLSX = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')

def clean(v):
    return ILLEGAL_XLSX.sub('', v) if isinstance(v, str) else v

with pd.ExcelWriter(f'{DATA_DIR}/AIPolicyReport_adjusted.xlsx', engine='openpyxl') as xl:
    out_df.map(clean).to_excel(xl, sheet_name='Data', index=False)
    comparison.to_excel(xl, sheet_name='Summary')
    with_policy_df['ai_policy_edit_class'].value_counts().to_frame('policies').to_excel(
        xl, sheet_name='Summary', startrow=8)
    dated.drop(columns=['key', 'is_version']).map(clean).to_excel(
        xl, sheet_name='template_versions', index=False)
    moved[['course_id', 'course_code', 'course_name', 'head_instructors',
           'ai_policy_created', 'ai_policy_template',
           'ai_policy_template_version_matched']].to_excel(
        xl, sheet_name='reclassified_Y_to_N', index=False)
print('wrote the workbook')
```

Archive the four input CSVs alongside the output. Neither source database keeps history, so a pull cannot be reproduced later by re-querying it — only by replaying its inputs. This is not a precaution; it is the only way any figure in this report can be defended after the fact.

```python
import shutil, datetime
stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
archive = f'{DATA_DIR}/runs/{stamp}'
!mkdir -p {archive}
for name in ('aipolicies', 'cd2courses', 'cd2people', 'templates', 'template_edits'):
    try:
        shutil.copy(f'{DATA_DIR}/{name}.csv', f'{archive}/{name}.csv')
    except FileNotFoundError:
        pass
print(f'inputs archived in {archive}')
```

## Step 12. Quick Analysis (optional)

Let's do some quick analysis on courses that do not have a published policy.

```python
published_df = merged_df[merged_df['workflow_state'] == 'published']
unpublished_df = merged_df[merged_df['workflow_state'] != 'published']
without_policy_df = merged_df[merged_df['ai_policy_exists'] == 'N']

print(f"Published courses: {len(published_df)}")
print(f"Unpublished courses: {len(unpublished_df)}")
print(f"Courses with policies: {len(with_policy_df)}")
print(f"Courses without policies: {len(without_policy_df)}")
```

```python
with_policy_df['ai_policy_template'].value_counts()
```

```python
import matplotlib.pyplot as plt

counts = (
    merged_df.groupby(['course_group', 'ai_policy_exists'])
      .size()
      .unstack(fill_value=0)
      .rename(columns={'Y': 'With AI Policy', 'N': 'No AI Policy'})
)

# To ensure consistent order
counts = counts.sort_values(['With AI Policy', 'No AI Policy'], ascending=False)
```

```python
total = counts.sum()
labels = [f'{label} ({value})' for label, value in zip(total.index, total.values)]
colors = ['lightgray', 'dodgerblue']  # No AI Policy, With AI Policy

plt.figure(figsize=(8,6))
plt.pie(
    total,
    labels=labels,
    autopct='%1.1f%%',
    colors=colors,
    startangle=90,
    wedgeprops={'edgecolor': 'black'}
)
plt.title('Overall AI Policy Adoption')
plt.axis('equal')
plt.tight_layout()
plt.show()
```

```python
template_counts = with_policy_df['ai_policy_template'].value_counts()
template_colors = ['#ffbe7d', '#92caf4', '#c7e9b4']
template_labels = [
    f'{label} ({value})' for label, value in zip(template_counts.index, template_counts.values)
]

plt.figure(figsize=(8, 6))
plt.pie(
    template_counts,
    labels=template_labels,
    autopct='%1.1f%%',
    colors=template_colors,
    startangle=90,
    wedgeprops={'edgecolor': 'black'}
)
plt.title('Breakdown of AI Policy Templates in Use')
plt.axis('equal')
plt.tight_layout()
plt.show()
```

The chart that matters for this notebook — what the adjustment changes:

```python
fig, (left, right) = plt.subplots(1, 2, figsize=(12, 5.5))
for ax, col, title in (
    (left, 'ai_policy_body_changed_original_method', 'Original method\n(vs current template)'),
    (right, 'ai_policy_body_changed', 'Adjusted\n(vs template as published)'),
):
    vc = with_policy_df[col].value_counts().reindex(['Y', 'N']).fillna(0)
    ax.pie(vc,
           labels=[f'Changed ({int(vc["Y"])})', f'Unchanged ({int(vc["N"])})'],
           autopct='%1.1f%%', colors=['#e15759', '#59a14f'],
           startangle=90, wedgeprops={'edgecolor': 'black'})
    ax.set_title(title)
    ax.axis('equal')
plt.suptitle('Did faculty change the template text?')
plt.tight_layout()
plt.show()
```

```python
edit_counts = with_policy_df['ai_policy_edit_class'].value_counts()
plt.figure(figsize=(9, 4.5))
plt.barh(edit_counts.index[::-1], edit_counts.values[::-1], color='#4e79a7', edgecolor='black')
for i, v in enumerate(edit_counts.values[::-1]):
    plt.text(v + max(edit_counts.values) * 0.01, i, str(v), va='center')
plt.title('What the policies actually are')
plt.xlabel('courses')
plt.tight_layout()
plt.show()
```

## What to tell OUE

**How many courses have a policy.** Solid — this comes from the publish date,
which is never overwritten. As of the 2026-09-22 pull, 320 of 1,653 courses
(19%).

**How many faculty changed the wording.** Quote the adjusted figure: **179 of
320, about 56%**. Said plainly: *a bit over half the faculty who published a
policy changed the wording; the rest used a template exactly as given.*

**If someone quotes a higher number from an earlier report, it was wrong.**
The August report said 82% of faculty had edited their policy. The real figure
for that data was 50%. Nothing changed in what faculty did — the old method
compared each policy against whatever the template said *on the day of the
report*, and all three templates were rewritten on 2026-08-28. Every policy
published before that date was counted as edited whether the instructor had
touched it or not. That is the whole reason this notebook exists.

**The yes/no answer is less useful than the breakdown.** "Wrote their own
policy from scratch" and "changed two words" both count as *changed*, and they
are not the same behaviour:

| | 2026-09-22 |
|---|---|
| used the template as given | 141 |
| changed a couple of words | 7 |
| reworded the template | 67 |
| wrote their own policy | 105 |

**Do not compare course-published counts between two pulls.** Term began
2026-09-02, so that number moves as instructors publish their courses. A jump
is the calendar, not a finding.

**Any figure you quote is a snapshot.** Neither source database keeps history,
so this pull cannot be reproduced later by re-running it — only by replaying
the CSVs it was built from. Keep the `data/` folder with the workbook.

## Known defects this notebook works around

Each of these is a reporting workaround for something that should be fixed in the application. They are listed so the workarounds can be deleted when the fixes land.

| # | Defect | Effect on reporting | Fix |
|---|---|---|---|
| 1 | `PolicyTemplates.updated_at` is `auto_now_add` | template edits have no timestamp; Steps 6 and 9 exist to reconstruct them | one word: `auto_now` |
| 2 | No template version history | Step 8 has to reconstruct versions from published policies | `PolicyTemplateVersions` table, and store `published_template_version_id` on each policy |
| 3 | `body_changed` compares a snapshot against live text | the whole reason for this notebook | report against the version as published |
| 4 | Deactivation uses a queryset `.update()`, bypassing `auto_now` | a policy can leave the report with no trace it was ever active | add `updated_at=timezone.now()` |
| 5 | No `updated_by` on either table | no edit is attributable to a person | add the field, and log the action |
| 6 | No unique constraint on one active policy per course | the Step 7 assertion has to guard the join | unique partial index on `(course_id) WHERE is_active = 1` |

Items 2, 3 and 5 are what would make this notebook unnecessary: with versioned templates, the adjusted flag becomes a join rather than a reconstruction.

## Related

- `04-adjusted-report-end-to-end.md` — this same work, fully automated: it fetches
  its own credentials, queries both databases and Splunk directly, and writes the
  workbook. Use that one to *produce* a report; use this one to *review* the
  method, since every query is on the page here.
- `01-policy-report-reproduction.md` — reproduces a past report exactly, and documents what cannot be recovered.
- `02-policy-report-current.md` — current figures using the original, unadjusted method, for continuity with older files.
- `GLOSSARY.md` — every column, state value and term used above.
