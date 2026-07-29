import { Injectable } from "@nestjs/common";
import { PrismaService } from "@/prisma/prisma.service";

@Injectable()
export class AdminUnitsService {
  constructor(private prisma: PrismaService) {}

  async findAll(limit = 100, offset = 0) {
    return this.prisma.administrativeUnit.findMany({
      take: limit,
      skip: offset,
      include: {
        parent: true,
        children: true,
        predecessors: true,
        successors: true,
      },
      orderBy: { validFrom: "desc" },
    });
  }

  async findById(id: string) {
    return this.prisma.administrativeUnit.findUnique({
      where: { id },
      include: {
        parent: true,
        children: true,
        predecessors: { include: { predecessor: true } },
        successors: { include: { successor: true } },
        legalDocs: true,
      },
    });
  }

  async findByCode(code: string) {
    return this.prisma.administrativeUnit.findUnique({
      where: { code },
      include: {
        parent: true,
        children: true,
      },
    });
  }

  async findCurrent() {
    // Find units valid now (validTo is null or in future)
    return this.prisma.administrativeUnit.findMany({
      where: {
        OR: [{ validTo: null }, { validTo: { gt: new Date() } }],
      },
      include: {
        parent: true,
        children: true,
      },
    });
  }
}
