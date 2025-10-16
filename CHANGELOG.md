# Changelog

All notable changes to dago-domenai will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-10-16

### 🎯 Dual Protocol WHOIS Implementation

Complete WHOIS profile with detailed domain data retrieval using DAS + standard WHOIS.

### Added
- **WHOISClient class** - Standard WHOIS protocol (port 43) implementation
  - Socket-based queries with timeout handling
  - Token bucket rate limiter (100 queries / 30 minutes)
  - Graceful error handling and degradation
  
- **WHOIS Response Parser** - Extract all available .lt WHOIS fields
  - Registrar details (name, website, email)
  - Registration dates (registered, expires)
  - Contact information (organization, email) for non-privacy domains
  - Nameservers with optional IP addresses
  - Derived fields: domain age, days until expiry
  - Privacy protection detection
  
- **Dual Protocol Strategy**
  - DAS first (fast) → Check registration status
  - WHOIS second (detailed) → Get full data for registered domains only
  - Early bailout for unregistered domains (5x faster)
  - Rate limit protection with graceful degradation

### Changed
- **`run_whois_check()`** - Updated to dual protocol flow
  - Returns complete JSONB structure for registered domains
  - Returns minimal structure for unregistered domains
  - Handles rate limiting gracefully (returns DAS-only data)
  
- **`config.yaml`** - Extended WHOIS configuration
  - Added `whois_server`, `whois_port`, `whois_timeout`
  - Added `whois_rate_limit` (100 per 30 minutes)
  - Maintained backward compatibility with existing DAS config

### Documentation
- **`docs/DAS_VS_WHOIS_ANALYSIS.md`** - Protocol comparison and test results
- **`docs/WHOIS_FIELD_ANALYSIS.md`** - Complete field mapping for .lt domains
- **`docs/V1.1_COMPLETION_SUMMARY.md`** - Implementation summary and test results
- Updated `docs/LAUNCH_PLAN.md` - Realistic v1.1 goals

### Performance
- **Unregistered domains:** 0.02s (DAS only, 5x faster than before)
- **Registered domains:** 0.10s (DAS + WHOIS, complete data)
- **Rate limiting:** Prevents IP blocking, automatic token bucket management

---

## [1.0.0] - 2025-10-15

### 🎉 First Production Release!

This is the first production-ready release of dago-domenai, featuring a complete profile system, professional test suite, and streamlined database setup.

### Added
- **Test Suite** - Professional testing infrastructure
  - 43 unit tests for profile system (100% passing)
  - `tests/` directory with proper structure (unit/, integration/, fixtures/)
  - pytest configuration with markers and coverage support
  - Test fixtures for sample data and mocks
  - Comprehensive test documentation in `tests/README.md`
  
- **Database Setup** - Simplified initialization
  - Interactive `db/setup.sh` script for fresh database creation
  - Database verification and statistics commands
  - Complete `db/README.md` with usage examples
  
- **Documentation**
  - `V1_RELEASE_SUMMARY.md` - Complete v1.0 overview
  - `CHANGELOG.md` - This file
  - Updated test and database documentation

### Changed
- **Version** - Updated to 1.0.0 in `src/__init__.py`
- **Requirements** - Added test dependencies (pytest, pytest-cov, pytest-asyncio, coverage)
- **Database Schema** - Consolidated all migrations into single `schema.sql`
- **Documentation** - Updated all docs to reflect v1.0 status

### Removed
- **Legacy Files** (Pre-v1.0 cleanup)
  - 11 legacy files removed (~100KB):
    - `test_db.py` - Old v0.6 test
    - `query_db.py` - Old v0.6 utility
    - 7 historical completion documents (V07-V10)
    - `db/seed.sql` - Legacy task definitions
    - `src/tasks/` - Empty module directory
    
- **Migration Files** (Streamlined for pre-production)
  - 5 migration files removed (~26KB):
    - `db/migrations/` directory with 4 SQL files
    - `db/migrate_v10.sh` migration script
  - Rationale: Fresh database deployments don't need migration history
  - Will be reintroduced post-v1.0 when production data exists

### Fixed
- Test suite compatibility with actual API
- Profile system test coverage (now at 100%)
- Documentation accuracy for current codebase

## [0.10.0] - 2025-10-14

### Added
- **Composable Profile System**
  - 21 profiles across 4 categories (core, analysis, intelligence, meta)
  - 6 meta profiles for common use cases
  - Dependency resolution with topological sorting
  - Execution planning with parallel group formation
  - `src/profiles/` module with schema and loader
  
- **Database Schema v0.10**
  - Profile tracking in tasks and results tables
  - 3 new analytics views (v_profile_execution_stats, v_profile_combinations, v_profile_dependency_stats)
  - `validate_profile_data()` function for consistency checks
  - Meta profiles pre-populated in tasks table

- **Orchestrator Integration**
  - `--profiles` CLI flag for profile-based execution
  - Profile-aware check selection
  - Execution plan logging

- **Documentation**
  - `PROFILE_QUICK_REFERENCE.md` - Profile system guide
  - `V10_COMPLETION.md` - Technical implementation details
  - `MIGRATION_SUMMARY.md` - Migration instructions

## [0.9.0] - 2025-10-13

### Added
- **Domain Discovery Tracking**
  - `domain_discoveries` table for redirect/discovery tracking
  - Discovery method categorization (redirect, dns, social, sitemap, etc.)
  - 2 analytics views (v_discovery_stats, v_top_discovery_sources)
  
- **Active Domain Check**
  - `active_check.py` module for domain activity validation
  - `check_domain_active()` function with DNS and HTTP validation
  - Automatic domain flag updates

- **Documentation**
  - `V09_REDIRECT_CAPTURE_DESIGN.md` - Discovery system design
  - Updated schema documentation

## [0.8.0] - 2025-10-12

### Added
- **Domain Flags System**
  - `is_registered` flag in domains table (from WHOIS)
  - `is_active` flag in domains table (from DNS/HTTP)
  - Early bailout optimization (skip checks for unregistered/inactive domains)
  - Automatic flag updates during analysis

- **Database Functions**
  - `update_domain_flags()` utility function
  - Indexed flags for fast filtering

- **Documentation**
  - `V08_IMPLEMENTATION_PLAN.md` - Flag system design
  - `V08_OPTIMIZATION_DESIGN.md` - Performance optimizations

### Changed
- Orchestrator now checks domain flags before running expensive checks
- Database queries can filter by registration/activity status

## [0.6.0] - 2025-10-10

### Added
- **Database Persistence**
  - `src/utils/db.py` - PostgreSQL integration
  - Automatic result saving after each scan
  - Connection pooling and context managers
  
- **Query Utilities**
  - `test_db.py` - Database connection testing
  - `query_db.py` - CLI tool for querying results
  - Statistics, domain listing, and result retrieval functions

- **Database Schema**
  - `domains` table - Domain registry
  - `tasks` table - Task definitions
  - `results` table - Analysis results (JSONB)

### Changed
- Orchestrator now saves results to database by default
- Added `save_results` configuration flag

## [0.5.0] - 2025-10-08

### Added
- **All Base Checks**
  - Redirect check (`redirect_check.py`)
  - Robots.txt check (`robots_check.py`)
  - Sitemap check (`sitemap_check.py`)
  - SSL certificate check (`ssl_check.py`)
  - WHOIS check (`whois_check.py`)

- **Result Schema**
  - Structured JSON result format
  - Grade calculation (A-F)
  - Summary generation

## [0.4.0] - 2025-10-06

### Added
- **DNS Check** (`dns_check.py`)
- **HTTP Status Check** (`status_check.py`)
- **Async Execution** - Concurrent domain processing

## [0.3.0] - 2025-10-04

### Added
- **Core Architecture**
  - `orchestrator.py` - Main entry point
  - `src/core/schema.py` - Result structure
  - `src/utils/config.py` - YAML configuration

## [0.2.0] - 2025-10-02

### Added
- **Configuration System**
  - `config.yaml` - Check configuration
  - Timeout settings
  - Concurrency controls

## [0.1.0] - 2025-10-01

### Added
- Initial project structure
- Basic domain input handling
- Logging setup

---

## Version Numbering

- **Major (X.0.0)**: Breaking changes, major new features
- **Minor (0.X.0)**: New features, non-breaking changes
- **Patch (0.0.X)**: Bug fixes, documentation updates

## Links

- **v1.0.0 Release Notes**: `V1_RELEASE_SUMMARY.md`
- **Profile System Guide**: `docs/PROFILE_QUICK_REFERENCE.md`
- **Database Setup**: `db/README.md`
- **Testing Guide**: `tests/README.md`

---

[1.0.0]: https://github.com/your-org/dago-domenai/releases/tag/v1.0.0
[0.10.0]: https://github.com/your-org/dago-domenai/releases/tag/v0.10.0
[0.9.0]: https://github.com/your-org/dago-domenai/releases/tag/v0.9.0
[0.8.0]: https://github.com/your-org/dago-domenai/releases/tag/v0.8.0
[0.6.0]: https://github.com/your-org/dago-domenai/releases/tag/v0.6.0
[0.5.0]: https://github.com/your-org/dago-domenai/releases/tag/v0.5.0
