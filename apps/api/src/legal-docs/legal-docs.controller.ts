import { Controller, Get, Param, Query } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { LegalDocsService } from "./legal-docs.service";

@ApiTags("Legal Documents")
@Controller("legal-docs")
export class LegalDocsController {
  constructor(private readonly legalDocsService: LegalDocsService) {}

  @Get()
  @ApiOperation({ summary: "List legal documents" })
  findAll(@Query("limit") limit?: string, @Query("offset") offset?: string) {
    return this.legalDocsService.findAll(
      limit ? parseInt(limit) : 100,
      offset ? parseInt(offset) : 0,
    );
  }

  @Get("search")
  @ApiOperation({ summary: "Search legal documents" })
  search(@Query("q") query: string, @Query("limit") limit?: string) {
    return this.legalDocsService.search(query, limit ? parseInt(limit) : 50);
  }

  @Get(":id")
  @ApiOperation({ summary: "Get legal document by ID" })
  findById(@Param("id") id: string) {
    return this.legalDocsService.findById(id);
  }
}
