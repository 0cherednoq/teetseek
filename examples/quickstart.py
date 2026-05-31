"""End-to-end example: feed raw text to textseek and pull out structured data.

Run it:

    uv run python examples/quickstart.py

The text below imitates a typical confirmation email. We extract the
confirmation code (near its label, mixing letters/digits/symbols) and the
magic link (matched by an example URL), then read the link's parts.
"""

from textseek import TextSeek, Extract

text = """\
Hello!

Your confirmation code is A8F3-K2P9.

Magic link:
https://example.com/auth/magic?token=real-token-123&email=test@example.com
"""


def main() -> None:
    seek = TextSeek(text)

    code = seek.extract_one(
        Extract.code(
            min_length=9,
            max_length=9,
            digits=True,
            alphabet=True,
            symbols=True,
            near="confirmation code",
        )
    )

    link = seek.extract_one(
        Extract.link(
            sample="https://example.com/auth/magic?token=abc&email=test@example.com"
        )
    )

    print("code:", code.value)
    print("link domain:", link.domain)
    print("link path:", link.path)
    print("token:", link.query_params["token"][0])


if __name__ == "__main__":
    main()
