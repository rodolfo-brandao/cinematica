"""Memory-efficient streaming readers for IMDb `.tsv.gz` datasets."""

import gzip
from pathlib import Path
from typing import Iterator, Dict


def stream_tsv_gz(file_path: Path) -> Iterator[Dict[str, str]]:
    """
    Streams row by row from a (large) `.tsv.gz` file, yielding each row as a
    dict keyed by the file's header columns. Generic across every IMDb dataset
    (`title.basics`, `title.ratings`, `title.principals`, `name.basics`).

    :param file_path: The `.tsv.gz` file path.
    :type file_path: Path

    :return: An iterable dictionary containing the file data.
    :rtype: Iterator[Dict[str, str]]
    """

    tab_char = "\t"
    utf8_bom = "\ufeff"  # Byte Order Mark

    with gzip.open(filename=file_path, mode="rt", encoding="utf-8") as file:
        headers = [h.strip().lstrip(utf8_bom) for h in file.readline().split(tab_char)]

        for line in file:
            values = [v.strip() for v in line.split(tab_char)]
            yield dict(zip(headers, values))
