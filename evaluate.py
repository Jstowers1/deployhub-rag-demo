import os
from dataclasses import dataclass

from generator import Generator, clear_usage_log
from retriever import Retriever


@dataclass
class TestCase:
    id: str
    query: str
    must_contain: list[str]  #factual keywords expected in answer
    must_not_contain: list[str]  #forbidden terms for hallucination check
    expected_source: str
    description: str


TEST_CASES = [
    TestCase(
        id="pricing_pro",
        query="How much does the Pro plan cost?",
        must_contain=["$29", "29/month"],
        must_not_contain=["$99", "free"],
        expected_source="pricing.md",
        description="Pro plan price lookup",
    ),
    TestCase(
        id="support_sla",
        query="What is the support response time on the Team plan?",
        must_contain=["4h", "4 hour"],
        must_not_contain=["24h"],
        expected_source="pricing.md",
        description="Team plan SLA",
    ),
    TestCase(
        id="free_limits",
        query="How many deployments do I get on the free plan?",
        must_contain=["100"],
        must_not_contain=["unlimited"],
        expected_source="deployment.md",
        description="Free tier deployment limit",
    ),
    TestCase(
        id="port_binding",
        query="My app returns 502 Bad Gateway, what should I do?",
        must_contain=["8080", "PORT"],
        must_not_contain=["404"],
        expected_source="troubleshooting.md",
        description="502 troubleshooting",
    ),
    TestCase(
        id="ssl_cert",
        query="How are SSL certificates provisioned?",
        must_contain=["Let's Encrypt", "auto"],
        must_not_contain=["self-signed"],
        expected_source="deployment.md",
        description="SSL auto-provisioning",
    ),
    TestCase(
        id="api_rate_limit",
        query="What are the API rate limits?",
        must_contain=["50 requests", "200 requests"],
        must_not_contain=["1000 requests"],
        expected_source="api.md",
        description="API rate limit lookup",
    ),
    TestCase(
        id="encryption",
        query="How is my data encrypted?",
        must_contain=["AES-256", "TLS"],
        must_not_contain=["unencrypted", "plaintext"],
        expected_source="security.md",
        description="Encryption at rest and in transit",
    ),
    TestCase(
        id="out_of_scope",
        query="Can DeployHub mine cryptocurrency?",
        must_contain=["not sure", "contact support", "not found", "don't have"],
        must_not_contain=["yes, we support mining", "cryptocurrency mining is"],
        expected_source="",
        description="Out-of-scope question should not hallucinate",
    ),
]


@dataclass
class TestResult:
    test_id: str
    query: str
    passed: bool
    answer: str
    keyword_pass: bool
    source_pass: bool
    hallucination_pass: bool
    details: list[str]


def run_tests():
    retriever = Retriever()
    generator = Generator()
    clear_usage_log()

    results = []
    for tc in TEST_CASES:
        search_results = retriever.search(tc.query, top_k=3)
        gen_result = generator.generate(tc.query, search_results)
        answer_lower = gen_result.answer.lower()
        details = []

        #check 1: factual keyword match
        keyword_pass = any(kw.lower() in answer_lower for kw in tc.must_contain)
        if not keyword_pass:
            details.append(f"MISSING keyword: expected one of {tc.must_contain}")

        #check 2: correct source retrieved
        source_pass = True
        if tc.expected_source:
            source_pass = tc.expected_source in gen_result.sources
            if not source_pass:
                details.append(
                    f"WRONG SOURCE: expected {tc.expected_source}, "
                    f"got {gen_result.sources}"
                )

        #check 3: no hallucinated forbidden terms
        hallucination_pass = True
        for forbidden in tc.must_not_contain:
            if forbidden.lower() in answer_lower:
                hallucination_pass = False
                details.append(f"FORBIDDEN TERM found: '{forbidden}'")
                break

        passed = keyword_pass and source_pass and hallucination_pass
        results.append(
            TestResult(
                test_id=tc.id,
                query=tc.query,
                passed=passed,
                answer=gen_result.answer,
                keyword_pass=keyword_pass,
                source_pass=source_pass,
                hallucination_pass=hallucination_pass,
                details=details,
            )
        )

    return results


if __name__ == "__main__":
    import sys

    if not os.environ.get("GEMINI_API_KEY"):
        print("set GEMINI_API_KEY to run evaluation suite")
        sys.exit(1)
    results = run_tests()
    passed = sum(1 for r in results if r.passed)
    print(f"\n{passed}/{len(results)} tests passed\n")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.test_id}: {r.query[:50]}")
        for d in r.details:
            print(f"         {d}")
