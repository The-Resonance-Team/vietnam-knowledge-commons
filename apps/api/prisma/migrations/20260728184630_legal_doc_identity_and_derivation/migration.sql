-- ADR-0004: legal document identity moves from [document_number, issue_date,
-- document_type] to the source page, and document_type adopts the canonical
-- English vocabulary from schemas/legal-document.schema.json.
--
-- DESTRUCTIVE. Verified safe only because every table was empty when this was
-- generated (legal_documents n_live_tup = 0, one prior migration applied):
--   * "title" is DROPPED, not renamed. It held a citation, not a subject; the
--     replacement columns are citation_title and subject_slug.
--   * The DocumentType enum is rebuilt. The old Vietnamese members
--     (hien_phap, bo_luat, luat, ...) cease to exist, so the USING cast on
--     line 10 below would fail on any pre-existing row.
--   * canonical_id and document_type_basis are added NOT NULL with no default.
-- Re-check row counts before applying this to any database holding data.

-- CreateEnum
CREATE TYPE "DocumentTypeBasis" AS ENUM ('title_prefix', 'number_suffix', 'fallback');

-- CreateEnum
CREATE TYPE "FetchStatus" AS ENUM ('fetched', 'discovered');

-- AlterEnum
BEGIN;
CREATE TYPE "DocumentType_new" AS ENUM ('constitution', 'code', 'law', 'ordinance', 'resolution', 'decree', 'decision', 'circular', 'joint-circular', 'directive', 'official-dispatch', 'treaty', 'consolidated-document', 'promulgation-order', 'historic-ordinance', 'other');
ALTER TABLE "legal_documents" ALTER COLUMN "document_type" TYPE "DocumentType_new" USING ("document_type"::text::"DocumentType_new");
ALTER TYPE "DocumentType" RENAME TO "DocumentType_old";
ALTER TYPE "DocumentType_new" RENAME TO "DocumentType";
DROP TYPE "public"."DocumentType_old";
COMMIT;

-- DropIndex
DROP INDEX "legal_documents_document_number_issue_date_document_type_key";

-- AlterTable
ALTER TABLE "legal_documents" DROP COLUMN "title",
ADD COLUMN     "canonical_id" TEXT NOT NULL,
ADD COLUMN     "citation_title" TEXT,
ADD COLUMN     "content_checksum" TEXT,
ADD COLUMN     "document_number_raw" TEXT,
ADD COLUMN     "document_type_basis" "DocumentTypeBasis" NOT NULL,
ADD COLUMN     "fetch_status" "FetchStatus" NOT NULL DEFAULT 'discovered',
ADD COLUMN     "issuing_authority_code" TEXT,
ADD COLUMN     "subject_slug" TEXT,
ALTER COLUMN "document_number" DROP NOT NULL,
ALTER COLUMN "issue_date" DROP NOT NULL,
ALTER COLUMN "effective_date" DROP NOT NULL,
ALTER COLUMN "issuing_body" DROP NOT NULL;

-- CreateIndex
CREATE UNIQUE INDEX "legal_documents_canonical_id_key" ON "legal_documents"("canonical_id");

-- CreateIndex
CREATE INDEX "legal_documents_document_number_idx" ON "legal_documents"("document_number");

-- CreateIndex
CREATE INDEX "legal_documents_fetch_status_idx" ON "legal_documents"("fetch_status");

-- CreateIndex
CREATE UNIQUE INDEX "legal_documents_source_url_key" ON "legal_documents"("source_url");

