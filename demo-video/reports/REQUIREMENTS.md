# Official hackathon requirements for the Barakah demo

Verified live on **2026-11-15**, approximately **11:21 UTC**. Read-only research: no repository edits, application runs, inference runs, staging, or delegation. Only this requested external report was written.

## Sources and retrieval

All four requested official pages returned HTTP 200, with unchanged final URLs:

- **S1:** https://highschoolhackathon.org/briefs — Project briefs and submission.
- **S2:** https://highschoolhackathon.org/faq — FAQ.
- **S3:** https://highschoolhackathon.org/judges — Judging Criteria.
- **S4:** https://highschoolhackathon.org/about — About and timeline.
- **S5:** https://drive.google.com/file/d/15tYD48XRmCgWbk1_lLDtc8lebi6qm-4-/view?usp=sharing — **Veritas AI International High School Hackathon 2026 Project Briefs.pdf**, directly linked by S1 as “Open the project briefs (PDF)”; Google Drive viewer returned HTTP 200. This is one 22-page document covering all tracks, not a separate Finance-only file. Finance is **§4.2, printed pages 8–11**.
- **S5 download:** https://drive.usercontent.google.com/uc?id=15tYD48XRmCgWbk1_lLDtc8lebi6qm-4-&export=download — download URL exposed by the official-linked Drive viewer. Successfully retrieved and extracted all 22 pages with macOS PDFKit. PDF quotations below normalize line wrapping/apostrophe spacing introduced by extraction.
- **Submission form linked by S1:** https://airtable.com/appypCyHN77hElIcS/shrXA5VBFdugmoXl6 — link verified in S1; **form contents not fetched or submitted**.

Research used live sources, not Hindsight or assumptions about Barakah. Static page HTML contains multiple time-phase announcement banners; hidden alternative banners were not treated as current submission status.

## 1. Deadline, build window, eligibility, duration

**Submission deadline: Sunday, November 15, 2026, 11:59 PM Eastern Time.**

S1, opening paragraph:
> Read your track's brief, build your project, and submit it by 11:59 PM ET on Sunday, November 15, 2026. One person submits for the whole team.

**Build window: Saturday November 14, 12:00 AM ET through Sunday November 15, 11:59 PM ET; described as 48 hours.** This is not permission to extend a pre-existing project.

S1, “What your team confirms”:
> All the work was done between 12:00 AM ET on November 14 and 11:59 PM ET on November 15, and doesn't extend a project you built before the hackathon.

S4, ground rules:
> All project code has to be written during the 48 hours. You can learn, practice and form your team beforehand.

S2, late submissions:
> Deadlines are firm, and late submissions aren't accepted. We strongly recommend submitting at least an hour early. We can't make exceptions for technical issues in the final minutes.

S5 p.22, work after deadline:
> Yes, but judges only see what you submitted before 11:59 PM ET on Sunday, November 15.

S1 permits repeated submissions before the deadline, judging the latest version. Its submission-error instruction is to email **contact@veritasai.com** immediately with code and write-up links; this is **not an explicit deadline extension**.

S2 eligibility:
> Any student enrolled in high school as of November 14, 2026, anywhere in the world. There are no grade, country or experience restrictions.

S4 team rule:
> Teams can have 1 to 3 members, from any school and any country.

S1 also requires everyone listed to have contributed. S4 lists registration closing November 13, 2026 at 11:59 PM ET. S5 p.22 says no kickoff call or check-in is required during the build weekend.

### Two different demo durations

- **Submission video: up to 2 minutes, optional but recommended.** S1: “Optional, but recommended. Up to 2 minutes, on YouTube as unlisted or shared from Google Drive with ‘anyone with the link can view’.”
- **Finalist live demo: 5 minutes, followed by questions.** S4: “Finalists present live on a public livestream: a 5-minute demo followed by questions from the judging panel of researchers and engineers from the world's leading AI labs.”
- S5 p.20 states the finals ceremony is **Saturday November 21 at 11:00 AM ET**; S4 dates it to 2026. Finalists/shortlisted students are emailed November 18 (S5 p.20). S4 gives Round 1 review as November 16–18, 2026.

S5 p.19 suggests, rather than mandates, a 2-minute video allocation: problem ~15 seconds, real-input demo ~60 seconds, how it works ~30 seconds, limitation/next steps ~15 seconds. It says:
> A screen recording with your voice over it is plenty. You don't need to edit it.

## 2. Submission contents and accessibility

S1, “What to submit,” requires:

- Code link: “A Google Colab notebook or GitHub repository that anyone with the link can view.”
- Write-up: “A Google Doc set to ‘anyone with the link can view’, your GitHub README, or an uploaded PDF or Word file. Only one of these.”
- One track: Health, Finance, Climate, or Languages.
- Every team member's full name, email, and school.
- Credits: “Every dataset, pretrained model, tutorial and AI tool you used, with links.”
- Optional recommended video as above.

S4 specifies working code that organizers can “open and run” and “A one-page write-up on the problem, your approach, and how well it worked.” S5 p.18 says “About one page” and “Save your notebook with its outputs visible.”

S1 pre-submit check:
> Open every link in a private or incognito window to make sure it works without signing in.

S5 p.19's write-up template asks for problem/user, what was built, own contribution, data size/cleaning, model and rationale, baseline/model held-out results, failure and explanation, next steps, and linked sources.

## 3. Blind judging and rubric

S3:
> Every Round 1 submission is reviewed blind by the Veritas AI team. The top projects advance to the live finals, where a new panel scores them. Final rankings combine the Finals (70%) and Round 1 (30%) scores.

S3:
> Your name and school are kept confidential throughout Round 1.

S4:
> Reviewers don't see your name or school.

**Do not infer a blanket ban on identifying information in submitted artifacts.** S1 explicitly requires team identities, and S5 p.19's template includes “Team: names.” The sources promise organizer-side blind Round 1 review, but do not explain anonymization mechanics or explicitly require anonymous video/code. The public live finals are not described as blind.

### Published numerical rubric (S3)

| Round 1 criterion — exact wording | Points |
|---|---:|
| Technical execution: does it work, and is it well built? | 30 |
| Originality: is this a fresh take on the problem? | 20 |
| Impact and track fit: does it solve a real problem in the track? | 20 |
| Testing and honesty: did you measure how well it works, and do you know where it fails? | 15 |
| Communication: are the write-up and video clear? | 15 |
| **Total** | **100** |

| Finals criterion — exact wording | Points |
|---|---:|
| Demo and clarity | 30 |
| Technical depth | 30 |
| Impact | 20 |
| Q&A | 20 |
| **Total** | **100** |

**Source difference:** S5 p.20 uses four qualitative headings—“Technical quality,” “Impact,” “Creativity,” “Clarity”—without numerical weights. S5 p.21 also refers to the “same four criteria.” That is not identical to S3's five-category Round 1 scoring table. Preserve this distinction; do not invent a four-way numerical allocation or claim the documents publish identical rubrics.

S5 p.20:
> If your results look too good to be true, test data has usually leaked into training. Judges score an honest, modest result higher than an unexplained high one.

## 4. AI, data, attribution, and honest-result limitations

### AI must perform the core task; AI-assisted coding alone is insufficient

S1:
> AI or machine learning does the main job in your project.

S5 p.3:
> Your project needs to use AI or machine learning to do its main job. If you build a regular website or app with AI coding tools, that doesn't count on its own.

### Existing models/APIs and coding assistants are allowed, with credits and understanding

S5 p.3:
> You can use public datasets, pretrained models, AI APIs (such as the free tier of the Gemini API), open-source libraries, tutorial code, and coding assistants or chatbots. Just cite all of them in your write-up. Your team should understand every part of the project and be ready to explain it to the judges.

S5 p.21, whether teams must train their own model:
> No. You can use pretrained models and AI APIs. Judges focus on what you build around them: your data, how you tested it and who it's for.

S2 permits ChatGPT/Claude “to debug, explain concepts or speed up routine code,” but requires understanding/explanation and notes finalists will be questioned live. S1 requires links crediting every dataset, pretrained model, tutorial and AI tool. S5 p.21 additionally says to list every AI tool in the write-up **and on the form**.

### Data restrictions and licensing

S1:
> You used only public or synthetic data, and didn't collect anyone's personal information without permission.

S5 p.3:
> Please don't collect anyone's personal information without their permission, and stick to public or synthetic data.

S5 p.21:
> You can use any public dataset. Just check its licence and cite it with a link.

**Nuance:** S5 p.4 also suggests “data you collected with permission” as an originality option. That does not clearly waive the explicit public-or-synthetic submission confirmation. For Barakah, public/synthetic demo and evaluation inputs are the straightforward compliant choice; do not treat permission alone as proven authorization to submit private financial records. No repository or actual data was inspected in this research.

### Report genuine held-out results, baseline, and a failure

S1:
> The results you report are the ones you actually got.

S5 p.3:
> Report the results you actually got, including weak ones.

S5 p.4:
> Report your baseline's score next to your model's score, so judges can see how much your model actually adds.

> Show at least one example your model gets wrong and explain why you think that happens.

> Make sure all your results come from test data your model didn't see during training.

S5 p.21 states **no minimum accuracy**. Therefore the Finance challenge's ambition to beat a simple rule is not permission to fabricate an improvement or suppress a weak result.

## 5. Finance-specific requirements and limitations

**Official Finance brief:** S5, §4.2, pp.8–11, exact viewer URL above.

### Core challenge and required evidence (p.8)

> Build an AI tool that helps a person or a small business make a safer or fairer money decision, and show that it beats a simple rule.

> In this track, your project should protect the person whose money is at stake.

“What your project needs”:

> Compare your model with at least one simple baseline and report both results.

> Choose a measure that fits the problem. For rare events such as fraud, report precision and recall rather than accuracy.

> If your data has dates, train on earlier data and test on later data.

> Include this line in your write-up: “This project is a prototype and is not financial advice.”

The disclaimer is explicitly required in the **write-up**. Showing it in the demo UI is a reasonable additional precaution, not an independently stated screen-overlay requirement in these sources.

### Permitted own ideas (p.10)

> You can build any project that meets the challenge. For example, you could build a budgeting assistant for teenagers with their first debit card, an inflation tracker for your city, or a tool that explains bank fees in plain language.

The four provided examples are scam text filtering, card fraud detection, a loan-model fairness audit, and news/stock-market prediction. They are **optional starting points**, not the only permitted Finance products.

### Credit/loan and investment-related examples—not categorical prohibitions

S5 p.9, loan model:
> Build a model that classifies loan applicants as good or bad credit risks, then test whether it treats groups of applicants differently.

> Report accuracy, the approval rate for each group, and the gap between them.

S5 p.10 suggests finding proxy features for protected/personal characteristics, testing a gap-reducing change and its accuracy cost, and comparing assumptions to local lending. It states the example dataset treats approving a bad risk as five times as costly as rejecting a good one; this is **dataset-specific example guidance**, not a competition-wide credit-cost mandate.

S5 p.10, stock example:
> Split by date, never at random. Train on 2008 to 2014 and test on 2015 to 2016.

> Say clearly what your results would and wouldn't justify an investor doing. If your results look far better than the baselines, first check that no later dates leaked into training.

These example-specific dates are not a universal Finance split requirement. The general chronological split rule still applies when data has dates.

S5 p.11, Finance judging emphasis:
> In this track, judges pay extra attention to whether you chose the right measure of success, whether you compared your model fairly against a simple baseline, and whether a real person could trust your tool enough to act on it. Teams that check for unfair treatment of a group, even when age or gender isn't a direct input, really stand out.

**No blanket ban on credit-risk or stock-related prototypes was found.** They appear explicitly as suggested projects. This is not permission to give real regulated financial advice, move money, use private financial records, or claim production readiness. The verified requirements are prototype labeling, no-financial-advice disclaimer, data constraints, fairness/appropriate testing, and honest results.

## 6. What this establishes for a Barakah demo—and what remains unverified

Source-grounded checklist, not a repository compliance assessment:

1. Make the specific Finance user and safer/fairer money decision explicit.
2. Show a real input producing an AI-powered result; a polished app created with AI tools alone is insufficient.
3. Show actual model-versus-simple-rule results on held-out inputs, with task-appropriate measures, plus a concrete failure and limitation.
4. Use public/synthetic data and link all dataset/model/tutorial/AI-tool credits.
5. Put the exact Finance prototype disclaimer in the write-up.
6. Keep the submission video within 2 minutes; do not confuse it with the 5-minute finalist demo.
7. Submit accessible code and write-up before the stated ET deadline, with truthful team/work-window confirmations.

**Unverified assertions:** The supplied research task contains no concrete user claims about Barakah's implementation, model performance, ownership, data provenance, code timing, or eligibility. None of those were verified. In particular, this research does not establish that Barakah was built only during the permitted window, that its evaluations beat a baseline, that its inputs are public/synthetic, or that any pre-existing work is eligible. Claims that AI-assisted coding is prohibited, training a model is mandatory, a video is mandatory, a 5-minute submission video is allowed, or all credit models are banned are **not supported** by the retrieved rules.

## 7. Validation and residual limitations

- Retrieved the four official pages with `curl -L -sS --max-time 30`; HTTP 200 for each.
- Read S1's actual linked PDF URL and retrieved its Drive viewer successfully.
- A redundant Python `urllib.request` fetch of S1 returned HTTP 403. This did not block research because the prior curl response contained the complete page and HTTP 200.
- `pdftotext` was not installed; the attempted pipeline failed. Used the locally available Swift/Foundation/PDFKit reader instead, successfully extracting **22 pages**, including all Finance requirements and general submission rules. No dependency installation was performed.
- `git -C /Users/hadi/Documents/Barakah diff --cached --name-only` returned no paths: **no staged files** at verification.
- No application/tests/inference were run; no repository files were changed. No unresolved source-access blocker remained.
- Remaining source ambiguities: website numerical rubric versus PDF qualitative rubric; public/synthetic confirmation versus permission-collected-data suggestion; organizer anonymization mechanics. The report exposes these instead of silently resolving them.
- Recommended next step: use this checklist to review the proposed demo/write-up and truthful provenance; consult `contact@veritasai.com` only if a material eligibility/data ambiguity must be resolved. Do not represent this research as approval of Barakah's compliance.
