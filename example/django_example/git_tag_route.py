from django.http import HttpRequest, JsonResponse

from example.django_example.utils import route_path, run_urlpatterns
from pait.app.django import pait
from pait.extra.tag import GitTag
from pait.g import get_ctx

route_commit_tag = GitTag(fallback="unreleased")


@pait(tag=(route_commit_tag,))
def route_version(request: HttpRequest) -> JsonResponse:
    """Return the Git tag selected from this route's source history."""
    resolved_tag = get_ctx().pait_core_model.tag[0]
    return JsonResponse({"route": "route_version", "tag": resolved_tag.name})


urlpatterns = [route_path("api/route-version", route_version, ["GET"], name="route-version")]


if __name__ == "__main__":
    run_urlpatterns(urlpatterns, "example.django_example.git_tag_route_urlconf")
