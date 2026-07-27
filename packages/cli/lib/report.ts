import fs from "node:fs";
import { formatRegistryReport, loadRegistry } from "@vnkc/sdk";

export function cmdReportSources(opts: { registry: string }): void {
  if (!fs.existsSync(opts.registry)) {
    console.error(`✗ registry not found: ${opts.registry}`);
    process.exit(1);
  }
  const { registry, errors } = loadRegistry(opts.registry);
  if (errors.length > 0) {
    console.error(
      `⚠ registry has ${errors.length} validation problem(s); report may be unreliable`,
    );
  }
  console.log(formatRegistryReport(registry));
}
