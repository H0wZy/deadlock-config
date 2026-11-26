# make  ->  injeta patches/complock_mirage_minimap.css no CompLock (addons/pak01_dir.vpk).
# Rode com o Deadlock fechado: o jogo só lê o VPK quando abre.

.PHONY: apply
apply:
	py patches/apply_complock_patch.py
