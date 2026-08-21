const form = document.getElementById("search-form");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const labels = document.getElementById("labels").value;
  const language = document.getElementById("language").value;
  const days = document.getElementById("days").value;
  const min_stars = document.getElementById("min_stars").value;

  const params = new URLSearchParams({ labels, language, days, min_stars });

  const submitBtn = form.querySelector("button");
  submitBtn.disabled = true;
  statusEl.textContent = "Searching GitHub...";
  resultsEl.innerHTML = "";

  try {
    const res = await fetch(`/api/search?${params.toString()}`);
    const data = await res.json();

    if (!res.ok) {
      statusEl.textContent = `Error: ${data.error || "something went wrong"}`;
      if (data.retry_after_seconds) {
        statusEl.textContent += ` (retry in ${data.retry_after_seconds}s)`;
      }
      submitBtn.disabled = false;
      return;
    }

    statusEl.textContent = `Found ${data.count} issue(s). Query: ${data.query}`;
    renderResults(data.issues);
  } catch (err) {
    statusEl.textContent = `Network error: ${err.message}`;
  } finally {
    submitBtn.disabled = false;
  }
});

function renderResults(issues) {
  if (!issues.length) {
    resultsEl.innerHTML = "<p>No matching issues found. Try loosening your filters.</p>";
    return;
  }

  resultsEl.innerHTML = issues
    .map(
      (issue) => `
    <div class="issue-card">
      <h3><a href="${issue.issue_url}" target="_blank" rel="noopener">${escapeHtml(issue.title)}</a></h3>
      <div class="repo-line">
        <a href="${issue.repo_url}" target="_blank" rel="noopener">${escapeHtml(issue.repo_full_name)}</a>
      </div>
      <div class="labels">
        ${issue.labels.map((l) => `<span class="label-chip">${escapeHtml(l)}</span>`).join("")}
      </div>
      <div class="meta">
        Created ${new Date(issue.created_at).toLocaleDateString()} ·
        ${issue.comments} comment(s)
      </div>
    </div>
  `
    )
    .join("");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// auto-run a search on page load with default filters
form.dispatchEvent(new Event("submit"));
