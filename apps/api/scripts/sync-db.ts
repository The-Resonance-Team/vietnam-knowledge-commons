import "dotenv/config";
import * as fs from "fs";
import * as path from "path";
import { PrismaClient, DocumentType, DocumentScope } from "@generated/client";
import { PrismaPg } from "@prisma/adapter-pg";

const adapter = new PrismaPg({
  connectionString: process.env.DATABASE_URL,
});

const prisma = new PrismaClient({ adapter });

const DATA_DIR = path.join(__dirname, "../../../data");

// Shards hold records in the canonical JSON Schema shape (snake_case, English
// document_type vocabulary) — see ADR-0004. Prisma enum identifiers cannot
// contain hyphens, so `joint-circular` is stored via @map but addressed as
// `joint_circular` through the client.
const toEnum = (v: string) => v.replace(/-/g, "_") as DocumentType;

// The schema omits fields it cannot supply rather than nulling them, so that
// "unknown" stays distinguishable from "asserted". Absent therefore means null.
const toDate = (v?: string | null) => (v ? new Date(v) : null);

// `jurisdiction` in the published record; `scope` in the DB.
const SCOPE: Record<string, DocumentScope> = { national: "nationwide", provincial: "provincial" };

const CHUNK = 25;

function fields(doc: any, sourceId: string) {
  return {
    canonicalId: doc.canonical_id,
    documentType: toEnum(doc.document_type),
    documentTypeBasis: doc.document_type_basis,
    documentNumber: doc.document_number ?? null,
    documentNumberRaw: doc.document_number_raw ?? null,
    // `title` in the published record is a citation, not a subject. See CONTEXT.md.
    citationTitle: doc.title ?? null,
    subjectSlug: doc.subject_slug ?? null,
    titleEn: doc.title_en ?? null,
    issueDate: toDate(doc.issue_date),
    effectiveDate: toDate(doc.effective_from),
    expiryDate: toDate(doc.effective_to),
    issuingAuthorityCode: doc.issuing_authority_code ?? null,
    issuingBody: doc.issuing_authority ?? null,
    fullText: doc.full_text ?? null,
    fetchStatus: doc.fetch_status,
    contentChecksum: doc.content_checksum ?? null,
    scope: SCOPE[doc.jurisdiction] ?? "nationwide",
    sourceId,
    sourceUrl: doc.official_url,
    retrievedAt: new Date(doc.retrieved_at),
    keywords: doc.keywords || [],
  };
}

async function syncLegalDocs() {
  const shardsDir = path.join(DATA_DIR, "legal-docs/shards");
  if (!fs.existsSync(shardsDir)) {
    console.log("No legal-docs shards found");
    return 0;
  }

  const shardFiles = fs
    .readdirSync(shardsDir)
    .filter((f) => f.startsWith("shard-") && f.endsWith(".json"))
    .sort();
  let count = 0;

  for (const file of shardFiles) {
    const parsed = JSON.parse(fs.readFileSync(path.join(shardsDir, file), "utf-8"));
    // Shards are plain arrays. Tolerate the legacy {docs:[...]} envelope.
    const docs: any[] = Array.isArray(parsed) ? parsed : parsed.docs || [];

    for (let i = 0; i < docs.length; i += CHUNK) {
      await Promise.all(
        docs.slice(i, i + CHUNK).map(async (doc) => {
          const sourceId = await getOrCreateSource(doc.official_url);
          const data = fields(doc, sourceId);
          // Identity is the source page (ADR-0004), not the document number.
          await prisma.legalDocument.upsert({
            where: { sourceUrl: data.sourceUrl },
            update: data,
            create: data,
          });
        }),
      );
      count += Math.min(CHUNK, docs.length - i);
    }
    console.log(`  ${file}: ${docs.length}`);
  }

  return count;
}

async function syncAdminUnits() {
  const shardsDir = path.join(DATA_DIR, "admin-units/shards");
  if (!fs.existsSync(shardsDir)) {
    console.log("No admin-units shards found");
    return 0;
  }

  const shardFiles = fs.readdirSync(shardsDir).filter((f) => f.endsWith(".json"));
  let count = 0;

  for (const file of shardFiles) {
    const shard = JSON.parse(fs.readFileSync(path.join(shardsDir, file), "utf-8"));
    const units = shard.units || [];

    for (const unit of units) {
      await prisma.administrativeUnit.upsert({
        where: { code: unit.code },
        update: {
          name: unit.name,
          nameEn: unit.nameEn,
          level: unit.level,
          validFrom: new Date(unit.validFrom),
          validTo: unit.validTo ? new Date(unit.validTo) : null,
          population: unit.population,
          areaKm2: unit.areaKm2,
          sourceUrl: unit.sourceUrl,
        },
        create: {
          code: unit.code,
          name: unit.name,
          nameEn: unit.nameEn,
          level: unit.level,
          validFrom: new Date(unit.validFrom),
          validTo: unit.validTo ? new Date(unit.validTo) : null,
          population: unit.population,
          areaKm2: unit.areaKm2,
          sourceUrl: unit.sourceUrl,
        },
      });
      count++;
    }
  }

  return count;
}

// Memoised: every document in a shard shares a handful of hosts, and without
// this the sync issues one source upsert per document.
const sourceIds = new Map<string, Promise<string>>();

function getOrCreateSource(sourceUrl: string): Promise<string> {
  const domain = new URL(sourceUrl).hostname;
  const cached = sourceIds.get(domain);
  if (cached) return cached;

  const pending: Promise<string> = prisma.source
    .upsert({
      where: { name: domain },
      update: {},
      create: {
        name: domain,
        baseUrl: `https://${domain}`,
        sourceType: "legal",
        // DATA_POLICY.md: sources that publish official texts without an
        // explicit redistribution licence are reference-only, not public domain.
        license: "reference-only",
        rateLimitSeconds: 1.5,
      },
    })
    .then((s: { id: string }) => s.id);
  sourceIds.set(domain, pending);
  return pending;
}

async function main() {
  console.log("Syncing JSON data to database...");

  const legalDocsCount = await syncLegalDocs();
  console.log(`✓ Synced ${legalDocsCount} legal documents`);

  const adminUnitsCount = await syncAdminUnits();
  console.log(`✓ Synced ${adminUnitsCount} administrative units`);

  console.log("Sync complete");
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
