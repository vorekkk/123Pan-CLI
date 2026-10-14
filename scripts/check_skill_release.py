"""Verify canonical resources, wheel/npm parity and installed npm/Python interoperability."""

import json
import os
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/pan123-cli"
NPM = "npm.cmd" if os.name == "nt" else "npm"
canonical = {
    p.relative_to(SKILL).as_posix(): p.read_bytes() for p in SKILL.rglob("*") if p.is_file()
}
for doc in [SKILL / "SKILL.md", *(SKILL / "references").glob("*.md")]:
    for target in re.findall(r"\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
        if not target.startswith(("http:", "https:", "#")):
            if not (doc.parent / unquote(target.split("#")[0])).is_file():
                raise SystemExit(f"Broken Skill link in {doc.name}: {target}")
wheels = list((ROOT / "dist").glob("*.whl"))
assert len(wheels) == 1, "Build exactly one wheel first"
with zipfile.ZipFile(wheels[0]) as archive:
    contents = {
        name.removeprefix("pan123_cli/skill_data/"): archive.read(name)
        for name in archive.namelist()
        if name.startswith("pan123_cli/skill_data/")
    }
assert contents == canonical, "wheel resources drifted from canonical Skill"
with tempfile.TemporaryDirectory(prefix="pan123-skill-release-") as directory:
    temp = Path(directory).resolve()
    packed = json.loads(
        subprocess.check_output(
            [NPM, "pack", "--json", "--pack-destination", str(temp)], cwd=ROOT, text=True
        )
    )[0]
    import tarfile

    with tarfile.open(temp / packed["filename"]) as archive:
        members = archive.getnames()
        assert not any(
            Path(n).name.startswith(".env")
            or Path(n).name in {"credentials.json", "token_cache.json"}
            for n in members
        )
        contents = {
            name.removeprefix("package/skills/pan123-cli/"): archive.extractfile(name).read()
            for name in members
            if name.startswith("package/skills/pan123-cli/") and archive.getmember(name).isfile()
        }
        assert contents == canonical, "npm resources drifted from canonical Skill"
    prefix = temp / "prefix"
    env = {
        **os.environ,
        "CODEX_HOME": str(temp / "codex"),
        "HOME": str(temp),
        "USERPROFILE": str(temp),
        "npm_config_cache": str(temp / "npm-cache"),
    }
    subprocess.run(
        [NPM, "install", "-g", "--prefix", str(prefix), str(temp / packed["filename"])],
        env=env,
        cwd=temp,
        check=True,
    )
    entry = (
        prefix
        / ("node_modules" if os.name == "nt" else "lib/node_modules")
        / "pan123-cli-skill/npm/cli.mjs"
    )
    # Lifecycle installed at least Codex; explicit dest lets both installers share a target.
    assert (temp / "codex/skills/pan123-cli/SKILL.md").is_file()
    target = temp / "shared"
    subprocess.run(
        ["node", str(entry), "install", "--dest", str(target)],
        env=env,
        cwd=temp,
        check=True,
        capture_output=True,
    )
    from pan123_cli.skills import manage

    assert manage("install", {"dest": str(target)})["results"][0]["status"] == "unchanged"
    manage("uninstall", {"dest": str(target)})
    manage("install", {"dest": str(target)})
    outcome = json.loads(
        subprocess.check_output(
            ["node", str(entry), "install", "--dest", str(target)], env=env, cwd=temp, text=True
        )
    )
    assert outcome["data"]["results"][0]["status"] == "unchanged"
print(f"Skill package parity and installer interoperability verified: {len(canonical)} files.")
