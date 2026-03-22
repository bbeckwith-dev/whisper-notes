from main import build_parser


def test_cli_default_args():
    parser = build_parser()
    args = parser.parse_args(["test.m4a"])
    assert args.input == "test.m4a"
    assert args.model == "small"
    assert args.claude_model == "sonnet"  # changed from haiku
    assert args.force is False
    assert args.no_format is False


def test_cli_force_flag():
    parser = build_parser()
    args = parser.parse_args(["test.m4a", "--force"])
    assert args.force is True


def test_cli_all_flags():
    parser = build_parser()
    args = parser.parse_args([
        "recordings/", "--model", "medium",
        "--claude-model", "opus", "--force",
    ])
    assert args.input == "recordings/"
    assert args.model == "medium"
    assert args.claude_model == "opus"
    assert args.force is True


def test_cli_no_format_flag():
    parser = build_parser()
    args = parser.parse_args(["test.m4a", "--no-format"])
    assert args.no_format is True
