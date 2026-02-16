-- =============================================================================
-- PostgreSQL initialization: enable required extensions
-- Runs automatically on first container start
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- trigram index for fuzzy text search
