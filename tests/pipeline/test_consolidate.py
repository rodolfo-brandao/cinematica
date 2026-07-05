"""Unit tests for src.pipeline.consolidate."""

from pathlib import Path

from src.pipeline.consolidate import consolidate_shards


def test_consolidate_shards_merges_in_filename_order(tmp_path: Path):
    shards_dir = tmp_path / "chunks"
    shards_dir.mkdir()
    (shards_dir / "movies_00001.jsonl").write_text('{"tconst": "tt2"}\n', encoding="utf-8")
    (shards_dir / "movies_00000.jsonl").write_text(
        '{"tconst": "tt1"}\n{"tconst": "tt1b"}\n', encoding="utf-8"
    )

    output_path = tmp_path / "movies.jsonl"
    count = consolidate_shards(shards_dir, output_path)

    assert count == 3
    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert lines == ['{"tconst": "tt1"}', '{"tconst": "tt1b"}', '{"tconst": "tt2"}']


def test_consolidate_shards_skips_blank_lines(tmp_path: Path):
    shards_dir = tmp_path / "chunks"
    shards_dir.mkdir()
    (shards_dir / "movies_00000.jsonl").write_text('{"tconst": "tt1"}\n\n', encoding="utf-8")

    output_path = tmp_path / "movies.jsonl"
    count = consolidate_shards(shards_dir, output_path)

    assert count == 1


def test_consolidate_shards_leaves_no_temporary_file(tmp_path: Path):
    shards_dir = tmp_path / "chunks"
    shards_dir.mkdir()
    (shards_dir / "movies_00000.jsonl").write_text('{"tconst": "tt1"}\n', encoding="utf-8")

    output_path = tmp_path / "movies.jsonl"
    consolidate_shards(shards_dir, output_path)

    assert not list(tmp_path.glob("*.tmp"))
