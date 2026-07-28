import { Injectable } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";

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
    // Full-text search via Meilisearch (to be implemented)
    // For now, basic SQL LIKE search
    return this.prisma.legalDocument.findMany({
      where: {
        OR: [
          { title: { contains: query, mode: "insensitive" } },
          { documentNumber: { contains: query, mode: "insensitive" } },
          { fullText: { contains: query, mode: "insensitive" } },
        ],
      },
      take: limit,
      include: { source: true },
    });
  }
}
