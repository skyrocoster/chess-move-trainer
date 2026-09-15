import { Checkbox } from "@base-ui/react/checkbox";
import { Button } from "../Button";
import { Field } from "../form-controls/Field";
import { Select } from "../form-controls/Select";
import { TextInput } from "../form-controls/TextInput";
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
            <Field
              className={styles.booleanFilter}
              disabled={disabled}
              htmlFor={controlId}
              key={definition.id}
              label={definition.label}
            >
              <Checkbox.Root
                id={controlId}
                className={styles.checkbox}
                checked={value === true}
                disabled={disabled}
                onCheckedChange={(checked) => onChange(definition.id, checked)}
              >
                <Checkbox.Indicator className={styles.checkboxIndicator}>✓</Checkbox.Indicator>
              </Checkbox.Root>
            </Field>
          );
        }

        if (kind === "select") {
          return (
            <Field
              className={styles.filterField}
              disabled={disabled}
              key={definition.id}
              label={definition.label}
            >
              <Select
                ariaLabel={definition.label}
                disabled={disabled}
                options={(definition.options ?? []).map((option) => ({
                  value: option.value,
                  label: option.label,
                }))}
                value={filterValueAsString(value)}
                placeholder={definition.placeholder ?? "Choose"}
                onValueChange={(nextValue) => onChange(definition.id, nextValue ?? "")}
              />
            </Field>
          );
        }

        return (
          <Field
            className={styles.filterField}
            disabled={disabled}
            key={definition.id}
            label={definition.label}
          >
            <TextInput
              id={controlId}
              type={kind === "search" ? "search" : "text"}
              value={filterValueAsString(value)}
              placeholder={definition.placeholder}
              disabled={disabled}
              onChange={(event) => onChange(definition.id, event.currentTarget.value)}
            />
          </Field>
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
