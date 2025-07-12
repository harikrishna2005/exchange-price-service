import aiofiles
import ujson as json  # Faster than stdlib json


async def load_last_pairs(file="streamed_pairs.json") -> set:
    try:
        async with aiofiles.open(file, "r") as f:
            content = await f.read()
            return set(json.loads(content))
    except Exception:
        return set()


async def save_current_pairs(pairs: Set[str], file="streamed_pairs.json"):
    async with aiofiles.open(file, "w") as f:
        await f.write(json.dumps(list(pairs)))
