# %%
"""Log Triage Task 1: four-way label triage (core)."""
from dataclasses import dataclass

import pandas as pd
import kaggle_benchmarks as kbench

# %%
LABELS = ("attack", "misconfig", "noise", "needs_more_data")
# === BEGIN EMBEDDED_ITEMS ===
EMBEDDED_ITEMS = [{'id': 'twin_wp_probe_attack', 'twin_id': 'twin_wp_probe', 'twin_role': 'attack', 'log_class': 'web_scan', 'source': 'nginx_access', 'showcase': True, 'gold_label': 'attack', 'log': '203.0.113.44 - - [04/Oct/2026:02:11:09 +0000] "GET /wp-login.php HTTP/1.1" 404 182 "-" "Mozilla/5.0"\n198.51.100.17 - - [04/Oct/2026:02:11:10 +0000] "GET /xmlrpc.php HTTP/1.1" 404 182 "-" "Mozilla/5.0"\n203.0.113.88 - - [04/Oct/2026:02:11:11 +0000] "GET /wp-admin/install.php HTTP/1.1" 404 182 "-" "curl/8.0"\n198.51.100.91 - - [04/Oct/2026:02:11:12 +0000] "GET /.env HTTP/1.1" 404 182 "-" "curl/8.0"\n203.0.113.12 - - [04/Oct/2026:02:11:13 +0000] "GET /vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php HTTP/1.1" 404 182 "-" "curl/8.0"', 'rationale': 'Many distinct external IPs probing exploit paths — hostile reconnaissance.'}, {'id': 'twin_wp_probe_noise', 'twin_id': 'twin_wp_probe', 'twin_role': 'noise', 'log_class': 'web_scan', 'source': 'nginx_access', 'showcase': False, 'gold_label': 'noise', 'log': '34.102.136.180 - - [04/Oct/2026:02:11:09 +0000] "GET /wp-login.php HTTP/1.1" 404 182 "-" "IridiumCI/1.0 (+https://ci.example.internal)"\n34.102.136.180 - - [04/Oct/2026:02:11:10 +0000] "GET /xmlrpc.php HTTP/1.1" 404 182 "-" "IridiumCI/1.0 (+https://ci.example.internal)"\n34.102.136.180 - - [04/Oct/2026:02:11:11 +0000] "GET /wp-admin/install.php HTTP/1.1" 404 182 "-" "IridiumCI/1.0 (+https://ci.example.internal)"\n34.102.136.180 - - [04/Oct/2026:02:11:12 +0000] "GET /.env HTTP/1.1" 404 182 "-" "IridiumCI/1.0 (+https://ci.example.internal)"\n# note: source IP matches allowlisted CI egress for nightly surface scan job scan-wp-paths', 'rationale': 'Same paths from a single allowlisted CI egress with an internal scanner UA — expected noise.'}, {'id': 'twin_iam_denied_misconfig', 'twin_id': 'twin_iam_denied', 'twin_role': 'misconfig', 'log_class': 'cloud_iam', 'source': 'cloudtrail_like', 'showcase': False, 'gold_label': 'misconfig', 'log': '2026-10-04T03:01:12Z event=UpdateRole principal=deploy-bot@ci.example.internal role=prod-app-role action=iam:PutRolePolicy effect=Allow change=remove s3:GetObject on arn:aws:s3:::prod-invoices/*\n2026-10-04T03:02:44Z event=GetObject principal=prod-app@ecs.example.internal bucket=prod-invoices key=customer/invoice-1042.pdf error=AccessDenied request_id=A1B2', 'rationale': 'Deploy bot tightened IAM; app AccessDenied follows — classic post-deploy misconfig.'}, {'id': 'twin_iam_denied_attack', 'twin_id': 'twin_iam_denied', 'twin_role': 'attack', 'log_class': 'cloud_iam', 'source': 'cloudtrail_like', 'showcase': False, 'gold_label': 'attack', 'log': '2026-10-04T03:01:12Z event=AssumeRole principal=unknown-oidc session=tmp-session-9f3a role=prod-app-role source_ip=185.220.101.44 mfa=false\n2026-10-04T03:02:10Z event=GetObject principal=tmp-session-9f3a bucket=prod-invoices key=customer/invoice-1042.pdf result=200 bytes=88214\n2026-10-04T03:02:11Z event=GetObject principal=tmp-session-9f3a bucket=prod-invoices key=customer/invoice-1043.pdf result=200 bytes=91002\n2026-10-04T03:02:12Z event=GetObject principal=tmp-session-9f3a bucket=prod-invoices key=customer/invoice-1044.pdf result=200 bytes=87440', 'rationale': 'Unknown OIDC assume + bulk successful invoice reads from Tor-ish IP — exfiltration pattern.'}, {'id': 'twin_api_post_needs_more_data', 'twin_id': 'twin_api_post', 'twin_role': 'needs_more_data', 'log_class': 'web_api', 'source': 'nginx_access', 'showcase': False, 'gold_label': 'needs_more_data', 'log': '198.51.100.44 - - [04/Oct/2026:04:22:01 +0000] "POST /api/v1/transfer HTTP/1.1" - - "-" "Mozilla/5.0"\n# upstream closed connection; response status missing; body truncated in shipper', 'rationale': 'Interesting endpoint but truncated status/body — cannot triage yet.'}, {'id': 'twin_api_post_attack', 'twin_id': 'twin_api_post', 'twin_role': 'attack', 'log_class': 'web_api', 'source': 'nginx_access', 'showcase': False, 'gold_label': 'attack', 'log': '198.51.100.44 - - [04/Oct/2026:04:22:01 +0000] "POST /api/v1/transfer HTTP/1.1" 200 48 "-" "sqlmap/1.8#stable"\nrequest_body=amount=50000&to_account=1+OR+1%3D1--&user_id=12', 'rationale': 'Complete line with sqlmap UA, 200, and SQLi-shaped body — attack.'}, {'id': 'twin_ssh_auth_noise', 'twin_id': 'twin_ssh_auth', 'twin_role': 'noise', 'log_class': 'auth', 'source': 'auth_log', 'showcase': False, 'gold_label': 'noise', 'log': 'Oct  4 01:10:01 bastion sshd[2201]: Failed password for invalid user admin from 45.33.32.156 port 51822 ssh2\nOct  4 01:10:03 bastion sshd[2203]: Failed password for invalid user root from 45.33.32.156 port 51830 ssh2\nOct  4 01:10:05 bastion sshd[2205]: Failed password for invalid user ubuntu from 93.184.216.34 port 44112 ssh2\nOct  4 01:10:08 bastion sshd[2207]: Connection closed by 203.0.113.9 port 22022 [preauth]', 'rationale': 'Internet background failed SSH for invalid users — routine noise.'}, {'id': 'twin_ssh_auth_attack', 'twin_id': 'twin_ssh_auth', 'twin_role': 'attack', 'log_class': 'auth', 'source': 'auth_log', 'showcase': False, 'gold_label': 'attack', 'log': 'Oct  4 01:10:01 bastion sshd[2201]: Failed password for user deploy from 185.220.101.44 port 51822 ssh2\nOct  4 01:10:08 bastion sshd[2210]: Accepted publickey for deploy from 185.220.101.44 port 51840 ssh2\nOct  4 01:10:12 bastion sudo: deploy : TTY=pts/0 ; USER=root ; COMMAND=/usr/bin/passwd root\nOct  4 01:10:40 app-1 sshd[884]: Accepted publickey for deploy from bastion port 44012 ssh2', 'rationale': 'Fail then success, privilege change, lateral hop — active compromise pattern.'}, {'id': 'twin_app_500_misconfig', 'twin_id': 'twin_app_500', 'twin_role': 'misconfig', 'log_class': 'app_error', 'source': 'app_json', 'showcase': False, 'gold_label': 'misconfig', 'log': '{"ts":"2026-10-04T05:00:02Z","level":"ERROR","service":"checkout","msg":"db connection refused","host":"db.prod.internal","port":5432,"deploy_id":"2026-10-04-r42"}\n{"ts":"2026-10-04T05:00:03Z","level":"ERROR","service":"checkout","msg":"db connection refused","host":"db.prod.internal","port":5432,"deploy_id":"2026-10-04-r42"}\n{"ts":"2026-10-04T04:59:50Z","level":"INFO","service":"deploy","msg":"switched DATABASE_HOST to db.prod.internal"}', 'rationale': 'Errors line up with a deploy flipping DATABASE_HOST — misconfig/outage, not intrusion.'}, {'id': 'twin_app_500_attack', 'twin_id': 'twin_app_500', 'twin_role': 'attack', 'log_class': 'app_error', 'source': 'app_json', 'showcase': False, 'gold_label': 'attack', 'log': '{"ts":"2026-10-04T05:00:02Z","level":"ERROR","service":"checkout","msg":"query failed","sql_error":"syntax error at or near \\"\\"","path":"/api/search","qs":"q=1\' OR SLEEP(5)--","ip":"198.51.100.77"}\n{"ts":"2026-10-04T05:00:08Z","level":"ERROR","service":"checkout","msg":"query failed","sql_error":"syntax error","path":"/api/search","qs":"q=UNION SELECT credit_card FROM cards--","ip":"198.51.100.77"}', 'rationale': 'SQLi payloads in query string causing DB errors — attack.'}, {'id': 'twin_waf_block_noise', 'twin_id': 'twin_waf_block', 'twin_role': 'noise', 'log_class': 'waf', 'source': 'waf_json', 'showcase': False, 'gold_label': 'noise', 'log': '{"ts":"2026-10-04T06:15:00Z","action":"BLOCK","rule":"GenericLFI","ip":"45.79.12.33","path":"/index.php","ua":"zgrab/0.x","country":"US","score":5}\n{"ts":"2026-10-04T06:15:01Z","action":"BLOCK","rule":"GenericLFI","ip":"45.79.12.33","path":"/index.php","ua":"zgrab/0.x","country":"US","score":5}', 'rationale': 'WAF blocking internet zgrab LFI probes — expected noise.'}, {'id': 'twin_waf_block_attack', 'twin_id': 'twin_waf_block', 'twin_role': 'attack', 'log_class': 'waf', 'source': 'waf_json', 'showcase': False, 'gold_label': 'attack', 'log': '{"ts":"2026-10-04T06:15:00Z","action":"ALLOW","rule":"-","ip":"203.0.113.50","path":"/admin/export","ua":"Mozilla/5.0","user":"alice@example.com","session":"SESS_9aa","bytes":2400000}\n{"ts":"2026-10-04T06:15:40Z","action":"ALLOW","rule":"-","ip":"203.0.113.50","path":"/admin/export","ua":"Mozilla/5.0","user":"alice@example.com","session":"SESS_9aa","bytes":2400000}\n{"ts":"2026-10-04T06:16:10Z","action":"ALLOW","rule":"-","ip":"198.51.100.9","path":"/admin/export","ua":"curl/8.4.0","user":"alice@example.com","session":"SESS_9aa","bytes":2400000}\n# note: password reset for alice completed 06:10 from 198.51.100.9; prior login geo=US-CA, new ip geo=RU', 'rationale': 'Authenticated bulk export after reset from new geo/IP — account takeover pattern.'}, {'id': 'twin_s3_public_misconfig', 'twin_id': 'twin_s3_public', 'twin_role': 'misconfig', 'log_class': 'cloud_storage', 'source': 's3_access', 'showcase': False, 'gold_label': 'misconfig', 'log': '2026-10-04T07:00:01Z terraform apply finished bucket=prod-assets acl_change=public-read\n2026-10-04T07:00:30Z REST.GET.OBJECT bucket=prod-assets key=branding/logo.png requester=- remote=93.184.216.34 http=200\n2026-10-04T07:01:00Z REST.GET.BUCKET bucket=prod-assets requester=- remote=93.184.216.34 http=200', 'rationale': 'Terraform just set public-read; public logo/list fits misconfig discovery, not proven theft intent yet — gold misconfig.'}, {'id': 'twin_s3_public_attack', 'twin_id': 'twin_s3_public', 'twin_role': 'attack', 'log_class': 'cloud_storage', 'source': 's3_access', 'showcase': False, 'gold_label': 'attack', 'log': '2026-10-04T07:00:30Z REST.GET.OBJECT bucket=prod-assets key=private/payroll-2026.csv requester=- remote=185.220.101.44 http=200 bytes=4502210\n2026-10-04T07:00:41Z REST.GET.OBJECT bucket=prod-assets key=private/payroll-2025.csv requester=- remote=185.220.101.44 http=200 bytes=4381102\n2026-10-04T07:00:55Z REST.GET.OBJECT bucket=prod-assets key=private/ssn-export.csv requester=- remote=185.220.101.44 http=200 bytes=2200441', 'rationale': 'Anonymous bulk download of private payroll/SSN objects — attack/exfil.'}, {'id': 'twin_vpn_login_needs_more_data', 'twin_id': 'twin_vpn_login', 'twin_role': 'needs_more_data', 'log_class': 'auth', 'source': 'vpn_json', 'showcase': False, 'gold_label': 'needs_more_data', 'log': '{"ts":"2026-10-04T08:11:00Z","event":"vpn_auth","user":"jsmith","result":"success","src_ip":"8.8.8.8","device":"-"}\n# device field empty; geo lookup timed out in shipper', 'rationale': 'Success login with missing device/geo — suspicious but incomplete.'}, {'id': 'twin_vpn_login_attack', 'twin_id': 'twin_vpn_login', 'twin_role': 'attack', 'log_class': 'auth', 'source': 'vpn_json', 'showcase': False, 'gold_label': 'attack', 'log': '{"ts":"2026-10-04T08:11:00Z","event":"vpn_auth","user":"jsmith","result":"success","src_ip":"45.141.87.12","device":"unknown-android","mfa":"bypassed_legacy","prev_login_geo":"US-NY","curr_geo":"KZ","hours_since_password_reset":0.2}\n{"ts":"2026-10-04T08:12:10Z","event":"vpn_connect","user":"jsmith","dest":"10.0.4.20","bytes_out":12000000}', 'rationale': 'MFA bypass, impossible travel, immediate large internal transfer — attack.'}, {'id': 'ctrl_noise_healthcheck', 'twin_id': None, 'twin_role': 'none', 'log_class': 'web_health', 'source': 'nginx_access', 'showcase': False, 'gold_label': 'noise', 'log': '10.0.0.15 - - [04/Oct/2026:00:00:01 +0000] "GET /healthz HTTP/1.1" 200 2 "-" "kube-probe/1.29"\n10.0.0.15 - - [04/Oct/2026:00:00:11 +0000] "GET /healthz HTTP/1.1" 200 2 "-" "kube-probe/1.29"\n10.0.0.15 - - [04/Oct/2026:00:00:21 +0000] "GET /healthz HTTP/1.1" 200 2 "-" "kube-probe/1.29"', 'rationale': 'Internal kube probes to /healthz — expected noise.'}, {'id': 'ctrl_misconfig_cors', 'twin_id': None, 'twin_role': 'none', 'log_class': 'app_config', 'source': 'app_json', 'showcase': False, 'gold_label': 'misconfig', 'log': '{"ts":"2026-10-04T09:00:00Z","level":"WARN","service":"api","msg":"CORS allow_origins set to *","env":"production","deploy_id":"2026-10-04-r55"}\n{"ts":"2026-10-04T09:00:05Z","level":"INFO","service":"api","msg":"config loaded","cors":"*"}', 'rationale': 'Prod CORS wildcard after deploy — misconfiguration, no exploit evidence yet.'}, {'id': 'ctrl_attack_credstuff', 'twin_id': None, 'twin_role': 'none', 'log_class': 'auth', 'source': 'auth_json', 'showcase': False, 'gold_label': 'attack', 'log': '{"ts":"2026-10-04T10:01:00Z","event":"login_fail","user":"alice@example.com","ip":"203.0.113.10"}\n{"ts":"2026-10-04T10:01:01Z","event":"login_fail","user":"bob@example.com","ip":"203.0.113.10"}\n{"ts":"2026-10-04T10:01:02Z","event":"login_fail","user":"carol@example.com","ip":"203.0.113.10"}\n{"ts":"2026-10-04T10:01:03Z","event":"login_ok","user":"dave@example.com","ip":"203.0.113.10"}\n{"ts":"2026-10-04T10:01:04Z","event":"login_fail","user":"erin@example.com","ip":"203.0.113.10"}', 'rationale': 'Many users, one IP, fail/success mix — credential stuffing.'}, {'id': 'ctrl_needs_truncated_stack', 'twin_id': None, 'twin_role': 'none', 'log_class': 'app_error', 'source': 'app_json', 'showcase': False, 'gold_label': 'needs_more_data', 'log': '{"ts":"2026-10-04T11:22:00Z","level":"ERROR","service":"payments","msg":"uncaught exception","stack":"TypeError: Cannot read properties of null (reading \'id\')\\n    at Object.<anonymous> (/app/…"}', 'rationale': 'Truncated stack with no request/user/IP context — needs more data.'}, {'id': 'ctrl_noise_cert_renew', 'twin_id': None, 'twin_role': 'none', 'log_class': 'ops', 'source': 'syslog', 'showcase': False, 'gold_label': 'noise', 'log': 'Oct  4 12:00:01 lb-1 certbot[991]: Certificate not yet due for renewal; no action taken\nOct  4 12:00:01 lb-1 systemd[1]: certbot.service: Succeeded.', 'rationale': 'Routine certbot noop — noise.'}, {'id': 'ctrl_misconfig_debug', 'twin_id': None, 'twin_role': 'none', 'log_class': 'app_config', 'source': 'app_json', 'showcase': False, 'gold_label': 'misconfig', 'log': '{"ts":"2026-10-04T13:00:00Z","level":"WARN","service":"api","msg":"DEBUG=true in production","env":"production","deploy_id":"2026-10-04-r60"}', 'rationale': 'Debug flag on in production — misconfig without active exploit evidence.'}]
# === END EMBEDDED_ITEMS ===


@dataclass
class TriageVerdict:
    label: str
    explanation: str


def load_items():
    return list(EMBEDDED_ITEMS)


def build_prompt(source: str, log: str) -> str:
    # Prompt isolation: never include twin_id, twin_role, gold_label, or rationale.
    return (
        "You are triaging a short synthetic log bundle for a SOC-lite queue.\n"
        "Choose exactly one label:\n"
        "- attack: evidence of malicious activity or compromise in progress "
        "(exploit probing at scale, credential stuffing with success, exfil, "
        "account takeover patterns)\n"
        "- misconfig: something was set up or deployed wrong; errors follow a "
        "config/IAM/CORS/debug change without clear active exploitation\n"
        "- noise: expected/benign background (health checks, internet scanners "
        "blocked or failing harmlessly, routine ops)\n"
        "- needs_more_data: interesting but incomplete/truncated — do not guess "
        "attack or misconfig without enough evidence\n\n"
        f"Log source hint: {source}\n"
        "Log bundle:\n"
        f"{log}\n"
        "Return structured fields label and explanation (2-4 sentences)."
    )


def _normalize_label(label: str | None) -> str | None:
    if not label:
        return None
    cleaned = str(label).strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "needs_more": "needs_more_data",
        "need_more_data": "needs_more_data",
        "insufficient_data": "needs_more_data",
        "unknown": "needs_more_data",
        "benign": "noise",
        "false_positive": "noise",
        "configuration": "misconfig",
        "misconfiguration": "misconfig",
        "malicious": "attack",
        "compromise": "attack",
    }
    cleaned = aliases.get(cleaned, cleaned)
    return cleaned if cleaned in LABELS else None


def _hits_by_param_id(completed_df: pd.DataFrame) -> dict[int, bool]:
    hits: dict[int, bool] = {}
    if completed_df is None or len(completed_df) == 0:
        return hits
    for _, crow in completed_df.iterrows():
        pid = crow.get("id")
        if pid is None or (isinstance(pid, float) and pd.isna(pid)):
            continue
        hits[int(pid)] = bool(crow.get("result"))
    return hits


def compute_log_triage_score(items: list, hits_by_id: dict[int, bool]) -> float:
    """LT = 0.35·attack + 0.25·misconfig + 0.20·noise + 0.20·needs_more_data."""
    buckets = {
        "attack": [0, 0],
        "misconfig": [0, 0],
        "noise": [0, 0],
        "needs_more_data": [0, 0],
    }
    for idx, row in enumerate(items):
        gold = row["gold_label"]
        if gold not in buckets:
            continue
        buckets[gold][1] += 1
        buckets[gold][0] += int(bool(hits_by_id.get(idx, False)))

    def acc(pair: list[int]) -> float:
        return (pair[0] / pair[1]) if pair[1] else 0.0

    return float(
        0.35 * acc(buckets["attack"])
        + 0.25 * acc(buckets["misconfig"])
        + 0.20 * acc(buckets["noise"])
        + 0.20 * acc(buckets["needs_more_data"])
    )


def compute_panic_gap(golds: list[str], preds: list[str]) -> float:
    """Fraction of noise/misconfig items predicted as attack."""
    denom = panic = 0
    for gold, pred in zip(golds, preds):
        if gold in ("noise", "misconfig"):
            denom += 1
            if pred == "attack":
                panic += 1
    return float(panic / denom) if denom else 0.0


# %%
@kbench.task(name="log-triage-label-item", store_task=False)
def log_triage_label_item(llm, source: str, log: str, gold_label: str) -> bool:
    prompt = build_prompt(source, log)
    verdict = llm.prompt(prompt, schema=TriageVerdict)
    label = _normalize_label(getattr(verdict, "label", None))
    if label is None:
        return False
    return label == gold_label


# %%
@kbench.task(name="log-triage-label")
def log_triage_label(llm) -> float:
    """Log Triage score in [0, 1]. Ranked metric is rewards.score."""
    items = load_items()
    df = pd.DataFrame(
        [
            {
                "source": row["source"],
                "log": row["log"],
                "gold_label": row["gold_label"],
            }
            for row in items
        ]
    )
    results = log_triage_label_item.evaluate(
        llm=[llm],
        evaluation_data=df,
        on_failure="continue",
        n_jobs=1,
    )
    completed = results.completed_runs.as_dataframe()
    hits = _hits_by_param_id(completed)
    score = compute_log_triage_score(items, hits)
    return max(0.0, min(1.0, round(score, 6)))


# %%
log_triage_label.run(kbench.llm)
