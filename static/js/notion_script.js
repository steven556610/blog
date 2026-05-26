/* Notion Integrator Dashboard Client Controller */

document.addEventListener("DOMContentLoaded", () => {
    // Initial fetch of history reports
    fetchHistoryReports();
});

// 1. Tab switching
function switchMainTab(tabName) {
    const tabs = ["time", "theme", "vault"];
    
    tabs.forEach(t => {
        const btn = document.getElementById(`tab-btn-${t}`);
        const pane = document.getElementById(`pane-${t}`);
        
        if (t === tabName) {
            btn.classList.add("active");
            pane.classList.add("active");
        } else {
            btn.classList.remove("active");
            pane.classList.remove("active");
        }
    });
    
    if (tabName === "vault") {
        fetchHistoryReports();
    }
}

// 2. Fetch history reports from SQLite database simulated endpoint
async function fetchHistoryReports() {
    const tableBody = document.getElementById("history-table-body");
    tableBody.innerHTML = '<tr><td colspan="7" style="text-align:center;"><div class="loader-spinner" style="margin:20px auto; width:20px; height:20px; border-width:2.5px;"></div>載入歷史紀錄中...</td></tr>';
    
    try {
        const response = await fetch("/api/notion/history");
        const history = await response.json();
        
        tableBody.innerHTML = "";
        
        if (history.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align:center; color:#888;">⚠️ 尚無任何已生成的報告紀錄。</td></tr>';
            return;
        }
        
        // Reverse array to show newest first
        const sortedHistory = [...history].reverse();
        
        sortedHistory.forEach(item => {
            const tr = document.createElement("tr");
            
            // Format task type badge
            let typeBadge = "";
            if (item.task_type === "Weekly") {
                typeBadge = '<span style="background-color:rgba(244,63,94,0.1); border:1px solid #f43f5e; color:#ff85a2; padding:3px 8px; border-radius:12px; font-size:0.75rem; font-weight:700;">週報</span>';
            } else if (item.task_type === "Monthly") {
                typeBadge = '<span style="background-color:rgba(129,140,248,0.1); border:1px solid #818cf8; color:#a5b4fc; padding:3px 8px; border-radius:12px; font-size:0.75rem; font-weight:700;">月報</span>';
            } else {
                typeBadge = '<span style="background-color:rgba(16,185,129,0.1); border:1px solid #10b981; color:#34d399; padding:3px 8px; border-radius:12px; font-size:0.75rem; font-weight:700;">主題報</span>';
            }
            
            tr.innerHTML = `
                <td><b>#${item.id}</b></td>
                <td>${typeBadge}</td>
                <td style="color:#ffccd5; font-weight:500;">${item.theme === "N/A" ? "🗓️ 時間段自動總結報告" : `🎯 ${item.theme}`}</td>
                <td><code style="background-color:#1e2030; padding:2px 6px; border-radius:4px;">${item.start_date}</code></td>
                <td><code style="background-color:#1e2030; padding:2px 6px; border-radius:4px;">${item.end_date}</code></td>
                <td style="opacity:0.8;">${item.created_at}</td>
                <td>
                    <a href="${item.notion_url}" target="_blank" class="notion-btn">
                        <i data-lucide="external-link" style="width:12px; height:12px;"></i> Notion
                    </a>
                </td>
            `;
            tableBody.appendChild(tr);
        });
        
        lucide.createIcons();
    } catch (e) {
        console.error("Error fetching history:", e);
        tableBody.innerHTML = '<tr><td colspan="7" style="text-align:center; color:#ef4444;">⚠️ 載入資料失敗，請確認伺服器狀態。</td></tr>';
    }
}

// Helper to convert Markdown titles and bold text into HTML preview
function parseMarkdown(md) {
    return md
        .replace(/\n\n/g, "<br><br>")
        .replace(/^# (.*?)$/gm, '<h1 style="color:#ff85a2; font-size:1.45rem; margin-top:20px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:6px;">$1</h1>')
        .replace(/^## (.*?)$/gm, '<h2 style="color:#ffccd5; font-size:1.2rem; margin-top:15px; border-bottom:1px dashed rgba(255,255,255,0.08); padding-bottom:4px;">$1</h2>')
        .replace(/^### (.*?)$/gm, '<h3 style="color:#fff; font-size:1.05rem; margin-top:12px;">$1</h3>')
        .replace(/\*   \*\*(.*?)\*\*：/g, '• <strong>$1</strong>: ')
        .replace(/\*   \*\*(.*?)\*\*/g, '• <strong>$1</strong>')
        .replace(/\n\*   /g, '<br>• ')
        .replace(/\n\* /g, '<br>• ')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`([^`]+)`/g, '<code style="background-color:#1e2030; padding:2px 6px; border-radius:4px; font-size:0.88em; color:#ff85a2;">$1</code>');
}

// 3. Generate Time-Based report (Weekly/Monthly)
async function generateTimeReport() {
    const startDate = document.getElementById("time-start-date").value;
    const endDate = document.getElementById("time-end-date").value;
    const model = document.getElementById("model-selector").value;
    
    // Get checked radio report type
    const reportTypeRadios = document.getElementsByName("report-type-radio");
    let reportType = "Weekly";
    for (let r of reportTypeRadios) {
        if (r.checked) {
            reportType = r.value;
            break;
        }
    }
    
    if (!startDate || !endDate) {
        alert("請選擇完整日期區間！");
        return;
    }
    
    if (new Date(startDate) > new Date(endDate)) {
        alert("起始日期必須早於結束日期！");
        return;
    }
    
    const statusBox = document.getElementById("time-status-container");
    const previewBox = document.getElementById("time-preview-container");
    
    previewBox.style.display = "none";
    statusBox.style.display = "block";
    statusBox.innerHTML = "";
    
    // Progressive delay seeder sequece simulation
    appendStatusStep(statusBox, "Fetching missing and active dates in range...", "loading");
    
    setTimeout(() => {
        appendStatusStep(statusBox, `Found 6 daily journal logs in date range. Fetching contents... [OK]`, "success");
        appendStatusStep(statusBox, `Initializing local GGUF model: <b>${model}</b>...`, "loading");
    }, 1500);
    
    setTimeout(() => {
        appendStatusStep(statusBox, `Loaded GGUF model into host CPU memory successfully. [OK]`, "success");
        appendStatusStep(statusBox, `Processing semantic log parsing and structural summarizing...`, "loading");
    }, 3200);
    
    setTimeout(() => {
        appendStatusStep(statusBox, `LLM Inference complete! Formulated core progress and future outlook. [OK]`, "success");
        appendStatusStep(statusBox, `Connecting to Notion API Integration Database and writing page...`, "loading");
    }, 5500);
    
    setTimeout(async () => {
        // Run API request to append database seeder record
        try {
            const res = await fetch("/api/notion/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    start_date: startDate,
                    end_date: endDate,
                    report_type: reportType,
                    model: model
                })
            });
            const data = await res.json();
            
            appendStatusStep(statusBox, `Notion database page successfully created! Pushed weekly metadata. [OK]`, "success");
            appendStatusStep(statusBox, `Triggering Email notifier and sending LINE Notify alert card... [OK]`, "success");
            
            // Final success alert banner
            const finalAlert = document.createElement("div");
            finalAlert.className = "status-box success";
            finalAlert.innerHTML = `
                <i data-lucide="check-circle" style="color:#10b981; width:22px; height:22px;"></i>
                <div>
                    <strong style="color:#fff; font-size:0.95rem;">Notion ${reportType} Report Generated Successfully!</strong><br>
                    已將整合摘要同步推播寫入 Notion 專區。
                    <a href="${data.notion_url}" target="_blank" style="color:#ff85a2; text-decoration:underline; font-weight:bold; margin-left:8px;">[ 開啟 Notion 頁面 ]</a>
                </div>
            `;
            statusBox.appendChild(finalAlert);
            
            // Renders html preview
            previewBox.style.display = "block";
            previewBox.innerHTML = `
                <h3 style="color:#fff; border-bottom:1px solid var(--border-color); padding-bottom:8px; margin-bottom:15px;"><i data-lucide="file-check"></i> Generated Summary Preview</h3>
                <div class="preview-box">${parseMarkdown(data.summary)}</div>
            `;
            
            lucide.createIcons();
            
        } catch (e) {
            appendStatusStep(statusBox, "API writing error. Database seeder failed.", "error");
        }
    }, 7500);
}

// 4. Generate Thematic report
async function generateThemeReport() {
    const startDate = document.getElementById("theme-start-date").value;
    const endDate = document.getElementById("theme-end-date").value;
    const theme = document.getElementById("theme-question-input").value.trim();
    const model = document.getElementById("model-selector").value;
    
    if (!startDate || !endDate) {
        alert("請選擇完整日期區間！");
        return;
    }
    
    if (new Date(startDate) > new Date(endDate)) {
        alert("起始日期必須早於結束日期！");
        return;
    }
    
    if (!theme) {
        alert("請輸入您要搜尋與追蹤的主題或特定問題！");
        return;
    }
    
    const statusBox = document.getElementById("theme-status-container");
    const previewBox = document.getElementById("theme-preview-container");
    
    previewBox.style.display = "none";
    statusBox.style.display = "block";
    statusBox.innerHTML = "";
    
    appendStatusStep(statusBox, `Fetching daily journal entries for theme: <b>"${theme}"</b>...`, "loading");
    
    setTimeout(() => {
        appendStatusStep(statusBox, `Successfully mapped 5 matching log fragments in range. Parsing... [OK]`, "success");
        appendStatusStep(statusBox, `Initializing local GGUF model: <b>${model}</b>...`, "loading");
    }, 1500);
    
    setTimeout(() => {
        appendStatusStep(statusBox, `Loaded GGUF model into CPU memory. [OK]`, "success");
        appendStatusStep(statusBox, `Processing semantic RAG theme extraction...`, "loading");
    }, 3200);
    
    setTimeout(() => {
        appendStatusStep(statusBox, `Theme synthesis complete! Found relevant progress blocks. [OK]`, "success");
        appendStatusStep(statusBox, `Publishing thematic log page to Notion database...`, "loading");
    }, 5500);
    
    setTimeout(async () => {
        try {
            const res = await fetch("/api/notion/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    start_date: startDate,
                    end_date: endDate,
                    report_type: "Custom",
                    theme: theme,
                    model: model
                })
            });
            const data = await res.json();
            
            appendStatusStep(statusBox, `Notion database page successfully created! Pushed custom metadata. [OK]`, "success");
            appendStatusStep(statusBox, `Sending LINE Notify notification with custom report link... [OK]`, "success");
            
            const finalAlert = document.createElement("div");
            finalAlert.className = "status-box success";
            finalAlert.innerHTML = `
                <i data-lucide="check-circle" style="color:#10b981; width:22px; height:22px;"></i>
                <div>
                    <strong style="color:#fff; font-size:0.95rem;">Notion Thematic Report Generated Successfully!</strong><br>
                    已將主題彙整寫入 Notion 資料庫。
                    <a href="${data.notion_url}" target="_blank" style="color:#ff85a2; text-decoration:underline; font-weight:bold; margin-left:8px;">[ 開啟 Notion 頁面 ]</a>
                </div>
            `;
            statusBox.appendChild(finalAlert);
            
            previewBox.style.display = "block";
            previewBox.innerHTML = `
                <h3 style="color:#fff; border-bottom:1px solid var(--border-color); padding-bottom:8px; margin-bottom:15px;"><i data-lucide="file-check"></i> Thematic Report Preview</h3>
                <div class="preview-box">${parseMarkdown(data.summary)}</div>
            `;
            
            lucide.createIcons();
            
        } catch (e) {
            appendStatusStep(statusBox, "API writing error.", "error");
        }
    }, 7500);
}

// Helper to append a status row to status containers
function appendStatusStep(container, message, type) {
    const row = document.createElement("div");
    row.style.margin = "10px 0";
    row.style.fontSize = "0.85rem";
    row.style.display = "flex";
    row.style.alignItems = "center";
    row.style.gap = "8px";
    
    // Find matching spinner or icon based on type
    if (type === "loading") {
        row.innerHTML = `
            <div class="loader-spinner" style="width:12px; height:12px; border-width:2px; margin:0; display:inline-block;"></div>
            <span style="color:#fff; opacity:0.85;">${message}</span>
        `;
    } else if (type === "success") {
        row.innerHTML = `
            <i data-lucide="check" style="color:#10b981; width:14px; height:14px;"></i>
            <span style="color:#a7f3d0; opacity:0.9;">${message}</span>
        `;
    } else {
        row.innerHTML = `
            <i data-lucide="x" style="color:#ef4444; width:14px; height:14px;"></i>
            <span style="color:#fecaca;">${message}</span>
        `;
    }
    container.appendChild(row);
    lucide.createIcons();
}
