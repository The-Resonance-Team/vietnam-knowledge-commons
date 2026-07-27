import { fileURLToPath } from "node:url";
import path from "node:path";

// ponytail: resolves schemas/ relative to repo root — fine inside the monorepo;
// bundling the JSON into the package is a publish-time concern (see ADR-0002).
export const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
export const SCHEMAS_DIR = path.join(REPO_ROOT, "schemas");
export const REGISTRY_PATH = path.join(REPO_ROOT, "registry", "sources.yaml");
