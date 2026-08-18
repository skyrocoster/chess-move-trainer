import { Route, Routes } from "react-router-dom";

import { AppShell } from "./features/app-shell/AppShell";
import PageNotFoundView from "./features/app-shell/PageNotFoundView";
import { StatusPage } from "./features/status/StatusPage";
import ViewerWorkspace from "./features/viewer/ViewerWorkspace";

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<StatusPage />} />
        <Route path="/viewer" element={<ViewerWorkspace />} />
        <Route path="*" element={<PageNotFoundView />} />
      </Routes>
    </AppShell>
  );
}
