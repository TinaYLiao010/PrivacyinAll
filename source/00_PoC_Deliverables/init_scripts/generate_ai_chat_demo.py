import os
import json

base_path = os.path.abspath(os.path.dirname(__file__))
DATA_JSON = os.path.join(base_path, "../poc_sample_datasets/poc_sample_law_dataset.json")
HTML_OUT = os.path.join(base_path, "../poc_visual_demos")
QA_LOG_DIR = os.path.join(HTML_OUT, "qa_history_storage")

# 兼容低版本Python，无exist_ok参数
if not os.path.exists(HTML_OUT):
    os.makedirs(HTML_OUT)
if not os.path.exists(QA_LOG_DIR):
    os.makedirs(QA_LOG_DIR)

# 8个标准维度
DIM_LIST = [
    "BasicDefinition",
    "DataSubjectRight",
    "DataControllerObligation",
    "AutomatedDecision",
    "MinorProtection",
    "CrossBorderTransfer",
    "Penalty",
    "ComplianceAssessment"
]
# 三大法域
JURIS_LIST = ["CN_PIPL", "JP_APPI", "KR_PIPA"]

# PoC预置合规问答
PRESET_QUESTIONS = [
    "What are the cross-border transfer requirements under CN-PIPL?",
    "How to protect minors' personal information in three jurisdictions?",
    "Explain data subject's right to deletion",
    "What penalties will be imposed for violating privacy laws?",
    "Rules for automated decision-making processing"
]

# 加载本地双语法条数据集
def load_law_dataset():
    if not os.path.exists(DATA_JSON):
        print(f"【错误】缺失数据集 {DATA_JSON}，请先执行PoC Step3 poc_struct_generator.py")
        exit(1)
    with open(DATA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✅ 成功读取双语法条总数：{len(data)}")
    return data

# 多层严格转义，彻底消除JS Invalid token 报错
def safe_encode_json(raw):
    s = json.dumps(raw, ensure_ascii=False, separators=(",", ":"))
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "\\'")
    s = s.replace('"', '\\"')
    s = s.replace("\n", "\\n")
    return s

if __name__ == "__main__":
    dataset = load_law_dataset()
    dataset_str = safe_encode_json(dataset)
    preset_q_str = safe_encode_json(PRESET_QUESTIONS)

    html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PoC AI Compliance Chat Demo | Claude Code Coding Plan | Bilingual Law</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:Arial, sans-serif;}
body{background:#f2f5fa;padding:20px;max-width:1200px;margin:0 auto;}
h1{text-align:center;color:#182a44;margin-bottom:10px;}
.desc{text-align:center;color:#555;margin-bottom:24px;font-size:14px;}
.control-bar{background:#fff;padding:18px;border-radius:8px;margin-bottom:20px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;}
#presetSelect{padding:8px;width:400px;border:1px solid #ccd6e0;border-radius:6px;}
#clearBtn{background:#e53e3e;color:#fff;border:none;padding:8px 14px;border-radius:6px;cursor:pointer;}
.chat-container{background:#fff;border-radius:10px;padding:20px;height:60vh;overflow-y:auto;margin-bottom:16px;border:1px solid #e2e8f0;}
.msg-user{background:#2563eb;color:#fff;padding:10px 14px;border-radius:12px 12px 2px 12px;max-width:70%;margin:10px 0 10px auto;word-wrap:break-word;white-space:pre-line;line-height:1.6;}
.msg-ai{background:#e8edf5;color:#111;padding:10px 14px;border-radius:12px 12px 12px 2px;max-width:70%;margin:10px auto 10px 0;word-wrap:break-word;white-space:pre-line;line-height:1.6;}
.input-area{display:flex;gap:10px;}
#userInput{flex:1;padding:10px;border:1px solid #ccd6e0;border-radius:6px;min-height:60px;resize:none;}
#sendBtn{background:#2563eb;color:#fff;border:none;padding:0 20px;border-radius:6px;cursor:pointer;}
.tip-small{font-size:12px;color:#777;margin-top:8px;}
/* 双语上下文样式区分 */
.ref-original{margin-top:6px;color:#111;}
.ref-en{margin-top:6px;color:#2563eb;border-top:1px dashed #ccc;padding-top:6px;}
</style>
</head>
<body>
<h1>PoC AI Privacy Compliance Q&A Demo</h1>
<div class="desc">Local Bilingual Law Context | Via Local Python Proxy Port 9000 | VolcEngine Claude Code Coding Plan</div>

<div class="control-bar">
    <label>Preset Compliance Questions:</label>
    <select id="presetSelect">
        <option value="">-- Select Demo Question --</option>
    </select>
    <button id="clearBtn">Clear Chat History</button>
</div>

<div class="chat-container" id="chatBox"></div>
<div class="input-area">
    <textarea id="userInput" placeholder="Input your privacy compliance question..."></textarea>
    <button id="sendBtn">Send</button>
</div>
<div class="tip-small">Note: Run ark_proxy.py on port 9000 first to avoid browser CORS restriction</div>

<script>
// 注入本地双语法条数据集
const fullLawData = JSON.parse('{{DATA_STR}}');
const presetQuestions = JSON.parse('{{PRESET_Q_STR}}');
const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const presetSelect = document.getElementById("presetSelect");
const clearBtn = document.getElementById("clearBtn");

// 填充预置问题下拉
presetQuestions.forEach(q=>{
    const opt = document.createElement("option");
    opt.value = q;
    opt.textContent = q;
    presetSelect.appendChild(opt);
})

presetSelect.addEventListener("change", function(){
    if(this.value) userInput.value = this.value;
})

// 清空对话
clearBtn.addEventListener("click", ()=>{
    chatBox.innerHTML = "";
})

// 渲染消息气泡
function addMessage(text, isUser){
    const div = document.createElement("div");
    div.className = isUser ? "msg-user" : "msg-ai";
    div.textContent = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 【更新：双语上下文拼接，同时输出原文+英文释义】
function getLawContext(question){
    let ctx = "=== Reference Multi-Jurisdiction Bilingual Privacy Clauses (CN-PIPL / JP-APPI / KR-PIPA) ===\\n\\n";
    const kwMap = {
        "cross-border":"CrossBorderTransfer",
        "minor":"MinorProtection",
        "deletion":"DataSubjectRight",
        "penalty":"Penalty",
        "automated":"AutomatedDecision"
    };
    let targetDim = null;
    const qLow = question.toLowerCase();
    for(let kw in kwMap){
        if(qLow.includes(kw)) targetDim = kwMap[kw];
    }
    const matchClauses = targetDim ? fullLawData.filter(item=>item.dimension === targetDim).slice(0,8) : fullLawData.slice(0,6);
    matchClauses.forEach(item=>{
        ctx += `[${item.law_code}] ${item.clause_no} | Dimension: ${item.dimension}\\n`;
        ctx += `Original Text: ${item.content_original}\\n`;
        ctx += `Official English Interpretation: ${item.content_en}\\n\\n`;
    })
    return ctx;
}

// 对接本地9000代理，前端不再携带Authorization鉴权头，适配火山Coding Plan
async function callArkCodingAPI(userQ){
    const ENDPOINT = "http://127.0.0.1:9000";
    const MODEL_ID = "ark-code-latest";
    const context = getLawContext(userQ);
    const sysPrompt = "You are a professional cross-jurisdiction privacy compliance consultant. Answer only based on the attached bilingual law context, compare CN-PIPL, JP-APPI and KR-PIPA, reply in clear English. If no matching clause exists, clearly state no relevant regulation found. Reference Context: " + context;
    
    const payload = {
        model: MODEL_ID,
        temperature: 0.3,
        max_tokens: 4096,
        messages: [
            {"role": "system", "content": sysPrompt},
            {"role": "user", "content": userQ}
        ]
    };

    try{
        const res = await fetch(ENDPOINT, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if(data.error){
            return "API Fail: " + data.error.message + "\\nCheck Coding Plan API Key inside ark_proxy.py";
        }
        return data.choices[0].message.content;
    }catch(err){
        return "Network Error: Please start ark_proxy.py local proxy on port 9000 first.";
    }
}

// 发送按钮点击事件
sendBtn.addEventListener("click", async()=>{
    console.log("Send button triggered");
    const q = userInput.value.trim();
    if(!q){
        alert("Please input compliance question first!");
        return;
    }
    addMessage(q, true);
    userInput.value = "";
    addMessage("Loading bilingual law context & requesting Claude Code via local proxy...", false);
    const ans = await callArkCodingAPI(q);
    chatBox.removeChild(chatBox.lastChild);
    addMessage(ans, false);
})

// 回车快捷发送
userInput.addEventListener("keydown", e=>{
    if(e.key === "Enter" && !e.shiftKey){
        e.preventDefault();
        sendBtn.click();
    }
})
</script>
</body>
</html>
'''
    final_html = html_template.replace("{{DATA_STR}}", dataset_str)
    final_html = final_html.replace("{{PRESET_Q_STR}}", preset_q_str)

    output_html = os.path.join(HTML_OUT, "PoC_AI_Chat_Demo.html")
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(final_html)

    print("======================================")
    print("✅ PoC_AI_Chat_Demo.html 生成完成")
    print(f"页面路径：{output_html}")
    print("【更新说明】")
    print("1. 自动读取poc_sample_datasets.json双语字段 content_original / content_en")
    print("2. 传给Claude的参考上下文同时展示法条原文+官方英文释义")
    print("3. 适配火山方舟Coding Plan，依赖本地9000端口ark_proxy.py中转消除CORS")
    print("4. 多层字符转义，无 Uncaught SyntaxError: Invalid or unexpected token")
    print("【运行流程】")
    print("① 修改ark_proxy.py填入Coding Plan专属API Key")
    print("② 终端1运行 python3 ark_proxy.py 启动本地代理")
    print("③ 终端进入poc_visual_demos执行 python3 -m http.server 8000")
    print("④ http://127.0.0.1:8000/PoC_AI_Chat_Demo.html 打开页面测试")
    print("======================================")