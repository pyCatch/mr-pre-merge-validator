from mr_validator.interfaces.cli import build_parser


def test_validate_command_parses_project_and_mr_iid() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "validate",
            "--project",
            "sztomi/mr-validator-homework",
            "--mr-iid",
            "1",
        ]
    )

    assert args.command == "validate"
    assert args.project == "sztomi/mr-validator-homework"
    assert args.mr_iid == 1