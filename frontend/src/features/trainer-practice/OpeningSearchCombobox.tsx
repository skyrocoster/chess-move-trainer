import { Search } from "lucide-react";
import { useEffect, useMemo, type FocusEvent, type MouseEvent } from "react";

import type { OpeningCatalogueItemResponse } from "../../api/client";
import { Combobox } from "../design-system/form-controls/Combobox";
import styles from "./OpeningSearchCombobox.module.css";

export const ALL_OPENINGS_VALUE = "__cmt_all_openings__";

/** Max dropdown rows built at once. The full catalogue has thousands of
 * openings, and mounting them all makes the first click feel stuck. */
export const OPENING_SEARCH_VISIBLE_LIMIT = 100;

export type OpeningSelection =
  | null
  | { kind: "specific"; key: string }
  | { kind: "all" };

export type OpeningSearchComboboxProps = {
  openings: OpeningCatalogueItemResponse[];
  query: string;
  selection: OpeningSelection;
  onQueryChange: (value: string) => void;
  onSelectionChange: (selection: OpeningSelection) => void;
  onMissingSelection: () => void;
  disabled?: boolean;
};

function searchText(opening: OpeningCatalogueItemResponse): string {
  return `${opening.name} ${opening.eco} ${opening.key}`.toLocaleLowerCase();
}

export function filterOpeningCatalogue(
  openings: OpeningCatalogueItemResponse[],
  query: string,
): OpeningCatalogueItemResponse[] {
  const normalized = query.trim().toLocaleLowerCase();
  if (normalized === "") {
    return openings;
  }
  return openings.filter((opening) => searchText(opening).includes(normalized));
}

function openingLabel(opening: OpeningCatalogueItemResponse): string {
  return `${opening.eco} ${opening.name} ${opening.key}`;
}

export function OpeningSearchCombobox({
  openings,
  query,
  selection,
  onQueryChange,
  onSelectionChange,
  onMissingSelection,
  disabled = false,
}: OpeningSearchComboboxProps) {
  const openingsByKey = useMemo(
    () => new Map(openings.map((opening) => [opening.key, opening] as const)),
    [openings],
  );
  const selectedOpening =
    selection?.kind === "specific" ? (openingsByKey.get(selection.key) ?? null) : null;

  useEffect(() => {
    if (selection?.kind === "specific" && selectedOpening === null) {
      onMissingSelection();
    }
  }, [onMissingSelection, selectedOpening, selection]);

  const options = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase();
    const matchingOpenings = filterOpeningCatalogue(openings, query).slice(
      0,
      OPENING_SEARCH_VISIBLE_LIMIT,
    );
    const allMatches = normalized === "" || "all openings".includes(normalized);
    const allOption = {
      value: ALL_OPENINGS_VALUE,
      label: "All openings",
      content: {
        primary: "All openings",
        secondary: "Search every opening",
      },
    };
    return [
      ...(allMatches ? [allOption] : []),
      ...matchingOpenings.map((opening) => ({
        value: opening.key,
        label: openingLabel(opening),
        content: {
          leading: <span className={styles.ecoBadge}>{opening.eco}</span>,
          primary: opening.name,
          trailing: (
            <span className={styles.routeCount}>
              {opening.route_count} {opening.route_count === 1 ? "line" : "lines"}
            </span>
          ),
        },
      })),
    ];
  }, [openings, query]);

  const effectiveSelection = selectedOpening
    ? { kind: "specific" as const, key: selectedOpening.key }
    : selection?.kind === "all"
      ? selection
      : null;
  const selectedValue =
    effectiveSelection?.kind === "specific"
      ? effectiveSelection.key
      : effectiveSelection?.kind === "all"
        ? ALL_OPENINGS_VALUE
        : null;
  const inputValue =
    selectedOpening?.name ?? (effectiveSelection?.kind === "all" ? "All openings" : query);
  const selectedEco = selectedOpening?.eco;

  function selectCommittedInput(
    event: FocusEvent<HTMLInputElement> | MouseEvent<HTMLInputElement>,
  ) {
    if (effectiveSelection !== null) {
      event.currentTarget.select();
    }
  }

  function handleValueChange(value: string | null) {
    if (value === null) {
      onQueryChange("");
      onSelectionChange(null);
      return;
    }
    if (value === ALL_OPENINGS_VALUE) {
      onQueryChange("");
      onSelectionChange({ kind: "all" });
      return;
    }
    const opening = openingsByKey.get(value);
    if (opening === undefined) {
      return;
    }
    onQueryChange("");
    onSelectionChange({ kind: "specific", key: opening.key });
  }

  function handleInputValueChange(value: string, reason: string) {
    if (reason === "input-change") {
      onSelectionChange(null);
      onQueryChange(value);
    } else if (reason === "input-clear" || reason === "clear-press") {
      onSelectionChange(null);
      onQueryChange("");
    }
  }

  return (
    <Combobox
      ariaLabel="Opening"
      disabled={disabled}
      inputValue={inputValue}
      leading={<Search aria-hidden="true" size={18} />}
      onInputClick={selectCommittedInput}
      onInputFocus={selectCommittedInput}
      onInputValueChange={handleInputValueChange}
      onValueChange={handleValueChange}
      options={options}
      placeholder="Search by name, ECO, or key"
      preferredPopupWidth="38rem"
      trailing={selectedEco ? <span className={styles.ecoBadge}>{selectedEco}</span> : null}
      value={selectedValue}
    />
  );
}
