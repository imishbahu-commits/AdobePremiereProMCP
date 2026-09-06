// PremierPro MCP — video render gallery + high-speed reference uploader.
// No dependencies. Parallel raw-chunk uploads land byte-exact in
// outputs/uploads/ (no multipart overhead), with HTTP Range streaming for
// smooth browser playback and auto poster frames via the local ffmpeg.
import http from "node:http";
import {
  createReadStream, createWriteStream, statSync, readdirSync,
  existsSync, mkdirSync, rmSync,
} from "node:fs";
import { readFile, unlink } from "node:fs/promises";
import { execFile } from "node:child_process";
import { extname, join, resolve, relative, sep, basename } from "node:path";
import { fileURLToPath } from "node:url";
import { pipeline } from "node:stream/promises";

const HERE = fileURLToPath(new URL(".", import.meta.url));
const PUBLIC = join(HERE, "public");
const OUTPUTS_ROOT = resolve(HERE, "..", "..");   // repo/outputs
const UPLOADS = join(OUTPUTS_ROOT, "uploads");
const PARTS = join(UPLOADS, ".parts");
const FFMPEG = join(HERE, "..", "ffmpeg_x64");
const PORT = Number(process.env.PORT || 8080);
const MAX_CHUNK = 32 * 1024 * 1024;               // 32 MB per chunk request

mkdirSync(UPLOADS, { recursive: true });
mkdirSync(PARTS, { recursive: true });
mkdirSync(join(PUBLIC, "posters"), { recursive: true });

const MIME = {
  ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".png": "image/png", ".jpg": "image/jpeg", ".mp4": "video/mp4",
  ".mov": "video/quicktime", ".webm": "video/webm", ".mkv": "video/x-matroska",
  ".m4v": "video/mp4", ".avi": "video/x-msvideo",
};
const VIDEO_EXT = new Set([".mp4", ".mov", ".webm", ".mkv", ".m4v"]);
const isVideo = (p) => VIDEO_EXT.has(extname(p).toLowerCase());

function walk(dir, acc = []) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "server" || entry.name === "pylibs" || entry.name === ".parts") continue;
    const p = join(dir, entry.name);
    if (entry.isDirectory()) walk(p, acc);
    else if (isVideo(p)) acc.push(p);
  }
  return acc;
}

const send = (res, code, headers, body) => { res.writeHead(code, headers); res.end(body); };
const sendJSON = (res, code, obj) =>
  send(res, code, { "Content-Type": MIME[".json"], "Cache-Control": "no-cache" }, JSON.stringify(obj));

function safeName(raw) {
  let n = basename(String(raw || "video.mp4")).replace(/[^\w.() -]+/g, "_").trim() || "video.mp4";
  if (n.startsWith(".")) n = "_" + n.slice(1);
  return n;
}

function streamFile(req, res, absPath) {
  if (!resolve(absPath).startsWith(OUTPUTS_ROOT + sep)) return send(res, 403, {}, "forbidden");
  let st;
  try { st = statSync(absPath); } catch { return send(res, 404, {}, "not found"); }
  const type = MIME[extname(absPath).toLowerCase()] || "application/octet-stream";
  const range = req.headers.range;
  if (range && type.startsWith("video/")) {
    const m = /^bytes=(\d*)-(\d*)$/.exec(range);
    let start = m && m[1] ? parseInt(m[1], 10) : 0;
    let end = m && m[2] ? Math.min(parseInt(m[2], 10), st.size - 1) : st.size - 1;
    if (m && !m[1]) { start = Math.max(0, st.size - parseInt(m[2], 10)); end = st.size - 1; }
    if (start >= st.size || start > end) {
      return send(res, 416, { "Content-Range": `bytes */${st.size}` }, "range not satisfiable");
    }
    res.writeHead(206, {
      "Content-Range": `bytes ${start}-${end}/${st.size}`, "Accept-Ranges": "bytes",
      "Content-Length": end - start + 1, "Content-Type": type, "Cache-Control": "no-cache",
    });
    createReadStream(absPath, { start, end }).pipe(res);
  } else {
    res.writeHead(200, {
      "Content-Length": st.size, "Content-Type": type,
      "Accept-Ranges": "bytes", "Cache-Control": "no-cache",
    });
    createReadStream(absPath).pipe(res);
  }
}

function videoEntry(absPath) {
  const st = statSync(absPath);
  const rel = relative(OUTPUTS_ROOT, absPath);
  const base = rel.split(sep).pop();
  const poster = join(PUBLIC, "posters", base.replace(/\.[^.]+$/, ".jpg"));
  return {
    name: base,
    path: rel,
    url: "/video/" + rel.split(sep).map(encodeURIComponent).join("/"),
    poster: existsSync(poster) ? "/posters/" + basename(poster) : null,
    uploaded: rel.startsWith("uploads" + sep),
    bytes: st.size,
    mtime: st.mtime,
  };
}

function makePoster(absPath, base) {
  const poster = join(PUBLIC, "posters", base.replace(/\.[^.]+$/, ".jpg"));
  execFile(FFMPEG, ["-y", "-hide_banner", "-loglevel", "error",
    "-ss", "1.5", "-i", absPath, "-frames:v", "1", "-q:v", "3", poster],
    { timeout: 30000 }, () => {});
}

async function readJsonBody(req, cap = 1e6) {
  let data = "", bytes = 0;
  for await (const chunk of req) {
    bytes += chunk.length;
    if (bytes > cap) throw new Error("body too large");
    data += chunk;
  }
  return JSON.parse(data || "{}");
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://x");
  const path = decodeURIComponent(url.pathname);

  try {
    if (path === "/api/videos" && req.method === "GET") {
      let files = [];
      try { files = walk(OUTPUTS_ROOT); } catch {}
      const videos = files.map(videoEntry)
        .sort((a, b) => new Date(b.mtime) - new Date(a.mtime));
      return sendJSON(res, 200, { root: OUTPUTS_ROOT, count: videos.length, videos });
    }

    // ── high-speed chunked upload ────────────────────────────────────────
    if (path === "/api/upload/chunk" && req.method === "PUT") {
      const id = url.searchParams.get("id") || "";
      const n = Number(url.searchParams.get("n"));
      if (!/^[A-Za-z0-9-]{8,64}$/.test(id)) return sendJSON(res, 400, { error: "bad id" });
      if (!Number.isInteger(n) || n < 0 || n > 99999) return sendJSON(res, 400, { error: "bad chunk no" });
      const len = Number(req.headers["content-length"] || 0);
      if (len <= 0 || len > MAX_CHUNK) return sendJSON(res, 400, { error: `chunk must be 1B..${MAX_CHUNK}B` });
      const dir = join(PARTS, id);
      mkdirSync(dir, { recursive: true });
      const file = join(dir, String(n).padStart(6, "0") + ".part");
      await pipeline(req, createWriteStream(file));
      const received = statSync(file).size;
      if (received !== len) {
        await unlink(file).catch(() => {});
        return sendJSON(res, 409, { error: "short read", received });
      }
      return sendJSON(res, 200, { ok: true, n, bytes: received });
    }

    if (path === "/api/upload/complete" && req.method === "POST") {
      const { id, name, chunks, size } = await readJsonBody(req);
      if (!/^[A-Za-z0-9-]{8,64}$/.test(String(id))) return sendJSON(res, 400, { error: "bad id" });
      const count = Number(chunks);
      if (!Number.isInteger(count) || count < 1) return sendJSON(res, 400, { error: "bad chunks" });
      const dir = join(PARTS, id);
      let base = safeName(name);
      if (!isVideo(base)) {
        const ext = Object.keys(MIME).find((e) => MIME[e].startsWith("video/"));
        base += ext || ".mp4";
      }
      let dest = join(UPLOADS, base);
      let k = 1;
      while (existsSync(dest)) dest = join(UPLOADS, base.replace(/(\.[^.]+)$/, `_${k++}$1`));
      base = basename(dest);

      let total = 0;
      for (let n = 0; n < count; n++) {
        const part = join(dir, String(n).padStart(6, "0") + ".part");
        if (!existsSync(part)) return sendJSON(res, 409, { error: `missing chunk ${n}` });
        total += statSync(part).size;
      }
      if (Number(size) && total !== Number(size)) {
        return sendJSON(res, 409, { error: `size mismatch ${total} != ${size}` });
      }

      const out = createWriteStream(dest);
      for (let n = 0; n < count; n++) {
        const part = join(dir, String(n).padStart(6, "0") + ".part");
        await pipeline(createReadStream(part), out, { end: false });
      }
      await new Promise((fin) => out.end(fin));
      rmSync(dir, { recursive: true, force: true });

      const entry = videoEntry(dest);
      makePoster(dest, base);
      console.log(`[upload] ${base}: ${total} bytes in ${count} chunk(s)`);
      return sendJSON(res, 200, { ok: true, video: entry });
    }

    if (path.startsWith("/video/")) {
      return streamFile(req, res, join(OUTPUTS_ROOT, path.slice("/video/".length)));
    }
    if (path.startsWith("/posters/")) {
      return streamFile(req, res, join(PUBLIC, path));
    }
    return streamFile(req, res, join(PUBLIC, path === "/" ? "/index.html" : path));
  } catch (err) {
    console.error(err);
    return sendJSON(res, 500, { error: String(err && err.message || err) });
  }
});

server.requestTimeout = 0; // long uploads must never time out
server.listen(PORT, "0.0.0.0", () => {
  console.log(`[gallery+upload] serving ${OUTPUTS_ROOT} on http://0.0.0.0:${PORT}`);
});
