import { Injectable, OnModuleInit } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import Typesense, { Client } from "typesense";

@Injectable()
export class SearchService implements OnModuleInit {
  private client: Client;

  constructor(private configService: ConfigService) {
    this.client = new Typesense.Client({
      nodes: [
        {
          host: this.configService.get<string>("TYPESENSE_HOST", "localhost"),
          port: this.configService.get<number>("TYPESENSE_PORT", 8108),
          protocol: this.configService.get<string>("TYPESENSE_PROTOCOL", "http"),
        },
      ],
      apiKey: this.configService.get<string>("TYPESENSE_API_KEY", "xyz"),
      connectionTimeoutSeconds: 5,
    });
  }

  async onModuleInit() {
    try {
      await this.client.health.retrieve();
      console.log("✓ Typesense connected");
    } catch (error: any) {
      console.warn("Typesense not available:", error.message);
    }
  }

  getClient() {
    return this.client;
  }

  async createCollections() {
    // Legal documents collection
    try {
      await this.client.collections("legal_documents").retrieve();
      console.log("Collection legal_documents exists");
    } catch {
      await this.client.collections().create({
        name: "legal_documents",
        fields: [
          { name: "id", type: "string" },
          { name: "documentType", type: "string", facet: true },
          { name: "documentNumber", type: "string" },
          { name: "title", type: "string" },
          { name: "titleEn", type: "string", optional: true },
          { name: "issueDate", type: "int64", facet: true },
          { name: "effectiveDate", type: "int64", facet: true },
          { name: "expiryDate", type: "int64", optional: true, facet: true },
          { name: "issuingBody", type: "string", facet: true },
          { name: "fullText", type: "string" },
          { name: "scope", type: "string", facet: true },
          { name: "keywords", type: "string[]", facet: true },
          { name: "abstract", type: "string", optional: true },
        ],
        default_sorting_field: "issueDate",
      });
      console.log("✓ Created collection legal_documents");
    }

    // Administrative units collection
    try {
      await this.client.collections("admin_units").retrieve();
      console.log("Collection admin_units exists");
    } catch {
      await this.client.collections().create({
        name: "admin_units",
        fields: [
          { name: "id", type: "string" },
          { name: "code", type: "string" },
          { name: "name", type: "string" },
          { name: "nameEn", type: "string", optional: true },
          { name: "level", type: "string", facet: true },
          { name: "validFrom", type: "int64", facet: true },
          { name: "validTo", type: "int64", optional: true, facet: true },
          { name: "population", type: "int32", optional: true },
          { name: "areaKm2", type: "float", optional: true },
        ],
        default_sorting_field: "validFrom",
      });
      console.log("✓ Created collection admin_units");
    }
  }

  async indexLegalDocuments(docs: any[]) {
    const documents = docs.map((doc) => ({
      id: doc.id,
      documentType: doc.documentType,
      documentNumber: doc.documentNumber,
      title: doc.title,
      titleEn: doc.titleEn,
      issueDate: Math.floor(new Date(doc.issueDate).getTime() / 1000),
      effectiveDate: Math.floor(new Date(doc.effectiveDate).getTime() / 1000),
      expiryDate: doc.expiryDate ? Math.floor(new Date(doc.expiryDate).getTime() / 1000) : null,
      issuingBody: doc.issuingBody,
      fullText: doc.fullText || "",
      scope: doc.scope,
      keywords: doc.keywords || [],
      abstract: doc.abstract,
    }));

    return this.client.collections("legal_documents").documents().import(documents);
  }

  async indexAdminUnits(units: any[]) {
    const documents = units.map((unit) => ({
      id: unit.id,
      code: unit.code,
      name: unit.name,
      nameEn: unit.nameEn,
      level: unit.level,
      validFrom: Math.floor(new Date(unit.validFrom).getTime() / 1000),
      validTo: unit.validTo ? Math.floor(new Date(unit.validTo).getTime() / 1000) : null,
      population: unit.population,
      areaKm2: unit.areaKm2,
    }));

    return this.client.collections("admin_units").documents().import(documents);
  }

  async searchLegalDocs(query: string, limit = 50) {
    return this.client.collections("legal_documents").documents().search({
      q: query,
      query_by: "title,documentNumber,fullText,keywords",
      per_page: limit,
    });
  }

  async searchAdminUnits(query: string, limit = 50) {
    return this.client.collections("admin_units").documents().search({
      q: query,
      query_by: "name,code,nameEn",
      per_page: limit,
    });
  }
}
