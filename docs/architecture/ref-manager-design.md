---
title: "Ref Manager: UUID Management System Design"
type: architecture
status: draft
created: 2025-12-12
updated: 2025-12-12
phase: future
priority: medium
tags: [architecture, uuid, reference-management, future-work]
---

# Ref Manager: UUID Management System Design

## Overview

This document outlines the research and recommended approach for implementing a Reference Manager (Ref Manager) system that facilitates creating and assigning permanent UUIDs to artifacts in the AgentQMS framework.

## Problem Statement

The Ref Manager is intended to:
- Create permanent UUIDs for artifacts
- Register UUIDs in a database
- Enable stable references across documentation
- Support migration from file-path-based references to UUID-based references

## Research: Existing Solutions

### 1. UUID Generation Libraries

#### Python (`uuid` module)
- **Standard Library**: Built-in `uuid` module provides multiple UUID versions
- **UUID4**: Random UUIDs (most common for new systems)
- **UUID1**: Time-based UUIDs (includes MAC address)
- **UUID5**: Name-based UUIDs using SHA-1 (deterministic)
- **Pros**: Standard library, no dependencies, multiple versions
- **Cons**: UUID5 requires namespace UUID + name string

#### JavaScript (`crypto.randomUUID()`)
- **Standard API**: Available in Node.js 14.17.0+ and modern browsers
- **Format**: RFC 4122 compliant UUID v4
- **Pros**: Native support, no dependencies
- **Cons**: Only generates random UUIDs (v4)

### 2. Database Patterns

#### SQLite
- **UUID Storage**: TEXT or BLOB (no native UUID type)
- **Indexing**: Can create indexes on UUID columns
- **Performance**: Good for small to medium datasets
- **Pros**: No server required, portable, good for AgentQMS
- **Cons**: No native UUID type, manual validation

#### PostgreSQL
- **UUID Type**: Native `UUID` data type
- **Indexing**: Built-in UUID indexing support
- **Extensions**: `uuid-ossp` for UUID generation functions
- **Pros**: Native support, excellent performance
- **Cons**: Requires PostgreSQL server (may be overkill for AgentQMS)

#### JSON File Storage
- **Pattern**: Store UUID mappings in JSON files
- **Structure**: `{ "uuid": "path", "path": "uuid" }` bidirectional mapping
- **Pros**: Simple, no database required, version-controllable
- **Cons**: Performance degrades with large datasets, concurrency issues

### 3. Reference Management Systems

#### Zotero Pattern
- **Approach**: Central database with UUIDs, metadata, and relationships
- **Storage**: SQLite database with UUID primary keys
- **Features**: Bidirectional references, citation tracking, metadata storage
- **Relevant**: Similar to AgentQMS artifact tracking needs

#### Mendeley Pattern
- **Approach**: Cloud-based UUID assignment with sync
- **Storage**: Centralized database with local cache
- **Features**: Conflict resolution, versioning
- **Less Relevant**: Requires cloud infrastructure

### 4. Artifact Tracking Systems

#### Git-based Approaches
- **Pattern**: Use Git commit hashes as stable identifiers
- **Pros**: Built-in versioning, no additional system needed
- **Cons**: Changes when content changes, not suitable for stable references

#### Content-Addressable Storage (CAS)
- **Pattern**: Hash content to generate identifier
- **Examples**: IPFS, Git objects
- **Pros**: Content-based, deduplication
- **Cons**: Changes when content changes (not suitable for artifact lifecycle)

## Recommended Architecture

### Phase 1: Simple File-Based Registry (MVP)

**Storage**: JSON file in `.agentqms/registry/uuid_mapping.json`

**Structure**:
```json
{
  "artifacts": {
    "550e8400-e29b-41d4-a716-446655440000": {
      "path": "docs/artifacts/implementation_plans/2025-12-12_1000_plan-feature-x.md",
      "id": "2025-12-12_1000_plan-feature-x",
      "created": "2025-12-12T10:00:00Z",
      "last_updated": "2025-12-12T10:00:00Z"
    }
  },
  "reverse_lookup": {
    "docs/artifacts/implementation_plans/2025-12-12_1000_plan-feature-x.md": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**API Design**:
- `POST /api/v1/ref/assign` - Assign UUID to artifact
- `GET /api/v1/ref/{uuid}` - Get artifact by UUID
- `GET /api/v1/ref/resolve/{path}` - Get UUID by path
- `PUT /api/v1/ref/{uuid}` - Update artifact reference

**Implementation Considerations**:
- Use Python `uuid.uuid4()` for generation
- Atomic file writes (write to temp file, then rename)
- Lock file for concurrent access prevention
- Periodic backup of registry file

### Phase 2: SQLite Database (Production)

**Storage**: SQLite database at `.agentqms/registry/refs.db`

**Schema**:
```sql
CREATE TABLE artifact_refs (
    uuid TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL,
    artifact_path TEXT NOT NULL UNIQUE,
    artifact_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_artifact_id ON artifact_refs(artifact_id);
CREATE INDEX idx_artifact_path ON artifact_refs(artifact_path);
CREATE INDEX idx_artifact_type ON artifact_refs(artifact_type);
```

**Benefits**:
- Better performance for large datasets
- ACID transactions
- Query capabilities
- Concurrent access handling

**Migration Path**:
- Read existing JSON file on first run
- Migrate to SQLite automatically
- Keep JSON as backup/export format

### Phase 3: Advanced Features (Future)

- **Bidirectional References**: Track which artifacts reference others
- **Reference Validation**: Check for broken UUID references
- **Bulk Operations**: Batch UUID assignment
- **Migration Tools**: Convert file-path links to UUID links
- **Versioning**: Track UUID changes over time

## Integration Points

### With AgentQMS Framework

1. **Artifact Creation**: Auto-assign UUID when artifact is created
2. **Frontmatter**: Add optional `uuid` field to artifact frontmatter
3. **Link Resolution**: Resolve UUID references in markdown links
4. **Tracking Database**: Store UUID in tracking database entries

### With Dashboard

1. **Ref Manager UI**: Interface for viewing/managing UUIDs
2. **Link Migrator**: Tool to convert file paths to UUIDs
3. **Reference Explorer**: Visualize UUID relationships

## Implementation Considerations

### UUID Version Choice

**Recommendation**: UUID v4 (random)
- **Reason**: No dependencies on MAC address or namespace
- **Uniqueness**: Sufficient for artifact tracking
- **Privacy**: No information leakage

**Alternative**: UUID v5 (name-based)
- **Use Case**: Deterministic UUIDs based on artifact path
- **Benefit**: Same artifact always gets same UUID
- **Drawback**: Requires namespace UUID management

### Concurrency Handling

**File-based (Phase 1)**:
- Use file locking (`fcntl` on Unix, `msvcrt` on Windows)
- Retry mechanism for lock acquisition
- Timeout to prevent deadlocks

**SQLite (Phase 2)**:
- SQLite handles concurrent reads well
- WAL mode for better concurrency
- Transaction-based writes

### Performance Considerations

- **Caching**: In-memory cache of UUID mappings
- **Lazy Loading**: Load registry on first access
- **Batch Operations**: Group multiple UUID assignments

### Error Handling

- **Duplicate UUIDs**: Extremely rare, but handle gracefully
- **Missing Artifacts**: UUID points to non-existent file
- **Corrupted Registry**: Backup and recovery mechanisms

## Migration Strategy

### From File Paths to UUIDs

1. **Scan Phase**: Identify all file-path references
2. **Assignment Phase**: Assign UUIDs to all artifacts
3. **Update Phase**: Replace file paths with UUIDs in content
4. **Validation Phase**: Verify all references resolve

### Backward Compatibility

- Support both file-path and UUID references during transition
- Auto-resolve file paths to UUIDs when possible
- Provide migration tools for bulk conversion

## Testing Strategy

1. **Unit Tests**: UUID generation, registry operations
2. **Integration Tests**: API endpoints, database operations
3. **Migration Tests**: File-path to UUID conversion
4. **Performance Tests**: Large dataset handling

## Future Enhancements

- **Distributed UUIDs**: Support for multi-repository UUIDs
- **UUID Aliases**: Short names for common artifacts
- **Reference Graphs**: Visualize artifact relationships
- **Conflict Resolution**: Handle UUID conflicts in merges

## Conclusion

The recommended approach is to start with a simple file-based registry (Phase 1) for MVP, then migrate to SQLite (Phase 2) for production use. This provides a clear migration path while keeping initial implementation simple.

**Status**: Research complete. Implementation deferred to future phase.

**Next Steps**: 
1. Implement Phase 1 (file-based registry) when Ref Manager feature is prioritized
2. Create API endpoints for UUID management
3. Build UI components for Ref Manager interface
4. Develop migration tools for existing artifacts

---

**Last Updated**: 2025-12-12  
**Status**: Research Complete - Awaiting Implementation Priority

