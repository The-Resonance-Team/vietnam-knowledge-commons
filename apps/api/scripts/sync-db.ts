import * as fs from "fs";
import * as path from "path";

const prisma = new (require("@prisma/client").PrismaClient)();

const DATA_DIR = path.join(__dirname, "../../../data");

async function syncLegalDocs() {
  const shardsDir = path.join(DATA_DIR, "legal-docs/shards");
  if (!fs.existsSync(shardsDir)) {
    console.log("No legal-docs shards found");
    return 0;
  }

  const shardFiles = fs.readdirSync(shardsDir).filter((f) => f.endsWith(".json"));
  let count = 0;

  for (const file of shardFiles) {
    const shard = JSON.parse(fs.readFileSync(path.join(shardsDir, file), "utf-8"));
    const docs = shard.docs || [];

    for (const doc of docs) {
      await prisma.legalDocument.upsert({
        where: {
          documentNumber_issueDate_documentType: {
            documentNumber: doc.documentNumber,
            issueDate: new Date(doc.issueDate),
            documentType: doc.documentType,
          },
        },
        update: {
          title: doc.title,
          titleEn: doc.titleEn,
          effectiveDate: new Date(doc.effectiveDate),
          expiryDate: doc.expiryDate ? new Date(doc.expiryDate) : null,
          issuingBody: doc.issuingBody,
          fullText: doc.fullText,
          scope: doc.scope,
          sourceUrl: doc.sourceUrl,
          retrievedAt: new Date(doc.retrievedAt),
          keywords: doc.keywords || [],
          abstract: doc.abstract,
        },
        create: {
          documentType: doc.documentType,
          documentNumber: doc.documentNumber,
          title: doc.title,
          titleEn: doc.titleEn,
          issueDate: new Date(doc.issueDate),
          effectiveDate: new Date(doc.effectiveDate),
          expiryDate: doc.expiryDate ? new Date(doc.expiryDate) : null,
          issuingBody: doc.issuingBody,
          fullText: doc.fullText,
          scope: doc.scope,
          sourceId: doc.sourceId || (await getOrCreateSource(doc.sourceUrl)),
          sourceUrl: doc.sourceUrl,
          retrievedAt: new Date(doc.retrievedAt),
          keywords: doc.keywords || [],
          abstract: doc.abstract,
        },
      });
      count++;
    }
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

async function getOrCreateSource(sourceUrl: string): Promise<string> {
  const domain = new URL(sourceUrl).hostname;
  const source = await prisma.source.upsert({
    where: { name: domain },
    update: {},
    create: {
      name: domain,
      baseUrl: `https://${domain}`,
      sourceType: "legal",
      license: "public domain",
      rateLimitSeconds: 1.5,
    },
  });
  return source.id;
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
