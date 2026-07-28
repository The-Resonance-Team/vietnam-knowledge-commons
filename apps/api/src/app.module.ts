import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";
import { PrismaModule } from "./prisma/prisma.module";
import { SearchModule } from "./search/search.module";
import { LegalDocsModule } from "./legal-docs/legal-docs.module";
import { AdminUnitsModule } from "./admin-units/admin-units.module";
import { McpModule } from "./mcp/mcp.module";

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: ".env",
    }),
    PrismaModule,
    SearchModule,
    LegalDocsModule,
    AdminUnitsModule,
    McpModule,
  ],
})
export class AppModule {}
