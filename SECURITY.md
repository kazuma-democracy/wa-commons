# Security Policy

WA Commons may process politically sensitive public evidence and, in future experiments, financial or civic workflows. Security failures could harm real people and organizations.

## Please report privately

Do not publish an exploit that could enable:

- unauthorized financial action;
- exposure of private contributor/user information;
- evidence-store tampering;
- provenance forgery;
- agent permission escalation;
- mass false classification;
- credential or secret disclosure.

Until a dedicated security contact is established, do not deploy WA Commons with real-money credentials or sensitive personal data.

## Default security posture

- least privilege;
- local/private secrets;
- immutable or append-oriented audit logs where practical;
- signed/versioned policy and evidence artifacts where practical;
- human approval for high-impact actions;
- explicit rate limits;
- no silent model-driven privilege escalation.
