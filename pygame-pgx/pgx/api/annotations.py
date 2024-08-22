from typing import Any, Callable
from .scriptctx import ScriptContext
from .app import PGXApp, ExportableNamespace

app: PGXApp
current_script: ScriptContext
exports: ExportableNamespace

exportfn: Callable[[Callable], None]
export: Callable[[str, Any], None]