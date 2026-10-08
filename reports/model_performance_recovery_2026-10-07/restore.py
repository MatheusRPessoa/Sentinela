"""Execute com %run -i para restaurar as variáveis e funções na sessão da IDE."""
import pickle as _restore_pickle
from pathlib import Path as _RestorePath

_restore_dir = _RestorePath(__file__).resolve().parent
with (_restore_dir / "variables.pkl").open("rb") as _restore_file:
    _restore_values = _restore_pickle.load(_restore_file)
globals().update(_restore_values)
exec(
    compile(
        (_restore_dir / "functions.py").read_text(),
        str(_restore_dir / "functions.py"),
        "exec",
    ),
    globals(),
)
print(f"Restauradas {len(_restore_values)} variáveis e as funções do notebook.")
del _restore_values, _restore_file, _restore_dir, _restore_pickle, _RestorePath
