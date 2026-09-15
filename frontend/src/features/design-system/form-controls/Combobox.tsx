import { Combobox as BaseCombobox } from "@base-ui/react/combobox";
import { ChevronDown, X } from "lucide-react";
import type { CSSProperties, FocusEventHandler, ReactNode } from "react";

import styles from "./FormControls.module.css";
import {
  DropdownItemBody,
  DropdownMessage,
  dropdownPositionerProps,
  type DropdownOptionDefinition,
} from "./private/DropdownParts";

export interface ComboboxProps {
  options: readonly DropdownOptionDefinition[];
  value: string | null;
  onValueChange: (value: string | null) => void;
  inputValue?: string;
  onInputValueChange?: (value: string, reason: string) => void;
  onInputFocus?: FocusEventHandler<HTMLInputElement>;
  placeholder?: string;
  disabled?: boolean;
  readOnly?: boolean;
  required?: boolean;
  loading?: boolean;
  loadingContent?: ReactNode;
  emptyContent?: ReactNode;
  leading?: ReactNode;
  trailing?: ReactNode;
  ariaLabel?: string;
  preferredPopupWidth?: string;
}

export function Combobox({
  options,
  value,
  onValueChange,
  inputValue,
  onInputValueChange,
  onInputFocus,
  placeholder = "Search options",
  disabled,
  readOnly,
  required,
  loading = false,
  loadingContent = "Loading…",
  emptyContent = "No options found.",
  leading,
  trailing,
  ariaLabel,
  preferredPopupWidth,
}: ComboboxProps) {
  const visibleOptions = loading ? [] : options;
  const labelFor = (optionValue: string) =>
    options.find((option) => option.value === optionValue)?.label ?? optionValue;

  return (
    <BaseCombobox.Root
      items={visibleOptions.map((option) => option.value)}
      itemToStringLabel={labelFor}
      filter={(optionValue, query) => labelFor(optionValue).toLocaleLowerCase().includes(query.toLocaleLowerCase())}
      value={value}
      onValueChange={(next) => onValueChange(next)}
      inputValue={inputValue}
      onInputValueChange={(next, details) => onInputValueChange?.(next, details.reason)}
      disabled={disabled}
      readOnly={readOnly}
      required={required}
      modal={false}
      openOnInputClick
    >
      <BaseCombobox.InputGroup className={styles.inputFrame}>
        {leading ? <span className={styles.inputSlot}>{leading}</span> : null}
        <BaseCombobox.Input
          className={styles.textInput}
          aria-label={ariaLabel}
          onFocus={onInputFocus}
          placeholder={placeholder}
        />
        {trailing ? <span className={styles.inputSlot}>{trailing}</span> : null}
        <BaseCombobox.Clear className={styles.iconButton} aria-label="Clear selection">
          <X aria-hidden="true" size={17} />
        </BaseCombobox.Clear>
        <BaseCombobox.Trigger className={styles.iconButton} aria-label="Show options">
          <ChevronDown aria-hidden="true" size={18} />
        </BaseCombobox.Trigger>
      </BaseCombobox.InputGroup>
      <BaseCombobox.Portal>
        <BaseCombobox.Positioner
          {...dropdownPositionerProps}
          className={styles.dropdownPositioner}
          style={{ "--preferred-popup-width": preferredPopupWidth } as CSSProperties}
        >
          <BaseCombobox.Popup className={styles.dropdownPopup}>
            <BaseCombobox.List className={styles.dropdownList}>
              {(optionValue: string, index: number) => {
                const option = visibleOptions.find((candidate) => candidate.value === optionValue);
                if (!option) return null;
                return (
                  <BaseCombobox.Item
                    aria-label={option.label}
                    className={styles.dropdownItem}
                    disabled={option.disabled}
                    index={index}
                    key={option.value}
                    value={option.value}
                  >
                    <DropdownItemBody
                      option={option}
                      indicator={<BaseCombobox.ItemIndicator>✓</BaseCombobox.ItemIndicator>}
                    />
                  </BaseCombobox.Item>
                );
              }}
            </BaseCombobox.List>
            <BaseCombobox.Empty className={styles.dropdownMessage}>
              {loading ? loadingContent : emptyContent}
            </BaseCombobox.Empty>
            <BaseCombobox.Status className={styles.visuallyHidden}>
              {loading ? "Loading options" : `${visibleOptions.length} options available`}
            </BaseCombobox.Status>
          </BaseCombobox.Popup>
        </BaseCombobox.Positioner>
      </BaseCombobox.Portal>
    </BaseCombobox.Root>
  );
}
