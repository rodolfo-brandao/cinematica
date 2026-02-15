import gzip
from pathlib import Path
from typing import Iterator, Dict


def stream_title_basics(file_path: Path) -> Iterator[Dict[str, str]]:
    """
    Streams row by row from a (large) `.tsv.gz` file.

    :param path: The `.tsv.gz` file path.
    :type path: Path

    :return: An iterable dictionary containing the file data.
    :rtype: Iterator[Dict[str, str]]
    """

    TAB_CHAR = "\t"
    UTF8_BOM = "\ufeff"  # Byte Order Mark

    with gzip.open(filename=file_path, mode="rt", encoding="utf-8") as file:
        headers = [h.strip().lstrip(UTF8_BOM) for h in file.readline().split(TAB_CHAR)]

        for line in file:
            values = [v.strip() for v in line.split(TAB_CHAR)]
            yield dict(zip(headers, values))
