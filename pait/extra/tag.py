import inspect
import re
import subprocess
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple, Union

from pait.model.tag import ExternalDocumentationModel, Tag, TagFactory

__all__ = ["GitTag", "GitTagError"]


class GitTagError(RuntimeError):
    """Raised when a route's commit tag cannot be resolved."""


class _GitTagAmbiguousError(GitTagError):
    """Raised when a route commit points at more than one tag."""


class GitTag(TagFactory):
    """Resolve a route tag from the Git commit responsible for its source line.

    The route's complete source range is inspected with Git blame. Among the
    commits responsible for those lines, the newest commit with an exact Git
    tag becomes the route's :class:`Tag`.
    """

    def __init__(
        self,
        repo_path: Optional[Union[str, Path]] = None,
        desc: str = "",
        external_docs: Optional["ExternalDocumentationModel"] = None,
        openapi_include: bool = True,
        label: Optional[str] = None,
        fallback: Optional[str] = None,
    ) -> None:
        """
        :param repo_path: Service repository path. By default it is discovered from each route's source file.
        :param desc: Tag description.
        :param external_docs: External documentation for OpenAPI.
        :param openapi_include: Whether to include the resolved tag in OpenAPI.
        :param label: Runtime tag label.
        :param fallback: Value used when no tagged commit can be resolved from the route source.
        """
        self.repo_path = Path(repo_path).resolve() if repo_path is not None else None
        self.desc = desc
        self.external_docs = external_docs
        self.openapi_include = openapi_include
        self.label = label
        self.fallback = fallback
        self._cache: Dict[Tuple[str, int, int], Tag] = {}

    def resolve(self, route: Callable) -> Tag:
        try:
            source_file, start_line, end_line = self._get_route_location(route)
            cache_key = (str(source_file), start_line, end_line)
            if cache_key not in self._cache:
                self._cache[cache_key] = self._resolve_tag(source_file, start_line, end_line)
            return self._cache[cache_key]
        except _GitTagAmbiguousError:
            raise
        except GitTagError:
            if self.fallback is None:
                raise
            return self._create_tag(self.fallback)

    def _resolve_tag(self, source_file: Path, start_line: int, end_line: int) -> Tag:
        lookup_path = self.repo_path or source_file.parent
        repo_root = Path(self._run_git(lookup_path, "rev-parse", "--show-toplevel")).resolve()
        try:
            relative_source_file = source_file.relative_to(repo_root)
        except ValueError as exc:
            raise GitTagError(
                "Route source file {!s} is not in repository {!s}".format(source_file, repo_root)
            ) from exc

        blame_output = self._run_git(
            repo_root,
            "blame",
            "--line-porcelain",
            "-L",
            "{},{}".format(start_line, end_line),
            "--",
            relative_source_file.as_posix(),
        )
        commit_set = {
            match.group(1).lstrip("^")
            for match in re.finditer(r"^(\^?[0-9a-fA-F]{40,64}) \d+ \d+(?: \d+)?$", blame_output, flags=re.MULTILINE)
        }
        commit_set = {commit for commit in commit_set if set(commit) != {"0"}}
        if not commit_set:
            raise GitTagError(
                "Unable to find a committed Git revision for route at {!s}:{}-{}".format(
                    source_file, start_line, end_line
                )
            )

        tagged_commit_list = []
        for commit in sorted(commit_set):
            tag_list = sorted(
                tag.strip()
                for tag in self._run_git(repo_root, "tag", "--points-at", commit).splitlines()
                if tag.strip()
            )
            if len(tag_list) > 1:
                raise _GitTagAmbiguousError(
                    "Route commit {} has multiple Git tags: {}".format(commit, ", ".join(tag_list))
                )
            if tag_list:
                commit_timestamp = int(self._run_git(repo_root, "show", "-s", "--format=%ct", commit))
                tagged_commit_list.append((commit_timestamp, commit, tag_list[0]))

        if not tagged_commit_list:
            raise GitTagError("No commit in the route source range has an exact Git tag")
        return self._create_tag(max(tagged_commit_list)[2])

    def _create_tag(self, name: str) -> Tag:
        return Tag(
            name=name,
            desc=self.desc,
            external_docs=self.external_docs,
            openapi_include=self.openapi_include,
            label=self.label,
        )

    @staticmethod
    def _get_route_location(route: Callable) -> Tuple[Path, int, int]:
        real_route = inspect.unwrap(route)
        source_file = inspect.getsourcefile(real_route)
        if not source_file:
            raise GitTagError("Unable to locate source code for route {!r}".format(route))
        try:
            source_line_list, start_line = inspect.getsourcelines(real_route)
        except (OSError, TypeError) as exc:
            raise GitTagError("Unable to locate source code for route {!r}".format(route)) from exc
        return Path(source_file).resolve(), start_line, start_line + len(source_line_list) - 1

    @staticmethod
    def _run_git(repo_path: Path, *args: str) -> str:
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_path)] + list(args),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                check=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise GitTagError("Unable to query Git repository {!s}".format(repo_path)) from exc
        return result.stdout.strip()
