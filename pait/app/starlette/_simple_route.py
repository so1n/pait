from typing import Dict, List, Optional, Union

from starlette.applications import Starlette
from starlette.routing import Match, Mount, Route
from starlette.types import Scope

from pait.app.base.simple_route import SimpleRoute, add_route_plugin
from pait.app.starlette.plugin.unified_response import UnifiedResponsePlugin


class RouteNode:
    def __init__(
        self,
        route_list: Optional[List[Route]] = None,
        node: Optional[Dict[str, "RouteNode"]] = None,
    ):
        self.route_list: List[Route] = route_list if route_list else []
        self.node: Dict[str, "RouteNode"] = node if node else dict()


class RouteTrie:
    def __init__(self) -> None:
        self.root_node: "RouteNode" = RouteNode()

        self.root: Dict[str, Union["RouteTrie", dict, Route, List[Route]]] = {}
        self.route_dict: Dict["RouteTrie", List[Route]] = {}

    def insert_by_app(self, app: Starlette) -> None:
        while True:
            sub_app: Starlette = getattr(app, "app", None)
            if not sub_app:
                break
            app = sub_app
        for route in app.routes:
            if not isinstance(route, Route):
                continue
            url: str = route.path
            self.insert(url, route)

    def insert(self, url_path: str, route: Route) -> None:
        cur_node: "RouteNode" = self.root_node
        for node_url in url_path.strip().split("/"):
            if node_url and "{" == node_url[0] and "}" == node_url[-1]:
                break
            elif node_url not in cur_node.node:
                cur_node.node[node_url] = RouteNode()
            cur_node = cur_node.node[node_url]
        cur_node.route_list.append(route)

    def _search_node(self, url_path: str) -> RouteNode:
        cur_node = self.root_node
        for url_node in url_path.strip().split("/"):
            if url_node in cur_node.node:
                cur_node = cur_node.node[url_node]
            else:
                break
        return cur_node

    def search_by_scope(self, url_path: str, scope: Scope) -> Optional[Route]:
        cur_node: "RouteNode" = self._search_node(url_path)
        route: Optional[Route] = None
        for route in cur_node.route_list:
            if route.path == url_path:
                break
            match, child_scope = route.matches(scope)
            if match == Match.FULL:
                break

        return route

    def search(self, url_path: str) -> Optional[List[Route]]:
        cur_node: "RouteNode" = self._search_node(url_path)
        if cur_node.route_list:
            return cur_node.route_list
        return None


def add_simple_route(
    app: Starlette,
    simple_route: "SimpleRoute",
) -> None:
    add_route_plugin(simple_route, UnifiedResponsePlugin)
    app.add_route(simple_route.url, simple_route.route, methods=simple_route.methods)


def add_multi_simple_route(
    app: Starlette,
    *simple_route_list: "SimpleRoute",
    prefix: str = "/",
    title: str = "",
) -> None:
    # prefix `/` route group must be behind other route group
    route_trie: RouteTrie = RouteTrie()
    route_trie.insert_by_app(app)
    if route_trie.search(prefix):
        for simple_route in simple_route_list:
            add_route_plugin(simple_route, UnifiedResponsePlugin)
            add_simple_route(app, simple_route)
    else:
        route_list: List[Route] = []
        for simple_route in simple_route_list:
            add_route_plugin(simple_route, UnifiedResponsePlugin)
            route_list.append(Route(simple_route.url, simple_route.route, methods=simple_route.methods))
        app.routes.append(Mount(prefix, name=title, routes=route_list))
