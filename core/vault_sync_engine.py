"""
Vault Sync Engine - Full vault sync to PostgreSQL

Syncs all notes, definitions, papers, and metadata from the Obsidian vault
to PostgreSQL for backup and external access.
"""

import psycopg2
from psycopg2.extras import execute_values
import sqlite3
import uuid
import time
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, date
from configparser import ConfigParser


def json_serializer(obj):
    """JSON serializer for objects not serializable by default."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def generate_uuid() -> str:
    return str(uuid.uuid4())


@dataclass
class SyncStats:
    notes_synced: int = 0
    notes_skipped: int = 0
    notes_archived: int = 0
    definitions_synced: int = 0
    papers_synced: int = 0
    tags_synced: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class VaultSyncEngine:
    """
    Full vault synchronization to PostgreSQL.
    
    Syncs:
    - All markdown notes with frontmatter
    - Definitions from lexicon
    - Papers metadata
    - Tags and relationships
    """
    
    POSTGRES_CONFIG = {
        "host": "192.168.1.177",
        "port": 2665,
        "database": "Theophysics",
        "user": "Yellowkid",
        "password": "Moss9pep28$"
    }
    
    def __init__(
        self,
        vault_path: str,
        sqlite_path: Optional[str] = None,
        postgres_config: Optional[Dict[str, Any]] = None
    ):
        self.vault_path = Path(vault_path)
        self.sqlite_path = Path(sqlite_path) if sqlite_path else self.vault_path / "theophysics.db"
        self.postgres_config = postgres_config or self._load_postgres_config()
        self.pg_conn = None
        self.stats = SyncStats()

    def _load_postgres_config(self) -> Dict[str, Any]:
        """Load the GUI database settings when available, with legacy defaults as fallback."""
        config = dict(self.POSTGRES_CONFIG)
        settings_path = Path(__file__).resolve().parent.parent / "config" / "settings.ini"
        if settings_path.exists():
            parser = ConfigParser()
            parser.read(settings_path, encoding="utf-8")
            if parser.has_section("database"):
                config.update({
                    "host": parser.get("database", "host", fallback=config["host"]),
                    "port": parser.getint("database", "port", fallback=int(config["port"])),
                    "database": parser.get("database", "database", fallback=config["database"]),
                    "user": parser.get("database", "user", fallback=config["user"]),
                    "password": parser.get("database", "password", fallback=config["password"]),
                })
        return config
    
    def connect_postgres(self) -> bool:
        """Connect to PostgreSQL."""
        try:
            self.pg_conn = psycopg2.connect(**self.postgres_config)
            return True
        except Exception as e:
            self.stats.errors.append(f"PostgreSQL connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from PostgreSQL."""
        if self.pg_conn:
            self.pg_conn.close()
            self.pg_conn = None
    
    def ensure_postgres_schema(self) -> bool:
        """Create all required tables in PostgreSQL."""
        if not self.pg_conn:
            if not self.connect_postgres():
                return False
        
        try:
            cur = self.pg_conn.cursor()
            
            # Notes table - stores all markdown notes
            cur.execute("""
            CREATE TABLE IF NOT EXISTS vault_notes (
                id SERIAL PRIMARY KEY,
                uuid TEXT UNIQUE NOT NULL,
                path TEXT UNIQUE NOT NULL,
                title TEXT,
                content TEXT,
                content_hash TEXT,
                frontmatter JSONB,
                tags JSONB DEFAULT '[]',
                links JSONB DEFAULT '[]',
                word_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_modified_at TIMESTAMP
            )
            """)

            cur.execute("ALTER TABLE vault_notes ADD COLUMN IF NOT EXISTS content_hash TEXT")
            cur.execute("ALTER TABLE vault_notes ADD COLUMN IF NOT EXISTS source_absolute_path TEXT")
            cur.execute("ALTER TABLE vault_notes ADD COLUMN IF NOT EXISTS last_seen_at TIMESTAMP")

            cur.execute("""
            CREATE TABLE IF NOT EXISTS vault_notes_history (
                id SERIAL PRIMARY KEY,
                original_note_id INTEGER,
                uuid TEXT,
                path TEXT NOT NULL,
                title TEXT,
                content TEXT,
                content_hash TEXT,
                frontmatter JSONB,
                tags JSONB DEFAULT '[]',
                links JSONB DEFAULT '[]',
                word_count INTEGER DEFAULT 0,
                file_modified_at TIMESTAMP,
                db_updated_at TIMESTAMP,
                archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                archive_reason TEXT DEFAULT 'local_markdown_changed'
            )
            """)
            
            # Definitions table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS vault_definitions (
                id SERIAL PRIMARY KEY,
                uuid TEXT UNIQUE NOT NULL,
                term TEXT UNIQUE NOT NULL,
                aliases JSONB DEFAULT '[]',
                definition TEXT,
                classification TEXT,
                relationships JSONB DEFAULT '{}',
                source_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Papers table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS vault_papers (
                id SERIAL PRIMARY KEY,
                uuid TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                paper_number TEXT,
                abstract TEXT,
                status TEXT,
                path TEXT,
                word_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Tags table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS vault_tags (
                id SERIAL PRIMARY KEY,
                uuid TEXT UNIQUE NOT NULL,
                tag_name TEXT UNIQUE NOT NULL,
                usage_count INTEGER DEFAULT 0,
                notes JSONB DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Note links/relationships
            cur.execute("""
            CREATE TABLE IF NOT EXISTS vault_links (
                id SERIAL PRIMARY KEY,
                uuid TEXT UNIQUE NOT NULL,
                source_path TEXT NOT NULL,
                target_path TEXT NOT NULL,
                link_type TEXT DEFAULT 'wikilink',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_path, target_path)
            )
            """)
            
            # Sync metadata
            cur.execute("""
            CREATE TABLE IF NOT EXISTS sync_metadata (
                id SERIAL PRIMARY KEY,
                sync_type TEXT UNIQUE NOT NULL,
                last_sync_at TIMESTAMP,
                records_synced INTEGER,
                status TEXT
            )
            """)
            
            # Create indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_notes_path ON vault_notes(path)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_notes_title ON vault_notes(title)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_notes_content_hash ON vault_notes(content_hash)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_notes_history_path ON vault_notes_history(path)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_defs_term ON vault_definitions(term)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_papers_title ON vault_papers(title)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_tags_name ON vault_tags(tag_name)")
            
            self.pg_conn.commit()
            return True
            
        except Exception as e:
            self.stats.errors.append(f"Schema creation failed: {e}")
            return False
    
    def sync_all(self, progress_callback=None) -> SyncStats:
        """
        Sync entire vault to PostgreSQL.
        
        Args:
            progress_callback: Optional function(current, total, message) for progress updates
        """
        self.stats = SyncStats()
        
        if not self.connect_postgres():
            return self.stats
        
        if not self.ensure_postgres_schema():
            return self.stats
        
        try:
            # Count total files for progress
            md_files = list(self.vault_path.rglob("*.md"))
            total = len(md_files)
            
            if progress_callback:
                progress_callback(0, total, "Starting sync...")
            
            # Sync notes in batches with reconnection
            batch_size = 50
            for i, md_file in enumerate(md_files):
                # Skip system folders
                if any(skip in str(md_file) for skip in [".obsidian", "node_modules", ".git"]):
                    continue
                
                try:
                    changed = self._sync_note(md_file)
                    if changed:
                        self.stats.notes_synced += 1
                    else:
                        self.stats.notes_skipped += 1
                except Exception as e:
                    self.stats.errors.append(f"Error syncing {md_file.name}: {e}")
                    # Reconnect on error
                    try:
                        self.pg_conn.rollback()
                    except:
                        self.connect_postgres()
                
                # Commit and reconnect every batch_size notes
                if i % batch_size == 0 and i > 0:
                    try:
                        self.pg_conn.commit()
                    except:
                        self.connect_postgres()
                    if progress_callback:
                        progress_callback(i, total, f"Syncing notes... {i}/{total}")
            
            # Final commit for notes
            try:
                self.pg_conn.commit()
            except:
                pass
            
            if progress_callback:
                progress_callback(total, total, "Syncing definitions...")
            
            # Sync definitions from lexicon
            self._sync_definitions()
            
            if progress_callback:
                progress_callback(total, total, "Syncing papers...")
            
            # Sync papers
            self._sync_papers()
            
            if progress_callback:
                progress_callback(total, total, "Syncing tags...")
            
            # Sync tags
            self._sync_tags()
            
            # Update sync metadata
            self._update_sync_metadata()
            
            self.pg_conn.commit()
            
            if progress_callback:
                progress_callback(total, total, "Sync complete!")
            
        except Exception as e:
            self.stats.errors.append(f"Sync failed: {e}")
        finally:
            self.disconnect()
        
        return self.stats
    
    def _sync_note(self, file_path: Path):
        """Sync a single note to PostgreSQL."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
            # Remove NUL characters
            content = content.replace('\x00', '')
        except:
            return
        
        rel_path = str(file_path.relative_to(self.vault_path))
        title = file_path.stem
        
        # Parse frontmatter
        frontmatter = {}
        body = content
        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if fm_match:
            try:
                import yaml
                frontmatter = yaml.safe_load(fm_match.group(1)) or {}
            except:
                pass
            body = content[fm_match.end():]
        
        # Extract tags
        tags = []
        if 'tags' in frontmatter:
            if isinstance(frontmatter['tags'], list):
                tags = [str(t) for t in frontmatter['tags'] if t]
            elif isinstance(frontmatter['tags'], str):
                tags = [frontmatter['tags']]
        
        # Also find inline tags
        inline_tags = re.findall(r'#([a-zA-Z][a-zA-Z0-9_/-]*)', body)
        tags.extend(inline_tags)
        tags = list(set(tags))
        
        # Extract wikilinks
        links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)
        
        # Word count
        word_count = len(body.split())
        
        # File modified time
        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        
        # Always generate new UUID based on path to avoid collisions
        note_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, rel_path))
        
        cur = self.pg_conn.cursor()

        cur.execute("""
        SELECT id, uuid, title, content, content_hash, frontmatter, tags, links,
               word_count, file_modified_at, updated_at
        FROM vault_notes
        WHERE path = %s
        """, (rel_path,))
        existing = cur.fetchone()

        if existing:
            existing_hash = existing[4]
            existing_content = existing[3] or ""
            if existing_hash == content_hash or (not existing_hash and existing_content == content):
                return False

            cur.execute("""
            INSERT INTO vault_notes_history (
                original_note_id, uuid, path, title, content, content_hash,
                frontmatter, tags, links, word_count, file_modified_at, db_updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                existing[0],
                existing[1],
                rel_path,
                existing[2],
                existing_content,
                existing_hash,
                json.dumps(existing[5], default=json_serializer) if existing[5] is not None else "{}",
                json.dumps(existing[6], default=json_serializer) if existing[6] is not None else "[]",
                json.dumps(existing[7], default=json_serializer) if existing[7] is not None else "[]",
                existing[8],
                existing[9],
                existing[10]
            ))
            self.stats.notes_archived += 1

        cur.execute("""
        INSERT INTO vault_notes (
            uuid, path, title, content, content_hash, frontmatter, tags, links,
            word_count, file_modified_at, source_absolute_path, updated_at, last_seen_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (path) DO UPDATE SET
            uuid = EXCLUDED.uuid,
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            content_hash = EXCLUDED.content_hash,
            frontmatter = EXCLUDED.frontmatter,
            tags = EXCLUDED.tags,
            links = EXCLUDED.links,
            word_count = EXCLUDED.word_count,
            file_modified_at = EXCLUDED.file_modified_at,
            source_absolute_path = EXCLUDED.source_absolute_path,
            updated_at = CURRENT_TIMESTAMP,
            last_seen_at = CURRENT_TIMESTAMP
        """, (
            note_uuid,
            rel_path,
            title,
            content,
            content_hash,
            json.dumps(frontmatter, default=json_serializer),
            json.dumps(tags),
            json.dumps(links),
            word_count,
            file_mtime,
            str(file_path)
        ))
        return True
    
    def _sync_definitions(self):
        """Sync definitions from lexicon folder."""
        lexicon_path = self.vault_path / "02_LIBRARY" / "4_LEXICON"
        if not lexicon_path.exists():
            return
        
        for def_file in lexicon_path.glob("*.md"):
            try:
                content = def_file.read_text(encoding='utf-8')
                term = def_file.stem
                
                # Parse frontmatter
                frontmatter = {}
                fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if fm_match:
                    try:
                        import yaml
                        frontmatter = yaml.safe_load(fm_match.group(1)) or {}
                    except:
                        pass
                
                # Extract definition
                definition = ""
                def_match = re.search(r'## (?:Core )?Definition\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
                if def_match:
                    definition = def_match.group(1).strip()
                
                aliases = frontmatter.get('aliases', [])
                if isinstance(aliases, str):
                    aliases = [aliases]
                
                classification = frontmatter.get('classification', '')
                
                # Generate UUID based on term to avoid collisions
                def_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"definition:{term}"))
                
                cur = self.pg_conn.cursor()
                try:
                    cur.execute("""
                    INSERT INTO vault_definitions (uuid, term, aliases, definition, classification, source_path, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (term) DO UPDATE SET
                        uuid = EXCLUDED.uuid,
                        aliases = EXCLUDED.aliases,
                        definition = EXCLUDED.definition,
                        classification = EXCLUDED.classification,
                        source_path = EXCLUDED.source_path,
                        updated_at = CURRENT_TIMESTAMP
                    """, (
                        def_uuid,
                        term,
                        json.dumps(aliases),
                        definition,
                        classification,
                        str(def_file.relative_to(self.vault_path))
                    ))
                    self.pg_conn.commit()
                    self.stats.definitions_synced += 1
                except Exception as e:
                    self.pg_conn.rollback()
                    self.stats.errors.append(f"Definition sync error {def_file.name}: {e}")
                
            except Exception as e:
                self.stats.errors.append(f"Definition read error {def_file.name}: {e}")
    
    def _sync_papers(self):
        """Sync papers from publications folder."""
        papers_path = self.vault_path / "03_PUBLICATIONS" / "COMPLETE_LOGOS_PAPERS_FINAL"
        if not papers_path.exists():
            return
        
        for paper_file in papers_path.glob("*.md"):
            if paper_file.name.startswith("_"):
                continue
            
            try:
                content = paper_file.read_text(encoding='utf-8')
                title = paper_file.stem
                
                # Extract paper number
                paper_num_match = re.search(r'P(\d+)', title)
                paper_number = f"P{paper_num_match.group(1)}" if paper_num_match else None
                
                # Parse frontmatter
                frontmatter = {}
                fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if fm_match:
                    try:
                        import yaml
                        frontmatter = yaml.safe_load(fm_match.group(1)) or {}
                    except:
                        pass
                
                # Extract abstract
                abstract = ""
                abs_match = re.search(r'## Abstract\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
                if abs_match:
                    abstract = abs_match.group(1).strip()[:2000]
                
                status = frontmatter.get('status', 'unknown')
                word_count = len(content.split())
                # Generate UUID based on title to avoid collisions
                paper_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"paper:{title}"))
                
                cur = self.pg_conn.cursor()
                cur.execute("""
                INSERT INTO vault_papers (uuid, title, paper_number, abstract, status, path, word_count, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (uuid) DO UPDATE SET
                    title = EXCLUDED.title,
                    paper_number = EXCLUDED.paper_number,
                    abstract = EXCLUDED.abstract,
                    status = EXCLUDED.status,
                    path = EXCLUDED.path,
                    word_count = EXCLUDED.word_count,
                    updated_at = CURRENT_TIMESTAMP
                """, (
                    paper_uuid,
                    title,
                    paper_number,
                    abstract,
                    status,
                    str(paper_file.relative_to(self.vault_path)),
                    word_count
                ))
                self.pg_conn.commit()
                
                self.stats.papers_synced += 1
                
            except Exception as e:
                self.stats.errors.append(f"Paper sync error {paper_file.name}: {e}")
    
    def _sync_tags(self):
        """Aggregate and sync all tags."""
        cur = self.pg_conn.cursor()
        
        # Get all tags from notes
        cur.execute("""
        SELECT tag, array_agg(path) as note_paths
        FROM vault_notes, jsonb_array_elements_text(tags) as tag
        GROUP BY tag
        """)
        
        for row in cur.fetchall():
            tag_name = row[0]
            note_paths = row[1]
            
            tag_uuid = generate_uuid()
            
            cur.execute("""
            INSERT INTO vault_tags (uuid, tag_name, usage_count, notes)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (tag_name) DO UPDATE SET
                usage_count = EXCLUDED.usage_count,
                notes = EXCLUDED.notes
            """, (
                tag_uuid,
                tag_name,
                len(note_paths),
                json.dumps(note_paths)
            ))
            
            self.stats.tags_synced += 1
    
    def _update_sync_metadata(self):
        """Update sync metadata."""
        cur = self.pg_conn.cursor()
        
        cur.execute("""
        INSERT INTO sync_metadata (sync_type, last_sync_at, records_synced, status)
        VALUES ('full_vault', CURRENT_TIMESTAMP, %s, 'success')
        ON CONFLICT (sync_type) DO UPDATE SET
            last_sync_at = CURRENT_TIMESTAMP,
            records_synced = EXCLUDED.records_synced,
            status = 'success'
        """, (self.stats.notes_synced,))
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status from PostgreSQL."""
        if not self.connect_postgres():
            return {"error": "Cannot connect to PostgreSQL"}
        
        try:
            cur = self.pg_conn.cursor()
            
            # Get counts
            counts = {}
            for table in ['vault_notes', 'vault_definitions', 'vault_papers', 'vault_tags']:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cur.fetchone()[0]
            
            # Get last sync
            cur.execute("SELECT last_sync_at, records_synced FROM sync_metadata WHERE sync_type = 'full_vault'")
            row = cur.fetchone()
            last_sync = row[0] if row else None
            
            return {
                "notes": counts.get('vault_notes', 0),
                "definitions": counts.get('vault_definitions', 0),
                "papers": counts.get('vault_papers', 0),
                "tags": counts.get('vault_tags', 0),
                "last_sync": str(last_sync) if last_sync else "Never"
            }
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            self.disconnect()


def run_full_sync(vault_path: str) -> SyncStats:
    """Convenience function to run a full vault sync."""
    engine = VaultSyncEngine(vault_path)
    return engine.sync_all()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sync an Obsidian markdown vault to PostgreSQL.")
    parser.add_argument(
        "vault_path",
        nargs="?",
        default=r"O:\_Theophysics_v4",
        help="Path to the Obsidian vault to sync."
    )
    args = parser.parse_args()
    vault_path = args.vault_path
    
    print("=" * 60)
    print("VAULT SYNC TO POSTGRESQL")
    print("=" * 60)
    print(f"Vault: {vault_path}")
    print("Target: PostgreSQL configured in VaultSyncEngine.POSTGRES_CONFIG")
    print()
    
    def progress(current, total, msg):
        pct = int(current / total * 100) if total > 0 else 0
        print(f"[{pct:3d}%] {msg}")
    
    engine = VaultSyncEngine(vault_path)
    stats = engine.sync_all(progress_callback=progress)
    
    print()
    print("=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"Notes synced: {stats.notes_synced}")
    print(f"Notes skipped unchanged: {stats.notes_skipped}")
    print(f"Prior DB note versions archived: {stats.notes_archived}")
    print(f"Definitions synced: {stats.definitions_synced}")
    print(f"Papers synced: {stats.papers_synced}")
    print(f"Tags synced: {stats.tags_synced}")
    
    if stats.errors:
        print(f"\nErrors ({len(stats.errors)}):")
        for err in stats.errors[:10]:
            print(f"  - {err}")
