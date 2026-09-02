import { useCallback, useState } from "react";

export function useMoveResponseSelection(fen: string, bottomColor: "white" | "black") {
  const [selectedResponse, setSelectedResponse] = useState<{
    key: string;
    uci: string;
  } | null>(null);
  const responseRequestKey = `${fen}\u0000${bottomColor}`;
  const selectedUci = selectedResponse?.key === responseRequestKey ? selectedResponse.uci : null;
  const clear = useCallback(() => setSelectedResponse(null), []);
  const select = useCallback(
    (uci: string) => setSelectedResponse({ key: responseRequestKey, uci }),
    [responseRequestKey],
  );

  return { clear, select, selectedUci };
}
