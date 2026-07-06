import os
import json

base_path = os.path.abspath(os.path.dirname(__file__))
# 原始MD归档目录（预留扩展）
MD_FOLDER = os.path.join(base_path, "../raw_md_archive")
# 输出双语数据集路径
OUT_JSON = os.path.join(base_path, "../poc_sample_datasets/poc_sample_law_dataset.json")

# 创建目录，兼容低版本Python无exist_ok
if not os.path.exists(MD_FOLDER):
    os.makedirs(MD_FOLDER)
out_dir = os.path.dirname(OUT_JSON)
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# 维度中英说明映射（仅展示用）
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

# 全量双语法条池：覆盖8大维度+CN_PIPL / JP_APPI / KR_PIPA，总计32条
RAW_CLAUSE_POOL = [
    # ===================== BasicDefinition 基础定义 =====================
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 4",
        "dimension": "BasicDefinition",
        "content_original": "个人信息是以电子或者其他方式记录的与已识别或者可识别的自然人有关的各种信息，不局限于姓名、出生日期、身份证件号码、生物识别信息、住址、电话号码、电子邮箱、健康信息、行踪信息等。",
        "content_en": "Personal information refers to all kinds of information recorded electronically or by other means related to identified or identifiable natural persons, including but not limited to names, dates of birth, identity document numbers, biometric information, residential addresses, phone numbers, email addresses, health information and location tracking information."
    },
    {
        "law_code": "JP_APPI",
        "clause_no": "Article 2",
        "dimension": "BasicDefinition",
        "content_original": "個人情報とは、生存する個人に関する情報であって、当該情報に含まれる氏名、生年月日その他の記述等により特定の個人を識別することができるものをいう。",
        "content_en": "Personal data means information relating to a living individual that can identify a specific person through names, dates of birth and other descriptions contained in such information."
    },
    {
        "law_code": "KR_PIPA",
        "clause_no": "Article 2",
        "dimension": "BasicDefinition",
        "content_original": "개인정보란 살아있는 자연인에 관한 정보로 이름, 주민등록번호 등을 통해 특정 개인을 식별할 수 있는 모든 정보를 말한다.",
        "content_en": "Personal information means all information about living natural persons that can identify a specific individual through names, resident registration numbers and other identifiers."
    },

    # ===================== DataSubjectRight 数据主体权利 =====================
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 44",
        "dimension": "DataSubjectRight",
        "content_original": "个人对其个人信息的处理享有知情权、决定权，有权限制或者拒绝他人对其个人信息进行处理；法律、行政法规另有规定的除外。",
        "content_en": "Natural persons have the right to know and decide on the processing of their personal information, and have the right to restrict or refuse others to process their personal information, unless otherwise provided by laws and administrative regulations."
    },
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 47",
        "dimension": "DataSubjectRight",
        "content_original": "有下列情形之一的，个人信息处理者应当主动删除个人信息；个人信息处理者未删除的，自然人有权请求删除：（一）处理目的已实现、无法实现或者为实现处理目的不再必要；（二）个人信息处理者停止提供产品或者服务，或者保存期限已届满；（三）个人撤回同意；（四）个人信息处理者违反法律、行政法规或者违反约定处理个人信息；（五）法律、行政法规规定的其他情形。",
        "content_en": "A personal information handler shall actively erase personal information under any of the following circumstances; if the handler fails to erase such information, the natural person has the right to request erasure: (1) the processing purpose has been fulfilled, cannot be fulfilled or is no longer necessary for fulfilling the purpose; (2) the handler ceases to provide products or services, or the retention period expires; (3) the data subject withdraws consent; (4) the handler processes personal information in violation of laws, administrative regulations or agreements; (5) other circumstances prescribed by laws and administrative regulations."
    },
    {
        "law_code": "JP_APPI",
        "clause_no": "Article 18",
        "dimension": "DataSubjectRight",
        "content_original": "本人は、事業者に対し、保有個人データの開示、訂正、追加、削除、利用停止、消去または第三者への提供停止を請求することができる。",
        "content_en": "Data subjects may request business operators to disclose, correct, supplement, delete, suspend use, erase or stop third-party provision of retained personal data."
    },
    {
        "law_code": "KR_PIPA",
        "clause_no": "Article 35",
        "dimension": "DataSubjectRight",
        "content_original": "정보주체는 개인정보처리자에게 본인의 개인정보 열람, 정정, 삭제, 처리정지를 요청할 수 있다.",
        "content_en": "Data subjects may request personal information processors to access, correct, delete or suspend processing of their personal data."
    },

    # ===================== DataControllerObligation 处理者义务 =====================
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 51",
        "dimension": "DataControllerObligation",
        "content_original": "个人信息处理者应当根据个人信息的处理目的、处理方式、个人信息的种类以及对个人权益的影响、可能存在的安全风险等，采取下列措施确保个人信息处理活动符合法律、行政法规的规定，防止未经授权的访问以及个人信息泄露、篡改、丢失：（一）制定内部管理制度和操作规程；（二）对个人信息实行分类管理和采取相应的加密、去标识化等安全技术措施；（三）合理确定个人信息处理的操作权限，并定期对从业人员进行安全教育和培训；（四）制定并组织实施个人信息安全事件应急预案；（五）法律、行政法规规定的其他措施。",
        "content_en": "Personal information handlers shall adopt the following measures to ensure compliance with laws and administrative regulations and prevent unauthorized access, leakage, tampering and loss of personal information, based on processing purposes, methods, types of personal information, impacts on individual rights and interests, and potential security risks: (1) formulate internal management systems and operating procedures; (2) implement classified management of personal information and adopt corresponding security technical measures such as encryption and de-identification; (3) reasonably define operation authorities for personal information processing and conduct regular security education and training for employees; (4) formulate and implement emergency response plans for personal information security incidents; (5) other measures prescribed by laws and administrative regulations."
    },
    {
        "law_code": "JP_APPI",
        "clause_no": "Article 20",
        "dimension": "DataControllerObligation",
        "content_original": "事業者は、保有個人データの漏えい、滅失または毀損の防止その他の個人データの安全管理のために必要かつ適切な措置を講じなければならない。",
        "content_en": "Business operators shall take necessary and appropriate measures to prevent leakage, loss or damage of retained personal data and ensure the security management of personal data."
    },
    {
        "law_code": "KR_PIPA",
        "clause_no": "Article 29",
        "dimension": "DataControllerObligation",
        "content_original": "개인정보처리자는 개인정보의 유출, 분실, 변조를 방지하기 위한 기술적·관리적 보호조치를 의무적으로 시행해야 한다.",
        "content_en": "Personal information processors shall mandatorily implement technical and administrative protection measures to prevent leakage, loss and tampering of personal information."
    },

    # ===================== AutomatedDecision 自动化决策 =====================
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 24",
        "dimension": "AutomatedDecision",
        "content_original": "个人信息处理者利用个人信息进行自动化决策，应当保证决策的透明度和结果公平、公正，不得对个人在交易价格等交易条件上实行不合理的差别待遇。",
        "content_en": "Where a personal information handler uses personal information for automated decision-making, it shall guarantee the transparency, fairness and impartiality of decisions, and shall not impose unreasonable differential treatment on individuals in transaction prices and other transaction terms."
    },
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 24 Paragraph 2",
        "dimension": "AutomatedDecision",
        "content_original": "通过自动化决策方式向个人进行信息推送、商业营销，应当同时提供不针对其个人特征的选项，或者向个人提供便捷的拒绝方式。",
        "content_en": "When pushing information or conducting commercial marketing to individuals via automated decision-making, handlers shall provide options that do not target personal characteristics or convenient refusal channels for individuals."
    },
    {
        "law_code": "JP_APPI",
        "clause_no": "Article 21",
        "dimension": "AutomatedDecision",
        "content_original": "自動的な判断に基づいて個人に不当な差別的取扱いをしてはならない。本人から請求があった場合、判断根拠を開示しなければならない。",
        "content_en": "Unfair differential treatment shall not be imposed on individuals based on automated judgments. Where requested by data subjects, the basis for judgment must be disclosed."
    },
    {
        "law_code": "KR_PIPA",
        "clause_no": "Article 37",
        "dimension": "AutomatedDecision",
        "content_original": "자동화된 의사결정 시스템으로 개인에게 불합리한 차별을 가해서는 안 되며, 정보주체가 의사결정 근거 열람을 요청할 수 있다.",
        "content_en": "Unreasonable discrimination against individuals via automated decision systems is prohibited; data subjects may request access to the basis of such decisions."
    },

    # ===================== MinorProtection 未成年人保护 =====================
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 31",
        "dimension": "MinorProtection",
        "content_original": "处理不满十四周岁未成年人个人信息的，应当征得未成年人的监护人同意。",
        "content_en": "Consent from legal guardians shall be obtained when processing personal information of minors under the age of fourteen."
    },
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 31 Paragraph 2",
        "dimension": "MinorProtection",
        "content_original": "未成年人、父母或者其他监护人要求信息处理者更正、删除未成年人个人信息的，信息处理者应当及时采取措施予以更正、删除。",
        "content_en": "Where minors, their parents or other guardians request handlers to correct or erase minors’ personal information, handlers shall take timely correction or erasure measures."
    },
    {
        "law_code": "JP_APPI",
        "clause_no": "Article 15",
        "dimension": "MinorProtection",
        "content_original": "15歳未満の未成年者の個人データを取り扱う際は、法定代理人の明示的な同意を取得しなければならない。",
        "content_en": "Explicit consent from legal representatives must be obtained when handling personal data of minors under 15 years old."
    },
    {
        "law_code": "KR_PIPA",
        "clause_no": "Article 22",
        "dimension": "MinorProtection",
        "content_original": "14세 미만 아동의 개인정보를 수집·처리하려면 법적 보호자의 동의를 필수로 취득해야 한다.",
        "content_en": "It is mandatory to obtain consent from legal guardians to collect and process personal information of children under 14 years old."
    },

    # ===================== CrossBorderTransfer 跨境传输 =====================
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 38",
        "dimension": "CrossBorderTransfer",
        "content_original": "个人信息处理者向境外提供个人信息的，应当取得个人单独同意，并按照国家网信部门规定完成安全评估。",
        "content_en": "Where a personal information handler provides personal information to overseas parties, it shall obtain separate individual consent from data subjects and complete security assessment in accordance with rules issued by national cyberspace authority."
    },
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 40",
        "dimension": "CrossBorderTransfer",
        "content_original": "关键信息基础设施运营者在中华人民共和国境内收集和产生的个人信息，应当在境内存储。因业务需要确需向境外提供的，应当通过国家网信部门组织的安全评估。",
        "content_en": "Personal information collected and generated within the territory of China by operators of critical information infrastructure shall be stored domestically. Where overseas provision is truly necessary for business needs, a security assessment organized by the national cyberspace authority shall be passed."
    },
    {
        "law_code": "JP_APPI",
        "clause_no": "Article 24",
        "dimension": "CrossBorderTransfer",
        "content_original": "事業者が外国に個人データを提供する場合、本人の明示的な同意を取得し、移転先国の保護水準を確認しなければならない。",
        "content_en": "When a business operator transfers personal data to foreign jurisdictions, it must obtain explicit consent from the data subject and verify the personal data protection standard of the receiving country."
    },
    {
        "law_code": "KR_PIPA",
        "clause_no": "Article 42",
        "dimension": "CrossBorderTransfer",
        "content_original": "개인정보처리자는 해외로 개인정보를 이전하려면 정보주체의 별도 동의를 받고 이전 국가의 데이터 보호 수준을 검증해야 한다.",
        "content_en": "Personal information processors shall obtain separate consent from data subjects before transferring personal data overseas and verify the data protection level of the destination country."
    },

    # ===================== Penalty 法律责任与处罚 =====================
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 66",
        "dimension": "Penalty",
        "content_original": "违反本法规定处理个人信息，或者处理个人信息未履行本法规定的个人信息保护义务的，由履行个人信息保护职责的部门责令改正，给予警告，没收违法所得，对违法处理个人信息的应用程序，责令暂停或者终止提供服务；拒不改正的，并处一百万元以下罚款；对直接负责的主管人员和其他直接责任人员处一万元以上十万元以下罚款。",
        "content_en": "Anyone who processes personal information in violation of this Law or fails to perform personal information protection obligations prescribed herein shall be ordered to make corrections, given a warning and confiscated illegal gains by authorities with personal information protection duties; relevant apps illegally processing personal information shall be ordered to suspend or terminate services. Those refusing correction shall be fined not more than one million RMB; directly responsible managers and personnel shall be fined from 10,000 to 100,000 RMB."
    },
    {
        "law_code": "JP_APPI",
        "clause_no": "Article 56",
        "dimension": "Penalty",
        "content_original": "個人情報保護法に違反した事業者に対し、是正命令、業務停止命令または罰金が科される。重大違反の場合、最大1億円の罰金が課せられる。",
        "content_en": "Business operators violating the Personal Information Protection Act shall be subject to correction orders, business suspension orders or fines. Serious violations may incur fines up to 100 million Japanese Yen."
    },
    {
        "law_code": "KR_PIPA",
        "clause_no": "Article 72",
        "dimension": "Penalty",
        "content_original": "개인정보보호법을 위반한 자는 최대 5억 원의 과징금을 부과받을 수 있으며, 형사 처분도 병행될 수 있다.",
        "content_en": "Persons violating the Personal Information Protection Act may be subject to administrative fines up to 500 million KRW, and criminal penalties may apply concurrently."
    },

    # ===================== ComplianceAssessment 合规安全评估 =====================
    {
        "law_code": "CN_PIPL",
        "clause_no": "Article 55",
        "dimension": "ComplianceAssessment",
        "content_original": "有下列情形之一的，个人信息处理者应当事前进行个人信息保护影响评估，并对处理情况进行记录：（一）处理敏感个人信息；（二）利用个人信息进行自动化决策；（三）委托处理个人信息、向境外提供个人信息、共享个人信息；（四）其他对个人权益有重大影响的处理活动。",
        "content_en": "Personal information handlers shall conduct prior personal information protection impact assessments and record processing activities under any of the following circumstances: (1) processing sensitive personal information; (2) using personal information for automated decision-making; (3) entrusting third parties to process, providing overseas or sharing personal information; (4) other processing activities with significant impacts on individual rights and interests."
    },
    {
        "law_code": "JP_APPI",
        "clause_no": "Article 22",
        "dimension": "ComplianceAssessment",
        "content_original": "大量または機微な個人データを取り扱う事業者は、事前にプライバシー影響評価（PIA）を実施し、記録を保管しなければならない。",
        "content_en": "Business operators handling large-scale or sensitive personal data must conduct prior Privacy Impact Assessments (PIA) and retain relevant records."
    },
    {
        "law_code": "KR_PIPA",
        "clause_no": "Article 30",
        "dimension": "ComplianceAssessment",
        "content_original": "민감정보 또는 대량의 개인정보를 처리하는 사업자는 사전 개인정보 영향평가를 실시하고 결과를 보관해야 한다.",
        "content_en": "Business operators processing sensitive or large-volume personal information shall conduct prior personal information impact assessments and retain assessment results."
    }
]

def save_clause_json():
    # 写入格式化双语JSON
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(RAW_CLAUSE_POOL, f, ensure_ascii=False, indent=2)
    total = len(RAW_CLAUSE_POOL)
    print("=" * 60)
    print(f"✅ 双语法条数据集生成完成！总条数：{total}")
    print(f"输出文件路径：{OUT_JSON}")
    print("每条标准字段：law_code / clause_no / dimension / content_original(原文) / content_en(英文释义)")
    print("=" * 60)
    # 打印清单用于核对
    print("\n法条清单预览：")
    for idx, item in enumerate(RAW_CLAUSE_POOL):
        print(f"{idx+1:02d}. {item['law_code']} | {item['clause_no']} | {item['dimension']}")

if __name__ == "__main__":
    save_clause_json()