#!/usr/bin/env python3
"""Build dataset/items.jsonl — synthetic log twins (no label leakage in logs)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dataset" / "items.jsonl"

# Each twin: same shape / timestamps / hosts where possible; one observation flips gold.
PAIRS: list[dict] = [
    {
        "twin_id": "twin_wp_probe",
        "log_class": "web_scan",
        "source": "nginx_access",
        "showcase": True,
        "a_role": "attack",
        "b_role": "noise",
        "a": (
            '203.0.113.44 - - [04/Oct/2026:02:11:09 +0000] "GET /wp-login.php HTTP/1.1" 404 182 "-" "Mozilla/5.0"\n'
            '198.51.100.17 - - [04/Oct/2026:02:11:10 +0000] "GET /xmlrpc.php HTTP/1.1" 404 182 "-" "Mozilla/5.0"\n'
            '203.0.113.88 - - [04/Oct/2026:02:11:11 +0000] "GET /wp-admin/install.php HTTP/1.1" 404 182 "-" "curl/8.0"\n'
            '198.51.100.91 - - [04/Oct/2026:02:11:12 +0000] "GET /.env HTTP/1.1" 404 182 "-" "curl/8.0"\n'
            '203.0.113.12 - - [04/Oct/2026:02:11:13 +0000] "GET /vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php HTTP/1.1" 404 182 "-" "curl/8.0"'
        ),
        "b": (
            '34.102.136.180 - - [04/Oct/2026:02:11:09 +0000] "GET /wp-login.php HTTP/1.1" 404 182 "-" "IridiumCI/1.0 (+https://ci.example.internal)"\n'
            '34.102.136.180 - - [04/Oct/2026:02:11:10 +0000] "GET /xmlrpc.php HTTP/1.1" 404 182 "-" "IridiumCI/1.0 (+https://ci.example.internal)"\n'
            '34.102.136.180 - - [04/Oct/2026:02:11:11 +0000] "GET /wp-admin/install.php HTTP/1.1" 404 182 "-" "IridiumCI/1.0 (+https://ci.example.internal)"\n'
            '34.102.136.180 - - [04/Oct/2026:02:11:12 +0000] "GET /.env HTTP/1.1" 404 182 "-" "IridiumCI/1.0 (+https://ci.example.internal)"\n'
            '# note: source IP matches allowlisted CI egress for nightly surface scan job scan-wp-paths'
        ),
        "rationale_a": "Many distinct external IPs probing exploit paths — hostile reconnaissance.",
        "rationale_b": "Same paths from a single allowlisted CI egress with an internal scanner UA — expected noise.",
    },
    {
        "twin_id": "twin_iam_denied",
        "log_class": "cloud_iam",
        "source": "cloudtrail_like",
        "showcase": False,
        "a_role": "misconfig",
        "b_role": "attack",
        "a": (
            "2026-10-04T03:01:12Z event=UpdateRole principal=deploy-bot@ci.example.internal role=prod-app-role "
            "action=iam:PutRolePolicy effect=Allow change=remove s3:GetObject on arn:aws:s3:::prod-invoices/*\n"
            "2026-10-04T03:02:44Z event=GetObject principal=prod-app@ecs.example.internal "
            "bucket=prod-invoices key=customer/invoice-1042.pdf error=AccessDenied request_id=A1B2"
        ),
        "b": (
            "2026-10-04T03:01:12Z event=AssumeRole principal=unknown-oidc session=tmp-session-9f3a "
            "role=prod-app-role source_ip=185.220.101.44 mfa=false\n"
            "2026-10-04T03:02:10Z event=GetObject principal=tmp-session-9f3a "
            "bucket=prod-invoices key=customer/invoice-1042.pdf result=200 bytes=88214\n"
            "2026-10-04T03:02:11Z event=GetObject principal=tmp-session-9f3a "
            "bucket=prod-invoices key=customer/invoice-1043.pdf result=200 bytes=91002\n"
            "2026-10-04T03:02:12Z event=GetObject principal=tmp-session-9f3a "
            "bucket=prod-invoices key=customer/invoice-1044.pdf result=200 bytes=87440"
        ),
        "rationale_a": "Deploy bot tightened IAM; app AccessDenied follows — classic post-deploy misconfig.",
        "rationale_b": "Unknown OIDC assume + bulk successful invoice reads from Tor-ish IP — exfiltration pattern.",
    },
    {
        "twin_id": "twin_api_post",
        "log_class": "web_api",
        "source": "nginx_access",
        "showcase": False,
        "a_role": "needs_more_data",
        "b_role": "attack",
        "a": (
            '198.51.100.44 - - [04/Oct/2026:04:22:01 +0000] "POST /api/v1/transfer HTTP/1.1" - - '
            '"-" "Mozilla/5.0"\n'
            "# upstream closed connection; response status missing; body truncated in shipper"
        ),
        "b": (
            '198.51.100.44 - - [04/Oct/2026:04:22:01 +0000] "POST /api/v1/transfer HTTP/1.1" 200 48 '
            '"-" "sqlmap/1.8#stable"\n'
            'request_body=amount=50000&to_account=1+OR+1%3D1--&user_id=12'
        ),
        "rationale_a": "Interesting endpoint but truncated status/body — cannot triage yet.",
        "rationale_b": "Complete line with sqlmap UA, 200, and SQLi-shaped body — attack.",
    },
    {
        "twin_id": "twin_ssh_auth",
        "log_class": "auth",
        "source": "auth_log",
        "showcase": False,
        "a_role": "noise",
        "b_role": "attack",
        "a": (
            "Oct  4 01:10:01 bastion sshd[2201]: Failed password for invalid user admin from 45.33.32.156 port 51822 ssh2\n"
            "Oct  4 01:10:03 bastion sshd[2203]: Failed password for invalid user root from 45.33.32.156 port 51830 ssh2\n"
            "Oct  4 01:10:05 bastion sshd[2205]: Failed password for invalid user ubuntu from 93.184.216.34 port 44112 ssh2\n"
            "Oct  4 01:10:08 bastion sshd[2207]: Connection closed by 203.0.113.9 port 22022 [preauth]"
        ),
        "b": (
            "Oct  4 01:10:01 bastion sshd[2201]: Failed password for user deploy from 185.220.101.44 port 51822 ssh2\n"
            "Oct  4 01:10:08 bastion sshd[2210]: Accepted publickey for deploy from 185.220.101.44 port 51840 ssh2\n"
            "Oct  4 01:10:12 bastion sudo: deploy : TTY=pts/0 ; USER=root ; COMMAND=/usr/bin/passwd root\n"
            "Oct  4 01:10:40 app-1 sshd[884]: Accepted publickey for deploy from bastion port 44012 ssh2"
        ),
        "rationale_a": "Internet background failed SSH for invalid users — routine noise.",
        "rationale_b": "Fail then success, privilege change, lateral hop — active compromise pattern.",
    },
    {
        "twin_id": "twin_app_500",
        "log_class": "app_error",
        "source": "app_json",
        "showcase": False,
        "a_role": "misconfig",
        "b_role": "attack",
        "a": (
            '{"ts":"2026-10-04T05:00:02Z","level":"ERROR","service":"checkout","msg":"db connection refused",'
            '"host":"db.prod.internal","port":5432,"deploy_id":"2026-10-04-r42"}\n'
            '{"ts":"2026-10-04T05:00:03Z","level":"ERROR","service":"checkout","msg":"db connection refused",'
            '"host":"db.prod.internal","port":5432,"deploy_id":"2026-10-04-r42"}\n'
            '{"ts":"2026-10-04T04:59:50Z","level":"INFO","service":"deploy","msg":"switched DATABASE_HOST to db.prod.internal"}'
        ),
        "b": (
            '{"ts":"2026-10-04T05:00:02Z","level":"ERROR","service":"checkout","msg":"query failed",'
            '"sql_error":"syntax error at or near \\"\\"","path":"/api/search","qs":"q=1\' OR SLEEP(5)--","ip":"198.51.100.77"}\n'
            '{"ts":"2026-10-04T05:00:08Z","level":"ERROR","service":"checkout","msg":"query failed",'
            '"sql_error":"syntax error","path":"/api/search","qs":"q=UNION SELECT credit_card FROM cards--","ip":"198.51.100.77"}'
        ),
        "rationale_a": "Errors line up with a deploy flipping DATABASE_HOST — misconfig/outage, not intrusion.",
        "rationale_b": "SQLi payloads in query string causing DB errors — attack.",
    },
    {
        "twin_id": "twin_waf_block",
        "log_class": "waf",
        "source": "waf_json",
        "showcase": False,
        "a_role": "noise",
        "b_role": "attack",
        "a": (
            '{"ts":"2026-10-04T06:15:00Z","action":"BLOCK","rule":"GenericLFI","ip":"45.79.12.33",'
            '"path":"/index.php","ua":"zgrab/0.x","country":"US","score":5}\n'
            '{"ts":"2026-10-04T06:15:01Z","action":"BLOCK","rule":"GenericLFI","ip":"45.79.12.33",'
            '"path":"/index.php","ua":"zgrab/0.x","country":"US","score":5}'
        ),
        "b": (
            '{"ts":"2026-10-04T06:15:00Z","action":"ALLOW","rule":"-","ip":"203.0.113.50",'
            '"path":"/admin/export","ua":"Mozilla/5.0","user":"alice@example.com","session":"SESS_9aa","bytes":2400000}\n'
            '{"ts":"2026-10-04T06:15:40Z","action":"ALLOW","rule":"-","ip":"203.0.113.50",'
            '"path":"/admin/export","ua":"Mozilla/5.0","user":"alice@example.com","session":"SESS_9aa","bytes":2400000}\n'
            '{"ts":"2026-10-04T06:16:10Z","action":"ALLOW","rule":"-","ip":"198.51.100.9",'
            '"path":"/admin/export","ua":"curl/8.4.0","user":"alice@example.com","session":"SESS_9aa","bytes":2400000}\n'
            "# note: password reset for alice completed 06:10 from 198.51.100.9; prior login geo=US-CA, new ip geo=RU"
        ),
        "rationale_a": "WAF blocking internet zgrab LFI probes — expected noise.",
        "rationale_b": "Authenticated bulk export after reset from new geo/IP — account takeover pattern.",
    },
    {
        "twin_id": "twin_s3_public",
        "log_class": "cloud_storage",
        "source": "s3_access",
        "showcase": False,
        "a_role": "misconfig",
        "b_role": "attack",
        "a": (
            "2026-10-04T07:00:01Z terraform apply finished bucket=prod-assets acl_change=public-read\n"
            "2026-10-04T07:00:30Z REST.GET.OBJECT bucket=prod-assets key=branding/logo.png "
            "requester=- remote=93.184.216.34 http=200\n"
            "2026-10-04T07:01:00Z REST.GET.BUCKET bucket=prod-assets requester=- remote=93.184.216.34 http=200"
        ),
        "b": (
            "2026-10-04T07:00:30Z REST.GET.OBJECT bucket=prod-assets key=private/payroll-2026.csv "
            "requester=- remote=185.220.101.44 http=200 bytes=4502210\n"
            "2026-10-04T07:00:41Z REST.GET.OBJECT bucket=prod-assets key=private/payroll-2025.csv "
            "requester=- remote=185.220.101.44 http=200 bytes=4381102\n"
            "2026-10-04T07:00:55Z REST.GET.OBJECT bucket=prod-assets key=private/ssn-export.csv "
            "requester=- remote=185.220.101.44 http=200 bytes=2200441"
        ),
        "rationale_a": "Terraform just set public-read; public logo/list fits misconfig discovery, not proven theft intent yet — gold misconfig.",
        "rationale_b": "Anonymous bulk download of private payroll/SSN objects — attack/exfil.",
    },
    {
        "twin_id": "twin_vpn_login",
        "log_class": "auth",
        "source": "vpn_json",
        "showcase": False,
        "a_role": "needs_more_data",
        "b_role": "attack",
        "a": (
            '{"ts":"2026-10-04T08:11:00Z","event":"vpn_auth","user":"jsmith","result":"success",'
            '"src_ip":"8.8.8.8","device":"-"}\n'
            "# device field empty; geo lookup timed out in shipper"
        ),
        "b": (
            '{"ts":"2026-10-04T08:11:00Z","event":"vpn_auth","user":"jsmith","result":"success",'
            '"src_ip":"45.141.87.12","device":"unknown-android","mfa":"bypassed_legacy",'
            '"prev_login_geo":"US-NY","curr_geo":"KZ","hours_since_password_reset":0.2}\n'
            '{"ts":"2026-10-04T08:12:10Z","event":"vpn_connect","user":"jsmith","dest":"10.0.4.20",'
            '"bytes_out":12000000}'
        ),
        "rationale_a": "Success login with missing device/geo — suspicious but incomplete.",
        "rationale_b": "MFA bypass, impossible travel, immediate large internal transfer — attack.",
    },
]

CONTROLS: list[dict] = [
    {
        "id": "ctrl_noise_healthcheck",
        "log_class": "web_health",
        "source": "nginx_access",
        "gold_label": "noise",
        "log": (
            '10.0.0.15 - - [04/Oct/2026:00:00:01 +0000] "GET /healthz HTTP/1.1" 200 2 "-" "kube-probe/1.29"\n'
            '10.0.0.15 - - [04/Oct/2026:00:00:11 +0000] "GET /healthz HTTP/1.1" 200 2 "-" "kube-probe/1.29"\n'
            '10.0.0.15 - - [04/Oct/2026:00:00:21 +0000] "GET /healthz HTTP/1.1" 200 2 "-" "kube-probe/1.29"'
        ),
        "rationale": "Internal kube probes to /healthz — expected noise.",
    },
    {
        "id": "ctrl_misconfig_cors",
        "log_class": "app_config",
        "source": "app_json",
        "gold_label": "misconfig",
        "log": (
            '{"ts":"2026-10-04T09:00:00Z","level":"WARN","service":"api","msg":"CORS allow_origins set to *",'
            '"env":"production","deploy_id":"2026-10-04-r55"}\n'
            '{"ts":"2026-10-04T09:00:05Z","level":"INFO","service":"api","msg":"config loaded","cors":"*"}'
        ),
        "rationale": "Prod CORS wildcard after deploy — misconfiguration, no exploit evidence yet.",
    },
    {
        "id": "ctrl_attack_credstuff",
        "log_class": "auth",
        "source": "auth_json",
        "gold_label": "attack",
        "log": (
            '{"ts":"2026-10-04T10:01:00Z","event":"login_fail","user":"alice@example.com","ip":"203.0.113.10"}\n'
            '{"ts":"2026-10-04T10:01:01Z","event":"login_fail","user":"bob@example.com","ip":"203.0.113.10"}\n'
            '{"ts":"2026-10-04T10:01:02Z","event":"login_fail","user":"carol@example.com","ip":"203.0.113.10"}\n'
            '{"ts":"2026-10-04T10:01:03Z","event":"login_ok","user":"dave@example.com","ip":"203.0.113.10"}\n'
            '{"ts":"2026-10-04T10:01:04Z","event":"login_fail","user":"erin@example.com","ip":"203.0.113.10"}'
        ),
        "rationale": "Many users, one IP, fail/success mix — credential stuffing.",
    },
    {
        "id": "ctrl_needs_truncated_stack",
        "log_class": "app_error",
        "source": "app_json",
        "gold_label": "needs_more_data",
        "log": (
            '{"ts":"2026-10-04T11:22:00Z","level":"ERROR","service":"payments","msg":"uncaught exception",'
            '"stack":"TypeError: Cannot read properties of null (reading \'id\')\\n    at Object.<anonymous> (/app/…"}'
        ),
        "rationale": "Truncated stack with no request/user/IP context — needs more data.",
    },
    {
        "id": "ctrl_noise_cert_renew",
        "log_class": "ops",
        "source": "syslog",
        "gold_label": "noise",
        "log": (
            "Oct  4 12:00:01 lb-1 certbot[991]: Certificate not yet due for renewal; no action taken\n"
            "Oct  4 12:00:01 lb-1 systemd[1]: certbot.service: Succeeded."
        ),
        "rationale": "Routine certbot noop — noise.",
    },
    {
        "id": "ctrl_misconfig_debug",
        "log_class": "app_config",
        "source": "app_json",
        "gold_label": "misconfig",
        "log": (
            '{"ts":"2026-10-04T13:00:00Z","level":"WARN","service":"api","msg":"DEBUG=true in production",'
            '"env":"production","deploy_id":"2026-10-04-r60"}'
        ),
        "rationale": "Debug flag on in production — misconfig without active exploit evidence.",
    },
]


def main() -> None:
    rows: list[dict] = []
    for pair in PAIRS:
        for role_key, log_key, rat_key in (
            ("a_role", "a", "rationale_a"),
            ("b_role", "b", "rationale_b"),
        ):
            role = pair[role_key]
            rows.append(
                {
                    "id": f"{pair['twin_id']}_{role}",
                    "twin_id": pair["twin_id"],
                    "twin_role": role,
                    "log_class": pair["log_class"],
                    "source": pair["source"],
                    "showcase": bool(pair.get("showcase") and role == pair["a_role"]),
                    "gold_label": role,
                    "log": pair[log_key],
                    "rationale": pair[rat_key],
                }
            )
    for ctrl in CONTROLS:
        rows.append(
            {
                "id": ctrl["id"],
                "twin_id": None,
                "twin_role": "none",
                "log_class": ctrl["log_class"],
                "source": ctrl["source"],
                "showcase": False,
                "gold_label": ctrl["gold_label"],
                "log": ctrl["log"],
                "rationale": ctrl["rationale"],
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} items -> {OUT}")


if __name__ == "__main__":
    main()
