import json

def mock_translate(data, lang_prefix):
    if isinstance(data, dict):
        return {k: mock_translate(v, lang_prefix) for k, v in data.items()}
    elif isinstance(data, list):
        return [mock_translate(item, lang_prefix) for item in data]
    elif isinstance(data, str):
        # 영문, 숫자 등 짧은 문자열은 그대로 두고, 한글이 포함된 경우에만 번역 흉내를 냄
        if any(u'\u3130' <= c <= u'\u318F' or u'\uAC00' <= c <= u'\uD7A3' for c in data):
            # 줄바꿈이 있는 긴 문자열(mermaid 등) 처리
            lines = data.split('\n')
            res_lines = []
            for line in lines:
                if any(u'\u3130' <= c <= u'\u318F' or u'\uAC00' <= c <= u'\uD7A3' for c in line):
                    res_lines.append(f"[{lang_prefix}] {line}")
                else:
                    res_lines.append(line)
            return '\n'.join(res_lines)
        return data
    else:
        return data

# ui 번역은 실제 번역을 적용
ui_translations = {
    "en": {
        "title": "MSA Architecture Diagram",
        "subtitle": "K3s Cluster Microservices Architecture Status and Improvement Plan",
        "last_updated": "Last Updated: ",
        "tab_posselect": "posselect.com",
        "tab_leedohyun": "leedohyun.com",
        "tab_infra": "Common Infra",
        "tab_domainsplit": "Domain Split",
        "tab_improved": "Improvement Plan",
        "tab_roadmap": "Long-term Roadmap",
        "tab_resources": "Resource Status",
        "status_deployed": "Deployed",
        "status_planned": "Planned",
        "status_manual": "Manual",
        "status_review": "Under Review",
        "status_decided": "Principle Confirmed",
        "status_confirmed": "Confirmed",
        "issues_posselect": "Issues with posselect.com",
        "issues_leedohyun": "Issues with leedohyun.com",
        "issues_infra": "Common Infra Issues",
        "changes_title": "Changes after migration",
        "resources_title": "Current Cluster Resource Usage",
        "resource_cpu": "CPU Usage",
        "resource_memory": "Memory Usage",
        "resource_nodes": "Node Count",
        "resource_type": "Cluster Type",
        "no_image": "No Image"
    },
    "ja": {
        "title": "MSA アーキテクチャ図",
        "subtitle": "K3s クラスター マイクロサービス アーキテクチャの現状と改善計画",
        "last_updated": "最終更新: ",
        "tab_posselect": "posselect.com",
        "tab_leedohyun": "leedohyun.com",
        "tab_infra": "共通インフラ",
        "tab_domainsplit": "ドメイン構成",
        "tab_improved": "改善計画",
        "tab_roadmap": "長期ロードマップ",
        "tab_resources": "リソース状況",
        "status_deployed": "デプロイ済",
        "status_planned": "計画済",
        "status_manual": "手動",
        "status_review": "検討対象",
        "status_decided": "原則確定",
        "status_confirmed": "確定",
        "issues_posselect": "posselect.com 側の問題点",
        "issues_leedohyun": "leedohyun.com 側の問題点",
        "issues_infra": "共通インフラの問題点",
        "changes_title": "移行後の変更点",
        "resources_title": "現在のクラスター リソース使用状況",
        "resource_cpu": "CPU 使用率",
        "resource_memory": "メモリ 使用率",
        "resource_nodes": "ノード数",
        "resource_type": "クラスター タイプ",
        "no_image": "画像なし"
    },
    "zh": {
        "title": "MSA 架构图",
        "subtitle": "K3s 集群微服务架构现状及改进计划",
        "last_updated": "最后更新: ",
        "tab_posselect": "posselect.com",
        "tab_leedohyun": "leedohyun.com",
        "tab_infra": "公共基础设施",
        "tab_domainsplit": "域名结构",
        "tab_improved": "改进计划",
        "tab_roadmap": "长期路线图",
        "tab_resources": "资源状况",
        "status_deployed": "已部署",
        "status_planned": "已计划",
        "status_manual": "手动",
        "status_review": "审核中",
        "status_decided": "原则确定",
        "status_confirmed": "已确定",
        "issues_posselect": "posselect.com 方面的问题",
        "issues_leedohyun": "leedohyun.com 方面的问题",
        "issues_infra": "公共基础设施的问题",
        "changes_title": "迁移后的变更",
        "resources_title": "当前集群资源使用情况",
        "resource_cpu": "CPU 使用率",
        "resource_memory": "内存 使用率",
        "resource_nodes": "节点数量",
        "resource_type": "集群类型",
        "no_image": "无图片"
    }
}

with open("data/ko.json", "r", encoding="utf-8") as f:
    ko_data = json.load(f)

for lang in ["en", "ja", "zh"]:
    # 깊은 복사 후 모의 번역
    lang_data = mock_translate(ko_data, lang.upper())
    # UI 부분은 실제 번역으로 덮어쓰기
    lang_data["ui"] = ui_translations[lang]
    # mermaid 다이어그램은 임의로 번역 시 [EN] 등이 붙어 Syntax Error가 발생하므로 원본을 유지함
    lang_data["mermaid"] = ko_data["mermaid"]
    
    with open(f"data/{lang}.json", "w", encoding="utf-8") as f:
        json.dump(lang_data, f, ensure_ascii=False, indent=2)

print("Translations generated.")
