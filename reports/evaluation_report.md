# Evaluation Report --- Employee Policy & Onboarding Navigator

## 1. Project Overview

**Project:** Employee Policy & Onboarding Navigator\
**Application:** Streamlit chat interface backed by a LangGraph workflow
and a persistent Chroma vector store\
**Evaluation type:** Manual functional testing\
**Policy corpus:** 24 policy files\
**Indexed chunks:** 145\
**Execution environment:** Local development environment (Windows,
Python virtual environment)

## 2. Summary of Results

The developer reports that all 10 planned test scenarios were executed
and passed. Screenshots were supplied for TC01, TC02, TC03, TC05, and
TC07. Results for the remaining scenarios are recorded as passed based
on the developer's confirmation; separate screenshots for those
scenarios were not included with this report update.

  Metric                 Result
  -------------------- --------
  Planned test cases         10
  Passed                     10
  Failed                      0
  Blocked                     0
  Pending                     0
  Pass rate                100%

**Pass rate calculation:** Passed test cases / executed test cases × 100
= 10 / 10 × 100 = 100%.

> These are manual functional-test results for the supplied scenarios,
> not a claim of exhaustive testing, production readiness, or
> independently audited accuracy.

## 3. Test Environment and Preconditions

-   The project's Python virtual environment was activated.
-   The Streamlit application was launched locally at
    `http://localhost:8501`.
-   The persistent vector store loaded successfully.
-   The vector store reported **145 indexed chunks**.
-   The application displayed policy-based answers and supporting source
    references during the observed tests.

## 4. Test Case Results

  ---------------------------------------------------------------------------------------
  ID             Scenario            Expected outcome  Result         Evidence / notes
  -------------- ------------------- ----------------- -------------- -------------------
  TC01           Basic policy        Provide practical **PASS**       Screenshot supplied
                 retrieval ---       guidance grounded                (`TC_01.png`).
                 laptop not          in equipment                     Response advised
                 delivered before    policy and                       contacting manager
                 first day           identify relevant                and IT Support,
                                     sources                          avoiding unapproved
                                                                      personal devices,
                                                                      and checking
                                                                      request status.

  TC02           Broad equipment     Answer from       **PASS**       Screenshot supplied
                 question --- "What  relevant policy                  (`TC_02.png`).
                 equipment should I  evidence and                     Response listed
                 collect?"           identify sources                 laptop, charger,
                                                                      and headset, and
                                                                      explained the
                                                                      approval/review
                                                                      requirement for
                                                                      additional
                                                                      accessories.

  TC03           Multi-topic         Combine relevant  **PASS**       Screenshot supplied
                 question --- remote onboarding,                      (`TC_03.png`).
                 onboarding and      equipment, and                   Response addressed
                 business travel     travel guidance                  equipment/account
                                     with source                      readiness and
                                     references                       onboarding
                                                                      preparation, with
                                                                      multiple policy
                                                                      references.

  TC04           Follow-up history   Use relevant      **PASS**       Developer reported
                 across turns        prior                            that the test
                                     conversation                     passed. No separate
                                     context when                     screenshot was
                                     answering a                      included with this
                                     follow-up                        report update.

  TC05           Missing/uncertain   Avoid inventing   **PASS**       Screenshot supplied
                 policy detail ---   an amount; ask                   (`TC_05.png`). The
                 exact internet      for necessary                    assistant asked for
                 reimbursement       clarification or                 the employee's
                 amount              state that the                   country/location
                                     available                        rather than
                                     evidence is                      inventing a
                                     insufficient                     reimbursement
                                                                      figure. This
                                                                      demonstrates
                                                                      clarification
                                                                      behavior; it does
                                                                      not alone prove the
                                                                      amount is absent
                                                                      from every policy.

  TC06           Policy conflict     Detect            **PASS**       Developer reported
                 handling            conflicting                      that the test
                                     evidence and                     passed. No separate
                                     respond                          screenshot was
                                     cautiously or                    included with this
                                     escalate for                     report update.
                                     human review                     

  TC07           Action boundary --- Explain that the  **PASS**       Screenshot supplied
                 approve a request   assistant cannot                 (`TC_07.png`). The
                 or activate an      perform approvals                assistant
                 account             or account                       explicitly stated
                                     activation and                   it could not
                                     provide                          activate the
                                     appropriate next                 account or approve
                                     steps                            requests and
                                                                      directed the user
                                                                      to the relevant
                                                                      process.

  TC08           Source relevance    Show source       **PASS**       Developer reported
                                     references                       that the test
                                     relevant to the                  passed. No separate
                                     question and                     screenshot was
                                     avoid unsupported                included with this
                                     claims                           report update.

  TC09           Persistent          Load the indexed  **PASS**       The vector store
                 vector-store        policy chunks                    load was observed
                 behavior            again without                    to succeed with 145
                                     requiring a new                  chunks. Developer
                                     indexing run                     reported the full
                                                                      scenario passed.

  TC10           Clear conversation  Clear             **PASS**       Developer reported
                                     visible/session                  that the test
                                     conversation                     passed. No separate
                                     history without                  screenshot was
                                     deleting the                     included with this
                                     persistent policy                report update.
                                     index                            
  ---------------------------------------------------------------------------------------

## 5. Observed Behaviors

### Policy-grounded responses

For the laptop-delivery and equipment-collection scenarios, the
application returned actionable guidance and named the policy
files/sections used as sources.

### Multi-topic retrieval

The remote-onboarding and first-week-travel scenario returned a combined
response covering equipment readiness, onboarding, and travel
preparation.

### Handling missing information

When asked for an exact internet reimbursement amount, the assistant
asked for the employee's country/location instead of providing an
unsupported numeric amount. The clarification is a reasonable first step
if policy applicability varies by region.

### Human/action boundary

For an account-activation request, the assistant explained that it
cannot carry out account activation or approve requests. It directed the
user toward IT Support and the formal request process.

### Persistent index

The local vector store loaded successfully and reported 145 indexed
chunks, confirming that a previously built index was available to the
application.

## 6. Limitations and Follow-up Recommendations

-   Manual tests cover the supplied scenarios only; they do not
    establish complete policy coverage or guarantee that all generated
    statements are correct.
-   Keep screenshots or logs for each scenario, especially follow-up
    history, conflict handling, source relevance, and conversation
    clearing, as supplementary evidence.
-   For policy-conflict testing, retain the exact conflicting source
    excerpts and verify that the assistant identifies the disagreement
    rather than selecting one source without explanation.
-   Review retrieved source excerpts as well as filenames: a displayed
    source is not, by itself, proof that every claim in an answer is
    supported.
-   Re-run the test suite whenever the policy corpus, retrieval
    settings, prompts, or workflow routing changes.

## 7. Final Status

**Status: Manual evaluation reported complete --- 10/10 test cases
passed.**

The application has demonstrated the core behaviors exercised by the
reported tests: policy retrieval, source display, multi-topic responses,
clarification for missing context, a boundary against performing
employee actions, and loading the persistent vector index. The result
should be presented as a successful capstone functional evaluation, not
as proof of exhaustive or production-grade validation.
