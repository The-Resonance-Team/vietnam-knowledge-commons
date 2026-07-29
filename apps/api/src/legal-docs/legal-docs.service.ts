import { Injectable } from "@nestjs/common";
import { PrismaService } from "@/prisma/prisma.service";

@Injectable()
export class LegalDocsService {
  constructor(private prisma: PrismaService) {}

  async findAll(limit = 100, offset = 0) {
    return this.prisma.legalDocument.findMany({
      take: limit,
      skip: offset,
      include: { source: true, files: true },
      orderBy: { issueDate: "desc" },
    });
  }

  async findById(id: string) {
    return this.prisma.legalDocument.findUnique({
      where: { id },
      include: { source: true, files: true, appliesToUnits: true },
    });
  }

  async search(query: string, limit = 50) {
    // Full-text search via Typesense (to be implemented). This is a basic SQL
    // LIKE search and, per ADR-0004, `citationTitle` is a citation
    // ("Thông tư 28/2026/TT-BYT của Bộ Y tế"), not a subject — so this only
    // matches what's literally in the citation, number, or (rarely present)
    // full text, not what a document is about.
    return this.prisma.legalDocument.findMany({
      where: {
        OR: [
          { citationTitle: { contains: query, mode: "insensitive" } },
          { documentNumber: { contains: query, mode: "insensitive" } },
          { fullText: { contains: query, mode: "insensitive" } },
        ],
      },
      take: limit,
      include: { source: true },
    });
  }
}
