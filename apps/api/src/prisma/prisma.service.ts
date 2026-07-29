import { Injectable, OnModuleInit, OnModuleDestroy } from "@nestjs/common";
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { PrismaClient } = require("../generated/prisma/client");
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { PrismaPg } = require("@prisma/adapter-pg");

const adapter = new PrismaPg({
  connectionString: process.env.DATABASE_URL,
});

@Injectable()
export class PrismaService extends (PrismaClient as any) implements OnModuleInit, OnModuleDestroy {
  constructor() {
    super({ adapter });
  }

  async onModuleInit() {
    await this.$connect();
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }
}
