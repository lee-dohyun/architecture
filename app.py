from flask import Flask, render_template, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# 아키텍처 데이터
architecture_data = {
    "current": {
        "title": "현재 K3s 클러스터 아키텍처 구조도 (실제 배포 상태)",
        "services": {
            "web_services": [
                {"name": "WordPress", "domains": ["leedohyun.com", "blog.leedohyun.com"], "status": "deployed"},
                {"name": "Redmine", "domains": ["alm.leedohyun.com", "redmine.leedohyun.com"], "status": "deployed"},
                {"name": "Keycloak", "domains": ["keycloak.leedohyun.com"], "status": "deployed"},
                {"name": "MinIO", "domains": ["minio.leedohyun.com", "static.leedohyun.com"], "status": "deployed"}
            ],
            "databases": [
                {"name": "MySQL", "services": ["WordPress", "Redmine"], "status": "deployed"},
                {"name": "PostgreSQL", "services": ["Keycloak"], "status": "deployed"}
            ],
            "cache": [
                {"name": "Redis", "services": ["WordPress"], "status": "deployed"}
            ],
            "infrastructure": [
                {"name": "Traefik Ingress", "status": "deployed"},
                {"name": "cert-manager", "status": "deployed"},
                {"name": "MetalLB", "status": "deployed"},
                {"name": "coredns", "status": "deployed"},
                {"name": "metrics-server", "status": "deployed"}
            ]
        },
        "issues": [
            "모니터링 부재 (Prometheus, Grafana 미배포)",
            "보안 취약점 (Service Mesh 부재, 통합 인증 연계 범위 제한)",
            "관찰성 부족 (분산 추적, APM 부재)",
            "스토리지 관리 (백업 시스템 부재)",
            "단일 장애점 (단일 노드 클러스터)"
        ]
    },
    "improved": {
        "title": "개선된 K3s 클러스터 아키텍처 구조도",
        "additional_services": [
            {"name": "Grafana", "domain": "grafana.leedohyun.com", "status": "planned"},
            {"name": "Prometheus", "domain": "prometheus.leedohyun.com", "status": "planned"},
            {"name": "Kiali", "domain": "kiali.leedohyun.com", "status": "planned"},
            {"name": "Jaeger", "domain": "jaeger.leedohyun.com", "status": "planned"}
        ]
    },
    "resources": {
        "cpu": "11% (1350m)",
        "memory": "38% (6GB/16GB)",
        "nodes": 1,
        "cluster_type": "K3s (단일 노드)"
    }
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
