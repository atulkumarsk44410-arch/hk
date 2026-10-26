const $ = (id) => document.getElementById(id);
document.querySelectorAll(".nav").forEach(btn => btn.addEventListener("click", () => {
  document.querySelectorAll(".nav").forEach(x => x.classList.toggle("active", x === btn));
  document.querySelectorAll("main section").forEach(s => s.classList.add("hidden"));
  $(btn.dataset.tab).classList.remove("hidden");
  if (btn.dataset.tab === "leads") loadLeads();
}));
$("generate").addEventListener("click", async () => {
  const button = $("generate");
  button.disabled = true; button.textContent = "कंटेंट बनाया जा रहा है...";
  $("notice").textContent = ""; $("output").textContent = "कृपया प्रतीक्षा करें...";
  try {
    const res = await fetch("/api/generate", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({
      product:$("product").value, audience:$("audience").value, language:$("language").value,
      kind:$("kind").value, details:$("details").value
    })});
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "कुछ गलत हुआ");
    $("output").textContent = data.result;
  } catch (e) { $("notice").textContent = e.message; $("output").textContent = "कंटेंट तैयार नहीं हो सका। ऊपर दिया संदेश देखें।"; }
  finally { button.disabled = false; button.textContent = "✦ AI से कंटेंट बनाएँ"; }
});
$("copy").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText($("output").textContent); $("copy").textContent = "कॉपी हो गया"; setTimeout(()=>$("copy").textContent="कॉपी करें", 1500); }
  catch { $("notice").textContent = "कॉपी नहीं हुआ; टेक्स्ट को चुनकर कॉपी करें।"; }
});
$("leadForm").addEventListener("submit", async (e) => {
  e.preventDefault(); $("leadNotice").textContent = "";
  try {
    const res = await fetch("/api/leads", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({name:$("leadName").value,phone:$("leadPhone").value,product:$("leadProduct").value})});
    const data = await res.json(); if (!res.ok) throw new Error(data.error || "लीड सेव नहीं हुई");
    $("leadForm").reset(); $("leadNotice").textContent = "लीड सेव हो गई।"; loadLeads();
  } catch (err) { $("leadNotice").textContent = err.message; }
});
async function loadLeads() {
  const tbody = $("leadRows"); tbody.innerHTML = "<tr><td colspan='5'>लोड हो रहा है...</td></tr>";
  try {
    const res = await fetch("/api/leads"); if (!res.ok) throw new Error("डेटा लोड नहीं हुआ");
    const rows = await res.json(); tbody.innerHTML = "";
    if (!rows.length) { tbody.innerHTML = "<tr><td colspan='5'>अभी कोई लीड नहीं है।</td></tr>"; return; }
    rows.forEach(lead => {
      const tr = document.createElement("tr");
      [lead.name, lead.phone, lead.product || "-", (lead.created_at || "").replace("T"," ")].forEach(value => { const td=document.createElement("td"); td.textContent=value; tr.appendChild(td); });
      const td=document.createElement("td"), sel=document.createElement("select");
      ["New","Contacted","Qualified","Won","Lost"].forEach(status=>{const opt=document.createElement("option");opt.value=status;opt.textContent=status;opt.selected=status===lead.status;sel.appendChild(opt);});
      sel.addEventListener("change", async ()=>{const r=await fetch(`/api/leads/${lead.id}`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify({status:sel.value})});if(!r.ok) alert("स्टेटस अपडेट नहीं हुआ");});
      td.appendChild(sel);tr.appendChild(td);tbody.appendChild(tr);
    });
  } catch(e) { tbody.innerHTML = "<tr><td colspan='5'>लीड लोड करने में समस्या हुई।</td></tr>"; }
}
$("metaPlan").addEventListener("click", () => { $("kind").value="meta"; document.querySelector('[data-tab="creator"]').click(); });
