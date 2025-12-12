#!/bin/bash
# Add more sample artifacts for Librarian page testing
# Usage: ./add_more_demo_artifacts.sh

mkdir -p demo_data/artifacts/{implementation_plans,assessments,audits,bug_reports,design_documents}

echo "Adding more sample artifacts..."

# Additional Implementation Plans
cat > demo_data/artifacts/implementation_plans/2025-12-02_0900_plan-user-authentication.md << 'EOF'
---
title: "Implementation Plan: User Authentication System"
type: implementation_plan
status: active
created: 2025-12-02 09:00 (KST)
phase: 1
priority: high
tags: [authentication, security, user-management]
---

# Implementation Plan: User Authentication System

## Objective
Implement secure user authentication with OAuth2 and JWT tokens.

## Tasks
- [x] Design authentication flow
- [x] Set up OAuth2 provider
- [ ] Implement JWT token generation
- [ ] Add password reset functionality
- [ ] Write integration tests

## Timeline
- Week 1: OAuth2 setup
- Week 2: JWT implementation
- Week 3: Testing and security audit

## Success Metrics
- Support for Google, GitHub OAuth
- Token refresh mechanism
- 99.9% uptime
EOF

cat > demo_data/artifacts/implementation_plans/2025-12-02_1400_plan-database-migration.md << 'EOF'
---
title: "Implementation Plan: Database Migration to PostgreSQL"
type: implementation_plan
status: completed
created: 2025-12-02 14:00 (KST)
phase: 3
priority: medium
tags: [database, migration, postgresql]
---

# Implementation Plan: Database Migration to PostgreSQL

## Objective
Migrate from SQLite to PostgreSQL for better scalability.

## Tasks
- [x] Set up PostgreSQL instance
- [x] Create migration scripts
- [x] Test data migration
- [x] Update application code
- [x] Deploy to production

## Timeline
- Week 1: Setup and planning
- Week 2: Migration scripts
- Week 3: Testing
- Week 4: Production deployment

## Success Metrics
- Zero data loss
- < 1 hour downtime
- Performance improvement > 20%
EOF

cat > demo_data/artifacts/implementation_plans/2025-12-03_1000_plan-api-rate-limiting.md << 'EOF'
---
title: "Implementation Plan: API Rate Limiting"
type: implementation_plan
status: draft
created: 2025-12-03 10:00 (KST)
phase: 1
priority: medium
tags: [api, rate-limiting, security]
---

# Implementation Plan: API Rate Limiting

## Objective
Implement rate limiting to prevent API abuse and ensure fair usage.

## Tasks
- [ ] Research rate limiting strategies
- [ ] Choose implementation (Redis-based)
- [ ] Implement middleware
- [ ] Configure limits per endpoint
- [ ] Add monitoring

## Timeline
- Week 1: Research and design
- Week 2: Implementation
- Week 3: Testing and tuning

## Success Metrics
- 100 requests/minute per IP
- 1000 requests/hour per API key
- < 5ms overhead per request
EOF

# Additional Assessments
cat > demo_data/artifacts/assessments/2025-12-02_1100_assessment-security-audit.md << 'EOF'
---
title: "Assessment: Security Audit Results"
type: assessment
status: complete
created: 2025-12-02 11:00 (KST)
category: security
tags: [assessment, security, audit]
---

# Assessment: Security Audit Results

## Summary
Comprehensive security audit of the application infrastructure and codebase.

## Findings
- ✅ Authentication: Secure (OAuth2 + JWT)
- ⚠️ API endpoints: Missing rate limiting
- ✅ Data encryption: Properly implemented
- ⚠️ Logging: Sensitive data in logs (needs sanitization)

## Recommendations
1. Implement API rate limiting
2. Sanitize logs to remove sensitive data
3. Add security headers (CSP, HSTS)
4. Regular dependency updates

## Risk Level
Medium - No critical vulnerabilities found
EOF

cat > demo_data/artifacts/assessments/2025-12-03_0900_assessment-performance-bottlenecks.md << 'EOF'
---
title: "Assessment: Performance Bottleneck Analysis"
type: assessment
status: active
created: 2025-12-03 09:00 (KST)
category: performance
tags: [assessment, performance, optimization]
---

# Assessment: Performance Bottleneck Analysis

## Summary
Identified performance bottlenecks in the API response times.

## Findings
- Database queries: 45% of response time
- External API calls: 30% of response time
- Serialization: 15% of response time
- Other: 10% of response time

## Recommendations
1. Add database query caching (Redis)
2. Implement connection pooling
3. Add request batching for external APIs
4. Optimize JSON serialization

## Expected Impact
- 50% reduction in average response time
- Support 2x more concurrent users
EOF

# Additional Audits
cat > demo_data/artifacts/audits/2025-12-02_1300_audit-dependency-vulnerabilities.md << 'EOF'
---
title: "Audit: Dependency Vulnerability Scan"
type: audit
status: active
created: 2025-12-02 13:00 (KST)
tags: [audit, security, dependencies]
---

# Audit: Dependency Vulnerability Scan

## Scope
Scan all npm and pip dependencies for known vulnerabilities.

## Findings
- ✅ Critical: 0 vulnerabilities
- ⚠️ High: 2 vulnerabilities (in dev dependencies)
- ⚠️ Medium: 5 vulnerabilities
- ✅ Low: 12 vulnerabilities

## Action Items
- [ ] Update `lodash` to latest version (high)
- [ ] Update `axios` to latest version (high)
- [ ] Review medium severity issues
- [ ] Set up automated dependency scanning

## Next Steps
- Schedule monthly dependency audits
- Integrate Dependabot for automated PRs
EOF

cat > demo_data/artifacts/audits/2025-12-03_1100_audit-code-coverage.md << 'EOF'
---
title: "Audit: Code Coverage Analysis"
type: audit
status: completed
created: 2025-12-03 11:00 (KST)
tags: [audit, testing, coverage]
---

# Audit: Code Coverage Analysis

## Scope
Review test coverage across frontend and backend codebases.

## Findings
- Backend coverage: 87% (target: 90%)
- Frontend coverage: 72% (target: 80%)
- Critical paths: 95% coverage
- Edge cases: 65% coverage

## Action Items
- [x] Increase backend coverage to 90%
- [ ] Add frontend component tests
- [ ] Improve edge case coverage
- [ ] Set up coverage gates in CI

## Status
Backend target achieved. Frontend needs improvement.
EOF

# Additional Bug Reports
cat > demo_data/artifacts/bug_reports/2025-12-02_1500_BUG_002_memory-leak.md << 'EOF'
---
title: "BUG-002: Memory Leak in Event Handlers"
type: bug_report
status: resolved
created: 2025-12-02 15:00 (KST)
updated: 2025-12-02 18:00 (KST)
severity: high
tags: [bug, memory-leak, frontend]
---

# BUG-002: Memory Leak in Event Handlers

## Description
Memory usage increases over time when using the dashboard, eventually causing browser slowdown.

## Steps to Reproduce
1. Open dashboard
2. Navigate between pages repeatedly
3. Monitor memory usage (Chrome DevTools)
4. Memory continues to grow

## Root Cause
Event listeners not removed when components unmount.

## Fix
Added cleanup in `useEffect` hooks to remove event listeners.

## Status
✅ Resolved in commit `b2c3d4e`
EOF

cat > demo_data/artifacts/bug_reports/2025-12-03_0800_BUG_003_api-timeout.md << 'EOF'
---
title: "BUG-003: API Timeout on Large Responses"
type: bug_report
status: active
created: 2025-12-03 08:00 (KST)
severity: medium
tags: [bug, api, performance]
---

# BUG-003: API Timeout on Large Responses

## Description
API requests timeout when fetching large artifact lists (>100 items).

## Steps to Reproduce
1. Request artifact list with limit=200
2. Request times out after 30 seconds
3. Error: "Request timeout"

## Root Cause
No pagination implemented. All artifacts loaded at once.

## Proposed Fix
- Implement pagination (limit/offset)
- Add streaming for large datasets
- Increase timeout for specific endpoints

## Status
🔧 In progress
EOF

cat > demo_data/artifacts/bug_reports/2025-12-03_1200_BUG_004_cors-error.md << 'EOF'
---
title: "BUG-004: CORS Error in Production"
type: bug_report
status: resolved
created: 2025-12-03 12:00 (KST)
updated: 2025-12-03 14:00 (KST)
severity: medium
tags: [bug, cors, deployment]
---

# BUG-004: CORS Error in Production

## Description
CORS errors occur when accessing API from production frontend domain.

## Steps to Reproduce
1. Deploy frontend to production
2. Try to access API endpoints
3. Browser console shows CORS error

## Root Cause
CORS middleware configured for localhost only.

## Fix
Updated CORS configuration to include production domain.

## Status
✅ Resolved in commit `c3d4e5f`
EOF

# Additional Design Documents
cat > demo_data/artifacts/design_documents/2025-12-02_1600_design-microservices.md << 'EOF'
---
title: "Design: Microservices Architecture"
type: design
status: active
created: 2025-12-02 16:00 (KST)
category: architecture
tags: [design, architecture, microservices]
---

# Design: Microservices Architecture

## Overview
Proposed migration from monolith to microservices architecture.

## Services
- **API Gateway**: Routing and authentication
- **Artifact Service**: CRUD operations
- **Validation Service**: Compliance checks
- **Tracking Service**: Status and metrics

## Communication
- REST APIs for synchronous calls
- Message queue (RabbitMQ) for async operations
- Service mesh for inter-service communication

## Benefits
- Independent scaling
- Technology diversity
- Fault isolation
- Team autonomy
EOF

cat > demo_data/artifacts/design_documents/2025-12-03_1300_design-ci-cd-pipeline.md << 'EOF'
---
title: "Design: CI/CD Pipeline Architecture"
type: design
status: completed
created: 2025-12-03 13:00 (KST)
category: devops
tags: [design, ci-cd, devops]
---

# Design: CI/CD Pipeline Architecture

## Overview
Automated CI/CD pipeline for continuous deployment.

## Stages
1. **Build**: Compile and package
2. **Test**: Unit and integration tests
3. **Security**: Vulnerability scanning
4. **Deploy**: Staging and production

## Tools
- GitHub Actions for CI
- Docker for containerization
- Kubernetes for orchestration
- ArgoCD for GitOps

## Status
✅ Implemented and operational
EOF

cat > demo_data/artifacts/design_documents/2025-12-03_1500_design-monitoring-stack.md << 'EOF'
---
title: "Design: Monitoring and Observability Stack"
type: design
status: draft
created: 2025-12-03 15:00 (KST)
category: operations
tags: [design, monitoring, observability]
---

# Design: Monitoring and Observability Stack

## Overview
Comprehensive monitoring solution for production systems.

## Components
- **Metrics**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: Jaeger for distributed tracing
- **Alerting**: AlertManager + PagerDuty

## Metrics to Track
- Request rate and latency
- Error rates
- Resource utilization
- Business metrics

## Status
📝 Design phase
EOF

echo ""
echo "✅ Added 12 more sample artifacts:"
echo "   - 3 Implementation Plans (active, completed, draft)"
echo "   - 2 Assessments (complete, active)"
echo "   - 2 Audits (active, completed)"
echo "   - 3 Bug Reports (resolved, active, resolved)"
echo "   - 3 Design Documents (active, completed, draft)"
echo ""
echo "Total artifacts: $(find demo_data/artifacts -name '*.md' | wc -l)"
echo ""
echo "Restart backend to see new artifacts, or refresh the Librarian page!"
