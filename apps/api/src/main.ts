import compression from "compression";
import cookieParser from "cookie-parser";
import express from "express";
import { NestFactory } from "@nestjs/core";
import { ConfigService } from "@nestjs/config";
import { ValidationPipe } from "@nestjs/common";
import { AppModule } from "@/app.module";

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    bufferLogs: false,
    abortOnError: false,
  });

  const expressApp = app.getHttpAdapter().getInstance() as express.Application;
  expressApp.set("trust proxy", 1);

  // HTTP compression
  app.use(compression({ level: 6, threshold: 1024 }));

  // Cookie parser
  app.use(cookieParser());

  // JSON body parser
  expressApp.use(express.json({ limit: "10mb" }));

  // Validation pipe
  app.useGlobalPipes(
    new ValidationPipe({
      transform: true,
      whitelist: true,
    }),
  );

  // Security headers
  const helmet = await import("helmet");
  app.use(helmet.default());

  // CORS
  const configService = app.get(ConfigService);
  const corsOrigins = configService
    .get<string>("CORS_ORIGINS", "")
    .split(",")
    .filter((s) => s.length > 0);

  const isDev = configService.get<string>("NODE_ENV") !== "production";
  const corsOrigin = isDev
    ? (origin: string | undefined, callback: (err: Error | null, allow?: boolean) => void) => {
        if (!origin) return callback(null, true);
        if (origin.startsWith("http://localhost:") || origin.startsWith("http://127.0.0.1:")) {
          return callback(null, true);
        }
        if (corsOrigins.includes(origin)) return callback(null, true);
        callback(new Error("Not allowed by CORS"));
      }
    : corsOrigins;

  app.enableCors({ origin: corsOrigin, credentials: true });

  // Global prefix
  app.setGlobalPrefix("v1");

  // Graceful shutdown
  const teardown = async (signal: string) => {
    console.log(`${signal} received — shutting down`);
    const httpServer = app.getHttpServer();
    httpServer.closeIdleConnections?.();
    httpServer.closeAllConnections?.();
    await new Promise<void>((resolve) => httpServer.close(() => resolve()));
    await app.close();
    process.exit(0);
  };

  process.once("SIGTERM", () => teardown("SIGTERM"));
  process.once("SIGINT", () => teardown("SIGINT"));

  const port = configService.get<number>("PORT", 3100);
  await app.listen(port, "0.0.0.0");

  console.log(`VNKC API running on http://0.0.0.0:${port}`);
}

bootstrap().catch((err) => {
  console.error("Fatal: API failed to start", err);
  process.exit(1);
});
