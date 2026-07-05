from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .analyzers import analyze_documents
from .charts import bar_chart, line_chart
from .loaders import load_json_text
from .reports import markdown_report


def run_server(host: str = "127.0.0.1", port: int = 8088) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Instagram Analytics UI running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server")
    finally:
        server.server_close()


class Handler(BaseHTTPRequestHandler):
    server_version = "InstagramAnalytics/0.1"

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            self._send_html(APP_HTML)
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if self.path != "/api/analyze":
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("content-length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            files = payload.get("files", [])
            documents = [
                load_json_text(item["content"], item.get("name", "uploaded.json"))
                for item in files
                if item.get("content")
            ]
            summary = analyze_documents(documents)
            response = {
                "summary": summary,
                "topAccountsChart": bar_chart(
                    summary["top_accounts"],
                    "account",
                    "count",
                    title="Top accounts",
                ),
                "monthlyChart": line_chart(
                    summary["monthly_counts"],
                    "month",
                    "count",
                    title="Interactions over time",
                ),
                "report": markdown_report(summary),
            }
            self._send_json(response)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=400)

    def log_message(self, format: str, *args) -> None:
        return

    def _send_html(self, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "text/html;charset=utf-8")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, body: dict, status: int = 200) -> None:
        encoded = json.dumps(body, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json;charset=utf-8")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


APP_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Instagram Analytics</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f7f5;
      --surface: #ffffff;
      --text: #232323;
      --muted: #74706c;
      --border: #dedbd5;
      --accent: #f06449;
      --teal: #1f9d8a;
      --shadow: 0 14px 40px rgba(35, 35, 35, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }
    header {
      height: 68px;
      padding: 0 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border);
      background: rgba(255, 255, 255, 0.78);
      backdrop-filter: blur(14px);
      position: sticky;
      top: 0;
      z-index: 3;
    }
    .brand { display: flex; align-items: baseline; gap: 14px; }
    h1 { margin: 0; font-size: 20px; letter-spacing: 0; }
    .brand span, .status { color: var(--muted); font-size: 13px; }
    main {
      display: grid;
      grid-template-columns: minmax(280px, 360px) 1fr;
      gap: 22px;
      padding: 24px;
      max-width: 1440px;
      margin: 0 auto;
    }
    .panel, .stat, .chart, .report {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }
    .panel { padding: 20px; align-self: start; position: sticky; top: 92px; }
    h2 { margin: 0 0 12px; font-size: 16px; }
    p { color: var(--muted); margin: 0 0 16px; font-size: 14px; }
    .drop {
      border: 1.5px dashed #bdb8ae;
      border-radius: 8px;
      padding: 28px 18px;
      background: #fbfbfa;
      text-align: center;
      cursor: pointer;
      transition: border-color .15s ease, background .15s ease;
    }
    .drop:hover, .drop.active { border-color: var(--accent); background: #fff8f5; }
    input[type="file"] { display: none; }
    .button {
      width: 100%;
      border: 0;
      border-radius: 8px;
      padding: 12px 14px;
      margin-top: 14px;
      font-weight: 700;
      background: var(--text);
      color: white;
      cursor: pointer;
    }
    .button:disabled { opacity: .45; cursor: not-allowed; }
    .file-list { margin-top: 16px; display: grid; gap: 8px; }
    .file-row {
      padding: 9px 10px;
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 13px;
      color: #3e3b38;
      background: #fff;
      overflow-wrap: anywhere;
    }
    .dashboard { display: grid; gap: 18px; min-width: 0; }
    .stats {
      display: grid;
      grid-template-columns: repeat(4, minmax(130px, 1fr));
      gap: 14px;
    }
    .stat { padding: 16px; min-height: 92px; }
    .stat .label { color: var(--muted); font-size: 12px; font-weight: 700; text-transform: uppercase; }
    .stat .value { margin-top: 9px; font-size: 27px; font-weight: 800; }
    .stat .note { color: var(--muted); font-size: 12px; margin-top: 4px; }
    .charts {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }
    .chart { padding: 16px; overflow: auto; min-height: 290px; }
    .chart svg { width: 100%; height: auto; display: block; }
    .report { padding: 18px; }
    .report-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
    textarea {
      width: 100%;
      min-height: 250px;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
      resize: vertical;
      font: 13px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      color: #333;
      background: #fbfbfa;
    }
    .mini-button {
      border: 1px solid var(--border);
      background: #fff;
      color: var(--text);
      border-radius: 8px;
      padding: 8px 10px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
    }
    .empty {
      padding: 36px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--surface);
      color: var(--muted);
      text-align: center;
    }
    .error { color: #b42318; font-size: 13px; margin-top: 12px; }
    @media (max-width: 980px) {
      main { grid-template-columns: 1fr; padding: 16px; }
      .panel { position: static; }
      .stats, .charts { grid-template-columns: 1fr; }
      header { padding: 0 16px; }
      .brand { display: block; }
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <h1>Instagram Analytics</h1>
      <span>Offline export analyzer</span>
    </div>
    <div class="status" id="status">No files loaded</div>
  </header>
  <main>
    <section class="panel">
      <h2>Upload export JSON</h2>
      <p>Select JSON files from your Instagram export. Your data stays on this local machine.</p>
      <label class="drop" id="drop">
        <strong>Drop JSON files here</strong><br>
        <span>or click to choose files</span>
        <input id="fileInput" type="file" accept=".json,application/json" multiple>
      </label>
      <button class="button" id="run" disabled>Analyze files</button>
      <div class="error" id="error"></div>
      <div class="file-list" id="files"></div>
    </section>
    <section class="dashboard" id="dashboard">
      <div class="empty">Upload Instagram export JSON files to see account rankings, interaction trends, and a report.</div>
    </section>
  </main>
  <script>
    const input = document.getElementById('fileInput');
    const drop = document.getElementById('drop');
    const run = document.getElementById('run');
    const filesEl = document.getElementById('files');
    const errorEl = document.getElementById('error');
    const dashboard = document.getElementById('dashboard');
    const statusEl = document.getElementById('status');
    let files = [];

    function setFiles(nextFiles) {
      files = Array.from(nextFiles).filter(file => file.name.endsWith('.json'));
      run.disabled = files.length === 0;
      statusEl.textContent = files.length ? `${files.length} file${files.length === 1 ? '' : 's'} ready` : 'No files loaded';
      filesEl.innerHTML = files.map(file => `<div class="file-row">${file.name}</div>`).join('');
      errorEl.textContent = '';
    }

    input.addEventListener('change', event => setFiles(event.target.files));
    drop.addEventListener('dragover', event => {
      event.preventDefault();
      drop.classList.add('active');
    });
    drop.addEventListener('dragleave', () => drop.classList.remove('active'));
    drop.addEventListener('drop', event => {
      event.preventDefault();
      drop.classList.remove('active');
      setFiles(event.dataTransfer.files);
    });

    async function readFile(file) {
      return { name: file.name, content: await file.text() };
    }

    run.addEventListener('click', async () => {
      errorEl.textContent = '';
      run.disabled = true;
      run.textContent = 'Analyzing...';
      try {
        const payload = { files: await Promise.all(files.map(readFile)) };
        const response = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Analysis failed');
        render(data);
      } catch (error) {
        errorEl.textContent = error.message;
      } finally {
        run.disabled = files.length === 0;
        run.textContent = 'Analyze files';
      }
    });

    function render(data) {
      const summary = data.summary;
      const top = summary.top_account || { account: 'none', count: 0 };
      const range = summary.date_range || {};
      dashboard.innerHTML = `
        <div class="stats">
          ${stat('Interactions', summary.total_interactions, 'Extracted records')}
          ${stat('Accounts', summary.unique_accounts, 'Unique account names')}
          ${stat('Top account', escapeHtml(top.account), `${top.count} interactions`)}
          ${stat('Date range', range.start || 'unknown', range.end || '')}
        </div>
        <div class="charts">
          <div class="chart">${data.topAccountsChart}</div>
          <div class="chart">${data.monthlyChart}</div>
        </div>
        <div class="report">
          <div class="report-head">
            <h2>Report preview</h2>
            <button class="mini-button" id="download">Download Markdown</button>
          </div>
          <textarea readonly>${escapeHtml(data.report)}</textarea>
        </div>
      `;
      document.getElementById('download').addEventListener('click', () => {
        const blob = new Blob([data.report], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'instagram-report.md';
        link.click();
        URL.revokeObjectURL(url);
      });
      statusEl.textContent = 'Analysis complete';
    }

    function stat(label, value, note) {
      return `<div class="stat">
        <div class="label">${label}</div>
        <div class="value">${value}</div>
        <div class="note">${note}</div>
      </div>`;
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
    }
  </script>
</body>
</html>
"""
