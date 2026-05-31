from textseek import Extract

# Each case: id, email text, expected confirmation code, kwargs for Extract.code,
# and an optional expected magic-link URL.
CASES = [
    (
        "github_2fa",
        "Hi! Your GitHub verification code is 583920. "
        "It expires in 10 minutes. Account id 100245.",
        "583920",
        dict(length=6, digits=True, near="verification code"),
        None,
    ),
    (
        "stripe_signin",
        "Use code 042913 to finish signing in. "
        "Do not share this code. Ref: 8847.",
        "042913",
        dict(length=6, digits=True, near="code"),
        None,
    ),
    (
        "alnum_invite",
        "Welcome aboard! Your invite code: A1B2C3D4. "
        "Redeem it at https://app.example.com/invite?code=A1B2C3D4",
        "A1B2C3D4",
        dict(length=8, digits=True, alphabet=True, require_each_type=True, near="invite code"),
        "https://app.example.com/invite?code=A1B2C3D4",
    ),
    (
        "symbol_reset",
        "Your password reset code is A8F3-K2P9. "
        "Enter it within 15 minutes.",
        "A8F3-K2P9",
        dict(min_length=8, max_length=12, digits=True, alphabet=True, symbols=True, near="reset code"),
        None,
    ),
    (
        "magic_link",
        "Click to sign in:\n"
        "https://example.com/auth/magic?token=real-token-123&email=test@example.com\n"
        "If you didn't request this, ignore the email.",
        None,
        None,
        "https://example.com/auth/magic?token=real-token-123&email=test@example.com",
    ),
    (
        "noise_numbers",
        "Order #99821 shipped on 2026-05-30 for $124. "
        "Your confirmation code is 730014. Tracking 1Z999.",
        "730014",
        dict(length=6, digits=True, near="confirmation code"),
        None,
    ),
    (
        "lowercase_code",
        "Hey, here is your one-time code: kf8d2a. Valid for 5 min.",
        "kf8d2a",
        dict(length=6, digits=True, alphabet=True, uppercase=False, near="one-time code"),
        None,
    ),
    (
        "sms_short",
        "G-4471 is your Google verification code.",
        "4471",
        dict(length=4, digits=True, near="verification code"),
        None,
    ),
    (
        "link_in_sentence",
        "Confirm your address here https://accounts.example.org/verify?u=42&sig=zz. Thanks!",
        None,
        None,
        "https://accounts.example.org/verify?u=42&sig=zz",
    ),
    (
        "two_codes_pick_near",
        "Promo 111111 is unrelated. Your login code is 246810 — use it now.",
        "246810",
        dict(length=6, digits=True, near="login code"),
        None,
    ),
]
