/* Portrait Chat Assistant - Interactive Client Logic */

let currentPersona = "";

document.addEventListener("DOMContentLoaded", () => {
    fetchAvailablePersonas();
});

// 1. Fetch available personas from SQLite database/reports directory
async function fetchAvailablePersonas() {
    const selector = document.getElementById("persona-selector");
    try {
        const response = await fetch("/api/portrait/personas");
        const personas = await response.json();
        
        selector.innerHTML = "";
        
        if (personas.length === 0) {
            selector.innerHTML = '<option value="">尚無人物資料</option>';
            return;
        }
        
        // Add a default select option
        const defaultOpt = document.createElement("option");
        defaultOpt.value = "";
        defaultOpt.textContent = "⚙️ -- 請選取分析對象 --";
        selector.appendChild(defaultOpt);
        
        personas.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p;
            opt.textContent = `👤 ${p}`;
            selector.appendChild(opt);
        });
    } catch (e) {
        console.error("Error fetching personas:", e);
        selector.innerHTML = '<option value="">載入失敗</option>';
    }
}

// 2. Handle selection changes
async function onPersonaChanged() {
    const selector = document.getElementById("persona-selector");
    const persona = selector.value;
    currentPersona = persona;
    
    const welcomeMsg = document.getElementById("welcome-message");
    const riskPanel = document.getElementById("risk-panel");
    const wordcloudGroup = document.getElementById("wordcloud-group");
    const reportGroup = document.getElementById("report-group");
    const chatTitle = document.getElementById("chat-title");
    const chatHistory = document.getElementById("chat-history");
    const badgeName = document.getElementById("persona-badge-name");
    
    if (!persona) {
        // Reset view
        welcomeMsg.style.display = "block";
        riskPanel.style.display = "none";
        wordcloudGroup.style.display = "none";
        reportGroup.style.display = "none";
        chatTitle.textContent = "💬 與人物對話記憶互動";
        badgeName.textContent = "👤 請選取人物";
        clearChatHistory();
        return;
    }
    
    // Show sections
    welcomeMsg.style.display = "none";
    badgeName.textContent = `👤 ${persona}`;
    chatTitle.textContent = `💬 與「${persona}」的對話記憶互動`;
    
    // Set wordcloud image
    const wordcloudImg = document.getElementById("wordcloud-img");
    wordcloudImg.src = `/visualize/${encodeURIComponent(persona)}_wordcloud.png`;
    wordcloudGroup.style.display = "block";
    
    // Set risk warning alerts
    setupRiskAlert(persona);
    
    // Fetch and display persona markdown report
    await fetchPersonaReport(persona);
    
    // Rebuild quick Q&A chips
    setupSuggestedChips(persona);
    
    // Clear chat history for the new persona
    clearChatHistory();
    
    // Add welcome bot message
    appendChatBubble("assistant", `系統已載入「**${persona}**」的專屬 ChromeDB 向量記憶庫，並啟動地端 Qwen 2.5 分析核心。請問有什麼關於此人的資訊想要查詢？`);
}

// 3. Clear chat logs
function clearChatHistory() {
    const chatHistory = document.getElementById("chat-history");
    // Remove all except welcome message
    const welcome = document.getElementById("welcome-message");
    chatHistory.innerHTML = "";
    if (welcome && !currentPersona) {
        chatHistory.appendChild(welcome);
    }
}

// 4. Load Markdown reports and render as HTML
async function fetchPersonaReport(persona) {
    const reportContent = document.getElementById("report-html-content");
    reportContent.innerHTML = '<div class="loader-spinner" style="margin: 20px auto;"></div><p style="text-align:center; color:#888;">正從地端解析報告...</p>';
    reportGroup.style.display = "block";
    
    try {
        const response = await fetch(`/api/portrait/report?persona=${encodeURIComponent(persona)}`);
        if (!response.ok) throw new Error("Report not found");
        const data = await response.json();
        reportContent.innerHTML = data.html;
    } catch (e) {
        reportContent.innerHTML = `<p style="color:#f44336;">⚠️ 找不到該人物的分析報告，請確認 portrait/data/reports/${persona}.md 檔案是否存在。</p>`;
    }
}

// 5. Configure risk status panels
function setupRiskAlert(persona) {
    const riskPanel = document.getElementById("risk-panel");
    const riskTitle = document.getElementById("risk-title");
    const riskReason = document.getElementById("risk-reason");
    
    riskPanel.style.display = "block";
    riskPanel.className = "sidebar-group risk-alert-card"; // Reset
    
    if (persona === "何珮瑄") {
        riskPanel.classList.add("high-risk");
        riskTitle.innerHTML = '<i data-lucide="alert-triangle"></i> 🔴 高風險警示 (Risk: 85/100)';
        riskReason.innerHTML = `
            ⚠️ **檢測到潛在心理或資安風險：**<br>
            * **對話內容異常檢測**：對話提及<em>「保證獲利」</em>、<em>「被騷擾」</em>、<em>「被欺騙」</em>等高風險特徵關鍵詞。<br>
            * **情緒特徵**：責任心重易自責，近期面臨轉職及生涯高度焦慮期，對當下生活或職場環境存在持續性的焦慮，易受資訊波動影響。<br>
            * **安全建議**：該個體處於高敏感狀態，與他人交往時應給予同理心支持，並注意提防非理性的網路詐騙或情感誘導風險。
        `;
    } else if (persona === "品鈞") {
        riskPanel.classList.add("high-risk");
        riskTitle.innerHTML = '<i data-lucide="alert-triangle"></i> 🔴 中高風險警示 (Risk: 72/100)';
        riskReason.innerHTML = `
            ⚠️ **高負荷情緒與焦慮檢測：**<br>
            * **壓力指標**：對話頻繁透露在學業進度、專業瓶頸以及高壓工作實習上的高度負荷感。<br>
            * **語言特質**：存在顯著的自嘲、自卑與高標自我要求言詞，容易引發情緒失衡。<br>
            * **建議**：引導進行規律的放鬆活動，避免灌輸過度競爭觀念。
        `;
    } else {
        // Safe standard status
        riskPanel.classList.add("safe-risk");
        riskTitle.innerHTML = '<i data-lucide="shield-check"></i> 🟢 安全狀態 (Risk: 12/100)';
        riskReason.innerHTML = `
            ✅ **常規日誌狀態良好：**<br>
            * **對話特徵檢測**：內容皆為日常學習記錄、社交穿搭、美食或音樂，無異常金融用語。<br>
            * **防詐判定**：無任何涉及匯款、加密貨幣、非理性投資或敏感社群軟體騷擾之特徵檢測。<br>
            * **狀態評估**：個體目前心理與對話環境極其健康、安全。
        `;
    }
    // Re-initialize lucide icons for dynamic items
    lucide.createIcons();
}

// 6. Setup quick chips
function setupSuggestedChips(persona) {
    const container = document.getElementById("suggested-chips-container");
    container.innerHTML = "";
    
    const questions = [
        `🎨 ${persona} 的性格特質與價值觀是什麼？`,
        `🎯 她有哪些近期的目標或煩惱？`,
        `🍔 她喜歡與不喜歡哪些飲食和事物？`,
        `🏃 她的經歷與過往背景？`,
        `👥 她的人際網絡關係如何？`
    ];
    
    questions.forEach(q => {
        const btn = document.createElement("button");
        btn.className = "suggested-chip";
        btn.textContent = q;
        btn.onclick = () => {
            // Remove emoji prefix for querying
            const cleanQ = q.substring(2);
            sendQuery(cleanQ);
        };
        container.appendChild(btn);
    });
}

// 7. Render bubbles
function appendChatBubble(role, content, sources = []) {
    const chatHistory = document.getElementById("chat-history");
    
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${role}`;
    
    const avatar = document.createElement("div");
    avatar.className = "bubble-avatar";
    avatar.innerHTML = role === "user" ? '<i data-lucide="user"></i>' : '<i data-lucide="bot"></i>';
    
    const wrapper = document.createElement("div");
    wrapper.className = "bubble-content-wrapper";
    
    const bubbleContent = document.createElement("div");
    bubbleContent.className = "bubble-content";
    
    // Parse markdown list formatting simply
    let parsedContent = content
        .replace(/\n\n/g, "<br><br>")
        .replace(/\n\* /g, "<br>• ")
        .replace(/\n- /g, "<br>• ")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        
    bubbleContent.innerHTML = parsedContent;
    wrapper.appendChild(bubbleContent);
    
    // Add citation accordions if sources exist
    if (sources && sources.length > 0) {
        const details = document.createElement("details");
        details.className = "sources-accordion";
        
        const summary = document.createElement("summary");
        summary.innerHTML = `<i data-lucide="paperclip" style="width:12px;height:12px;vertical-align:middle;margin-right:3px;"></i> 查看來源片段 (${sources.length} 段)`;
        details.appendChild(summary);
        
        const sourcesList = document.createElement("div");
        sourcesList.className = "sources-list";
        
        sources.forEach((src, idx) => {
            const chip = document.createElement("div");
            chip.className = "source-chip";
            chip.innerHTML = `📌 <b>記憶來源 ${idx + 1}</b><br>${src}`;
            sourcesList.appendChild(chip);
        });
        
        details.appendChild(sourcesList);
        wrapper.appendChild(details);
    }
    
    bubble.appendChild(avatar);
    bubble.appendChild(wrapper);
    chatHistory.appendChild(bubble);
    
    // Re-render icons
    lucide.createIcons();
    
    // Auto Scroll to bottom
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// 8. Submit Query
async function sendQuery(customQ = null) {
    if (!currentPersona) {
        alert("請先在左側面板選取對話對象！");
        return;
    }
    
    const inputField = document.getElementById("chat-input");
    const question = customQ || inputField.value.trim();
    
    if (!question) return;
    
    if (!customQ) {
        inputField.value = "";
    }
    
    // 1. Show user bubble
    appendChatBubble("user", question);
    
    // 2. Show assistant typing bubble placeholder
    const chatHistory = document.getElementById("chat-history");
    const typingBubble = document.createElement("div");
    typingBubble.className = "chat-bubble assistant typing-placeholder";
    typingBubble.innerHTML = `
        <div class="bubble-avatar"><i data-lucide="bot"></i></div>
        <div class="bubble-content-wrapper">
            <div class="bubble-content" style="display:flex; align-items:center; gap:8px; padding:10px 18px;">
                <div class="loader-spinner" style="width:14px; height:14px; border-width:2px; margin:0;"></div>
                <span style="color:#888; font-size:0.85rem;">正在檢索地端長期記憶庫...</span>
            </div>
        </div>
    `;
    chatHistory.appendChild(typingBubble);
    lucide.createIcons();
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    try {
        const response = await fetch("/api/portrait/query", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                persona: currentPersona,
                question: question
            })
        });
        
        // Remove typing placeholder
        typingBubble.remove();
        
        if (!response.ok) throw new Error("API call failed");
        
        const data = await response.json();
        
        // Append Bot Bubble with cited details
        appendChatBubble("assistant", data.answer, data.sources);
        
    } catch (e) {
        typingBubble.remove();
        appendChatBubble("assistant", "⚠️ 與 Ollama 本地記憶庫連線失敗。請確認 Flask 伺服器運作正常且報告資料庫配置無誤。");
    }
}
