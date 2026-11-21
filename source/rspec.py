"""Helpers for writing autograded Rust exercises (practice sets and the career module).

ex(...) registers one exercise. Wrong answers in `bad` are either full programs or
(old, new) replacements applied to the solution, which keeps them close to real mistakes.
"""
EXERCISES = []

ASYNC_PRELUDE = '''fn block_on<F: std::future::Future>(f: F) -> F::Output {
    let mut f = std::pin::pin!(f);
    let mut cx = std::task::Context::from_waker(std::task::Waker::noop());
    loop {
        if let std::task::Poll::Ready(v) = f.as_mut().poll(&mut cx) {
            return v;
        }
    }
}'''


def ex(lid, title, prompt, starter, solution, cases, bad, hints, explain, prelude="", eid=None, mutation=None, loose=False):
    """cases: list of (name, body) or (name, body, attrs); attrs like '#[should_panic(expected = "zero")]'."""
    spec_cases = []
    for c in cases:
        name, body = c[0], c[1]
        item = {"name": name, "body": body}
        if len(c) > 2:
            item["attrs"] = c[2]
        spec_cases.append(item)
    bads = []
    for b in bad:
        if isinstance(b, tuple):
            old, new = b
            assert solution.count(old) >= 1, f"{lid}: bad replacement not found: {old!r}"
            bads.append(solution.replace(old, new, 1))
        else:
            bads.append(b)
    for i, b in enumerate(bads):
        assert b != solution, f"{lid} bad#{i} equals the solution"
    spec = {"rust": True, "starter": starter, "cases": spec_cases}
    if prelude:
        spec["prelude"] = prelude
    if mutation:
        spec["mutation"] = mutation
    EXERCISES.append({"eid": eid or lid + "c", "lesson": lid, "title": "Practice: " + title, "prompt": prompt,
                      "starter": starter, "solution": solution, "spec": spec, "bad": bads,
                      "hints": hints, "explain": explain, "loose": loose})
