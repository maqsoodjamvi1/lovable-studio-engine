import React, { useState } from "react";
import { WorkspaceDashboard } from "./WorkspaceDashboard";
import { ProjectSelector } from "./ProjectSelector";

export default function App() {
  const [projectId, setProjectId] = useState<string | null>(null);

  if (!projectId) {
    return <ProjectSelector onSelect={setProjectId} />;
  }

  return <WorkspaceDashboard projectId={projectId} onBack={() => setProjectId(null)} />;
}
