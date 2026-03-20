from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    dataset: str
    rule: str
    message: str


class DataValidationError(Exception):
    def __init__(self, issues: Sequence[ValidationIssue]) -> None:
        self.issues = list(issues)
        summary = "; ".join(
            f"{issue.dataset}.{issue.rule}: {issue.message}" for issue in self.issues
        )
        super().__init__(summary)


def ensure_required_columns(
    frame: pd.DataFrame,
    *,
    dataset: str,
    required_columns: Sequence[str],
) -> None:
    missing_columns = [column for column in required_columns if column not in frame.columns]
    if missing_columns:
        raise DataValidationError(
            [
                ValidationIssue(
                    dataset=dataset,
                    rule="required_columns",
                    message=f"Missing columns: {', '.join(sorted(missing_columns))}",
                )
            ]
        )


def ensure_not_null(frame: pd.DataFrame, *, dataset: str, columns: Sequence[str]) -> None:
    issues: list[ValidationIssue] = []
    for column in columns:
        invalid_count = int(frame[column].isna().sum())
        if invalid_count:
            issues.append(
                ValidationIssue(
                    dataset=dataset,
                    rule="not_null",
                    message=f"{column} has {invalid_count} null value(s)",
                )
            )

    _raise_if_issues(issues)


def ensure_parsed_dates(frame: pd.DataFrame, *, dataset: str, columns: Sequence[str]) -> None:
    issues: list[ValidationIssue] = []
    for column in columns:
        invalid_count = int(frame[column].isna().sum())
        if invalid_count:
            issues.append(
                ValidationIssue(
                    dataset=dataset,
                    rule="valid_dates",
                    message=f"{column} has {invalid_count} unparsable date value(s)",
                )
            )

    _raise_if_issues(issues)


def ensure_numeric(frame: pd.DataFrame, *, dataset: str, columns: Sequence[str]) -> None:
    issues: list[ValidationIssue] = []
    for column in columns:
        invalid_count = int(frame[column].isna().sum())
        if invalid_count:
            issues.append(
                ValidationIssue(
                    dataset=dataset,
                    rule="numeric",
                    message=f"{column} has {invalid_count} non-numeric value(s)",
                )
            )

    _raise_if_issues(issues)


def ensure_allowed_values(
    frame: pd.DataFrame,
    *,
    dataset: str,
    column: str,
    allowed_values: Iterable[str],
) -> None:
    allowed = set(allowed_values)
    invalid_values = sorted(
        {
            str(value)
            for value in frame.loc[~frame[column].isin(allowed) & frame[column].notna(), column]
        }
    )

    if invalid_values:
        raise DataValidationError(
            [
                ValidationIssue(
                    dataset=dataset,
                    rule="allowed_values",
                    message=(
                        f"{column} contains unsupported value(s): {', '.join(invalid_values)}"
                    ),
                )
            ]
        )


def _raise_if_issues(issues: Sequence[ValidationIssue]) -> None:
    if issues:
        raise DataValidationError(issues)
