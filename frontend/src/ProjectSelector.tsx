import React, { useState, useEffect } from "react";

interface ProjectMeta {
  project_id: string;
  path: string;
  created: string;
}

interface Props {
  onSelect: (projectId: string) => void;
}

export const ProjectSelector: React.FC<Props> = ({ onSelect }) => {
  const [name, setName] = useState("My First App");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [existing, setExisting] = useState<ProjectMeta[]>([]);

  const loadProjects = async () => {
    try {
      const res = await fetch("/api/projects");
      const data = await res.json();
      if (res.ok) setExisting(data.projects || []);
    } catch {
      /* backend may not be up yet */
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const createProject = async () => {
    setLoading(true);
    setError(null);
    const projectId = crypto.randomUUID();

    try {
      const res = await fetch("/api/project/provision", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: projectId, project_name: name }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Provisioning failed");
      }
      onSelect(projectId);
    } catch (err: any) {
      setError(
        err.message ||
          "Could not reach the orchestrator. Is the backend running on :8000?"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 p-6">
      <div className="w-full max-w-md space-y-8">
        <div className="space-y-2 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Lovable Studio Engine
          </h1>
          <p className="text-sm text-slate-400">
            Self-hosted · Plan mode · Visual edits · Zero lock-in · Vanilla
            Postgres
          </p>
        </div>

        <div className="space-y-5 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-slate-400">
              Project name
            </label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="My awesome SaaS"
            />
          </div>

          {error && (
            <div className="rounded-lg border border-red-900 bg-red-950/50 px-3 py-2 text-xs text-red-300">
              {error}
            </div>
          )}

          <button
            onClick={createProject}
            disabled={loading || !name.trim()}
            className="w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-700"
          >
            {loading ? "Provisioning sandbox…" : "Create new project"}
          </button>

          {existing.length > 0 && (
            <>
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-800" />
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="bg-slate-900 px-2 text-slate-500">
                    existing projects
                  </span>
                </div>
              </div>
              <div className="max-h-40 space-y-1.5 overflow-y-auto">
                {existing.map((p) => (
                  <button
                    key={p.project_id}
                    type="button"
                    onClick={() => onSelect(p.project_id)}
                    className="flex w-full items-center justify-between rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-left text-xs transition hover:border-slate-600 hover:bg-slate-900"
                  >
                    <span className="truncate font-mono text-slate-300">
                      {p.project_id.slice(0, 8)}…
                    </span>
                    <span className="text-[10px] text-slate-600">
                      {new Date(p.created).toLocaleDateString()}
                    </span>
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        <p className="text-center text-[11px] text-slate-600">
          Backend must be running at{" "}
          <code className="text-slate-500">localhost:8000</code>
        </p>
      </div>
    </div>
  );
};
