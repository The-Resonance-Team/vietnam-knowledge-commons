import { Controller, Get, Param, Query } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { AdminUnitsService } from "./admin-units.service";

@ApiTags("Administrative Units")
@Controller("admin-units")
export class AdminUnitsController {
  constructor(private readonly adminUnitsService: AdminUnitsService) {}

  @Get()
  @ApiOperation({ summary: "List administrative units" })
  findAll(@Query("limit") limit?: string, @Query("offset") offset?: string) {
    return this.adminUnitsService.findAll(
      limit ? parseInt(limit) : 100,
      offset ? parseInt(offset) : 0,
    );
  }

  @Get("current")
  @ApiOperation({ summary: "Get current administrative units (valid now)" })
  findCurrent() {
    return this.adminUnitsService.findCurrent();
  }

  @Get("code/:code")
  @ApiOperation({ summary: "Get administrative unit by GSO code" })
  findByCode(@Param("code") code: string) {
    return this.adminUnitsService.findByCode(code);
  }

  @Get(":id")
  @ApiOperation({ summary: "Get administrative unit by ID" })
  findById(@Param("id") id: string) {
    return this.adminUnitsService.findById(id);
  }
}
