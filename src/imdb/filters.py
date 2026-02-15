from typing import Dict


def is_movie(record: Dict[str, str]) -> bool:
    """
    Defines if a given film record is of type "movie"
    (expected the dict key to be "titleType").

    :param record: A record from a `.tsv.gz` file.
    :type record: Dict[str, str]

    :return: `True` if the given record is of type movie, otherwise `False`.
    :rtype: bool
    """

    return record.get("titleType") == "movie"


def is_short(record: Dict[str, str]) -> bool:
    """
    Defines if a given film record is of type "short"
    (expected the dict key to be "titleType").

    :param record: A record from a `.tsv.gz` file.
    :type record: Dict[str, str]

    :return: `True` if the given record is of type short, otherwise `False`.
    :rtype: bool
    """

    return record.get("titleType") == "short"
