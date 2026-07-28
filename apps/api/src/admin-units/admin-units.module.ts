import { Module } from "@nestjs/common";
import { AdminUnitsService } from "./admin-units.service";
import { AdminUnitsController } from "./admin-units.controller";

@Module({
  controllers: [AdminUnitsController],
  providers: [AdminUnitsService],
  exports: [AdminUnitsService],
})
export class AdminUnitsModule {}
