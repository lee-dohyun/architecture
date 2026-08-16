import json
import os
import sys

# app.py에서 데이터 추출 (기존 코드의 일부분을 import하거나 파싱)
sys.path.append(os.getcwd())
from app import architecture_data

# 구조 잡기: UI 관련 텍스트 추가
ko_data = {
    "ui": {
        "title": "MSA 아키텍처 구조도",
        "subtitle": "K3s 클러스터 마이크로서비스 아키텍처 현황 및 개선 계획",
        "last_updated": "최종 업데이트: ",
        "tab_posselect": "posselect.com",
        "tab_leedohyun": "leedohyun.com",
        "tab_infra": "공통 인프라",
        "tab_domainsplit": "도메인 구성",
        "tab_improved": "개선 계획",
        "tab_roadmap": "장기 로드맵",
        "tab_resources": "리소스 현황",
        "status_deployed": "배포됨",
        "status_planned": "계획됨",
        "status_manual": "수동",
        "status_review": "검토 대상",
        "status_decided": "원칙 확정",
        "status_confirmed": "확정",
        "issues_posselect": "posselect.com 쪽 문제점",
        "issues_leedohyun": "leedohyun.com 쪽 문제점",
        "issues_infra": "공통 인프라 문제점",
        "changes_title": "이전하면서 바뀐 것들",
        "resources_title": "현재 클러스터 리소스 사용량",
        "resource_cpu": "CPU 사용률",
        "resource_memory": "메모리 사용률",
        "resource_nodes": "노드 수",
        "resource_type": "클러스터 타입",
        "no_image": "이미지 없음"
    },
    "data": architecture_data,
    "mermaid": {
        "posselect": """
            Internet[인터넷] --> DNS2[Route 53<br/>posselect.com]
            DNS2 --> Router[가정용 라우터<br/>포트포워딩 80/443/25]
            Router --> Traefik[Traefik Ingress<br/>kube-system, MetalLB IP 공유]
            Traefik --> GW[Spring Cloud Gateway<br/>leedohyun.com과 공용 진입점 — 자세한 건 '공통 인프라' 탭]

            GW --> HF[home.front]
            GW --> CF[customer.front]
            GW --> PF[product.front]
            GW --> ADF[admin.front]
            GW --> AA[auth.api]
            GW --> PA[product-api]
            GW --> OA[order-api]
            GW --> KC[Keycloak<br/>keycloak.posselect.com]
            GW --> GF[Grafana<br/>monitoring.posselect.com]
            GW --> IP[imgproxy<br/>image.posselect.com]
            GW --> UI[posselect-ui<br/>ui.posselect.com]

            AA --> KC
            ADF -.-> KC
            CF -.-> AA
            HF -.-> AA
            PA -.-> OA
            IP -.->|design-assets 버킷| MO2[MinIO<br/>leedohyun.com 탭과 동일 인스턴스]
            UI -.->|서명 URL| IP

            GF -.->|메트릭 스크레이핑| GW
            GF -.->|메트릭 스크레이핑| AA
            GF -.->|메트릭 스크레이핑| PA
            GF -.->|메트릭 스크레이핑| OA
            GF -.->|익스포터 경유| PG2
            GF -.->|익스포터 경유| Redis2

            KC --> PG1[PostgreSQL]
            PA --> PG2[PostgreSQL<br/>catalog]
            OA --> PG3[PostgreSQL<br/>orders]
            PA --> Redis2[Redis<br/>장바구니]
        """,
        "leedohyun": """
            Internet[인터넷] --> DNS1[Route 53<br/>leedohyun.com]
            DNS1 --> Router[가정용 라우터<br/>포트포워딩 80/443/25]
            Router --> Traefik[Traefik Ingress<br/>kube-system, MetalLB IP 공유]
            Traefik --> GW[Spring Cloud Gateway<br/>posselect.com과 공용 진입점 — 자세한 건 '공통 인프라' 탭]

            GW --> WP[WordPress<br/>leedohyun.com / blog]
            GW --> RM[Redmine<br/>alm / redmine]
            GW --> MO[MinIO<br/>minio / static]
            GW --> TL[Tool]
            GW --> AW[Architecture Web<br/>지금 보고 계신 이 페이지]
            GW --> RT[라우터 관리화면 프록시]

            WP --> MySQL1[MySQL]
            RM --> MySQL1
            WP --> Redis1[Redis]
        """,
        "infra": """
            GW[Spring Cloud Gateway<br/>두 도메인 공용 진입점] -.->|메일 발송| MAIL[자체 메일서버<br/>leedohyun.com + posselect.com]

            PROM[Prometheus] --> GF2[Grafana]
            GF2 --> AM[Alertmanager<br/>Email 알림]
            LOKI[Loki / Promtail<br/>로그 수집]
            JG[Jaeger<br/>분산 트레이싱]
            VL[Velero<br/>PVC 백업]

            PROM -.->|메트릭 스크레이핑| GW
            LOKI -.->|전 네임스페이스| GW
            JG -.->|OTel javaagent| GW
            VL -.->|node-agent, MinIO에 저장| MO[MinIO]
        """,
        "domainsplit": """
            subgraph before[이전: leedohyun.com 단일 도메인]
                B1[leedohyun.com] --> B2[home / customer / product / admin]
                B1 --> B3[blog / redmine / minio / tool / ...]
                B2 --> B4[Keycloak<br/>keycloak.leedohyun.com]
            end

            subgraph after[현재: 도메인 분리]
                A1[leedohyun.com<br/>개인 전용] --> A2[blog / redmine / minio / tool / architecture / router / monitoring]
                A3[posselect.com<br/>쇼핑몰 전용] --> A4[home / customer / product / admin]
                A3 --> A5[Keycloak<br/>keycloak.posselect.com]
            end

            before -.전환.-> after
        """,
        "improved": """
            Internet[인터넷] --> DNS[Route 53 DNS<br/>leedohyun.com + posselect.com]
            DNS --> Router[개인 라우터]
            Router --> Traefik[Traefik Ingress]
            Traefik --> GW[Spring Cloud Gateway<br/>단일 진입점 - 이미 완료]
            Traefik --> Istio[Istio 서비스 메시<br/>mTLS]

            GW --> WP[WordPress]
            GW --> RM[Redmine]
            GW --> KC[Keycloak]
            GW --> Shop[쇼핑몰 - posselect.com]

            GW --> Monitor[모니터링/로그 스택<br/>Prometheus/Grafana/Loki - 완료]
            Monitor --> AlertManager[Alertmanager<br/>Email 완료, Slack 계획]

            GW --> Observability[관찰성 스택]
            Observability --> Kiali[Kiali]
            Observability --> Jaeger[Jaeger<br/>Java 백엔드 4개 완료]

            GW --> Storage[스토리지]
            Storage --> MinIO[MinIO]
            Storage --> Velero[Velero<br/>PVC 자동 백업 완료]
        """,
        "roadmap": """
            subgraph now["지금 — 홈서버 (과도기)"]
                direction TB
                MinIO2[MinIO<br/>shop/static, shop/image]
                ImgProxy[imgproxy<br/>이미지 가공]
            end

            subgraph later["나중 — 클라우드 전환 시점"]
                direction TB
                S3[S3 호환 스토리지<br/>동일한 키 구조 그대로 이전]
                CDN2[CloudFront / Cloudflare<br/>단일 cdn.posselect.com + 경로 구분]
            end

            subgraph newcap["신규 기능 — 처음부터 클라우드로"]
                direction TB
                Video[VOD<br/>Cloudflare Stream / Mux 등]
                Live[라이브 스트리밍<br/>AWS IVS / MediaConvert 등]
            end

            now -.->|"이름/URL 체계는 유지, 백엔드만 교체"| later
        """
    }
}

os.makedirs("data", exist_ok=True)
with open("data/ko.json", "w", encoding="utf-8") as f:
    json.dump(ko_data, f, ensure_ascii=False, indent=2)
