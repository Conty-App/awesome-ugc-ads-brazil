# Taxonomia (v1)

## Campos obrigatórios
- `id` (string única, ex: `br_001`)
- `platform`: `reels` | `tiktok` | `shorts`
- `language`: `pt-BR`
- `ugc_type`: `testimonial` | `unboxing` | `before_after` | `review` | `tutorial` | `qna` | `offer` | `educational` | `trend` | `product_haul`
- `hook_text`: primeira frase/ideia forte (string)
- `cta_text`: call-to-action final (string)
- `script_text`: roteiro/transcrição do vídeo (string)
- `video_url`: link público do vídeo (string, http/https)
- `terms_ok`: `true` (o contribuinte declara que tem permissão e/ou o uso é compatível com os termos)


## Campos opcionais
- `brand`, `category`, `caption_text`, `duration_sec`, `aspect_ratio` (ex: `9:16`), `notes`

## Regras
- Apenas **pt-BR** no MVP.
- **Não faça upload de mídia** (sem arquivos de vídeo/áudio/imagem).
- `video_url` deve apontar para um conteúdo **público** (TikTok, Reels/Instagram, Shorts/YouTube).
- `script_text` pode ser transcrição manual ou gerada por IA; mantenha-a fiel e legível.
- Se o link cair (link rot), mantenha o registro; novos PRs podem atualizar `video_url`.

## Qualidade de contribuição
- `hook_text` curto e claro.
- `cta_text` específico (ex: “Comente ‘quero’…”, “Link na bio”, “Baixe grátis”).
- `script_text` com linhas/frases separadas por ponto/queBRA simples; nada de HTML.