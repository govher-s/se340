#!/usr/bin/env bash
# Builds a static snapshot of the Nomad Postcards site into docs/ for GitHub Pages.
# Run from the project folder (with the project's packages installed):  ./build_pages.sh
# Then commit and push the docs/ folder.
set -e
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
PORT=8765

$PY manage.py runserver "$PORT" --noreload >/dev/null 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null' EXIT
sleep 3

rm -rf docs && mkdir docs
(cd docs && wget -q --recursive --level=4 --page-requisites --convert-links \
  --adjust-extension --no-host-directories \
  --reject-regex '(accounts/|register/|admin/|create/|mine/|delete/|\?)' \
  "http://127.0.0.1:$PORT/" || true)
touch docs/.nojekyll

$PY - "$PORT" <<'EOF'
import pathlib, re, sys
port = sys.argv[1]
docs = pathlib.Path("docs")

FILTER_JS = """
<script>
(function () {
  var params = new URLSearchParams(location.search);
  var q = (params.get("q") || "").trim().toLowerCase();
  var exclude = params.getAll("exclude");
  var box = document.getElementById("post-search");
  if (box) box.value = params.get("q") || "";
  document.querySelectorAll('input[name="exclude"]').forEach(function (cb) {
    cb.checked = exclude.indexOf(cb.value) !== -1;
  });
  var badge = { "profanity": ".badge-red", "long": ".badge-green", "external-links": ".badge-blue" };
  document.querySelectorAll(".post-card").forEach(function (card) {
    var show = !q || card.textContent.toLowerCase().indexOf(q) !== -1;
    exclude.forEach(function (label) {
      if (badge[label] && card.querySelector(badge[label])) show = false;
    });
    card.style.display = show ? "" : "none";
  });
})();
</script>
"""

for page in docs.rglob("*.html"):
    html = page.read_text(encoding="utf-8")
    # Login/accounts and writing need a server, so drop those links.
    html = re.sub(r'\s*<a href="http://127\.0\.0\.1:%s/accounts/login/">Account</a>' % port, "", html)
    html = re.sub(r'\s*<section class="write-banner container">.*?</section>', "", html, flags=re.S)
    if page == docs / "index.html":
        # Home-page search goes to the Stories page, which filters in the browser.
        html = html.replace('action="index.html"', 'action="posts/index.html"')
    if page == docs / "posts" / "index.html":
        html = html.replace("</body>", FILTER_JS + "</body>")
    leftover = re.findall(r'http://127\.0\.0\.1:%s[^"]*' % port, html)
    if leftover:
        print("warning: local links left in", page, leftover)
    page.write_text(html, encoding="utf-8")
print("Built", sum(1 for _ in docs.rglob("*.html")), "pages into docs/")
EOF
