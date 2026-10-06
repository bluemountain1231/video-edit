#!/usr/bin/env python3
"""Resolve, rank, lock, and import video-shotcraft recipes without executing them."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import difflib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


REPO_SLUG = "Vincentwei1021/video-shotcraft"
REPO_URL = f"https://github.com/{REPO_SLUG}"
API_ROOT = f"https://api.github.com/repos/{REPO_SLUG}"
RAW_ROOT = f"https://raw.githubusercontent.com/{REPO_SLUG}"
GALLERY_ROOT = "https://vincentwei1021.github.io/video-shotcraft/"
LIBRARY_PATH = "gallery/api/library.json"
DEFAULT_REF = "main"
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SNAPSHOT_ROOT = SCRIPT_DIR.parent / "assets" / "shotcraft-snapshot"
MAX_HTTP_BYTES = 40 * 1024 * 1024
MAX_ARCHIVE_BYTES = 120 * 1024 * 1024
MAX_EXTRACTED_BYTES = 300 * 1024 * 1024

ALIAS_GROUPS = (
    (
        ("scroll", "scrolling", "downward", "tape", "fixed pointer", "滚动", "下滑", "滚轮", "长卷"),
        ("tape-scroll-fixed-pointer", "gauge-readout-moves", "scroll-brake-moves", "brake-reticle-lock", "changelog-scroll-brake"),
    ),
    (
        ("metal", "metallic", "mechanical", "金属", "机械", "咔", "哐"),
        ("tape-scroll-fixed-pointer", "brake-reticle-lock", "gauge-readout-moves", "impact-feedback"),
    ),
    (
        ("click", "cursor", "mouse", "点击", "鼠标", "按下"),
        ("cursor-performance", "input-trigger-moves", "crash-zoom-punch"),
    ),
    (
        ("zoom", "push in", "punch in", "放大", "推近", "急推"),
        ("crash-zoom-punch", "cursor-performance", "input-trigger-moves"),
    ),
    (
        ("ink press", "ink-press", "墨压", "纸墨", "editorial"),
        ("ink-press",),
    ),
    (
        ("landing page", "website", "web page", "落地页", "网页"),
        ("scroll-brake-moves", "crash-zoom-punch", "input-trigger-moves", "page-waterfall-wall"),
    ),
)

SOURCE_SUFFIXES = (".ts", ".tsx", ".js", ".jsx")
IMPORT_RE = re.compile(r"(?:from\s+|import\s*\(\s*|require\s*\(\s*)['\"]([^'\"]+)['\"]")
STATIC_FILE_RE = re.compile(r"staticFile\(\s*['\"]([^'\"]+)['\"]\s*\)")


class RouterError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(value: str) -> str:
    value = value.lower().replace("_", "-")
    value = re.sub(r"[^a-z0-9\u3400-\u9fff-]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def slug_tokens(value: str) -> set[str]:
    normalized = normalize(value)
    tokens = set(re.findall(r"[a-z0-9]+|[\u3400-\u9fff]+", normalized))
    tokens.update(part for part in normalized.split("-") if part)
    return {token for token in tokens if len(token) > 1}


def expanded_query(query: str) -> tuple[str, list[str]]:
    normalized = normalize(query)
    additions: list[str] = []
    matched: list[str] = []
    for cues, expansions in ALIAS_GROUPS:
        if any(normalize(cue) in normalized for cue in cues):
            additions.extend(expansions)
            matched.extend(cue for cue in cues if normalize(cue) in normalized)
    return " ".join([query, *additions]), sorted(set(matched))


def safe_repo_path(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise RouterError(f"Unsafe upstream path: {value}")
    return path.as_posix()


def request_bytes(url: str, *, accept: str | None = None, limit: int = MAX_HTTP_BYTES) -> tuple[bytes, dict[str, str]]:
    headers = {"User-Agent": "cinematic-web-promo-shotcraft-router/1"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    if accept:
        headers["Accept"] = accept
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > limit:
                raise RouterError(f"Download exceeds {limit} bytes: {url}")
            data = response.read(limit + 1)
            if len(data) > limit:
                raise RouterError(f"Download exceeds {limit} bytes: {url}")
            return data, {key.lower(): value for key, value in response.headers.items()}
    except urllib.error.HTTPError as error:
        detail = error.read(1000).decode("utf-8", errors="replace")
        raise RouterError(f"HTTP {error.code} for {url}: {detail}") from error
    except urllib.error.URLError as error:
        raise RouterError(f"Network error for {url}: {error.reason}") from error


def request_json(url: str) -> dict[str, Any]:
    data, _ = request_bytes(url, accept="application/vnd.github+json", limit=10 * 1024 * 1024)
    try:
        value = json.loads(data)
    except json.JSONDecodeError as error:
        raise RouterError(f"Invalid JSON from {url}: {error}") from error
    if not isinstance(value, dict):
        raise RouterError(f"Expected JSON object from {url}")
    return value


def resolve_remote_ref(ref: str) -> str:
    if re.fullmatch(r"[0-9a-f]{40}", ref):
        return ref
    candidates = [f"refs/heads/{ref}", f"refs/tags/{ref}^{{}}", f"refs/tags/{ref}"]
    try:
        output = subprocess.check_output(
            ["git", "ls-remote", REPO_URL, *candidates], text=True, stderr=subprocess.STDOUT, timeout=45
        )
        resolved = {}
        for line in output.splitlines():
            parts = line.split()
            if len(parts) == 2 and re.fullmatch(r"[0-9a-f]{40}", parts[0]):
                resolved[parts[1]] = parts[0]
        for candidate in candidates:
            if candidate in resolved:
                return resolved[candidate]
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    payload = request_json(f"{API_ROOT}/commits/{urllib.parse.quote(ref, safe='')}")
    commit = payload.get("sha")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise RouterError(f"GitHub returned an invalid commit for ref {ref!r}")
    return commit


def extract_remote_archive(commit: str, destination: Path) -> None:
    archive_url = f"https://codeload.github.com/{REPO_SLUG}/tar.gz/{commit}"
    payload, _ = request_bytes(archive_url, accept="application/gzip", limit=MAX_ARCHIVE_BYTES)
    total_size = 0
    try:
        archive = tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz")
    except tarfile.TarError as error:
        raise RouterError(f"Invalid Shotcraft archive for {commit}: {error}") from error
    with archive:
        for member in archive.getmembers():
            if member.isdir():
                continue
            if not member.isfile():
                raise RouterError(f"Refuse non-regular archive entry: {member.name}")
            source_path = PurePosixPath(member.name)
            if len(source_path.parts) < 2:
                raise RouterError(f"Archive entry has no repository root: {member.name}")
            relative = PurePosixPath(*source_path.parts[1:])
            repo_path = safe_repo_path(relative.as_posix())
            total_size += member.size
            if total_size > MAX_EXTRACTED_BYTES:
                raise RouterError("Shotcraft archive exceeds the extracted-size safety limit.")
            source = archive.extractfile(member)
            if source is None:
                raise RouterError(f"Cannot read archive entry: {member.name}")
            target = destination / repo_path
            target.parent.mkdir(parents=True, exist_ok=True)
            with source, target.open("wb") as output:
                shutil.copyfileobj(source, output)


def resolve_offline_ref(root: Path, ref: str) -> str:
    if (root / ".git").exists():
        try:
            return subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", ref], text=True, stderr=subprocess.STDOUT
            ).strip()
        except (OSError, subprocess.CalledProcessError) as error:
            raise RouterError(f"Cannot resolve {ref!r} in offline repository: {error}") from error
    if re.fullmatch(r"[0-9a-f]{40}", ref):
        return ref
    raise RouterError("An offline source without .git requires --ref with the exact 40-character commit.")


def remote_tree(commit: str) -> list[str]:
    payload = request_json(f"{API_ROOT}/git/trees/{commit}?recursive=1")
    if payload.get("truncated"):
        raise RouterError("GitHub returned a truncated repository tree; refuse an incomplete import.")
    result = []
    for item in payload.get("tree", []):
        if isinstance(item, dict) and item.get("type") == "blob" and isinstance(item.get("path"), str):
            result.append(safe_repo_path(item["path"]))
    return sorted(result)


def offline_tree(root: Path) -> list[str]:
    result = []
    for item in root.rglob("*"):
        if item.is_symlink():
            raise RouterError(f"Refuse symlink in offline upstream: {item}")
        if item.is_file() and ".git" not in item.relative_to(root).parts:
            result.append(safe_repo_path(item.relative_to(root).as_posix()))
    return sorted(result)


class Upstream:
    def __init__(self, ref: str, offline_root: Path | None):
        self.requested_ref = ref
        self._tempdir: tempfile.TemporaryDirectory[str] | None = None
        self.mode = "offline"
        self.offline_root = offline_root.resolve() if offline_root else None
        if self.offline_root:
            if not self.offline_root.is_dir():
                raise RouterError(f"Offline root does not exist: {self.offline_root}")
            self.commit = resolve_offline_ref(self.offline_root, ref)
            self.paths = offline_tree(self.offline_root)
        else:
            self.commit = resolve_remote_ref(ref)
            self._tempdir = tempfile.TemporaryDirectory(prefix="shotcraft-router-")
            self.offline_root = Path(self._tempdir.name)
            extract_remote_archive(self.commit, self.offline_root)
            self.paths = offline_tree(self.offline_root)
            self.mode = "remote-archive"
        self.path_set = set(self.paths)
        self._cache: dict[str, bytes] = {}
        self.expected_hashes: dict[str, str] = {}

    def read(self, repo_path: str) -> bytes:
        repo_path = safe_repo_path(repo_path)
        if repo_path not in self.path_set:
            raise RouterError(f"Path is absent at {self.commit}: {repo_path}")
        if repo_path in self._cache:
            return self._cache[repo_path]
        if self.offline_root:
            data = (self.offline_root / repo_path).read_bytes()
        else:
            quoted = "/".join(urllib.parse.quote(part) for part in PurePosixPath(repo_path).parts)
            data, _ = request_bytes(f"{RAW_ROOT}/{self.commit}/{quoted}")
        expected_hash = self.expected_hashes.get(repo_path)
        if expected_hash and sha256_bytes(data) != expected_hash:
            raise RouterError(f"Embedded source hash mismatch: {repo_path}")
        self._cache[repo_path] = data
        return data

    def matching(self, prefix: str) -> list[str]:
        prefix = safe_repo_path(prefix).rstrip("/") + "/"
        return [item for item in self.paths if item.startswith(prefix)]


def load_snapshot_manifest(snapshot_root: Path) -> dict[str, Any]:
    manifest_path = snapshot_root / "SNAPSHOT.json"
    repo_root = snapshot_root / "repo"
    if not manifest_path.is_file() or not repo_root.is_dir():
        raise RouterError(f"Embedded Shotcraft snapshot is incomplete: {snapshot_root}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RouterError(f"Invalid embedded snapshot manifest: {manifest_path}: {error}") from error
    upstream = manifest.get("upstream")
    if not isinstance(upstream, dict):
        raise RouterError(f"Embedded snapshot has no upstream metadata: {manifest_path}")
    commit = upstream.get("resolvedCommit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise RouterError(f"Embedded snapshot has an invalid commit: {manifest_path}")
    return manifest


def select_upstream(
    source: str, ref: str, offline_root: Path | None, embedded_root: Path
) -> tuple[Upstream, dict[str, Any] | None, Path | None]:
    if offline_root:
        upstream = Upstream(ref, offline_root)
        upstream.mode = "authorized-local"
        return upstream, None, None

    if source != "remote":
        snapshot_root = embedded_root.resolve()
        manifest = load_snapshot_manifest(snapshot_root)
        commit = str(manifest["upstream"]["resolvedCommit"])
        ref_matches = ref == DEFAULT_REF or ref == commit
        if ref_matches:
            upstream = Upstream(commit, snapshot_root / "repo")
            upstream.mode = "embedded-snapshot"
            upstream.expected_hashes = {
                str(item["path"]): str(item["sha256"])
                for item in manifest.get("sourceFiles", [])
                if isinstance(item, dict)
                and isinstance(item.get("path"), str)
                and isinstance(item.get("sha256"), str)
            }
            return upstream, manifest, snapshot_root
        if source == "embedded":
            raise RouterError(
                f"Requested ref {ref!r} does not match embedded commit {commit}. "
                "Use --source remote to refresh/import another version."
            )

    upstream = Upstream(ref, None)
    return upstream, None, None


def load_library(upstream: Upstream) -> dict[str, Any]:
    try:
        value = json.loads(upstream.read(LIBRARY_PATH))
    except json.JSONDecodeError as error:
        raise RouterError(f"Invalid {LIBRARY_PATH}: {error}") from error
    if not isinstance(value, dict) or not isinstance(value.get("cards"), list):
        raise RouterError(f"Unexpected schema in {LIBRARY_PATH}")
    return value


def candidate_rows(library: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for card in library["cards"]:
        if not isinstance(card, dict):
            continue
        name = card.get("name")
        category = card.get("category")
        source = card.get("source")
        styles = card.get("styles")
        if not all(isinstance(item, str) for item in (name, category, source)) or not isinstance(styles, list):
            continue
        for style in styles:
            if not isinstance(style, dict) or not isinstance(style.get("key"), str):
                continue
            media = style.get("media") if isinstance(style.get("media"), dict) else {}
            rows.append(
                {
                    "card": name,
                    "style": style["key"],
                    "category": category,
                    "source": source,
                    "summary": str(card.get("summary", "")),
                    "use": str(card.get("use", "")),
                    "intention": str(card.get("intention", "")),
                    "tags": [str(tag) for tag in card.get("tags", [])] if isinstance(card.get("tags"), list) else [],
                    "mediaPath": str(media.get("url", "")),
                    "mediaType": str(media.get("type", "")),
                }
            )
    return rows


def score_row(row: dict[str, Any], query: str, expanded: str) -> tuple[float, list[str]]:
    original = normalize(query)
    search = normalize(expanded)
    query_tokens = slug_tokens(search)
    card = normalize(row["card"])
    style = normalize(row["style"])
    category = normalize(row["category"])
    body = normalize(" ".join([row["summary"], row["use"], row["intention"], *row["tags"]]))
    card_tokens = slug_tokens(card)
    style_tokens = slug_tokens(style)
    body_tokens = slug_tokens(body)
    score = 0.0
    reasons = []
    if style and (style in original or style.replace("-", " ") in original):
        score += 180
        reasons.append("exact-style")
    if card and (card in original or card.replace("-", " ") in original):
        score += 140
        reasons.append("exact-card")
    overlap_style = query_tokens & style_tokens
    overlap_card = query_tokens & card_tokens
    overlap_body = query_tokens & body_tokens
    score += 18 * len(overlap_style) + 11 * len(overlap_card) + 2 * min(len(overlap_body), 12)
    if category in query_tokens:
        score += 8
    if overlap_style:
        reasons.append("style:" + ",".join(sorted(overlap_style)))
    if overlap_card:
        reasons.append("card:" + ",".join(sorted(overlap_card)))
    if overlap_body:
        reasons.append("semantic:" + ",".join(sorted(overlap_body)[:6]))
    return score, reasons


def nearest_names(value: str, rows: list[dict[str, Any]]) -> list[str]:
    names = sorted({row["card"] for row in rows} | {row["style"] for row in rows} | {"ink-press"})
    return difflib.get_close_matches(normalize(value), names, n=5, cutoff=0.35)


def forced_selection(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = normalize(name)
    if normalized in {"ink-press", "ink press", "墨压"}:
        return {
            "kind": "template",
            "card": "ink-press",
            "style": "ink-press",
            "category": "template",
            "source": "template/TEMPLATE.md",
            "score": 1000,
            "reasons": ["forced-template"],
        }
    style_match = next((row for row in rows if normalize(row["style"]) == normalized), None)
    if style_match:
        return {**style_match, "kind": "recipe", "score": 1000, "reasons": ["forced-style"]}
    card_matches = [row for row in rows if normalize(row["card"]) == normalized]
    if card_matches:
        row = card_matches[0]
        return {**row, "kind": "recipe", "score": 950, "reasons": ["forced-card-default-style"]}
    suggestions = nearest_names(name, rows)
    suffix = f" Nearest: {', '.join(suggestions)}" if suggestions else ""
    raise RouterError(f"Unknown Shotcraft card/style: {name}.{suffix}")


def select_rows(
    rows: list[dict[str, Any]], query: str, forced: list[str], top: int
) -> tuple[list[dict[str, Any]], list[str]]:
    expanded, aliases = expanded_query(query)
    if forced:
        selected = [forced_selection(name, rows) for name in forced]
    else:
        scored = []
        for row in rows:
            score, reasons = score_row(row, query, expanded)
            scored.append({**row, "kind": "recipe", "score": round(score, 3), "reasons": reasons})
        scored.sort(key=lambda item: (-item["score"], item["card"], item["style"]))
        selected = []
        seen_cards = set()
        for row in scored:
            if row["score"] <= 0 or row["card"] in seen_cards:
                continue
            selected.append(row)
            seen_cards.add(row["card"])
            if len(selected) >= top:
                break
        normalized_query = normalize(query)
        if any(cue in normalized_query for cue in ("ink press", "ink-press", "墨压")):
            selected.insert(0, forced_selection("ink-press", rows))
    deduped = []
    seen = set()
    for row in selected:
        key = (row["kind"], row["card"], row["style"])
        if key not in seen:
            deduped.append(row)
            seen.add(key)
    if not deduped:
        raise RouterError("No Shotcraft recipes matched the request. Use --recipe with a Gallery card/style name.")
    return deduped, aliases


def camel_words(value: str) -> set[str]:
    expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    return slug_tokens(expanded)


def implementation_candidates(row: dict[str, Any], upstream: Upstream) -> list[str]:
    if row["kind"] == "template":
        return ["template/src/aifl/Main.tsx"] if "template/src/aifl/Main.tsx" in upstream.path_set else []
    documented = []
    recipe_text = upstream.read(row["source"]).decode("utf-8", errors="replace")
    for match in re.findall(r"(?:template|demos)/[A-Za-z0-9_./-]+\.(?:tsx|ts|jsx|js)", recipe_text):
        repo_path = safe_repo_path(match)
        if repo_path in upstream.path_set and repo_path not in documented:
            documented.append(repo_path)
    demo_prefix = f"demos/{row['category']}/{row['card']}"
    source_files = [item for item in upstream.matching(demo_prefix) if item.endswith(SOURCE_SUFFIXES)]
    style_tokens = slug_tokens(row["style"])
    card_tokens = slug_tokens(row["card"])
    ranked = []
    for repo_path in source_files:
        stem_tokens = camel_words(PurePosixPath(repo_path).stem)
        score = 8 * len(style_tokens & stem_tokens) + 3 * len(card_tokens & stem_tokens)
        try:
            content = upstream.read(repo_path).decode("utf-8", errors="replace")
        except RouterError:
            content = ""
        normalized_content = normalize(content[:5000])
        if normalize(row["style"]) in normalized_content:
            score += 40
        ranked.append((score, repo_path))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return documented + [repo_path for _, repo_path in ranked if repo_path not in documented]


def collect_repo_paths(
    selected: list[dict[str, Any]], upstream: Upstream, implementations: dict[str, list[str]]
) -> list[str]:
    wanted = {"LICENSE", "demos/README.md", "references/shots/ATTRIBUTION.md"}
    for prefix in ("assets/lib", "demos/_fixtures", "demos/_textures", "template/public"):
        wanted.update(upstream.matching(prefix))
    for row in selected:
        wanted.add(row["source"])
        key = f"{row['card']}::{row['style']}"
        for implementation in implementations.get(key, []):
            wanted.add(implementation)
            if implementation.startswith("template/src/"):
                wanted.update(upstream.matching("template/src"))
        if row["kind"] == "template":
            wanted.update(upstream.matching("template"))
        else:
            wanted.update(upstream.matching(f"demos/{row['category']}/{row['card']}"))
    return sorted(path for path in wanted if path in upstream.path_set)


def preview_url(row: dict[str, Any]) -> str | None:
    if row["kind"] == "template" or not row.get("mediaPath"):
        return None
    media_path = row["mediaPath"].split("?", 1)[0]
    return urllib.parse.urljoin(GALLERY_ROOT, media_path.lstrip("./"))


def atomic_write(destination: Path, data: bytes) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = sha256_bytes(data)
    if destination.exists():
        current = sha256_bytes(destination.read_bytes())
        if current == digest:
            return digest
        raise RouterError(f"Refuse to overwrite content with a different hash: {destination}")
    with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=f".{destination.name}.", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
    try:
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    return digest


def import_source_files(
    upstream: Upstream, repo_paths: list[str], import_root: Path, workers: int
) -> list[dict[str, Any]]:
    def load(repo_path: str) -> tuple[str, bytes]:
        return repo_path, upstream.read(repo_path)

    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(load, repo_path) for repo_path in repo_paths]
        for future in concurrent.futures.as_completed(futures):
            repo_path, data = future.result()
            destination = import_root / repo_path
            digest = atomic_write(destination, data)
            records.append({"path": repo_path, "sha256": digest, "bytes": len(data)})
    return sorted(records, key=lambda item: item["path"])


def import_previews(
    selected: list[dict[str, Any]], preview_root: Path, library_revision: str, workers: int
) -> list[dict[str, Any]]:
    requests = []
    for row in selected:
        url = preview_url(row)
        if url:
            requests.append((row["style"], url))

    def load(item: tuple[str, str]) -> tuple[str, str, bytes, dict[str, str]]:
        style, url = item
        last_error: RouterError | None = None
        for attempt in range(4):
            try:
                data, headers = request_bytes(url, accept="video/mp4")
                return style, url, data, headers
            except RouterError as error:
                last_error = error
                if attempt < 3:
                    time.sleep(0.5 * (2**attempt))
        assert last_error is not None
        raise last_error

    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(load, item) for item in requests]
        for future in concurrent.futures.as_completed(futures):
            style, url, data, headers = future.result()
            destination = preview_root / library_revision / f"{style}.mp4"
            digest = atomic_write(destination, data)
            records.append(
                {
                    "style": style,
                    "url": url,
                    "path": destination.relative_to(preview_root.parent).as_posix(),
                    "sha256": digest,
                    "bytes": len(data),
                    "etag": headers.get("etag"),
                    "lastModified": headers.get("last-modified"),
                }
            )
    return sorted(records, key=lambda item: item["style"])


def import_embedded_previews(
    selected: list[dict[str, Any]],
    preview_root: Path,
    library_revision: str,
    snapshot_root: Path,
    snapshot_manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    manifest_records = {
        item.get("style"): item
        for item in snapshot_manifest.get("previews", [])
        if isinstance(item, dict) and isinstance(item.get("style"), str)
    }
    records = []
    for row in selected:
        url = preview_url(row)
        if not url:
            continue
        style = row["style"]
        source = snapshot_root / "previews" / library_revision / f"{style}.mp4"
        if not source.is_file():
            raise RouterError(f"Embedded preview is missing: {source}")
        data = source.read_bytes()
        manifest_record = manifest_records.get(style, {})
        expected_hash = manifest_record.get("sha256")
        actual_hash = sha256_bytes(data)
        if expected_hash and expected_hash != actual_hash:
            raise RouterError(f"Embedded preview hash mismatch: {source}")
        destination = preview_root / library_revision / f"{style}.mp4"
        digest = atomic_write(destination, data)
        records.append(
            {
                "style": style,
                "url": url,
                "path": destination.relative_to(preview_root.parent).as_posix(),
                "sha256": digest,
                "bytes": len(data),
                "etag": manifest_record.get("etag"),
                "lastModified": manifest_record.get("lastModified"),
                "sourceMode": "embedded-snapshot",
            }
        )
    return sorted(records, key=lambda item: item["style"])


def integration_hints(
    selected: list[dict[str, Any]], upstream: Upstream, candidates: dict[str, list[str]]
) -> dict[str, Any]:
    dependencies = set()
    static_files = set()
    for row in selected:
        key = f"{row['card']}::{row['style']}"
        for repo_path in candidates.get(key, [])[:3]:
            if not repo_path.endswith(SOURCE_SUFFIXES):
                continue
            text = upstream.read(repo_path).decode("utf-8", errors="replace")
            for module in IMPORT_RE.findall(text):
                if not module.startswith("."):
                    dependencies.add(module.split("/", 1)[0] if not module.startswith("@") else "/".join(module.split("/")[:2]))
            static_files.update(STATIC_FILE_RE.findall(text))
    mappings = []
    for public_path in sorted(static_files):
        candidates_for_asset = [
            f"template/public/{public_path}",
            f"demos/_textures/{PurePosixPath(public_path).name}",
        ]
        source = next((item for item in candidates_for_asset if item in upstream.path_set), None)
        mappings.append({"staticFile": public_path, "source": source})
    return {
        "packageDependencies": sorted(dependencies),
        "staticFileMappings": mappings,
        "reviewBeforeExecution": True,
        "adaptationRule": "Preserve tuned timing/easing/mask logic; replace product assets, copy, brand tokens, and measured coordinates.",
    }


def write_lock(path: Path, payload: dict[str, Any], force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if not force:
            raise RouterError(f"Lock already exists: {path}. Pass --force-lock to back it up and replace it.")
        stamp = dt.datetime.now().strftime("%Y%m%d%H%M%S")
        backup = path.with_name(f"{path.name}.backup.{stamp}")
        shutil.move(path, backup)
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    atomic_write(path, encoded)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="", help="Natural-language motion and story intent.")
    parser.add_argument("--recipe", action="append", default=[], help="Exact Gallery card/style name; repeatable.")
    parser.add_argument("--top", type=int, default=5, help="Maximum distinct recipe cards for automatic routing.")
    parser.add_argument("--ref", default=DEFAULT_REF, help="Upstream branch, tag, or exact commit. Resolved commit is locked.")
    parser.add_argument(
        "--source",
        choices=("auto", "embedded", "remote"),
        default="auto",
        help="Source policy. auto prefers the bundled snapshot; remote explicitly refreshes from GitHub.",
    )
    parser.add_argument(
        "--embedded-root",
        type=Path,
        default=DEFAULT_SNAPSHOT_ROOT,
        help="Bundled Shotcraft snapshot root.",
    )
    parser.add_argument("--offline-root", type=Path, help="Authorized local video-shotcraft checkout/archive root.")
    parser.add_argument("--out-dir", type=Path, help="Project routing directory. Omit for a read-only search plan.")
    parser.add_argument("--no-previews", action="store_true", help="Do not download selected Gallery MP4 previews.")
    parser.add_argument("--force-lock", action="store_true", help="Back up and replace an existing shotcraft-lock.json.")
    parser.add_argument("--workers", type=int, default=8, help="Concurrent source/preview downloads (1-16).")
    parser.add_argument("--json", action="store_true", help="Print the full routing result as JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.query and not args.recipe:
        raise RouterError("Provide --query or at least one --recipe.")
    if args.top < 1 or args.top > 12:
        raise RouterError("--top must be between 1 and 12.")
    if args.workers < 1 or args.workers > 16:
        raise RouterError("--workers must be between 1 and 16.")

    upstream, snapshot_manifest, snapshot_root = select_upstream(
        args.source, args.ref, args.offline_root, args.embedded_root
    )
    library = load_library(upstream)
    rows = candidate_rows(library)
    selected, aliases = select_rows(rows, args.query, args.recipe, args.top)

    implementations: dict[str, list[str]] = {}
    for row in selected:
        key = f"{row['card']}::{row['style']}"
        implementations[key] = implementation_candidates(row, upstream)
        row["implementationCandidates"] = implementations[key]
        row["previewUrl"] = preview_url(row)

    result: dict[str, Any] = {
        "schemaVersion": 1,
        "generatedAt": utc_now(),
        "query": args.query,
        "aliasCues": aliases,
        "upstream": {
            "repository": REPO_URL,
            "requestedRef": args.ref,
            "resolvedCommit": upstream.commit,
            "libraryRevision": str(library.get("revision", "unknown")),
            "libraryGeneratedAt": library.get("generatedAt"),
            "license": "Apache-2.0",
            "mode": upstream.mode,
        },
        "selected": selected,
        "integration": integration_hints(selected, upstream, implementations),
    }
    if snapshot_manifest is not None:
        result["upstream"]["snapshotGeneratedAt"] = snapshot_manifest.get("generatedAt")
        result["upstream"]["snapshotSchemaVersion"] = snapshot_manifest.get("schemaVersion")

    if args.out_dir:
        out_dir = args.out_dir.resolve()
        lock_path = out_dir / "shotcraft-lock.json"
        if lock_path.exists() and not args.force_lock:
            raise RouterError(f"Lock already exists: {lock_path}. Pass --force-lock to back it up and replace it.")
        import_root = out_dir / "vendor" / "video-shotcraft" / upstream.commit
        repo_paths = collect_repo_paths(selected, upstream, implementations)
        source_files = import_source_files(upstream, repo_paths, import_root, args.workers)
        preview_files = []
        if not args.no_previews:
            revision = re.sub(r"[^a-zA-Z0-9._-]+", "-", str(library.get("revision", "unversioned")))
            if snapshot_manifest is not None and snapshot_root is not None:
                preview_files = import_embedded_previews(
                    selected, out_dir / "previews", revision, snapshot_root, snapshot_manifest
                )
            else:
                preview_files = import_previews(selected, out_dir / "previews", revision, args.workers)
        result["import"] = {
            "root": import_root.relative_to(out_dir).as_posix(),
            "sourceFiles": source_files,
            "previews": preview_files,
        }
        write_lock(lock_path, result, args.force_lock)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"Shotcraft commit: {upstream.commit}")
        for index, row in enumerate(selected, 1):
            implementation = row["implementationCandidates"][0] if row["implementationCandidates"] else "custom implementation required"
            print(f"{index}. {row['card']} · {row['style']} -> {implementation}")
        if args.out_dir:
            print(f"Lock: {(args.out_dir.resolve() / 'shotcraft-lock.json')}")
        else:
            print("Plan only: pass --out-dir to import locked source and previews.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RouterError as error:
        print(f"shotcraft-router: {error}", file=sys.stderr)
        raise SystemExit(2)
