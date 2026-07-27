import fs from "node:fs";
import path from "node:path";
import { SCHEMA_KINDS, validateRecord, type SchemaKind } from "@vnkc/schemas";
import { loadRegistry } from "@vnkc/sdk";

function fail(message: string): never {
  console.error(`✗ ${message}`);
  process.exit(1);
}

export function cmdValidateSources(opts: { registry: string }): void {
  if (!fs.existsSync(opts.registry)) fail(`registry not found: ${opts.registry}`);
  const { registry, errors } = loadRegistry(opts.registry);
  if (errors.length > 0) {
    console.error(`✗ ${opts.registry} — ${errors.length} problem(s):`);
    for (const e of errors) console.error(`  - ${e}`);
    process.exit(1);
  }
  console.log(`✓ ${opts.registry} — ${registry.sources.length} sources valid`);
}

function isSchemaKind(name: string): name is SchemaKind {
  return (SCHEMA_KINDS as readonly string[]).includes(name);
}

function* walkJson(dir: string): Generator<string> {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) yield* walkJson(full);
    else if (entry.name.endsWith(".json")) yield full;
  }
}

function validateOne(file: string): string[] {
  const kind = path.basename(path.dirname(file));
  if (!isSchemaKind(kind)) {
    return [`${file}: parent directory '${kind}' is not a known schema kind`];
  }
  const data = JSON.parse(fs.readFileSync(file, "utf8"));
  return validateRecord(kind, data).errors.map((e) => `${file}: ${e}`);
}

export function cmdValidateRecord(opts: { file?: string; all?: string }): void {
  const errors: string[] = [];
  if (opts.file) {
    errors.push(...validateOne(opts.file));
  } else if (opts.all) {
    let count = 0;
    for (const file of walkJson(opts.all)) {
      count++;
      errors.push(...validateOne(file));
    }
    if (count === 0) fail(`no JSON records found under ${opts.all}`);
  } else {
    fail("pass --file <path> or --all <dir>");
  }

  if (errors.length > 0) {
    console.error(`✗ ${errors.length} validation error(s):`);
    for (const e of errors) console.error(`  - ${e}`);
    process.exit(1);
  }
  console.log(`✓ all records valid`);
}
