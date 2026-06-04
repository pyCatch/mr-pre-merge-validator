import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mr-validator",
        description="Validate GitLab merge requests before merge.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a GitLab merge request against Jira workflow rules.",
    )
    validate_parser.add_argument(
        "--project",
        required=True,
        help="GitLab project path, for example: sztomi/mr-validator-homework.",
    )
    validate_parser.add_argument(
        "--mr-iid",
        required=True,
        type=int,
        help="GitLab merge request IID.",
    )

    return parser


def run_validate(project: str, mr_iid: int) -> int:
    print("MR Pre-Merge Validator")
    print(f"Project: {project}")
    print(f"MR IID: {mr_iid}")
    print("Status: NOT IMPLEMENTED YET")
    return 2


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "validate":
        raise SystemExit(run_validate(project=args.project, mr_iid=args.mr_iid))

    raise SystemExit(2)


if __name__ == "__main__":
    main()