import { ErrorBoundary, type FallbackProps } from "react-error-boundary";

import { PageFeedback } from "../design-system/feedback/PageFeedback";
import styles from "./PageContentBoundary.module.css";

function BoundaryFallback({
  onReset,
  resetErrorBoundary,
}: FallbackProps & { onReset?: () => void }) {
  const handleReset = () => {
    onReset?.();
    resetErrorBoundary();
  };

  return (
    <div className={styles.fallback} role="region" aria-labelledby="page-unavailable-heading">
      <PageFeedback
        severity="error"
        heading="Page unavailable"
        message="Something went wrong while displaying this page."
      />
      <button className={styles.retry} type="button" onClick={handleReset}>
        Try again
      </button>
    </div>
  );
}

interface PageContentBoundaryProps {
  children: React.ReactNode;
  onReset?: () => void;
}

export function PageContentBoundary({ children, onReset }: PageContentBoundaryProps) {
  return (
    <ErrorBoundary fallbackRender={(props) => <BoundaryFallback {...props} onReset={onReset} />}>
      {children}
    </ErrorBoundary>
  );
}
