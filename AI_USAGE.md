# AI Usage Log

## Tool Used
Claude (Anthropic) — used as an AI pair programmer throughout the project.

---

## How It Was Used

I used Claude as an accelerator, not an author. Every meaningful decision came from understanding the problem and directing the solution. Claude generated code to my specifications — I reviewed, validated, corrected, and shaped everything before committing.

---

## Key Decisions I Made That Claude Did Not Suggest

**1. Splitting `full_name` into `first_name` + `last_name`**
Claude's initial model had a single `full_name` field. I identified that the seed script uses `first_names.txt` and `last_names.txt` as separate files, and the data model should reflect that. I directed the split and `full_name` as a computed `@property`.

**2. HR-only system — removing employee login entirely**
Claude built a full role-based permission system (EMPLOYEE, HR, MANAGER, ADMIN) with employees able to log in and view their own profiles. I recognised this was solving a problem that didn't exist — the user persona is an HR manager, not a self-service employee portal. I made the call to strip it all back to HR-only access.

**3. Removing the `role` field from the Employee model**
After removing employee login, I identified that the `role` field on the Employee model was now redundant. HR identity is handled by Django's auth system (having a User account), not by a field on the data record. Claude hadn't flagged this inconsistency — I caught it during a review pass.

**4. No password required when HR creates an employee**
Claude's initial `perform_create` required a password and created a Django User for every new employee. I questioned this — if employees don't log in, why create User accounts for them? I directed removing `perform_create` entirely so employees are pure data records.

**5. Removing `RegisterSerializer` and `auth_views.py` as dead code**
During the final review I identified that `RegisterSerializer` was still sitting in `serializers.py` from a flow we had removed. Claude hadn't flagged it. I caught it and directed the cleanup.

**6. Choosing same-repo monorepo with Docker Compose**
I made the decision to keep frontend and backend in the same repository and wire them together with Docker Compose so reviewers can run the full stack with one command. This was a deliberate product thinking decision — reducing friction for the person evaluating the submission.

**7. Separating name files into a `data/` directory**
Claude put `first_names.txt` and `last_names.txt` at the project root. I identified this was messy and directed creating a dedicated `data/` directory — a cleaner separation of concerns.

**8. Database architecture — single Employee table**
I initiated the design discussion about whether to use a single table or separate HR/Employee tables. I drove the decision toward a single table after understanding the trade-offs, not because Claude defaulted to it.

**9. Soft delete over hard delete**
I made the conscious decision to implement soft delete (`is_active=False`) because salary history should be preserved for auditing. Claude implemented what I specified.

**10. Questioning `is_admin` boolean**
Claude's first design suggestion used `is_admin=True/False`. I questioned whether a boolean was sufficient and drove the discussion toward a `Role` enum — which I later simplified again when the permission system was removed.

**11. Option A for auth — no public registration**
When given three options for authentication design, I evaluated them and chose Option A: no public registration, HR accounts only via Django admin or management command. This is the right design for an internal HR tool.

**12. Frontend placement — Option B (flat monorepo)**
Given the choice between restructuring Django into a `backend/` folder or keeping it at root and adding `frontend/` alongside, I chose Option B deliberately to avoid risk of breaking existing imports mid-assessment.

---

## Corrections I Made During the Process

**1. Missing `__init__.py` files**
Claude's initial project scaffold omitted `__init__.py` files throughout the package structure. I caught this immediately and asked for them to be added — without them, Python wouldn't treat directories as packages and imports would fail.

**2. Git tracking `__pycache__`**
I noticed `__pycache__` was committed in the first commit. I identified the root cause (files already tracked before `.gitignore` was set up) and the fix: `git rm -r --cached`. I also spotted the bug in the `.gitignore` — a leading `./` that would prevent the pattern from matching subdirectories.

**3. Seed script wrong path depth**
Claude used `Path(__file__).resolve().parents[4]` to find the project root. When I ran the seed script it crashed with `FileNotFoundError` pointing to `/home/anamika/first_names.txt` instead of the project directory. I identified the off-by-one error (`parents[3]` was correct) by counting the directory levels myself.

**4. Docker `create_hr_user` arguments broken**
I ran Docker Compose and observed from the logs that `create_hr_user` was failing with "arguments are required" errors. I traced this to the YAML multiline `>` block folding — the shell was interpreting each argument line as a separate command. I directed fixing it by collapsing to a single line.

**5. Flat frontend structure**
After setting up the frontend, I ran `find . -not -path './node_modules/*' -type f | sort` and identified that all files had been dumped flat in `frontend/` with no `src/` subdirectory structure. I caught that `index.html`, `vite.config.js`, `tailwind.config.js` were all missing, and directed the correct reorganisation.

**6. Vite running on port 5173 instead of 3000**
I noticed the frontend was unreachable and identified from the logs that Vite had fallen back to its default port 5173. I traced this to the `vite.config.js` not being picked up and directed fixing it by passing `--port 3000` explicitly in the Dockerfile CMD.

**7. `ALLOWED_HOSTS` missing `0.0.0.0`**
From the Docker backend logs I spotted `Invalid HTTP_HOST header: '0.0.0.0:8000'`. I understood this was because gunicorn binds to `0.0.0.0` inside the container and directed adding it to `ALLOWED_HOSTS`.

**8. Test fixture pollution skewing aggregation averages**
A test asserting that the average Engineer salary in India was `70,000` was failing with `73,333`. I traced this to the `hr_client` fixture creating an employee with `job_title="Engineer"` (the default in `make_employee`) and `country="India"` — so three engineers were being averaged instead of two. I directed fixing it by giving the HR fixture a distinct `job_title="HR Manager"`.

**9. 404 vs 403 for employee object access**
Tests expected 403 when an employee tried to access another employee's record. I understood that `get_queryset` filtering means the object simply isn't visible — returning 404 is actually more secure (doesn't leak that the record exists). I directed updating the tests to expect 404 and wrote the explanation of why.

**10. Pagination breaking list tests**
Tests were failing with `TypeError: string indices must be integers` because `response.data` was a paginated dict (`{"count": N, "results": [...]}`) rather than a list. I identified the root cause (pagination enabled in settings but not accounted for in tests) and directed the fix via a `conftest.py` autouse fixture.

**11. Role field still present during final review**
After deciding to remove `role`, I caught that `models.py` still had the `Role` TextChoices class. Claude hadn't removed it when implementing the field removal. I caught this during the pre-submission review pass.

**12. `RegisterSerializer` still in `serializers.py`**
After removing the registration flow, `RegisterSerializer` remained as dead code in `serializers.py` along with an unused `User` import. I identified this during the final review and directed the cleanup.

**13. `perform_create` not updated after removing password requirement**
After deciding employees don't need login accounts, `views.py` still had `perform_create` creating Django Users and requiring a password. I identified this inconsistency and directed removing `perform_create` entirely.

---

## What This Demonstrates

Using AI effectively isn't about generating code and committing it. It's about:
- Knowing enough to give precise instructions
- Reviewing output critically rather than blindly accepting it
- Recognising when a generated solution solves the wrong problem
- Catching regressions and inconsistencies across a large codebase
- Making product decisions that AI cannot make (what the system *should* do)
