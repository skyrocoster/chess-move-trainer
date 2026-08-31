import { Save as SaveIcon, Trash2 } from "lucide-react";

import { Button, type ButtonProps } from "../design-system/Button";
import styles from "./PreferredMoveActionButtons.module.css";

export type PreferredMoveActionButtonProps = Omit<ButtonProps, "children" | "variant"> & {
  pending?: boolean;
};

function actionClass(className: string | undefined): string {
  return [styles.actionButton, className].filter(Boolean).join(" ");
}

export function SavePreferredMoveButton({
  pending = false,
  disabled = false,
  className,
  ...props
}: PreferredMoveActionButtonProps) {
  return (
    <Button
      {...props}
      variant="primary"
      className={actionClass(className)}
      disabled={disabled || pending}
      aria-busy={pending || undefined}
    >
      <SaveIcon className={styles.actionIcon} aria-hidden="true" focusable="false" />
      <span>Save</span>
    </Button>
  );
}

export function RemovePreferredMoveButton({
  pending = false,
  disabled = false,
  className,
  ...props
}: PreferredMoveActionButtonProps) {
  return (
    <Button
      {...props}
      variant="ghost"
      className={actionClass([styles.removeButton, className].filter(Boolean).join(" "))}
      disabled={disabled || pending}
      aria-busy={pending || undefined}
    >
      <Trash2 className={styles.actionIcon} aria-hidden="true" focusable="false" />
      <span>Remove</span>
    </Button>
  );
}
