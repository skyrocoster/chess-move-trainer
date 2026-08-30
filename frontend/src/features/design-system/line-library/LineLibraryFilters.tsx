import { Checkbox } from "@base-ui/react/checkbox";
import { Input } from "@base-ui/react/input";
import { Select } from "@base-ui/react/select";
import { Button } from "../Button";
import styles from "./LineLibrary.module.css";
import type {
  LineLibraryFilterApplyMode,
  LineLibraryFilterDefinition,
  LineLibraryFilterValue,
  LineLibraryFilterValues,
} from "./lineLibraryTypes";

function filterValueAsString(value: LineLibraryFilterValue | undefined): string {
  return value == null ? "" : String(value);
}

export interface LineLibraryFilterBarProps {
  definitions: readonly LineLibraryFilterDefinition[];
  values: LineLibraryFilterValues;
  mode: LineLibraryFilterApplyMode;
  onChange: (id: string, value: LineLibraryFilterValue) => void;
  onApply: () => void;
  disabled: boolean;
}

export function LineLibraryFilters({
  definitions,
  values,
  mode,
  onChange,
  onApply,
  disabled,
}: LineLibraryFilterBarProps) {
  if (definitions.length === 0) return null;

  return (
    <div className={styles.filters} aria-label="Line Library filters">
      {definitions.map((definition) => {
        const value = values[definition.id];
        const controlId = `line-library-filter-${definition.id}`;
        const kind = definition.kind ?? "text";

        if (kind === "boolean") {
          return (
            <label className={styles.booleanFilter} key={definition.id} htmlFor={controlId}>
              <Checkbox.Root
                id={controlId}
                className={styles.checkbox}
                checked={value === true}
                disabled={disabled}
                onCheckedChange={(checked) => onChange(definition.id, checked)}
              >
                <Checkbox.Indicator className={styles.checkboxIndicator}>✓</Checkbox.Indicator>
              </Checkbox.Root>
              <span>{definition.label}</span>
            </label>
          );
        }

        if (kind === "select") {
          return (
            <label className={styles.filterField} key={definition.id} htmlFor={controlId}>
              <span className={styles.filterLabel}>{definition.label}</span>
              <Select.Root
                value={filterValueAsString(value)}
                disabled={disabled}
                onValueChange={(nextValue) => onChange(definition.id, nextValue ?? "")}
              >
                <Select.Trigger id={controlId} className={styles.selectTrigger}>
                  <Select.Value placeholder={definition.placeholder ?? "Choose"} />
                </Select.Trigger>
                <Select.Portal>
                  <Select.Positioner className={styles.selectPositioner} sideOffset={4}>
                    <Select.Popup className={styles.selectPopup}>
                      <Select.List>
                        {(definition.options ?? []).map((option) => (
                          <Select.Item
                            className={styles.selectItem}
                            key={option.value}
                            value={option.value}
                          >
                            <Select.ItemText>{option.label}</Select.ItemText>
                          </Select.Item>
                        ))}
                      </Select.List>
                    </Select.Popup>
                  </Select.Positioner>
                </Select.Portal>
              </Select.Root>
            </label>
          );
        }

        return (
          <label className={styles.filterField} key={definition.id} htmlFor={controlId}>
            <span className={styles.filterLabel}>{definition.label}</span>
            <Input
              id={controlId}
              className={styles.input}
              type={kind === "search" ? "search" : "text"}
              value={filterValueAsString(value)}
              placeholder={definition.placeholder}
              disabled={disabled}
              onValueChange={(nextValue) => onChange(definition.id, nextValue)}
            />
          </label>
        );
      })}
      {mode === "explicit" ? (
        <Button type="button" size="sm" variant="secondary" onClick={onApply} disabled={disabled}>
          Apply filters
        </Button>
      ) : null}
    </div>
  );
}
