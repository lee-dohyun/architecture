from flask import Flask, render_template, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# 아키텍처 데이터 (2026-08-05 최신화 — Loki/Velero/Jaeger 관찰성 스택, 로그인 부가기능, MinIO design-assets 버킷/imgproxy CDN 실사용, posselect-ui 반영)
architecture_data = {
    "current": {
        "title": "현재 K3s 클러스터 아키텍처 구조도 (실제 배포 상태)",
        "services": {
            "gateway": [
                {"name": "Spring Cloud Gateway", "domains": ["*.leedohyun.com 전체 + *.posselect.com 전체의 실제 진입점 (단일 게이트웨이 공유)"], "status": "deployed"}
            ],
            "personal_line": [
                {"name": "WordPress", "domains": ["leedohyun.com", "blog.leedohyun.com"], "status": "deployed"},
                {"name": "Redmine", "domains": ["alm.leedohyun.com", "redmine.leedohyun.com"], "status": "deployed"},
                {"name": "MinIO", "domains": ["minio.leedohyun.com", "static.leedohyun.com"], "desc": "S3 호환 오브젝트 스토리지 — 개인용 버킷(book/common/image/web)뿐 아니라 posselect.com 쪽 shop-images/shop-static/design-assets 버킷도 같은 인스턴스를 공유", "status": "deployed"},
                {"name": "Tool", "domains": ["tool.leedohyun.com"], "status": "deployed"},
                {"name": "Architecture Web", "domains": ["architecture.leedohyun.com", "architecture.posselect.com"], "status": "deployed"},
                {"name": "라우터 관리화면 프록시", "domains": ["router.leedohyun.com"], "status": "deployed"}
            ],
            "shop_line": [
                {"name": "home.front", "domains": ["home.posselect.com"], "desc": "쇼핑몰 메인 랜딩 페이지 (Next.js)", "status": "deployed"},
                {"name": "customer.front / auth.api", "domains": ["customer.posselect.com"], "desc": "로그인/회원가입/이메일 인증/정보수정, Keycloak(customer realm) 위임 인증. 2026-08-04: 아이디 찾기, 비밀번호 찾기, 로그인 상태 유지(리프레시 토큰 자동 갱신) 추가", "status": "deployed"},
                {"name": "product.front / product-api", "domains": ["product.posselect.com"], "desc": "상품 목록/장바구니, 비로그인도 이용 가능(OPTIONAL_AUTH_HOSTS)", "status": "deployed"},
                {"name": "order-api", "domains": ["/api/orders/** (customer.posselect.com, product.posselect.com)"], "desc": "주문/결제(mock), 로그인 시 계정에 자동 연결", "status": "deployed"},
                {"name": "admin.front", "domains": ["admin.posselect.com"], "desc": "관리자 백오피스, Keycloak(staff realm) 로그인", "status": "deployed"},
                {"name": "Keycloak", "domains": ["keycloak.posselect.com"], "desc": "SSO/OAuth2·OIDC — 2026-08-02부로 쇼핑몰 전용, 개인 서비스와 완전 분리", "status": "deployed"},
                {"name": "Grafana (모니터링)", "domains": ["monitoring.posselect.com"], "desc": "2026-08-02: monitoring.leedohyun.com에서 이전, 쇼핑몰 전용 모니터링으로 재정의. gateway/auth-api/order-api/product-api의 /actuator/prometheus + postgres-exporter + redis-exporter를 실제로 스크레이핑", "status": "deployed"},
                {"name": "imgproxy CDN", "domains": ["image.posselect.com (imgproxy 리사이징)", "static.posselect.com (MinIO 직접 서빙)"], "desc": "2026-08-05: 2026-08-02에 배포만 되어 있던 인프라(실사용 사례 없음)를 처음 실사용 — MinIO에 design-assets 버킷(브랜드 로고/파비콘 등) 신규 구축, 서명 URL로 imgproxy 경유 서빙", "status": "deployed"},
                {"name": "posselect-ui", "domains": ["ui.posselect.com"], "desc": "디자인 시스템 레퍼런스 페이지(claude.ai 디자인 툴 standalone export를 nginx로 서빙). 2026-08-05: 브랜드 로고/파비콘 6종을 페이지에 통째로 임베드된 base64 대신 image.posselect.com CDN 참조로 전환", "status": "deployed"}
            ],
            "mail": [
                {"name": "자체 메일서버 (docker-mailserver)", "domains": ["customer-service@leedohyun.com", "customer-service@posselect.com"], "desc": "인증메일/주문알림 발신, 두 도메인 모두 DKIM 서명", "status": "deployed"}
            ],
            "databases": [
                {"name": "MySQL", "services": ["WordPress", "Redmine"], "status": "deployed"},
                {"name": "PostgreSQL (keycloak)", "services": ["Keycloak"], "status": "deployed"},
                {"name": "PostgreSQL (catalog-postgres, orders-postgres)", "services": ["product-api", "order-api"], "status": "deployed"},
                {"name": "PostgreSQL (postgres-service, customer ns)", "services": ["레거시, 인증 목적 미사용"], "status": "deployed"}
            ],
            "cache": [
                {"name": "Redis (default ns)", "services": ["WordPress"], "status": "deployed"},
                {"name": "Redis (customer ns)", "services": ["product-api 장바구니"], "status": "deployed"}
            ],
            "infrastructure": [
                {"name": "Traefik Ingress (kube-system)", "status": "deployed"},
                {"name": "cert-manager (와일드카드 *.leedohyun.com + *.posselect.com, 2개 도메인 각각 별도 Certificate)", "status": "deployed"},
                {"name": "MetalLB", "status": "deployed"},
                {"name": "coredns", "status": "deployed"},
                {"name": "metrics-server", "status": "deployed"},
                {"name": "kube-prometheus-stack (Prometheus/Grafana/Alertmanager)", "desc": "2026-08-04: Alertmanager Email 알림 채널 연동 완료(자체 메일서버 경유), Grafana에 Traefik 공식 대시보드 import", "status": "deployed"},
                {"name": "Loki / Promtail", "desc": "2026-08-04 배포. 전 네임스페이스 컨테이너 로그 수집, 보관 14일, Grafana Explore에서 조회", "status": "deployed"},
                {"name": "Jaeger (분산 트레이싱)", "desc": "2026-08-04 배포. OTel Java 자동계측(javaagent)으로 gateway/auth-api/order-api/product-api 계측, HTTP+JDBC 스팬 수집. UI 미노출(port-forward 전용), Next.js 프론트는 미계측", "status": "deployed"},
                {"name": "Velero (백업 자동화)", "desc": "2026-08-04 배포. MinIO를 백업 스토리지로 재사용, node-agent(fs-backup)로 PVC 데이터 포함 전 네임스페이스 매일 백업(보관 10일). 백업 성공은 확인, 실제 restore 리허설은 아직 미검증", "status": "deployed"}
            ],
            "cicd": [
                {"name": "GitHub Actions CI (이미지 빌드+푸시)", "scope": "전 저장소", "status": "deployed"},
                {"name": "self-hosted runner 기반 CD (자동 배포)", "scope": "gateway / auth.api / home.front / customer.front / admin.front / order.api / product.api", "status": "deployed"},
                {"name": "수동 배포", "scope": "architecture-web, wordpress, tool 등", "status": "manual"}
            ]
        },
        "issues": [
            "백업은 자동화됐으나(Velero) 실제 restore 리허설 미검증 — 백업 성공이 복구 가능을 보장하지 않음",
            "보안 강화 미적용 (RBAC 세분화, NetworkPolicy, Istio mTLS — 계획 문서만 존재)",
            "분산 트레이싱은 Java 백엔드 4개만 계측됨(Next.js 프론트 4개는 미계측), Kiali/서비스 메시 관찰성은 여전히 없음",
            "단일 장애점 (단일 노드 클러스터, 이중화 없음)",
            "Alertmanager는 Email만 연동됨, Slack 등 추가 채널 미연동",
            "자체 메일서버가 가정용 유동 IP+PTR 미설정이라 스팸함 도달 가능성 있음 (구조적 한계)",
            "architecture-web/tool/wordpress는 여전히 수동 배포",
            "customer.front 간편 로그인(카카오/네이버/구글)·휴대폰 본인인증·약관 실제 페이지·마케팅 수신동의 백엔드 저장 미구현 (UI만 존재)"
        ]
    },
    "domain_split": {
        "title": "도메인 재구성: leedohyun.com(개인) / posselect.com(쇼핑몰) 분리 (2026-08-02)",
        "summary": "원래 쇼핑몰(customer 제품 라인)이 leedohyun.com의 서브도메인으로 얹혀 있었으나, 별도 도메인 posselect.com을 구매해 완전히 분리했다. K3s 클러스터/게이트웨이/메일서버는 계속 공유하되, DNS·TLS 인증서·Ingress·Keycloak·인증 쿠키까지 도메인 단위로 독립시켰다.",
        "leedohyun_com": ["leedohyun.com/www → blog.leedohyun.com 리다이렉트", "blog/wordpress", "alm/redmine", "minio/static", "tool", "architecture", "router", "monitoring"],
        "posselect_com": ["posselect.com/www → home.posselect.com 리다이렉트", "home", "customer", "product", "admin", "keycloak"],
        "migrated_items": [
            "Route53: posselect.com 신규 호스팅 영역, A(root+wildcard)/MX/SPF/DMARC/DKIM 레코드",
            "TLS: posselect.com 전용 와일드카드 Certificate 신규 발급 (leedohyun.com과 별개)",
            "Ingress: posselect-com-ingress.yaml 신규 (leedohyun-com-ingress.yaml과 동일한 단일 진입점 패턴)",
            "게이트웨이: JwtAuthenticationFilter의 EXPECTED_ISSUER/PROTECTED_HOSTS/OPTIONAL_AUTH_HOSTS/redirect 대상을 GatewaySecurityProperties로 외부화 — 도메인이 또 바뀌어도 코드 수정 불필요",
            "쿠키: ACCESS_TOKEN Domain을 .leedohyun.com → .posselect.com으로 전환 (auth.api, property화)",
            "Keycloak: KC_HOSTNAME을 keycloak.posselect.com으로 변경, 쇼핑몰 전용으로 완전 분리",
            "메일: customer-service@posselect.com 계정 신규 생성, DKIM 키 별도 발급"
        ],
        "backward_compat": "구 leedohyun.com 쪽 쇼핑몰 호스트 5개(home/customer/product/admin/keycloak.leedohyun.com)는 삭제하지 않고 posselect.com으로 302 리다이렉트 — 기존 북마크/링크 호환성 유지"
    },
    "resources": {
        "cpu": "9% (1146m / 6코어, 변동폭 큼)",
        "memory": "50% (16.1Gi / 31Gi)",
        "nodes": 1,
        "cluster_type": "K3s v1.33 (단일 노드, control-plane 겸 worker)"
    },
    "updated_at": "2026-08-05"
}

@app.route('/')
def index():
    return render_template('index.html', data=architecture_data)

@app.route('/api/architecture')
def api_architecture():
    return jsonify(architecture_data)

@app.route('/api/status')
def api_status():
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "personal_services": len(architecture_data["current"]["services"]["personal_line"]),
        "shop_services": len(architecture_data["current"]["services"]["shop_line"])
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
