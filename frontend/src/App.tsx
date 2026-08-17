import { AppShell } from "./features/app-shell/AppShell";
import { StatusPage } from "./features/status/StatusPage";

export default function App() {
  return (
    <AppShell>
      <StatusPage />
    </AppShell>
  );
}
