# Multi-Agent Implementation Guide
## Practical Steps to Deploy Autonomous Development Agents

This guide shows you **exactly how to set up and use** the multi-agent system described in the Strategic Roadmap.

---

## 🚀 Quick Start (15 Minutes)

### Step 1: Enable Claude Code GitHub Action

The `claude-code.yml` workflow is already configured! You just need to add your API key.

**Add Anthropic API Key:**
1. Go to: https://github.com/agrabowski5/CANOPI_Prototyping/settings/secrets/actions
2. Click "New repository secret"
3. Name: `ANTHROPIC_API_KEY`
4. Value: Your Claude API key from https://console.anthropic.com/
5. Click "Add secret"

**Done!** Now you can trigger agents with `@claude` mentions.

---

### Step 2: Create Your First Agent Task

**Method 1: GitHub Issue (Recommended)**

1. Go to: https://github.com/agrabowski5/CANOPI_Prototyping/issues/new
2. Title: `[Data Agent] Integrate CAISO OASIS API`
3. Body:
   ```markdown
   @claude

   ## Context
   We need real-time electricity price data from CAISO (California ISO).

   ## Task
   Create a data pipeline to fetch hourly LMP (Locational Marginal Pricing) data from the CAISO OASIS API.

   ## Requirements
   - Fetch data for all nodes (500+ locations)
   - Store in PostgreSQL database
   - Handle rate limiting and retries
   - Add data quality checks
   - Write tests

   ## Resources
   - CAISO API docs: http://www.caiso.com/market/Pages/ReportsBulletinsList.aspx
   - Backend code: `/backend/app/data_pipelines/`

   ## Success Criteria
   - API integration working
   - Data stored in database
   - Tests passing
   - Documentation updated
   ```
4. Add labels: `agent:data-pipeline`, `priority:high`
5. Click "Submit new issue"

**What happens next:**
- GitHub Action triggers automatically
- Claude agent reads the issue
- Agent writes code, tests, and documentation
- Agent commits changes to a new branch
- Agent opens a pull request
- Agent comments on the issue with progress
- You review and merge the PR

---

**Method 2: Pull Request Comment**

On any PR, comment:
```markdown
@claude Please add error handling to the API endpoints and write integration tests.
```

The agent will:
- Read the PR changes
- Add error handling
- Write tests
- Push commits to the PR branch

---

**Method 3: Direct Command (In Issue/PR)**

```markdown
@claude /run data-pipeline-agent "Integrate PJM API for real-time pricing"
```

---

## 🤖 Agent Configurations

### 1. Data Pipeline Agent

**GitHub Label:** `agent:data-pipeline`

**System Prompt:**
```markdown
You are the Data Pipeline Agent for CANOPI Energy Planning Platform.

Mission: Build and maintain data infrastructure for grid planning.

Responsibilities:
- Integrate external APIs (CAISO, PJM, ERCOT, NREL, etc.)
- Data quality monitoring and validation
- ETL pipeline development
- Database schema design
- Data documentation

Tech Stack:
- Python (pandas, requests, asyncio)
- PostgreSQL + TimescaleDB
- Apache Airflow (orchestration)
- Redis (caching)

Rules:
- Always validate data quality
- Handle rate limiting gracefully
- Write comprehensive tests
- Document data sources and schemas
- Use async/await for concurrent requests

Current Directory: /backend/app/data_pipelines/
```

**Example Tasks:**
- "Integrate CAISO OASIS API for LMP data"
- "Add data validation for grid topology"
- "Create ETL pipeline for NREL wind data"
- "Optimize database queries for time-series data"

---

### 2. Algorithm Agent

**GitHub Label:** `agent:algorithm`

**System Prompt:**
```markdown
You are the Algorithm Agent for CANOPI Energy Planning Platform.

Mission: Enhance and maintain the CANOPI optimization engine.

Responsibilities:
- Optimization algorithm development
- Performance tuning (solve time, memory)
- New constraint implementation
- Mathematical model validation
- Algorithm documentation

Tech Stack:
- Python (NumPy, SciPy)
- Gurobi optimizer
- NetworkX for graph algorithms
- pytest for testing

Domain Knowledge:
- DC power flow equations
- Unit commitment models
- Transmission expansion planning
- N-1 contingency analysis
- Bundle method optimization

Rules:
- Validate against research paper (arXiv:2510.03484)
- Benchmark performance improvements
- Write mathematical documentation
- Test on multiple network sizes
- Ensure convergence guarantees

Current Directory: /canopi_engine/
```

**Example Tasks:**
- "Optimize bundle method convergence by 2x"
- "Add ramping constraints for generators"
- "Implement energy storage optimization"
- "Add N-1-1 contingency analysis"

---

### 3. Frontend Agent

**GitHub Label:** `agent:frontend`

**System Prompt:**
```markdown
You are the Frontend Agent for CANOPI Energy Planning Platform.

Mission: Build professional-grade UI for energy planners.

Responsibilities:
- React component development
- UI/UX improvements
- Map visualizations (Mapbox GL JS)
- Dashboard and charts (Recharts, D3.js)
- Responsive design
- Accessibility (WCAG 2.1)

Tech Stack:
- React 18 + TypeScript
- Redux Toolkit for state
- Mapbox GL JS for maps
- Recharts for charts
- Tailwind CSS for styling
- Jest + React Testing Library

Design Principles:
- Clean, professional interface
- Mobile-first responsive
- Fast interactions (60 FPS)
- Accessible to all users
- Clear visual hierarchy

Rules:
- Write component tests
- Follow TypeScript strict mode
- Use semantic HTML
- Optimize bundle size
- Document complex components

Current Directory: /frontend/src/
```

**Example Tasks:**
- "Create optimization progress dashboard"
- "Add 3D terrain visualization to map"
- "Build scenario comparison tool"
- "Implement dark mode"

---

### 4. Backend Agent

**GitHub Label:** `agent:backend`

**System Prompt:**
```markdown
You are the Backend Agent for CANOPI Energy Planning Platform.

Mission: Build scalable, reliable APIs and infrastructure.

Responsibilities:
- REST and GraphQL API development
- Database design and optimization
- Caching strategies
- Authentication and authorization
- Background job processing
- API documentation

Tech Stack:
- FastAPI + Python 3.10+
- PostgreSQL + PostGIS + TimescaleDB
- Redis for caching and queues
- Celery for async tasks
- SQLAlchemy ORM
- Alembic for migrations

Rules:
- Follow REST best practices
- Write OpenAPI documentation
- Implement comprehensive error handling
- Add rate limiting for public endpoints
- Write integration tests
- Optimize database queries

Current Directory: /backend/app/
```

**Example Tasks:**
- "Add GraphQL API for project queries"
- "Optimize database indexes for LMP queries"
- "Implement SSO authentication (OAuth 2.0)"
- "Add WebSocket support for real-time updates"

---

### 5. Testing Agent

**GitHub Label:** `agent:testing`

**System Prompt:**
```markdown
You are the Testing Agent for CANOPI Energy Planning Platform.

Mission: Ensure code quality and prevent regressions.

Responsibilities:
- Write unit tests for new code
- Generate integration tests
- Create E2E test scenarios
- Performance testing
- Security vulnerability scanning
- Test coverage monitoring

Tech Stack:
- Frontend: Jest, React Testing Library, Playwright
- Backend: pytest, pytest-asyncio, pytest-cov
- Load testing: Locust
- Security: Snyk, Trivy

Testing Principles:
- Test behavior, not implementation
- Aim for 95% coverage
- Fast tests (< 10 min full suite)
- Clear test names
- Isolated tests (no dependencies)

Rules:
- Run tests locally before committing
- Fix flaky tests immediately
- Update tests when code changes
- Document test scenarios
- Monitor test coverage

Current Directory: /backend/tests/, /frontend/src/**/__tests__/
```

**Example Tasks:**
- "Write tests for new API endpoints"
- "Add E2E test for optimization workflow"
- "Generate load test scenarios (1000 concurrent users)"
- "Scan for security vulnerabilities"

---

### 6. Documentation Agent

**GitHub Label:** `agent:documentation`

**System Prompt:**
```markdown
You are the Documentation Agent for CANOPI Energy Planning Platform.

Mission: Maintain clear, comprehensive documentation.

Responsibilities:
- API reference documentation
- User guides and tutorials
- Architecture documentation
- Code comments and docstrings
- Video scripts
- Release notes

Tech Stack:
- MkDocs Material theme
- OpenAPI spec for API docs
- Mermaid for diagrams
- Jupyter notebooks for tutorials

Documentation Standards:
- Clear, concise language
- Code examples for all APIs
- Screenshots and diagrams
- Step-by-step tutorials
- Search-friendly (SEO)

Rules:
- Update docs with code changes
- Write for beginner audience
- Include troubleshooting sections
- Add links to related docs
- Keep examples up-to-date

Current Directory: /docs/
```

**Example Tasks:**
- "Document new GraphQL API endpoints"
- "Write tutorial: Solar farm siting in 10 minutes"
- "Create architecture diagram for data pipeline"
- "Update API reference after endpoint changes"

---

## 📋 Agent Coordination Workflows

### Workflow 1: New Feature Development

**Example: Add Energy Storage Optimization**

1. **Product Owner creates Epic:**
   ```markdown
   Title: [Epic] Energy Storage Optimization
   Labels: epic, priority:high

   ## Goal
   Enable users to optimize battery storage placement and dispatch.

   ## User Stories
   - As a developer, I want to find optimal battery locations
   - As a planner, I want to model battery dispatch over 24 hours
   - As an analyst, I want to see battery economics (ROI, payback)

   ## Success Criteria
   - Battery placement optimization working
   - Dispatch schedules generated
   - ROI calculator implemented
   - Tests passing
   - Documentation complete
   ```

2. **Break down into agent tasks:**

   **Issue 1:** `[Algorithm Agent] Implement battery optimization model`
   ```markdown
   @claude

   Add energy storage to the CANOPI optimization model.

   Requirements:
   - Storage charging/discharging variables
   - State of charge constraints
   - Power and energy capacity limits
   - Efficiency losses
   - Cycling degradation (optional)

   Location: /canopi_engine/models/storage.py

   Reference: Research papers on storage optimization
   ```

   **Issue 2:** `[Backend Agent] Add storage API endpoints`
   ```markdown
   @claude

   Create REST API endpoints for battery storage.

   Endpoints:
   - POST /api/v1/storage/optimize
   - GET /api/v1/storage/results/{job_id}
   - GET /api/v1/storage/economics

   Location: /backend/app/api/v1/storage.py
   ```

   **Issue 3:** `[Frontend Agent] Build storage dashboard`
   ```markdown
   @claude

   Create UI for battery storage optimization.

   Components:
   - Battery configuration form
   - Dispatch schedule chart (24-hour)
   - Economics summary (ROI, payback period)
   - Map with battery locations

   Location: /frontend/src/components/Storage/
   ```

   **Issue 4:** `[Testing Agent] Write storage tests`
   ```markdown
   @claude

   Create comprehensive tests for storage feature.

   Tests needed:
   - Unit tests: Battery model
   - Integration tests: Storage API
   - E2E test: Full workflow
   - Performance test: 100+ batteries

   Coverage target: 95%
   ```

   **Issue 5:** `[Documentation Agent] Document storage feature`
   ```markdown
   @claude

   Write documentation for energy storage optimization.

   Docs needed:
   - User guide: How to optimize batteries
   - API reference: Storage endpoints
   - Tutorial: Battery placement case study
   - FAQ: Common questions

   Location: /docs/features/storage.md
   ```

3. **Agents work in parallel:**
   - All 5 issues created simultaneously
   - Each agent triggers independently
   - Agents coordinate via API contracts
   - Backend agent waits for algorithm agent (dependency)

4. **Review and merge:**
   - Product owner reviews PRs
   - Merge in order: Algorithm → Backend → Frontend → Tests → Docs
   - Deploy to staging
   - Validate with users
   - Deploy to production

---

### Workflow 2: Bug Fix

**Example: API returning 500 error**

1. **Create issue:**
   ```markdown
   Title: [Bug] API 500 error when querying large networks
   Labels: bug, priority:critical, agent:backend

   @claude

   ## Problem
   GET /api/v1/grid/topology returns 500 error for networks > 10,000 buses.

   ## Error
   ```
   Timeout after 30 seconds
   Database query too slow
   ```

   ## Expected
   Return data in < 5 seconds

   ## Task
   - Identify slow query
   - Optimize database indexes
   - Add pagination
   - Add caching
   - Write regression test

   ## Files
   - /backend/app/api/v1/grid_data.py
   - /backend/app/database.py
   ```

2. **Backend agent automatically:**
   - Reproduces the bug
   - Profiles the database query
   - Adds database indexes
   - Implements pagination
   - Adds Redis caching
   - Writes regression test
   - Opens PR with fix

3. **Testing agent validates:**
   - Runs all tests
   - Verifies fix works
   - Confirms no new issues

4. **Merge and deploy:**
   - Review PR
   - Merge to main
   - Auto-deploy to production
   - Monitor for issues

---

### Workflow 3: Data Pipeline Update

**Example: Daily CAISO data ingestion**

1. **Create scheduled task:**
   ```markdown
   Title: [Data Agent] Daily CAISO LMP data update
   Labels: agent:data-pipeline, automation

   @claude

   ## Task
   Set up automated daily pipeline to fetch CAISO LMP data.

   ## Schedule
   Run daily at 6 AM Pacific (after CAISO publishes data)

   ## Steps
   1. Fetch previous day's LMP data from CAISO OASIS
   2. Validate data quality (no missing values, reasonable ranges)
   3. Load into TimescaleDB
   4. Update aggregation tables
   5. Send alert if any issues

   ## Error Handling
   - Retry failed API calls (3 times)
   - Alert on-call engineer if all retries fail
   - Skip bad data points, don't fail entire pipeline

   ## Files
   - /backend/app/data_pipelines/caiso_lmp.py
   - /backend/airflow_dags/daily_caiso.py

   ## Monitoring
   - Track ingestion time
   - Monitor data quality metrics
   - Alert if data is missing
   ```

2. **Data agent creates:**
   - Airflow DAG for scheduling
   - Python script for data fetching
   - Data quality checks
   - Alert notifications
   - Monitoring dashboard

3. **Deploy and monitor:**
   - Deploy Airflow DAG
   - Monitor first few runs
   - Adjust schedule if needed
   - Set up alerts

---

## 🎛️ Advanced Agent Features

### 1. Multi-Agent Collaboration

**Example: Algorithm agent needs new data**

```markdown
[Algorithm Agent Issue]
Title: Need hourly wind speed data for optimization

@claude

I need hourly wind speed data at turbine hub height (100m) for all wind projects.

@data-pipeline-agent Can you add this data source?

Requirements:
- 100m wind speed
- Historical (2020-2023)
- Forecast (7 days)
- 1 hour resolution
- All project locations
```

**Data agent responds:**
```markdown
@algorithm-agent

I can add NOAA HRRR (High-Resolution Rapid Refresh) data.

API: https://nomads.ncep.noaa.gov/
Resolution: 3km spatial, 1 hour temporal
Height: Interpolate to 100m

ETA: 2 days

Will notify when ready.
```

---

### 2. Agent Self-Improvement

**Example: Agent identifies performance issue**

```markdown
[Algorithm Agent Comment on PR]

I noticed the optimization solve time increased by 20% after this change.

Profiling shows bottleneck in contingency generation.

I can optimize this. Creating issue: #456

@testing-agent Please add performance regression tests.
```

---

### 3. Agent Code Review

**Example: Backend agent reviews frontend PR**

```markdown
[Backend Agent Comment on Frontend PR]

@frontend-agent

I see you're calling GET /api/v1/grid/topology without pagination.

This will timeout for large networks (> 10k buses).

Recommendation:
- Add pagination: /api/v1/grid/topology?page=1&limit=1000
- Or use streaming: /api/v1/grid/topology/stream

I can update the API if needed.
```

---

## 📊 Monitoring Agent Performance

### Metrics Dashboard

Create a dashboard to track:

```yaml
Agent Productivity:
  - Tasks completed per week
  - Average task completion time
  - Code quality (test coverage, linting)
  - PR merge rate

Agent Coordination:
  - Cross-agent collaboration events
  - Blocked tasks waiting on other agents
  - Conflict resolution time

Code Quality:
  - Test coverage (target: 95%)
  - Bug introduction rate
  - Performance regressions
  - Security vulnerabilities

User Impact:
  - Feature adoption rate
  - User satisfaction (NPS)
  - Support ticket reduction
  - Time-to-value improvements
```

**Tools:**
- GitHub Insights for activity
- CodeCov for test coverage
- SonarQube for code quality
- Custom scripts for agent metrics

---

## 🔧 Troubleshooting

### Issue: Agent not responding

**Possible causes:**
1. API key not configured
2. Workflow permissions incorrect
3. Rate limit exceeded

**Solutions:**
1. Check: https://github.com/agrabowski5/CANOPI_Prototyping/settings/secrets/actions
2. Check: https://github.com/agrabowski5/CANOPI_Prototyping/settings/actions (need "Read and write")
3. Check Claude usage: https://console.anthropic.com/

---

### Issue: Agent code doesn't pass tests

**Possible causes:**
1. Agent doesn't understand test requirements
2. Complex task needs human guidance

**Solutions:**
1. Add clearer requirements in issue
2. Provide example test cases
3. Break task into smaller steps

---

### Issue: Agents conflict on same file

**Possible causes:**
1. Two agents editing same code
2. Parallel PRs modifying same file

**Solutions:**
1. Coordinate in GitHub issue comments
2. Merge first PR, then rebase second
3. Human arbitration if needed

---

## 💰 Cost Management

### Estimate Claude API Costs

```yaml
Per Agent Task:
  - Average tokens: 50k-200k (input + output)
  - Cost: $0.50 - $2.00 per task
  - Tasks per agent per day: 2-5
  - Daily cost per agent: $1-10

Monthly Cost (6 agents):
  - Low activity: $200 (2 tasks/agent/day)
  - Medium activity: $1,000 (5 tasks/agent/day)
  - High activity: $2,000 (10 tasks/agent/day)

Cost Optimization:
  - Use caching for repeated prompts
  - Batch similar tasks
  - Use Haiku for simple tasks
  - Use Sonnet for complex tasks
  - Reserve Opus for critical features
```

### Budget Alerts

Set up alerts when:
- Daily spend > $100
- Weekly spend > $500
- Monthly spend > $2,000

**How:**
1. Monitor usage: https://console.anthropic.com/usage
2. Set up billing alerts in Anthropic console
3. Add cost tracking to agent metrics dashboard

---

## 📚 Best Practices

### 1. Clear Task Descriptions

**Good:**
```markdown
@claude

Add CAISO API integration for real-time LMP data.

Requirements:
- Fetch hourly LMP for all 500+ nodes
- Store in TimescaleDB table `caiso_lmp`
- Handle rate limiting (max 10 req/sec)
- Retry failed requests (3 attempts)
- Add data quality checks (range: -$500 to $1000/MWh)

Files:
- /backend/app/data_pipelines/caiso.py
- /backend/tests/test_caiso.py

Success criteria:
- All tests pass
- Documentation updated
- Data flowing to database
```

**Bad:**
```markdown
@claude Fix the CAISO API thing
```

---

### 2. Incremental Tasks

Break large features into small tasks (< 1 day each):

**Good:**
```markdown
[Issue 1] Add database schema for storage
[Issue 2] Implement storage optimization model
[Issue 3] Add storage API endpoints
[Issue 4] Create storage UI components
[Issue 5] Write tests for storage
[Issue 6] Document storage feature
```

**Bad:**
```markdown
[Issue 1] Add complete energy storage feature
```

---

### 3. Provide Context

Include relevant context:
- Link to related issues/PRs
- Reference documentation
- Example code
- Research papers
- Industry standards

---

### 4. Review Agent Work

Always review PR before merging:
- Run tests locally
- Check code quality
- Verify requirements met
- Test manually

---

## 🎯 Next Steps

### This Week

1. **Add Anthropic API key** to GitHub secrets
2. **Test agent** with simple issue
   - Create test issue: "Add docstring to main.py"
   - Tag with `@claude`
   - Verify agent responds

3. **Create first real task**
   - Choose from roadmap (e.g., "Integrate CAISO API")
   - Write detailed issue
   - Let agent work
   - Review and merge

### This Month

1. **Set up all 6 agents** with custom prompts
2. **Create first sprint backlog** (10-15 issues)
3. **Run first sprint** (2 weeks)
4. **Review progress** and adjust

### This Quarter

1. **Complete Phase 1** of roadmap (Data Foundation)
2. **Onboard 10 beta users**
3. **Collect feedback** and iterate
4. **Plan Phase 2**

---

## 📞 Support

**Questions about multi-agent setup?**
- GitHub Discussions: https://github.com/agrabowski5/CANOPI_Prototyping/discussions
- Email: support@canopi.energy (when available)

**Report agent issues:**
- GitHub Issue with label `agent-system`
- Include: Task description, agent response, expected behavior

---

**You're ready to start!** 🚀

Create your first agent task now:
👉 https://github.com/agrabowski5/CANOPI_Prototyping/issues/new

---

**Last Updated:** January 13, 2026
