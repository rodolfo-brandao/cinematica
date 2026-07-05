"""Consolidation of enriched JSONL shards into a single output file."""

import os
from pathlib import Path

from src.logger import get_logger


_logger = get_logger(__name__)

_SHARD_GLOB = "movies_*.jsonl"


def consolidate_shards(shards_dir: Path, output_path: Path) -> int:
    """
    Concatenates every JSONL shard in `shards_dir` (in filename order, so the
    result is deterministic) into a single JSONL file at `output_path`. The
    write is atomic: content is assembled in a temporary file first and then
    moved into place, so a crash mid-write cannot corrupt the consolidated file.

    :param shards_dir: Directory containing the `movies_*.jsonl` shard files.
    :type shards_dir: Path
    :param output_path: Path of the consolidated JSONL file to write.
    :type output_path: Path

    :return: The total number of records written.
    :rtype: int
    """

    shard_paths = sorted(shards_dir.glob(_SHARD_GLOB))
    _logger.info("Consolidating %d shard(s) from %s", len(shard_paths), shards_dir)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    record_count = 0

    with open(file=tmp_path, mode="w", encoding="utf-8") as output_file:
        for shard_path in shard_paths:
            with open(file=shard_path, mode="r", encoding="utf-8") as shard_file:
                for line in shard_file:
                    line = line.strip()

                    if not line:
                        continue

                    output_file.write(line + "\n")
                    record_count += 1

    os.replace(tmp_path, output_path)
    _logger.info("Wrote %d record(s) to %s", record_count, output_path)
    return record_count
