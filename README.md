# deadlock-config

Minha configuração do Deadlock: `gameinfo.gi` focado em FPS e clareza visual, mais a config do mod QOL Lock.

## Arquivos

| Arquivo | O que é |
|---|---|
| `gameinfo.gi` | Config do motor (convars). Base: **OptimizationLock v3.2** (Otimização do Deadlock, @nokeimee), com ajustes meus. |
| `qol_lock_settings.txt` | Código de configuração do mod [QOL Lock](https://moglock.gg) (versão `QOL-4-1-0-C`). Cola no menu do mod pra restaurar. |
| `addons/` | Mods (`.vpk`) e o manifesto do Deadlock Mod Manager (`.dmm.json`). |

O repositório é a própria pasta `Deadlock\game\citadel`: o `.gitignore` ignora tudo e libera só os arquivos acima, então o resto do jogo (gerenciado pela Steam) fica fora do git. O `.gitattributes` desliga a conversão de fim de linha pra os arquivos ficarem idênticos aos que o jogo lê.

## Como instalar

Clone direto na pasta do jogo (ou copie `gameinfo.gi` e `addons/` para `Steam\steamapps\common\Deadlock\game\citadel\`) e abra o jogo.

> A cada atualização do Deadlock a Steam pode sobrescrever o `gameinfo.gi`. Se a config "sumir", `git checkout gameinfo.gi` restaura.
> Se o jogo fechar com `FATAL ERROR: Unable to find child ... in layout file 'panorama\layout\...'`, o culpado é um mod de HUD desatualizado (ex.: QOL Lock), não o gameinfo. Desative o mod até sair a versão nova.

## Destaques da config

Os convars ficam no bloco `ConVars`, organizados por seção com comentários (`// --- N. Seção ---`).

### Contorno através da parede
Inimigos e minions ficam com contorno visível sempre, inclusive atrás de paredes:

```
r_citadel_selection_outline2_offset 1
r_citadel_selection_outline2_alpha 255
r_citadel_selection_outline2_fade_pow -inf
citadel_player_outline_fade_range_min inf
citadel_player_outline_fade_range_max -inf
```

O `fade_range` infinito impede o contorno de sumir pela distância. A cor do contorno **não** é controlada pelo gameinfo.

### HUD e visibilidade
- Barras de status de aliados visíveis através da parede (`citadel_unit_status_allies_see_thru_walls`).
- Vida de objetivos (guardiões, walkers) sempre no HUD (`citadel_hud_objective_health_enabled 2`).
- Relatório de dano ligado; indicador de dano fora da tela desligado.
- Desenho no minimapa mais preciso (`citadel_distance_mouse_move_for_minimap_drawing 1`).
- Proporção esticada `r_aspectratio 2.20` (FOV horizontal maior).

### Câmera
- Sem tremida de melee e sem wobble da câmera.
- Câmera sem atraso (`cam_ideallag 0`, `cam_idealdelta 0`) e distância de visão maior (`citadel_camera_see_distance_max 7000`).

### Desempenho
- Sombras pré-calculadas e luzes estacionárias desligadas.
- Texturas com filtro e mip mais leves (`r_texture_stream_mip_bias 3`, `r_texturefilteringquality 0`).
- Panorama (UI) limitado a 30 FPS e sem transições, aliviando a CPU.
- Partículas, LOD, grama, ragdolls e animações simplificados (seções próprias no arquivo).

## Mods usados

- **QOL Lock** (GameBanana 650634): HUD e qualidade de vida.
- Mod de barras de vida numéricas.

Os `.vpk` ficam em `addons/`. Os créditos e licenças são dos autores de cada mod no GameBanana.

## Créditos

- Base do `gameinfo.gi`: OptimizationLock v3.2 / Otimização do Deadlock (@nokeimee).
- Truque do contorno: gameinfo do streamer Farinha GM.
