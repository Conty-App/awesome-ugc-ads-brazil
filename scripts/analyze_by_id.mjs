#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import "dotenv/config";
import { Command } from "commander";
import { z } from "zod";
import { streamText } from "ai";
import { createOpenAI } from "@ai-sdk/openai";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..", "");

const adSchema = z.object({
  id: z.string(),
  platform: z.string(),
  brand: z.string().optional(),
  category: z.string().optional(),
  language: z.string(),
  ugc_type: z.string(),
  video_url: z.string().url(),
  hook_text: z.string(),
  cta_text: z.string(),
  caption_text: z.string().nullable().optional(),
  script_text: z.string(),
  duration_sec: z.number().nullable().optional(),
  aspect_ratio: z.string().optional(),
  terms_ok: z.boolean(),
  notes: z.string().optional(),
});

const program = new Command();
program
  .name("analyze-by-id")
  .description("Analisa um anúncio por id ou filtro de URL usando OpenAI via Vercel AI SDK")
  .option("--id <id>", "ID do anúncio, ex: br_001")
  .option("--url-contains <substr>", "Substring para filtrar por video_url")
  .option("--model <model>", "Modelo OpenAI", process.env.OPENAI_MODEL || "gpt-4o-mini")
  .option("--file <path>", "Caminho para ads.jsonl", path.join(rootDir, "data", "ads.jsonl"))
  .option("--temperature <num>", "Temperatura do modelo", (v) => Number(v), 0.2)
  .parse(process.argv);

const opts = program.opts();

if (!opts.id && !opts["urlContains"]) {
  // Commander converts --url-contains to urlContains
  if (!opts.id && !opts.urlContains) {
    console.error("Erro: informe --id ou --url-contains");
    process.exit(1);
  }
}

const openaiApiKey = process.env.OPENAI_API_KEY;
if (!openaiApiKey) {
  console.error("Erro: defina a variável de ambiente OPENAI_API_KEY");
  process.exit(1);
}

const openai = createOpenAI({ apiKey: openaiApiKey });

function readAds(filePath) {
  const content = fs.readFileSync(filePath, "utf-8");
  const lines = content.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  const out = [];
  for (const line of lines) {
    try {
      const obj = JSON.parse(line);
      const ad = adSchema.parse(obj);
      out.push(ad);
    } catch (e) {
      // skip invalid lines silently
    }
  }
  return out;
}

function selectAd(ads) {
  if (opts.id) {
    const found = ads.find((a) => a.id === opts.id);
    if (!found) {
      console.error(`Não encontrado id ${opts.id}`);
      process.exit(1);
    }
    return found;
  }
  if (opts.urlContains) {
    const matches = ads.filter((a) => (a.video_url || "").includes(opts.urlContains));
    if (matches.length === 0) {
      console.error(`Nenhum registro com url contendo '${opts.urlContains}'`);
      process.exit(1);
    }
    if (matches.length > 1) {
      console.error(`Mais de um registro encontrado para url-contains. Use --id. IDs: ${matches.map(m => m.id).join(", ")}`);
      process.exit(1);
    }
    return matches[0];
  }
}

async function analyze(ad) {
  const system = [
    "Você é um analista de criativos UGC em pt-BR.",
    "Avalie o anúncio considerando: clareza do hook, proposta de valor, prova social, timing do CTA, objeções e copy.",
    "Responda em JSON estrito, sem texto adicional.",
  ].join(" ");

  const user = {
    id: ad.id,
    platform: ad.platform,
    brand: ad.brand || "",
    category: ad.category || "",
    language: ad.language,
    ugc_type: ad.ugc_type,
    video_url: ad.video_url,
    hook_text: ad.hook_text,
    cta_text: ad.cta_text,
    caption_text: ad.caption_text || "",
    script_text: ad.script_text,
    duration_sec: ad.duration_sec ?? null,
    aspect_ratio: ad.aspect_ratio || "",
  };

  const schema = {
    type: "object",
    properties: {
      id: { type: "string" },
      summary: { type: "string" },
      hook_quality: { type: "string", enum: ["fraco", "mediano", "forte"] },
      cta_quality: { type: "string", enum: ["fraco", "mediano", "forte"] },
      messaging_notes: { type: "array", items: { type: "string" } },
      objections_addressed: { type: "array", items: { type: "string" } },
      risks: { type: "array", items: { type: "string" } },
      suggestions: { type: "array", items: { type: "string" } },
      score_overall: { type: "number" },
    },
    required: ["id", "summary", "hook_quality", "cta_quality", "suggestions", "score_overall"],
    additionalProperties: false,
  };

  const prompt = `Analise o anúncio abaixo e responda em JSON válido seguindo este schema: ${JSON.stringify(schema)}. Dados do anúncio: ${JSON.stringify(user)}`;

  const result = await streamText({
    model: openai(opts.model),
    system,
    messages: [{ role: "user", content: prompt }],
    temperature: opts.temperature,
  });

  let fullText = "";
  for await (const delta of result.textStream) {
    process.stdout.write(delta);
    fullText += delta;
  }
  process.stdout.write("\n");

  const parsed = JSON.parse(fullText || "{}");
  if (!parsed.id) parsed.id = ad.id;
  return parsed;
}

(async () => {
  const ads = readAds(opts.file);
  const ad = selectAd(ads);
  const result = await analyze(ad);
})().catch((err) => {
  console.error("Falha na análise:", err?.message || err);
  process.exit(1);
});


