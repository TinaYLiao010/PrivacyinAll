import os
import json

base_path = os.path.abspath(os.path.dirname(__file__))
MD_FOLDER = os.path.join(base_path, "../raw_md_archive")
OUT_JSON = os.path.join(base_path, "../poc_sample_datasets/poc_sample_law_dataset.json")

# 创建文件夹
if not os.path.exists(MD_FOLDER):
    os.makedirs(MD_FOLDER)
if not os.path.exists(os.path.dirname(OUT_JSON)):
    os.makedirs(os.path.dirname(OUT_JSON))

# 维度映射 + 配套标准英文翻译（可自行批量替换）
DIM_MAP = {
    "BasicDefinition": "Basic Definition & Terminology",
    "DataSubjectRight": "Data Subject Rights",
    "DataControllerObligation": "Data Controller Obligations",
    "AutomatedDecision": "Automated Decision-Making Processing",
    "MinorProtection": "Minors Personal Information Protection",
    "CrossBorderTransfer": "Cross-Border Data Transfer",
    "Penalty": "Administrative Penalties & Liability",
    "ComplianceAssessment": "Compliance & Security Assessment"
}
# 三大法域原始文本+预制专业英文释义（演示用，可批量导入真实官方译文）
RAW_CLAUSE_POOL = [
    # CN-PIPL 跨境传输示例
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 38",
        "dimension": "CrossBorderTransfer",
        "content_original": "个人信息处理者向境外提供个人信息的，应当取得个人单独同意，并按照国家网信部门规定完成安全评估。",
        "content_en": "Where a personal information handler provides personal information to overseas parties, it shall obtain separate individual consent from data subjects and complete security assessment in accordance with rules issued by national cyberspace authority."
    },
    {
        "law_code": "JP_APPI",
        "clause_no": "Article 24",
        "dimension": "CrossBorderTransfer",
        "content_original": "事業者が外国に個人データを提供する場合、本人の明示的な同意を取得し、移転先の国の保護水準を確認しなければならない。",
        "content_en": "When a business operator transfers personal data to foreign jurisdictions, it must obtain explicit consent from the data subject and verify the personal data protection standard of the receiving country."
    },
    {
        "law_code": "KR_PIPA",
        "clause_no": "Article 42",
        "dimension": "CrossBorderTransfer",
        "content_original": "개인정보처리자는 해외로 개인정보를 이전하려면 정보주체의 별도 동의를 받고 이전 국가의 보호수준을 검증해야 한다.",
        "content_en": "Personal information processors shall obtain separate consent from data subjects before transferring personal data overseas and verify the data protection level of the destination country."
    },
    # 未成年人保护
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 31",
        "dimension": "MinorProtection",
        "content_original": "处理不满十四周岁未成年人个人信息，应当征得监护人同意。",
        "content_en": "Processing personal information of minors under the age of 14 shall obtain consent from their legal guardians."
    },
    {
        "law_code": "JP_APPI",
        "clause_no": "Article 18",
        "dimension": "MinorProtection",
        "content_original": "15歳未満の未成年者の個人データを取り扱う際は保護者の同意を要する。",
        "content_en": "Consent from guardians is required when handling personal data of minors under 15 years old."
    },
    {
        "law_code": "KR_PIPA",
        "clause_no": "Article 22",
        "dimension": "MinorProtection",
        "content_original": "14세 미만 아동의 개인정보 처리 시 법적 보호자의 동의를 필수로 취득해야 한다.",
        "content_en": "It is mandatory to obtain consent from legal guardians when processing personal information of children under 14."
    },
    # 删除权
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 47",
        "dimension": "DataSubjectRight",
        "content_original": "个人有权要求处理者删除、清除其个人信息。",
        "content_en": "Data subjects have the right to request handlers to delete and erase their personal information."
    },
    # 处罚条款
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 66",
        "dimension": "Penalty",
        "content_original": "违法处理个人信息的，可处五千万元以下罚款；情节严重吊销相关业务许可。",
        "content_en": "Violations of personal information processing rules may incur fines up to 50 million RMB; severe violations will result in revocation of relevant business permits."
    }
]

def save_clause_json():
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(RAW_CLAUSE_POOL, f, ensure_ascii=False, indent=2)
    print(f"✅ 双语法条JSON生成完成，总条数：{len(RAW_CLAUSE_POOL)}")
    print(f"输出路径：{OUT_JSON}")
    print("每条结构：law_code / clause_no / dimension / content_original(原文) / content_en(英文释义)")

if __name__ == "__main__":
    save_clause_json()