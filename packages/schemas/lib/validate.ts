import fs from "node:fs";
import path from "node:path";
import Ajv, { type ErrorObject } from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import { SCHEMAS_DIR } from "./paths.js";

export const SCHEMA_KINDS = [
  "source",
  "source-registry",
  "legal-document",
  "administrative-procedure",
  "official-form",
  "organization",
  "jurisdiction",
  "relationship",
  "dataset-release",
  "provenance",
] as const;

export type SchemaKind = (typeof SCHEMA_KINDS)[number];

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

let ajv: Ajv | undefined;

function getAjv(): Ajv {
  if (ajv) return ajv;
  ajv = new Ajv({ allErrors: true, strict: false });
  addFormats(ajv);
  for (const file of fs.readdirSync(SCHEMAS_DIR)) {
    if (!file.endsWith(".schema.json")) continue;
    const schema = JSON.parse(fs.readFileSync(path.join(SCHEMAS_DIR, file), "utf8"));
    ajv.addSchema(schema);
  }
  return ajv;
}

export function loadSchema(kind: SchemaKind): object {
  return JSON.parse(fs.readFileSync(path.join(SCHEMAS_DIR, `${kind}.schema.json`), "utf8"));
}

function formatError(err: ErrorObject): string {
  return `${err.instancePath || "(root)"} ${err.message ?? "invalid"}`;
}

export function validateRecord(kind: SchemaKind, data: unknown): ValidationResult {
  const validate = getAjv().getSchema(`${kind}.schema.json`);
  if (!validate) {
    return { valid: false, errors: [`unknown schema kind: ${kind}`] };
  }
  const valid = validate(data);
  return { valid: Boolean(valid), errors: (validate.errors ?? []).map(formatError) };
}
