import argparse
import asyncio

from mr_validator.clients.gitlab_client import GitLabClient
from mr_validator.config import Settings


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


async def run_validate(
    project: str,
    mr_iid: int,
) -> int:
    settings = Settings()

    gitlab_client = GitLabClient(settings)

    mr = await gitlab_client.get_merge_request(
        project=project,
        mr_iid=mr_iid,
    )

    print("MR Pre-Merge Validator")
    print(f"Title: {mr.title}")
    print(f"Branch: {mr.source_branch}")
    print(f"Draft: {mr.is_draft}")
    print(f"Commits: {len(mr.commits)}")

    return 0


async def async_main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "validate":
        return await run_validate(
            project=args.project,
            mr_iid=args.mr_iid,
        )

    return 2

def main() -> None:
    raise SystemExit(
        asyncio.run(async_main())
    )


if __name__ == "__main__":
    main()