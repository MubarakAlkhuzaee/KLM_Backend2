import asyncio, json
from pathlib import Path
from sqlalchemy import select
from app.db import AsyncSessionLocal
from app.models import DictionaryWord

WORDS_PATH = Path(__file__).parent.parent / "data" / "arabic_100_with_roots_with_source.json"

async def main():
    data = json.loads(WORDS_PATH.read_text(encoding="utf-8"))
    async with AsyncSessionLocal() as db:
        for item in data:
            meta = {"root": item.get("root"), "source": item.get("source")}
            w = DictionaryWord(word=item["word"], definition=item["definition"], meta=meta)
            db.add(w)
        await db.commit()

if __name__ == "__main__":
    asyncio.run(main())
