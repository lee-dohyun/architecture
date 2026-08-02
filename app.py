from flask import Flask, render_template, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# 아키텍처 데이터 (2026-08-02 최신화 — posselect.com 쇼핑몰 도메인 분리 반영)
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
                {"name": "MinIO", "domains": ["minio.leedohyun.com", "static.leedohyun.com"], "status": "deployed"},
                {"name": "Tool", "domains": ["tool.leedohyun.com"], "status": "deployed"},
                {"name": "Architecture Web", "domains": ["architecture.leedohyun.com"], "status": "deployed"},
                {"name": "라우터 관리화면 프록시", "domains": ["router.leedohyun.com"], "status": "deployed"}
            ],
            "shop_line": [
                {"name": "home.front", "domains": ["home.posselect.com"], "desc": "쇼핑몰 메인 랜딩 페이지 (Next.js)", "status": "deployed"},
                {"name": "customer.front / auth.api", "domains": ["customer.posselect.com"], "desc": "로그인/회원가입/정보수정, Keycloak(customer realm) 위임 인증", "status": "deployed"},
                {"name": "product.front / product-api", "domains": ["product.posselect.com"], "desc": "상품 목록/장바구니, 비로그인도 이용 가능(OPTIONAL_AUTH_HOSTS)", "status": "deployed"},
                {"name": "order-api", "domains": ["/api/orders/** (customer.posselect.com, product.posselect.com)"], "desc": "주문/결제(mock), 로그인 시 계정에 자동 연결", "status": "deployed"},
                {"name": "admin.front", "domains": ["admin.posselect.com"], "desc": "관리자 백오피스, Keycloak(staff realm) 로그인", "status": "deployed"},
                {"name": "Keycloak", "domains": ["keycloak.posselect.com"], "desc": "SSO/OAuth2·OIDC — 2026-08-02부로 쇼핑몰 전용, 개인 서비스와 완전 분리", "status": "deployed"},
                {"name": "Grafana (모니터링)", "domains": ["monitoring.posselect.com"], "desc": "2026-08-02: monitoring.leedohyun.com에서 이전, 쇼핑몰 전용 모니터링으로 재정의. gateway/auth-api/order-api/product-api의 /actuator/prometheus + postgres-exporter + redis-exporter를 실제로 스크레이핑", "status": "deployed"}
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
                {"name": "kube-prometheus-stack (Prometheus/Grafana/Alertmanager)", "status": "deployed"}
            ],
            "cicd": [
                {"name": "GitHub Actions CI (이미지 빌드+푸시)", "scope": "전 저장소", "status": "deployed"},
                {"name": "self-hosted runner 기반 CD (자동 배포)", "scope": "gateway / auth.api / home.front / customer.front / admin.front / order.api / product.api", "status": "deployed"},
                {"name": "수동 배포", "scope": "architecture-web, wordpress, tool 등", "status": "manual"}
            ]
        },
        "issues": [
            "백업 체계 없음 (PVC가 local-path 기반, 노드 장애 시 데이터 손실 위험)",
            "보안 강화 미적용 (RBAC 세분화, NetworkPolicy, Istio mTLS — 계획 문서만 존재)",
            "관찰성 부족 (분산 추적, APM 부재 — 메트릭 수집만 됨)",
            "단일 장애점 (단일 노드 클러스터, 이중화 없음)",
            "Alertmanager 외부 알림 채널(Email/Slack) 미연동 — 알림 규칙은 평가되나 실시간 통보 안 됨",
            "자체 메일서버가 가정용 유동 IP+PTR 미설정이라 스팸함 도달 가능성 있음 (구조적 한계)",
            "architecture-web/tool/wordpress는 여전히 수동 배포"
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
        "cpu": "4% (580m / 6코어)",
        "memory": "23% (7.6Gi / 31Gi)",
        "nodes": 1,
        "cluster_type": "K3s v1.33 (단일 노드, control-plane 겸 worker)"
    },
    "updated_at": "2026-08-02"
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
