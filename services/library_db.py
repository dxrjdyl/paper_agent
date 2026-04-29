import sqlite3
from pathlib import Path
from config import DB_PATH

class LibraryDB:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.connect() as con:
            con.execute("""
            CREATE TABLE IF NOT EXISTS papers(
                paper_id TEXT PRIMARY KEY,
                title TEXT,
                authors TEXT,
                year TEXT,
                pdf_path TEXT,
                poster_path TEXT,
                key_info TEXT,
                deep_analysis TEXT,
                interpretation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            con.execute("""
            CREATE TABLE IF NOT EXISTS chunks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id TEXT,
                chunk_id TEXT,
                content TEXT,
                page_hint TEXT,
                FOREIGN KEY(paper_id) REFERENCES papers(paper_id)
            )
            """)

    def upsert_paper(self, paper_id, title, authors, year, pdf_path, poster_path='', key_info='', deep_analysis='', interpretation=''):
        with self.connect() as con:
            con.execute("""
            INSERT INTO papers(paper_id,title,authors,year,pdf_path,poster_path,key_info,deep_analysis,interpretation)
            VALUES(?,?,?,?,?,?,?,?,?)
            ON CONFLICT(paper_id) DO UPDATE SET
                title=excluded.title,
                authors=excluded.authors,
                year=excluded.year,
                pdf_path=excluded.pdf_path,
                poster_path=excluded.poster_path,
                key_info=excluded.key_info,
                deep_analysis=excluded.deep_analysis,
                interpretation=excluded.interpretation
            """, (paper_id, title, authors, year, str(pdf_path), str(poster_path), key_info, deep_analysis, interpretation))

    def add_chunks(self, paper_id: str, chunks: list[str]):
        with self.connect() as con:
            con.execute("DELETE FROM chunks WHERE paper_id=?", (paper_id,))
            con.executemany(
                "INSERT INTO chunks(paper_id, chunk_id, content, page_hint) VALUES(?,?,?,?)",
                [(paper_id, f"{paper_id}_{i}", c, "") for i, c in enumerate(chunks)]
            )

    def list_papers(self):
        with self.connect() as con:
            con.row_factory = sqlite3.Row
            rows = con.execute("SELECT * FROM papers ORDER BY created_at DESC").fetchall()
            return [dict(r) for r in rows]

    def get_paper(self, paper_id: str):
        with self.connect() as con:
            con.row_factory = sqlite3.Row
            row = con.execute("SELECT * FROM papers WHERE paper_id=?", (paper_id,)).fetchone()
            return dict(row) if row else None
