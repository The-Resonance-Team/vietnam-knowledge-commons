import { Controller, Get, Post, Body, Res } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { Response } from "express";
import { McpService } from "./mcp.service";

@ApiTags("MCP (Model Context Protocol)")
@Controller("mcp")
export class McpController {
  constructor(private readonly mcpService: McpService) {}

  @Get("tools")
  @ApiOperation({ summary: "List available MCP tools" })
  listTools() {
    return {
      tools: this.mcpService.getToolDefinitions(),
    };
  }

  @Post("call")
  @ApiOperation({ summary: "Call an MCP tool" })
  async callTool(@Body() body: { name: string; arguments: any }, @Res() res: Response) {
    const { name, arguments: args } = body;

    // SSE transport for streaming (MCP spec)
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");

    try {
      let result: any;

      switch (name) {
        case "search_legal_docs":
          result = await this.mcpService.searchLegalDocs(args.query, args.limit);
          break;
        case "get_legal_doc":
          result = await this.mcpService.getLegalDoc(args.id);
          break;
        case "list_admin_units":
          result = await this.mcpService.listAdminUnits(args.limit, args.offset);
          break;
        case "get_admin_unit":
          result = await this.mcpService.getAdminUnit(args.id);
          break;
        case "find_current_units":
          result = await this.mcpService.findCurrentUnits();
          break;
        default:
          throw new Error(`Unknown tool: ${name}`);
      }

      // Send result as SSE event
      res.write(`data: ${JSON.stringify({ type: "result", data: result })}\n\n`);
      res.end();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      res.write(`data: ${JSON.stringify({ type: "error", message })}\n\n`);
      res.end();
    }
  }
}
