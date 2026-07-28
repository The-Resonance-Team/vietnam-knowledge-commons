-- CreateEnum
CREATE TYPE "AdminUnitLevel" AS ENUM ('province', 'district', 'ward');

-- CreateEnum
CREATE TYPE "DocumentType" AS ENUM ('hien_phap', 'bo_luat', 'luat', 'nghi_quyet', 'phap_lenh', 'nghi_dinh', 'quyet_dinh', 'thong_tu', 'chi_thi');

-- CreateEnum
CREATE TYPE "DocumentScope" AS ENUM ('nationwide', 'provincial', 'district', 'ward');

-- CreateEnum
CREATE TYPE "FileType" AS ENUM ('pdf', 'docx', 'xlsx', 'other');

-- CreateEnum
CREATE TYPE "SourceType" AS ENUM ('legal', 'administrative', 'gazette', 'ministry');

-- CreateTable
CREATE TABLE "administrative_units" (
    "id" UUID NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "name_en" TEXT,
    "level" "AdminUnitLevel" NOT NULL,
    "valid_from" TIMESTAMP(3) NOT NULL,
    "valid_to" TIMESTAMP(3),
    "parent_id" UUID,
    "population" INTEGER,
    "area_km2" DOUBLE PRECISION,
    "source_url" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "administrative_units_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "admin_unit_relations" (
    "id" UUID NOT NULL,
    "predecessor_id" UUID NOT NULL,
    "successor_id" UUID NOT NULL,
    "relationship_type" TEXT NOT NULL DEFAULT 'merger',
    "effective_date" TIMESTAMP(3) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "admin_unit_relations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "legal_documents" (
    "id" UUID NOT NULL,
    "document_type" "DocumentType" NOT NULL,
    "document_number" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "title_en" TEXT,
    "issue_date" TIMESTAMP(3) NOT NULL,
    "effective_date" TIMESTAMP(3) NOT NULL,
    "expiry_date" TIMESTAMP(3),
    "issuing_body" TEXT NOT NULL,
    "full_text" TEXT,
    "scope" "DocumentScope" NOT NULL DEFAULT 'nationwide',
    "source_id" UUID NOT NULL,
    "source_url" TEXT NOT NULL,
    "retrieved_at" TIMESTAMP(3) NOT NULL,
    "keywords" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "abstract" TEXT,
    "is_duplicate" BOOLEAN NOT NULL DEFAULT false,
    "canonical_doc_id" UUID,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "legal_documents_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "files" (
    "id" UUID NOT NULL,
    "legal_document_id" UUID NOT NULL,
    "filename" TEXT NOT NULL,
    "file_type" "FileType" NOT NULL,
    "file_size_bytes" INTEGER NOT NULL,
    "storage_url" TEXT NOT NULL,
    "source_url" TEXT NOT NULL,
    "checksum_sha256" TEXT NOT NULL,
    "retrieved_at" TIMESTAMP(3) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "files_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "sources" (
    "id" UUID NOT NULL,
    "name" TEXT NOT NULL,
    "base_url" TEXT NOT NULL,
    "source_type" "SourceType" NOT NULL,
    "license" TEXT NOT NULL DEFAULT 'public domain',
    "rate_limit_seconds" DOUBLE PRECISION NOT NULL DEFAULT 1.5,
    "description" TEXT,
    "contact" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "sources_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "_DocumentAppliesToUnits" (
    "A" UUID NOT NULL,
    "B" UUID NOT NULL,

    CONSTRAINT "_DocumentAppliesToUnits_AB_pkey" PRIMARY KEY ("A","B")
);

-- CreateIndex
CREATE UNIQUE INDEX "administrative_units_code_key" ON "administrative_units"("code");

-- CreateIndex
CREATE UNIQUE INDEX "admin_unit_relations_predecessor_id_successor_id_relationsh_key" ON "admin_unit_relations"("predecessor_id", "successor_id", "relationship_type");

-- CreateIndex
CREATE INDEX "legal_documents_document_type_idx" ON "legal_documents"("document_type");

-- CreateIndex
CREATE INDEX "legal_documents_issue_date_idx" ON "legal_documents"("issue_date");

-- CreateIndex
CREATE INDEX "legal_documents_effective_date_idx" ON "legal_documents"("effective_date");

-- CreateIndex
CREATE INDEX "legal_documents_scope_idx" ON "legal_documents"("scope");

-- CreateIndex
CREATE UNIQUE INDEX "legal_documents_document_number_issue_date_document_type_key" ON "legal_documents"("document_number", "issue_date", "document_type");

-- CreateIndex
CREATE INDEX "files_legal_document_id_idx" ON "files"("legal_document_id");

-- CreateIndex
CREATE UNIQUE INDEX "sources_name_key" ON "sources"("name");

-- CreateIndex
CREATE INDEX "_DocumentAppliesToUnits_B_index" ON "_DocumentAppliesToUnits"("B");

-- AddForeignKey
ALTER TABLE "administrative_units" ADD CONSTRAINT "administrative_units_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "administrative_units"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin_unit_relations" ADD CONSTRAINT "admin_unit_relations_predecessor_id_fkey" FOREIGN KEY ("predecessor_id") REFERENCES "administrative_units"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "admin_unit_relations" ADD CONSTRAINT "admin_unit_relations_successor_id_fkey" FOREIGN KEY ("successor_id") REFERENCES "administrative_units"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "legal_documents" ADD CONSTRAINT "legal_documents_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "sources"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "legal_documents" ADD CONSTRAINT "legal_documents_canonical_doc_id_fkey" FOREIGN KEY ("canonical_doc_id") REFERENCES "legal_documents"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "files" ADD CONSTRAINT "files_legal_document_id_fkey" FOREIGN KEY ("legal_document_id") REFERENCES "legal_documents"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_DocumentAppliesToUnits" ADD CONSTRAINT "_DocumentAppliesToUnits_A_fkey" FOREIGN KEY ("A") REFERENCES "administrative_units"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_DocumentAppliesToUnits" ADD CONSTRAINT "_DocumentAppliesToUnits_B_fkey" FOREIGN KEY ("B") REFERENCES "legal_documents"("id") ON DELETE CASCADE ON UPDATE CASCADE;
