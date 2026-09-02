import type { PositionPickerNavigation } from "./positionPickerSession";

type HistorySelectionHandler = (selection: PositionPickerNavigation, status: string) => void;

export function historyNavigationHandlers(onSelection: HistorySelectionHandler) {
  return {
    next: () => onSelection("next", "Moved to the next local position."),
    previous: () => onSelection("previous", "Moved to the previous local position."),
  };
}

export function cancelPromotionWithStatus(
  cancelPromotion: () => void,
  setSessionStatus: (status: string) => void,
) {
  cancelPromotion();
  setSessionStatus("Promotion cancelled; the current position is unchanged.");
}
