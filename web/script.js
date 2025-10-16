const repoUser = "dggamino";
const repoName = "trust-messenger-mvp";
const jsonURL = `https://raw.githubusercontent.com/${repoUser}/${repoName}/main/data/trust_log.json`;

async function fetchData() {
  try {
    const res = await fetch(jsonURL + '?t=' + Date.now());
    const data = await res.json();
    renderTable(data);
    renderRanking(data);
  } catch (e) {
    console.error("Error cargando datos:", e);
  }
}

function renderTable(data) {
  const tbody = document.querySelector("#trustTable tbody");
  tbody.innerHTML = "";
  data.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.user}</td>
      <td>${row.message}</td>
      <td>$${row.amount}</td>
      <td>${row.due_date}</td>
      <td>${row.status === "COMPLETED" ? "✅ Cumplido" : "⏳ Pendiente"}</td>
      <td>${row.hash.slice(0,12)}…</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderRanking(data) {
  const usersDiv = document.querySelector("#users");
  usersDiv.innerHTML = "";
  const users = {};
  data.forEach(r => {
    if (!users[r.user]) users[r.user] = { total: 0, done: 0 };
    users[r.user].total++;
    if (r.status === "COMPLETED") users[r.user].done++;
  });

  const ranking = Object.entries(users)
    .map(([u, v]) => ({ user: u, score: ((v.done/v.total)*100).toFixed(1) }))
    .sort((a,b) => b.score - a.score);

  ranking.forEach((r, i) => {
    const div = document.createElement("div");
    div.className = "user-card";
    const avatar = `https://api.dicebear.com/8.x/identicon/svg?seed=${r.user}`;
    div.innerHTML = `
      <img src="${avatar}" alt="avatar">
      <h3>#${i+1} ${r.user}</h3>
      <p>Reputación: <strong>${r.score}%</strong></p>
    `;
    usersDiv.appendChild(div);
  });
}

fetchData();
setInterval(fetchData, 60000);

