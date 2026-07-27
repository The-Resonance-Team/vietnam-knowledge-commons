#!/usr/bin/env tsx
import { Command } from "commander";
import { cmdValidateRecord, cmdValidateSources } from "./lib/validate.js";
import { cmdReportSources } from "./lib/report.js";

const program = new Command();

program
  .name("vnkc")
  .description("Viet Nam Knowledge Commons — Phase 0 validation CLI. Does not crawl anything.")
  .version("0.0.0");

program
  .command("validate-sources")
  .description("Validate the source registry against schemas/source-registry.schema.json")
  .option("--registry <path>", "path to sources.yaml", "registry/sources.yaml")
  .action(cmdValidateSources);

program
  .command("validate-record")
  .description("Validate example record(s) against their schemas")
  .option(
    "--file <path>",
    "validate a single JSON record; kind inferred from parent directory name",
  )
  .option("--all <dir>", "validate every JSON record under a directory tree (e.g. examples)")
  .action(cmdValidateRecord);

program
  .command("report-sources")
  .description("Print a summary report of the source registry")
  .option("--registry <path>", "path to sources.yaml", "registry/sources.yaml")
  .action(cmdReportSources);

program.parse();
