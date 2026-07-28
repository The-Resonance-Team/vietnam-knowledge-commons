import * as fs from "fs";
import * as path from "path";

const DATA_DIR = path.join(__dirname, "../../../data");
const SHARD_SIZE = 1000;

interface Manifest {
  version: string;
  legal_documents: { count: number; index_file: string; shards: string; shard_size: number };
  administrative_units: { count: number; index_file: string; shards: string; shard_size: number };
  sources: { index_file: string };
  last_sync: string | null;
}

function buildLegalDocShards() {
  const metadataDir = path.join(DATA_DIR, "legal-docs/metadata");
  const fulltextDir = path.join(DATA_DIR, "legal-docs/fulltext");
  const shardsDir = path.join(DATA_DIR, "legal-docs/shards");

  if (!fs.existsSync(metadataDir)) {
    console.log("No legal-docs metadata found");
    return 0;
  }

  // Read index
  const indexPath = path.join(metadataDir, "index.json");
  if (!fs.existsSync(indexPath)) {
    console.log("No legal-docs index found");
    return 0;
  }

  const index = JSON.parse(fs.readFileSync(indexPath, "utf-8"));
  const docs = index.docs || [];

  if (docs.length === 0) {
    console.log("Legal-docs index empty");
    return 0;
  }

  // Load full records from individual metadata files
  const fullDocs: any[] = [];
  for (const entry of docs) {
    const metaPath = path.join(metadataDir, `${entry.id}.meta.json`);
    if (fs.existsSync(metaPath)) {
      const meta = JSON.parse(fs.readFileSync(metaPath, "utf-8"));

      // Load fulltext if exists
      const fulltextPath = path.join(fulltextDir, `${entry.id}.txt`);
      if (fs.existsSync(fulltextPath)) {
        meta.fullText = fs.readFileSync(fulltextPath, "utf-8");
      }

      fullDocs.push(meta);
    }
  }

  // Shard
  if (!fs.existsSync(shardsDir)) fs.mkdirSync(shardsDir, { recursive: true });

  const shardCount = Math.ceil(fullDocs.length / SHARD_SIZE);
  for (let i = 0; i < shardCount; i++) {
    const start = i * SHARD_SIZE;
    const end = start + SHARD_SIZE;
    const shardDocs = fullDocs.slice(start, end);

    const shard = {
      shard_id: `shard-${String(i + 1).padStart(3, "0")}`,
      docs: shardDocs,
    };

    const shardPath = path.join(shardsDir, `${shard.shard_id}.json`);
    fs.writeFileSync(shardPath, JSON.stringify(shard, null, 2));
  }

  // Update index with shard references
  for (let i = 0; i < docs.length; i++) {
    const shardIndex = Math.floor(i / SHARD_SIZE);
    docs[i].shard = `shard-${String(shardIndex + 1).padStart(3, "0")}`;
  }

  fs.writeFileSync(indexPath, JSON.stringify({ ...index, docs }, null, 2));

  return fullDocs.length;
}

function buildAdminUnitShards() {
  const metadataDir = path.join(DATA_DIR, "admin-units/metadata");
  const shardsDir = path.join(DATA_DIR, "admin-units/shards");

  if (!fs.existsSync(metadataDir)) {
    console.log("No admin-units metadata found");
    return 0;
  }

  const indexPath = path.join(metadataDir, "index.json");
  if (!fs.existsSync(indexPath)) {
    console.log("No admin-units index found");
    return 0;
  }

  const index = JSON.parse(fs.readFileSync(indexPath, "utf-8"));
  const units = index.units || [];

  if (units.length === 0) {
    console.log("Admin-units index empty");
    return 0;
  }

  // Load full records
  const fullUnits: any[] = [];
  for (const entry of units) {
    const metaPath = path.join(metadataDir, `${entry.code}.meta.json`);
    if (fs.existsSync(metaPath)) {
      const meta = JSON.parse(fs.readFileSync(metaPath, "utf-8"));
      fullUnits.push(meta);
    }
  }

  // Shard
  if (!fs.existsSync(shardsDir)) fs.mkdirSync(shardsDir, { recursive: true });

  const shardCount = Math.ceil(fullUnits.length / SHARD_SIZE);
  for (let i = 0; i < shardCount; i++) {
    const start = i * SHARD_SIZE;
    const end = start + SHARD_SIZE;
    const shardUnits = fullUnits.slice(start, end);

    const shard = {
      shard_id: `shard-${String(i + 1).padStart(3, "0")}`,
      units: shardUnits,
    };

    const shardPath = path.join(shardsDir, `${shard.shard_id}.json`);
    fs.writeFileSync(shardPath, JSON.stringify(shard, null, 2));
  }

  // Update index with shard references
  for (let i = 0; i < units.length; i++) {
    const shardIndex = Math.floor(i / SHARD_SIZE);
    units[i].shard = `shard-${String(shardIndex + 1).padStart(3, "0")}`;
  }

  fs.writeFileSync(indexPath, JSON.stringify({ ...index, units }, null, 2));

  return fullUnits.length;
}

function updateManifest(legalDocsCount: number, adminUnitsCount: number) {
  const manifestPath = path.join(DATA_DIR, "manifest.json");
  const manifest: Manifest = JSON.parse(fs.readFileSync(manifestPath, "utf-8"));

  manifest.legal_documents.count = legalDocsCount;
  manifest.administrative_units.count = adminUnitsCount;
  manifest.last_sync = new Date().toISOString();

  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
}

function main() {
  console.log("Building shards from metadata...");

  const legalDocsCount = buildLegalDocShards();
  console.log(
    `✓ Built ${Math.ceil(legalDocsCount / SHARD_SIZE)} shards for ${legalDocsCount} legal documents`,
  );

  const adminUnitsCount = buildAdminUnitShards();
  console.log(
    `✓ Built ${Math.ceil(adminUnitsCount / SHARD_SIZE)} shards for ${adminUnitsCount} administrative units`,
  );

  updateManifest(legalDocsCount, adminUnitsCount);
  console.log("✓ Updated manifest.json");

  console.log("Build complete");
}

main();
