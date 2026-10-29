from pathlib import Path

from sentinela.bootstrap import (
    prepare_sentinela_environment,
)


INFLUD_PATH = Path(
    "data/raw/INFLUD26-19-10-2026.csv"
)


env = prepare_sentinela_environment(
    influd_path=INFLUD_PATH,
    year=2026,
)


print(
    env.readiness_summary
)
