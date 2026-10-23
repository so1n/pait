import subprocess
from pathlib import Path

import pytest
from pytest_mock import MockFixture

from pait.extra.tag import GitTag, GitTagError
from pait.model.core import PaitCoreModel
from pait.model.tag import Tag
from pait.param_handle import ParamHandler
from tests.util import FakeAppHelper


def route_for_git_tag_test() -> None:
    pass


class TestGitTag:
    def test_non_first_line_tag_is_selected(self, mocker: MockFixture, tmp_path: Path) -> None:
        source_file = tmp_path / "api.py"
        old_commit = "a" * 40
        newest_commit = "b" * 40
        git_tag = GitTag(repo_path=tmp_path, desc="route release")
        mocker.patch.object(git_tag, "_get_route_location", return_value=(source_file, 18, 27))
        run_git_mock = mocker.patch.object(
            git_tag,
            "_run_git",
            side_effect=[
                str(tmp_path),
                "{} 18 18 9\nauthor tester\n{} 27 27 1\nauthor tester".format(old_commit, newest_commit),
                "service-v1.0.0",
                "100",
                "service-v2.0.0",
                "200",
            ],
        )

        resolved_tag = git_tag.resolve(route_for_git_tag_test)

        assert isinstance(resolved_tag, Tag)
        assert resolved_tag.name == "service-v2.0.0"
        assert resolved_tag.desc == "route release"
        assert run_git_mock.call_args_list == [
            mocker.call(tmp_path, "rev-parse", "--show-toplevel"),
            mocker.call(tmp_path, "blame", "--line-porcelain", "-L", "18,27", "--", "api.py"),
            mocker.call(tmp_path, "tag", "--points-at", old_commit),
            mocker.call(tmp_path, "show", "-s", "--format=%ct", old_commit),
            mocker.call(tmp_path, "tag", "--points-at", newest_commit),
            mocker.call(tmp_path, "show", "-s", "--format=%ct", newest_commit),
        ]

    def test_pait_core_model_resolves_git_tag(self, mocker: MockFixture) -> None:
        git_tag = GitTag()
        resolved_tag = Tag("service-route-v2", label="route-version")
        resolve_mock = mocker.patch.object(git_tag, "resolve", return_value=resolved_tag)

        core_model = PaitCoreModel(route_for_git_tag_test, FakeAppHelper, ParamHandler, tag=(git_tag,))

        assert core_model.tag == (resolved_tag,)
        assert core_model.tag_label["service-route-v2"] == "route-version"
        resolve_mock.assert_called_once_with(route_for_git_tag_test)

    def test_resolve_result_is_cached_per_route(self, mocker: MockFixture, tmp_path: Path) -> None:
        source_file = tmp_path / "api.py"
        git_tag = GitTag(fallback="service-dev")
        mocker.patch.object(git_tag, "_get_route_location", return_value=(source_file, 18, 27))
        resolve_mock = mocker.patch.object(git_tag, "_resolve_tag", return_value=Tag("service-cached-tag"))

        assert git_tag.resolve(route_for_git_tag_test).name == "service-cached-tag"
        assert git_tag.resolve(route_for_git_tag_test).name == "service-cached-tag"
        resolve_mock.assert_called_once_with(source_file, 18, 27)

    def test_use_fallback_when_route_commit_has_no_tag(self, mocker: MockFixture, tmp_path: Path) -> None:
        git_tag = GitTag(fallback="service-dev")
        mocker.patch.object(git_tag, "_get_route_location", return_value=(tmp_path / "api.py", 18, 27))
        mocker.patch.object(git_tag, "_resolve_tag", side_effect=GitTagError("commit has no tag"))

        assert git_tag.resolve(route_for_git_tag_test).name == "service-dev"

    def test_raise_without_fallback(self, mocker: MockFixture, tmp_path: Path) -> None:
        git_tag = GitTag()
        mocker.patch.object(git_tag, "_get_route_location", return_value=(tmp_path / "api.py", 18, 27))
        mocker.patch.object(git_tag, "_resolve_tag", side_effect=GitTagError("commit has no tag"))

        with pytest.raises(GitTagError, match="commit has no tag"):
            git_tag.resolve(route_for_git_tag_test)

    def test_raise_when_route_commit_has_multiple_tags(self, mocker: MockFixture, tmp_path: Path) -> None:
        source_file = tmp_path / "api.py"
        commit = "b" * 40
        git_tag = GitTag(repo_path=tmp_path, fallback="service-dev")
        mocker.patch.object(git_tag, "_get_route_location", return_value=(source_file, 18, 27))
        mocker.patch.object(
            git_tag,
            "_run_git",
            side_effect=[str(tmp_path), "{} 18 18 10".format(commit), "service-v2\nservice-latest"],
        )

        with pytest.raises(GitTagError, match="multiple Git tags: service-latest, service-v2"):
            git_tag.resolve(route_for_git_tag_test)

    def test_run_git_command(self, mocker: MockFixture, tmp_path: Path) -> None:
        run_mock = mocker.patch(
            "pait.extra.tag.subprocess.run",
            return_value=subprocess.CompletedProcess([], 0, stdout="result\n", stderr=""),
        )

        assert GitTag._run_git(tmp_path, "rev-parse", "--show-toplevel") == "result"
        run_mock.assert_called_once_with(
            ["git", "-C", str(tmp_path), "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True,
        )
