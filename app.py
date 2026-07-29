from flask import Flask, render_template, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# 아키텍처 데이터 (2026-07-29 최신화)
architecture_data = {
    "current": {
        "title": "현재 K3s 클러스터 아키텍처 구조도 (실제 배포 상태)",
        "services": {
            "gateway": [
                {"name": "Spring Cloud Gateway", "domains": ["모든 *.leedohyun.com 도메인의 실제 진입점"], "status": "deployed"}
            ],
            "web_services": [
                {"name": "WordPress", "domains": ["leedohyun.com", "blog.leedohyun.com"], "status": "deployed"},
                {"name": "Redmine", "domains": ["alm.leedohyun.com", "redmine.leedohyun.com"], "status": "deployed"},
                {"name": "Keycloak", "domains": ["keycloak.leedohyun.com"], "status": "deployed"},
                {"name": "MinIO", "domains": ["minio.leedohyun.com", "static.leedohyun.com"], "status": "deployed"},
                {"name": "Tool", "domains": ["tool.leedohyun.com"], "status": "deployed"},
                {"name": "Architecture Web", "domains": ["architecture.leedohyun.com"], "status": "deployed"},
                {"name": "라우터 관리화면 프록시", "domains": ["router.leedohyun.com"], "status": "deployed"}
            ],
            "customer_line": [
                {"name": "home.front", "domains": ["home.leedohyun.com"], "desc": "메인 랜딩 페이지 (Next.js)", "status": "deployed"},
                {"name": "customer.front", "domains": ["customer.leedohyun.com"], "desc": "로그인/회원가입/정보수정 UI (Next.js)", "status": "deployed"},
                {"name": "auth.api", "domains": ["/api/auth/** (customer.leedohyun.com, home.leedohyun.com)"], "desc": "Keycloak 위임 인증 어댑터 (Spring Boot)", "status": "deployed"}
            ],
            "databases": [
                {"name": "MySQL", "services": ["WordPress", "Redmine"], "status": "deployed"},
                {"name": "PostgreSQL", "services": ["Keycloak"], "status": "deployed"},
                {"name": "PostgreSQL/Redis (customer ns)", "services": ["인증 목적 미사용, 비즈니스 데이터용 대기"], "status": "deployed"}
            ],
            "cache": [
                {"name": "Redis", "services": ["WordPress"], "status": "deployed"}
            ],
            "infrastructure": [
                {"name": "Traefik Ingress (kube-system)", "status": "deployed"},
                {"name": "cert-manager (진짜 와일드카드 *.leedohyun.com)", "status": "deployed"},
                {"name": "MetalLB", "status": "deployed"},
                {"name": "coredns", "status": "deployed"},
                {"name": "metrics-server", "status": "deployed"}
            ],
            "cicd": [
                {"name": "GitHub Actions CI (이미지 빌드+푸시)", "scope": "전 저장소", "status": "deployed"},
                {"name": "self-hosted runner 기반 CD (자동 배포)", "scope": "gateway / auth.api / home.front", "status": "deployed"},
                {"name": "수동 배포", "scope": "customer.front, wordpress, tool 등", "status": "manual"}
            ]
        },
        "issues": [
            "모니터링 부재 (Prometheus, Grafana, AlertManager 미배포)",
            "백업 체계 없음 (PVC가 local-path 기반, 노드 장애 시 데이터 손실 위험)",
            "보안 강화 미적용 (RBAC 세분화, NetworkPolicy, Istio mTLS — 계획 문서만 존재)",
            "관찰성 부족 (분산 추적, APM 부재)",
            "단일 장애점 (단일 노드 클러스터, 이중화 없음)",
            "customer.front는 아직 CD 자동화 미구축 (수동 배포 중)"
        ]
    },
    "improved": {
        "title": "개선된 K3s 클러스터 아키텍처 구조도",
        "additional_services": [
            {"name": "Grafana", "domain": "grafana.leedohyun.com", "status": "planned"},
            {"name": "Prometheus", "domain": "prometheus.leedohyun.com", "status": "planned"},
            {"name": "Kiali", "domain": "kiali.leedohyun.com", "status": "planned"},
            {"name": "Jaeger", "domain": "jaeger.leedohyun.com", "status": "planned"},
            {"name": "Velero (백업 자동화)", "domain": "-", "status": "planned"}
        ]
    },
    "resources": {
        "cpu": "4% (580m / 6코어)",
        "memory": "23% (7.6Gi / 31Gi)",
        "nodes": 1,
        "cluster_type": "K3s v1.33 (단일 노드, control-plane 겸 worker)"
    },
    "updated_at": "2026-07-29"
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
        "services": len(architecture_data["current"]["services"]["web_services"])
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
