from typing import Any

from .ContextQualityFilterInterface import (
    ContextQualityFilterInterface,
)


class ContextQualityFilter(
    ContextQualityFilterInterface
):

    TOC_MARKERS = (
        "table of contents",
        "table of content",
    )

    def filter(
        self,
        results: list[Any],
        min_score: float,
        max_results: int,
    ) -> list[Any]:

        if not results:
            return []

        if max_results <= 0:
            raise ValueError(
                "max_results must be greater than zero."
            )

        filtered_results = []

        for item in results:

            reranker_score = float(
                item["reranker_score"]
            )

            # -----------------------------------------------------
            # 1. Remove weak results
            # -----------------------------------------------------

            if reranker_score < min_score:
                continue

            result = item["result"]

            payload = (
                getattr(
                    result,
                    "payload",
                    None,
                )
                or {}
            )

            text = payload.get(
                "text",
                "",
            ).strip()

            # -----------------------------------------------------
            # 2. Remove empty chunks
            # -----------------------------------------------------

            if not text:
                continue

            # -----------------------------------------------------
            # 3. Remove obvious TOC chunks
            # -----------------------------------------------------

            normalized_text = self._normalize_text(
                text
            )

            if self._is_table_of_contents(
                normalized_text
            ):
                continue

            # -----------------------------------------------------
            # 4. Keep valid context
            # -----------------------------------------------------

            filtered_results.append(item)

            if len(filtered_results) >= max_results:
                break

        return filtered_results

    # =============================================================
    # Text normalization
    # =============================================================

    def _normalize_text(
        self,
        text: str,
    ) -> str:

        return " ".join(
            text.lower().split()
        )

    # =============================================================
    # TOC detection
    # =============================================================

    def _is_table_of_contents(
        self,
        text: str,
    ) -> bool:

        # Direct TOC marker
        for marker in self.TOC_MARKERS:

            if marker in text:
                return True

        # ---------------------------------------------------------
        # Heuristic:
        #
        # A chunk containing many section headings and page numbers
        # is very likely a Table Of Contents.
        # ---------------------------------------------------------

        section_count = text.count("section")

        page_number_patterns = (
            " section 01 ",
            " section 02 ",
            " section 03 ",
            " section 04 ",
            " section 05 ",
            " section 06 ",
            " section 07 ",
            " section 08 ",
            " section 09 ",
            " section 10 ",
            " section 11 ",
            " section 12 ",
            " section 13 ",
            " section 14 ",
        )

        numbered_sections = sum(
            1
            for pattern in page_number_patterns
            if pattern in f" {text} "
        )

        if section_count >= 4:
            return True

        if numbered_sections >= 3:
            return True

        return False