import { Injectable } from "@nestjs/common";
import { LegalDocsService } from "@/legal-docs/legal-docs.service";
import { AdminUnitsService } from "@/admin-units/admin-units.service";

@Injectable()
export class McpService {
  constructor(
    private legalDocsService: LegalDocsService,
    private adminUnitsService: AdminUnitsService,
  ) {}

  // MCP Tool: search_legal_docs
  async searchLegalDocs(query: string, limit = 50) {
    return this.legalDocsService.search(query, limit);
  }

  // MCP Tool: get_legal_doc
  async getLegalDoc(id: string) {
    return this.legalDocsService.findById(id);
  }

  // MCP Tool: list_admin_units
  async listAdminUnits(limit = 100, offset = 0) {
    return this.adminUnitsService.findAll(limit, offset);
  }

  // MCP Tool: get_admin_unit
  async getAdminUnit(id: string) {
    return this.adminUnitsService.findById(id);
  }

  // MCP Tool: find_current_units
  async findCurrentUnits() {
    return this.adminUnitsService.findCurrent();
  }

  // MCP Tool definitions for SDK
  getToolDefinitions() {
    return [
      {
        name: "search_legal_docs",
        description: "Search Vietnamese legal documents by keyword",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string", description: "Search query" },
            limit: { type: "number", description: "Max results (default 50)", default: 50 },
          },
          required: ["query"],
        },
      },
      {
        name: "get_legal_doc",
        description: "Get a legal document by ID",
        inputSchema: {
          type: "object",
          properties: {
            id: { type: "string", description: "Document UUID" },
          },
          required: ["id"],
        },
      },
      {
        name: "list_admin_units",
        description: "List Vietnamese administrative units (province/district/ward)",
        inputSchema: {
          type: "object",
          properties: {
            limit: { type: "number", description: "Max results (default 100)", default: 100 },
            offset: {
              type: "number",
              description: "Offset for pagination (default 0)",
              default: 0,
            },
          },
        },
      },
      {
        name: "get_admin_unit",
        description: "Get an administrative unit by ID",
        inputSchema: {
          type: "object",
          properties: {
            id: { type: "string", description: "Unit UUID" },
          },
          required: ["id"],
        },
      },
      {
        name: "find_current_units",
        description: "Get all current administrative units (valid now)",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
    ];
  }
}
