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
        "tab_posselect_desc": " — Shopping Mall Service",
        "tab_leedohyun": "leedohyun.com",
        "tab_leedohyun_desc": " — Personal Service",
        "tab_infra": "Common Infra",
        "tab_infra_desc": " — Shared by both domains",
        "tab_domainsplit": "Domain Split",
        "domain_split_personal": "leedohyun.com — Personal Use",
        "domain_split_shop": "posselect.com — Shopping Mall Use",
        "domain_split_compat": "Legacy Domain Compatibility",
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
        "no_image": "No Image",
        "infra_desc": "Spring Cloud Gateway, Cluster Infrastructure, Monitoring/Log/Tracing/Backup, Mail Server, and CI/CD are shared between leedohyun.com and posselect.com. To avoid repeating these in each domain's diagram, they are separated into this tab.",
        "domain_split_title": "Domain Split: leedohyun.com (Personal) / posselect.com (Shop) separation (2026-08-02)",
        "roadmap_title": "Long-term Roadmap — Assuming Cloud Transition and Large-scale Expansion (Confirmed 2026-08-06)"
    },
    "ja": {
        "title": "MSA アーキテクチャ図",
        "subtitle": "K3s クラスター マイクロサービス アーキテクチャの現状と改善計画",
        "last_updated": "最終更新: ",
        "tab_posselect": "posselect.com",
        "tab_posselect_desc": " — ショッピングモールサービス",
        "tab_leedohyun": "leedohyun.com",
        "tab_leedohyun_desc": " — 個人サービス",
        "tab_infra": "共通インフラ",
        "tab_infra_desc": " — 両ドメインで共有するもの",
        "tab_domainsplit": "ドメイン構成",
        "domain_split_personal": "leedohyun.com — 個人専用",
        "domain_split_shop": "posselect.com — ショッピングモール専用",
        "domain_split_compat": "旧ドメインの互換性",
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
        "no_image": "画像なし",
        "infra_desc": "Spring Cloud Gatewayをはじめ、クラスターインフラ、監視・ログ・トレース・バックアップ、メールサーバー、CI/CDはleedohyun.comとposselect.comで共有されています。ドメインごとの構成図で毎回繰り返すと分かりにくくなるため、別タブに分けています。",
        "domain_split_title": "ドメイン再構成：leedohyun.com（個人） / posselect.com（ショッピングモール）の分離 (2026-08-02)",
        "roadmap_title": "長期ロードマップ — クラウド移行および大規模拡張を前提 (2026-08-06確定)"
    },
    "zh": {
        "title": "MSA 架构图",
        "subtitle": "K3s 集群微服务架构现状及改进计划",
        "last_updated": "最后更新: ",
        "tab_posselect": "posselect.com",
        "tab_posselect_desc": " — 商城服务",
        "tab_leedohyun": "leedohyun.com",
        "tab_leedohyun_desc": " — 个人服务",
        "tab_infra": "公共基础设施",
        "tab_infra_desc": " — 两个域名共用的部分",
        "tab_domainsplit": "域名结构",
        "domain_split_personal": "leedohyun.com — 个人专用",
        "domain_split_shop": "posselect.com — 商城专用",
        "domain_split_compat": "旧域名兼容性",
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
        "no_image": "无图片",
        "infra_desc": "Spring Cloud Gateway 以及集群基础设施、监控/日志/追踪/备份、邮件服务器、CI/CD 由 leedohyun.com 和 posselect.com 共享。为了避免在每个域的架构图中重复这些内容，将它们单独放在此标签页中。",
        "domain_split_title": "域名结构重组：leedohyun.com(个人) / posselect.com(商城) 分离 (2026-08-02)",
        "roadmap_title": "长期路线图 — 以云端迁移及大规模扩展为前提 (2026-08-06 确定)"
    }
}

with open("data/ko.json", "r", encoding="utf-8") as f:
    ko_data = json.load(f)

mermaid_dict = {
    "인터넷": {"en": "Internet", "ja": "インターネット", "zh": "互联网"},
    "가정용 라우터": {"en": "Home Router", "ja": "家庭用ルーター", "zh": "家用路由器"},
    "포트포워딩": {"en": "Port Forwarding", "ja": "ポート転送", "zh": "端口转发"},
    "IP 공유": {"en": "IP Sharing", "ja": "IP共有", "zh": "IP共享"},
    "과 공용 진입점": {"en": " Shared Entrypoint", "ja": " 共有エントリポイント", "zh": " 共享入口"},
    "자세한 건 '공통 인프라' 탭": {"en": "See 'Common Infra' tab", "ja": "詳細は「共通インフラ」タブへ", "zh": "详见“通用基础设施”标签页"},
    "버킷": {"en": "Bucket", "ja": "バケット", "zh": "存储桶"},
    "탭과 동일 인스턴스": {"en": "Same instance as tab", "ja": "タブと同じインスタンス", "zh": "与标签页相同实例"},
    "서명 URL": {"en": "Signed URL", "ja": "署名付きURL", "zh": "签名URL"},
    "메트릭 스크레이핑": {"en": "Metric Scraping", "ja": "メトリクススクレイピング", "zh": "指标抓取"},
    "익스포터 경유": {"en": "Via Exporter", "ja": "エクスポーター経由", "zh": "通过Exporter"},
    "장바구니": {"en": "Cart", "ja": "カート", "zh": "购物车"},
    "지금 보고 계신 이 페이지": {"en": "This page you are viewing", "ja": "現在ご覧のページ", "zh": "您当前正在查看的页面"},
    "라우터 관리화면 프록시": {"en": "Router Admin Proxy", "ja": "ルーター管理プロキシ", "zh": "路由器管理代理"},
    "두 도메인 공용 진입점": {"en": "Two domains Shared Entrypoint", "ja": "両ドメイン共有エントリポイント", "zh": "两个域名共享入口"},
    "자체 메일서버": {"en": "Self-hosted Mail", "ja": "自前メールサーバー", "zh": "自建邮件服务器"},
    "메일 발송": {"en": "Send mail", "ja": "メール送信", "zh": "发送邮件"},
    "알림": {"en": "Alert", "ja": "通知", "zh": "警报"},
    "로그 수집": {"en": "Log Collection", "ja": "ログ収集", "zh": "日志收集"},
    "분산 트레이싱": {"en": "Distributed Tracing", "ja": "分散トレーシング", "zh": "分布式追踪"},
    "백업": {"en": "Backup", "ja": "バックアップ", "zh": "备份"},
    "전 네임스페이스": {"en": "All Namespaces", "ja": "全ネームスペース", "zh": "所有命名空间"},
    "에 저장": {"en": " saved to", "ja": " に保存", "zh": " 保存至"},
    "이전:": {"en": "Before:", "ja": "以前:", "zh": "以前:"},
    "단일 도메인": {"en": "Single Domain", "ja": "単一ドメイン", "zh": "单一域名"},
    "현재: 도메인 분리": {"en": "Current: Domain Split", "ja": "現在: ドメイン分離", "zh": "当前: 域名分离"},
    "개인 전용": {"en": "Personal Use", "ja": "個人専用", "zh": "个人专用"},
    "쇼핑몰 전용": {"en": "Shop Use", "ja": "ショップ専用", "zh": "商城专用"},
    "전환": {"en": "Transition", "ja": "移行", "zh": "迁移"},
    "개인 라우터": {"en": "Personal Router", "ja": "個人ルーター", "zh": "个人路由器"},
    "단일 진입점 - 이미 완료": {"en": "Single Entrypoint - Completed", "ja": "単一エントリポイント - 完了", "zh": "单一入口 - 已完成"},
    "서비스 메시": {"en": "Service Mesh", "ja": "サービスメッシュ", "zh": "服务网格"},
    "쇼핑몰 -": {"en": "Shop -", "ja": "ショップ -", "zh": "商城 -"},
    "모니터링/로그 스택": {"en": "Monitor/Log Stack", "ja": "監視/ログスタック", "zh": "监控/日志栈"},
    "완료, Slack 계획": {"en": "Completed, Slack planned", "ja": "完了、Slack計画中", "zh": "已完成，计划支持Slack"},
    "완료": {"en": "Completed", "ja": "完了", "zh": "已完成"},
    "관찰성 스택": {"en": "Observability Stack", "ja": "可観測性スタック", "zh": "可观测性栈"},
    "Java 백엔드 4개 완료": {"en": "Java Backend 4 Completed", "ja": "Javaバックエンド4つ完了", "zh": "4个Java后端已完成"},
    "스토리지": {"en": "Storage", "ja": "ストレージ", "zh": "存储"},
    "자동 백업 완료": {"en": "Auto Backup Completed", "ja": "自動バックアップ完了", "zh": "自动备份完成"},
    "지금 — 홈서버 (과도기)": {"en": "Now - Home Server (Transitional)", "ja": "現在 - ホームサーバー（過渡期）", "zh": "现在 - 家庭服务器（过渡期）"},
    "이미지 가공": {"en": "Image Processing", "ja": "画像処理", "zh": "图像处理"},
    "나중 — 클라우드 전환 시점": {"en": "Later - Cloud Transition", "ja": "将来 - クラウド移行時", "zh": "未来 - 云端迁移时"},
    "호환 스토리지": {"en": "Compatible Storage", "ja": "互換ストレージ", "zh": "兼容存储"},
    "동일한 키 구조 그대로 이전": {"en": "Migrate with same key structure", "ja": "同じキー構造で移行", "zh": "使用相同的键结构迁移"},
    "단일": {"en": "Single", "ja": "単一", "zh": "单一"},
    "경로 구분": {"en": "Path Routing", "ja": "パスルーティング", "zh": "路径路由"},
    "신규 기능 — 처음부터 클라우드로": {"en": "New Feature - Cloud Native", "ja": "新機能 - 最初からクラウドへ", "zh": "新功能 - 云原生"},
    "라이브 스트리밍": {"en": "Live Streaming", "ja": "ライブストリーミング", "zh": "直播"},
    "이름/URL 체계는 유지, 백엔드만 교체": {"en": "Keep Name/URL scheme, replace backend", "ja": "名前/URL体系は維持、バックエンドのみ交換", "zh": "保持名称/URL体系，仅替换后端"},
    "Cloudflare Stream / Mux 등": {"en": "Cloudflare Stream / Mux, etc.", "ja": "Cloudflare Stream / Mux 等", "zh": "Cloudflare Stream / Mux 等"},
    "AWS IVS / MediaConvert 등": {"en": "AWS IVS / MediaConvert, etc.", "ja": "AWS IVS / MediaConvert 等", "zh": "AWS IVS / MediaConvert 等"}
}

def mock_translate_mermaid(data, lang):
    lang_key = lang.lower()
    if isinstance(data, dict):
        return {k: mock_translate_mermaid(v, lang) for k, v in data.items()}
    elif isinstance(data, str):
        res = data
        # Sort keys by length descending to prevent partial replacements
        sorted_keys = sorted(mermaid_dict.keys(), key=len, reverse=True)
        for k in sorted_keys:
            res = res.replace(k, mermaid_dict[k][lang_key])
        return res
    return data

import os

for lang in ["en", "ja", "zh"]:
    # 깊은 복사 후 모의 번역 (fallback)
    lang_data = mock_translate(ko_data, lang.upper())
    
    # UI 부분은 실제 번역으로 덮어쓰기
    lang_data["ui"] = ui_translations[lang]
    
    # 실제 데이터 번역본이 있으면 덮어쓰기
    data_file = f"data/{lang}_data.json"
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as df:
            lang_data["data"] = json.load(df)
            
    # mermaid 다이어그램은 정규식을 이용해 한글 부분만 안전하게 번역 모의
    lang_data["mermaid"] = mock_translate_mermaid(ko_data["mermaid"], lang)
    
    with open(f"data/{lang}.json", "w", encoding="utf-8") as f:
        json.dump(lang_data, f, ensure_ascii=False, indent=2)

print("Translations generated.")
