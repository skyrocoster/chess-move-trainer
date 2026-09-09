import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";

import { AppShell } from "./features/app-shell/AppShell";
import PageNotFoundView from "./features/app-shell/PageNotFoundView";
import { StatusPage } from "./features/status/StatusPage";

const RepertoireBuilderWorkspace = lazy(
  () => import("./features/repertoire-builder/RepertoireBuilderWorkspace"),
);

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<StatusPage />} />
        <Route
          path="/repertoire"
          element={
            <Suspense fallback={<p role="status">Loading Repertoire Builder...</p>}>
              <RepertoireBuilderWorkspace />
            </Suspense>
          }
        />
        <Route path="*" element={<PageNotFoundView />} />
      </Routes>
    </AppShell>
  );
}
