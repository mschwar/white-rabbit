# White Rabbit — User Guide

A friendly, plain-English walkthrough for operators. No coding required.

White Rabbit helps you turn a sentence like *"K-12 IT directors in Albuquerque"* into a ranked list of real people you could contact, with reasons for each rank.

---

## 1. Logging in

1. Open White Rabbit in your browser.
2. You'll see a **Login** page asking for the shared password.
3. Type the password and press **Enter**.
4. You'll land on the home screen, with links to **Scout / Full**, **Recipes**, and **Batch**.

If you forget the password, ask Matt — there's only one and we all share it.

To **sign out**, click the logout link in the header. You'll have to enter the password again next time.

---

## 2. The big picture in 60 seconds

White Rabbit has three main pages:

| Page | What it's for | When to use it |
|------|---------------|----------------|
| **Scout / Full** | Search for leads from one query | Most of your day |
| **Recipes** | See saved searches and how well they did | Friday reviews, refining queries |
| **Batch** | Run several queries at once | When you have a list of cities, verticals, etc. |

Two ideas to remember:

- **A query** is one sentence describing who you want to find.
- **A recipe** is a query you've decided is worth keeping. Recipes get saved, scored, and reused.

---

## 3. Your first search (Scout vs Full)

Open the **Scout / Full** page. At the top you'll see two buttons:

### Scout — quick, cheap preview
- Returns roughly **10–20 leads**.
- Doesn't save anything.
- Use it to **try out a query** before committing to a full run.

### Full — the real thing
- Returns up to **100 leads**.
- **Saves** the recipe and the run, so you can come back to it later.
- Asks you to give the recipe a name (e.g. *"K-12 IT directors – NM"*).

### How to run a search

1. Pick **Scout** or **Full**.
2. (Full only) Type a **Recipe name** — a short label you'll recognize later.
3. In **Prospecting query**, describe who you want to find in one sentence:
   - Good: *"Heads of marketing at DTC skincare brands with 20–100 employees"*
   - Bad: *"marketing people"* (too vague — White Rabbit will warn you)
4. In **Location / filter**, narrow it down (e.g. *"New Mexico"*, *"USA"*, or a city).
5. Click **Run Scout search** or **Run Full search**.
6. Wait ~10–30 seconds. Leads appear below.

### What if my query is too vague?

White Rabbit has a built-in coach. If your query is missing key info (a role, a vertical, a region), you'll see a **yellow** or **red** banner suggesting what to add. Take its advice — vague queries waste your sandbox quota.

---

## 4. Reading a lead card

Each result is a card that looks roughly like this:

> **Rank 1 · gate passed**
> **Jane Doe**
> IT Director · Albuquerque Public Schools
> Found: jane.doe@aps.edu
>
> | Fit | Evidence | Contact |
> |-----|----------|---------|
> | 0.91 | 0.87 | 0.95 |
>
> *Ranked because the title matched an IT decision-maker, the organization matched a K-12 district, source came from the district website, and the email was deduced from a known pattern.*
>
> [usable] [wrong persona] [bad source] [bad contact] [duplicate] · View source

### What the three scores mean

These are the heart of White Rabbit. Every lead gets all three:

- **Fit** — How well does this person match who you asked for? (Right title, right kind of organization, right level.)
- **Evidence** — How trustworthy and recent are the sources we found this person in?
- **Contact** — How usable is the email/phone/title? An email we found on a public page beats one we deduced from a pattern.

Each score runs from **0.00 (bad)** to **1.00 (great)**.

### Why three scores instead of one?

A single number hides what's wrong. With three, you can spot patterns: *"Fit is high but Contact is low — I need to find their email another way."* Don't trust any tool that gives you one mystery score.

### "Gate passed" vs "review"

A lead **passes the gate** when **all three scores are at least 0.6**. Gate-passed leads are the ones you should actually look at. The rest are shown for context but flagged as "review."

### The explanation line

Every card has one sentence telling you *why* this lead was ranked the way it was. Read it. If the explanation doesn't match what you wanted, the recipe needs tuning.

---

## 5. Sorting and reviewing the list

Above the list of cards, there's a **Sort leads** dropdown. You can sort by:

- **Original rank** (default — the system's best overall guess)
- **Fit** — when ICP match is what matters most today
- **Evidence** — when you want only the most well-documented leads
- **Contact** — when you need usable emails right now
- **Gate** — pass/fail status

Sort however helps you triage faster.

---

## 6. Giving feedback (the buttons under each lead)

This is the most important habit in White Rabbit. Click one button per lead:

| Button | When to click |
|--------|---------------|
| **usable** | You'd actually reach out to this person. |
| **wrong persona** | Wrong title, wrong seniority, wrong job. |
| **bad source** | The source URL is broken, outdated, or the wrong organization. |
| **bad contact** | Email or phone is wrong, missing, or unverifiable. |
| **duplicate** | Already in your CRM or pipeline. |

Why bother? Two reasons:

1. The **scoreboard** for each recipe (next section) uses these to tell you which recipes actually produce usable leads.
2. The **Friday review** uses these to decide which recipes to keep, kill, or tweak.

If you skip feedback, you can't measure anything.

---

## 7. Closing out a Full run

After a Full run, you'll see a green box at the top with:

- The **Recipe ID** and **Run ID** (for reference).
- An **Operator minutes** box.
- A **Close run** button.
- A **Build lead export** button.

### Operator minutes

Type how many minutes **you** spent reviewing the leads (e.g., `18.5`). Then click **Close run**. This is what powers our headline KPI: *minutes per usable lead*.

### Lead export (CSV)

Click **Build lead export**, then **Download CSV**. You'll get a spreadsheet with every lead, all three scores, gate status, the explanation, and the source. Drop it into your CRM, share it with a customer, or open it in Excel/Google Sheets.

---

## 8. The Recipe library

Click **Recipes** in the header. This page is your history.

### What you'll see

- **Saved recipes** on the left — every recipe you've named with a Full run.
- A **Scoreboard** on the right when you click a recipe, with:
  - **Leads returned** — total across all runs.
  - **Usable leads** — how many you marked as `usable`.
  - **API cost spent** — the dollar number.
  - **Operator minutes** — how long you've spent reviewing.
  - **Minutes / usable lead** — the headline number. Lower is better.
  - **API cost / usable lead** — secondary economics.
  - **Feedback breakdown** — counts by label.
- **Runs** — each individual run, when it happened, how many leads, how many minutes.

### Friday recipe review export

Each Friday, the team meets for 30 minutes to talk through the week's recipes. To prep:

1. Open the **Recipes** page.
2. Click a recipe.
3. Scroll to **Friday recipe review export**.
4. Click **Generate export**. You get:
   - A **CSV** to share or print.
   - A **printable markdown preview** for the meeting.

Bring this to the meeting. Decide for each recipe: **keep, tune, or kill.**

---

## 9. Batch — running many queries at once

Open the **Batch** page when you have a list of related queries (e.g., the same role across 10 cities, or 8 verticals in one region).

### How to set up a batch

1. Give it a **batch label** (e.g., *"Monday prospecting sweep"*).
2. Add queries one at a time, each with its own **Query** and **Location**. You can also paste queries in.
3. Click the run button.
4. Watch the result card and run summaries fill in as queries complete.

A batch is just a tidy way to launch many Full runs together. Each query becomes its own saved recipe and run, visible in the Recipe library afterwards.

---

## 10. Sandbox quota — the friendly speed limit

On the right of the Scout / Full page you'll see a green **Sandbox quota** card:

- **Queries** used vs. allowed (e.g. `3 / 10 used`).
- **Rows** used vs. allowed (e.g. `120 / 1000 used`).
- A **reset time**.
- A **Reset sandbox** button.

### Why this exists

To keep API costs predictable. The sandbox caps how many searches and how many lead rows we'll generate before forcing a pause.

### What to do when you hit it

Either:
- **Wait** for the auto-reset time, or
- Click **Reset sandbox** if you genuinely need to keep going.

If you're hitting it constantly, your queries may be too broad — tighten them up.

---

## 11. Tips for getting better leads

- **Be specific about role.** "VP of Engineering" beats "engineering leader."
- **Be specific about company type.** "Series A SaaS in fintech" beats "tech startups."
- **Add geographic detail.** "Austin TX" or "USA West Coast," not just "anywhere."
- **Run a Scout first.** It's the cheapest way to find out your query is wrong.
- **Read the explanation line.** If it says *"matched on title and region but no organization match,"* that tells you exactly what to tighten.
- **Click feedback buttons.** Always. Even on bad leads — especially on bad leads.

---

## 12. When something looks broken

| Symptom | Try |
|---------|-----|
| Login keeps rejecting the password | Confirm with Matt that the password hasn't rotated. |
| "Search failed" red banner | Wait 30 seconds and re-run. If it persists, screenshot it for Matt. |
| Sandbox quota seems wrong | Click **Reset sandbox**. If that doesn't help, flag it. |
| Feedback buttons don't seem to do anything | Make sure you ran a **Full** search, not Scout. Scout doesn't save lead IDs. |
| Lead emails look wrong | Mark **bad contact**. The recipe's Contact score weights will adjust over time. |
| A whole batch looks low quality | Don't scroll past it — kill the recipe at Friday review and rebuild. |

---

## 13. Glossary (one-liners)

- **Query** — your sentence describing who you want to find.
- **Recipe** — a saved query, ready to re-run.
- **Run** — one execution of a recipe.
- **Scout run** — quick, cheap, no save, ~10–20 leads.
- **Full run** — full effort, saved, up to 100 leads.
- **Batch** — many queries launched together.
- **Fit / Evidence / Contact** — the three scores on every lead.
- **Gate** — a lead passes when all three scores are ≥ 0.60.
- **Sandbox** — the running quota of queries and rows you're allowed.
- **Operator minutes** — how long you spent reviewing a run.
- **Minutes per usable lead** — the headline KPI; lower is better.

---

That's it. The whole tool boils down to: *write a clear query, run Scout, run Full, click feedback, log your minutes, and review on Friday.* Everything else is just polish on top of that loop.
