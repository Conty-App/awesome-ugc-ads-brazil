# 🇧🇷 Awesome UGC Ads Brazil
O **primeiro dataset aberto de anúncios UGC em português (pt-BR)** — focado em ganchos (hooks), CTAs e estrutura narrativa.

## Por que existe?
Não havia um dataset simples e público em pt-BR. Ajuda creators, growth e devs a estudar padrões que funcionam em vídeo curto.

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

O script usa yt-dlp para baixar vídeos e openai-whisper para transcrição. ffmpeg deve estar instalado no sistema.

## Como usar

### Análise básica
```bash
python3 scripts/analyze_hooks.py
```

### Ingestão de novos anúncios
```bash
python3 ingest/ingest_url.py --url "https://instagram.com/reel/VIDEO_ID/" --ugc-type review --brand "NomeMarca" --category "beleza" --terms-ok true
```

Parâmetros:
- `--url`: URL do vídeo (Instagram, YouTube, etc.)
- `--ugc-type`: Tipo do conteúdo (testimonial, unboxing, review, etc.)
- `--brand`: Nome da marca
- `--category`: Categoria do produto
- `--terms-ok`: Aceitou os termos (true/false)

## Solução de problemas

### Erro "No module named 'pydub'"
O script usa ffmpeg diretamente agora. Se ainda der erro, instale ffmpeg:

```bash
# macOS com Homebrew
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Outros sistemas, veja documentação do ffmpeg
```

### Erro "No module named 'faster_whisper'"
Trocamos para openai-whisper porque faster-whisper tinha problemas de compilação. Se der erro de import:

```bash
pip uninstall faster-whisper
pip install openai-whisper
```

### Erro de compilação com av/ctypes
Se der erro de compilação relacionado a av ou ctypes, o problema é provavelmente com faster-whisper. Use openai-whisper:

```bash
pip uninstall faster-whisper av
pip install openai-whisper
```

### Vídeo não baixa
Verifique se a URL está correta e se yt-dlp consegue acessar. Alguns sites bloqueiam downloads automatizados.

### Transcrição falha
Whisper precisa de GPU para ser rápido. Em CPU pode ser lento. Use um modelo menor se precisar:

```bash
python3 ingest/ingest_url.py --model tiny --url "..."
```

Modelos disponíveis: tiny, base, small, medium, large

## Estrutura do projeto

```
data/
  ads.jsonl          # Dataset principal
  taxonomy.md        # Categorias e tipos

ingest/
  ingest_url.py      # Script de ingestão

scripts/
  analyze_hooks.py   # Análise básica
  validate.py        # Validação do dataset
```