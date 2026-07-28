import { Module } from "@nestjs/common";
import { McpService } from "./mcp.service";
import { McpController } from "./mcp.controller";
import { LegalDocsModule } from "../legal-docs/legal-docs.module";
import { AdminUnitsModule } from "../admin-units/admin-units.module";

@Module({
  imports: [LegalDocsModule, AdminUnitsModule],
  controllers: [McpController],
  providers: [McpService],
  exports: [McpService],
})
export class McpModule {}
