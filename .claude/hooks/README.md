Los hooks del MVP están en `.claude/settings.example.json`.

Para activarlos:

```bash
cp .claude/settings.example.json .claude/settings.json
```

El hook de edición ejecuta `python -m py_compile src/*.py` tras cambios en archivos.
El hook de Bash bloquea comandos `rm -rf *`.
