import { Module } from "@nestjs/common";
import { LegalDocsService } from "./legal-docs.service";
import { LegalDocsController } from "./legal-docs.controller";

@Module({
  controllers: [LegalDocsController],
  providers: [LegalDocsService],
  exports: [LegalDocsService],
})
export class LegalDocsModule {}
