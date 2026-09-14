"""patent-search-mcp: EPO OPSを検索・書誌取得するMCPサーバー。

`.mcp.json`（patent-projectsリポジトリ側）の `patent-search-mcp` エントリから
stdio経由で起動される想定。
"""

from __future__ import annotations

import json

from mcp.server.mcpserver import MCPServer

from .config import ConfigError, get_settings
from .ops_client import OPSClient, OPSError

mcp = MCPServer(
    name="patent-search-mcp",
    instructions=(
        "EPO Open Patent Services (OPS) 経由で特許を検索・取得するツール群。"
        "search_patents で公開特許をCQLクエリで検索し、"
        "get_bibliographic_data で個々の特許番号の書誌・要約を取得する。"
    ),
)

_client: OPSClient | None = None


def _get_client() -> OPSClient:
    global _client
    if _client is None:
        _client = OPSClient(get_settings())
    return _client


@mcp.tool()
async def search_patents(query: str, range_begin: int = 1, range_end: int = 25) -> str:
    """EPO OPSのpublished-data searchで特許を検索し、ヒット結果をJSON文字列で返す。

    Args:
        query: OPSのCQL検索式。例: 'ti=drone AND pd within "2020-2026"'
        range_begin: 取得範囲の開始位置（1始まり）
        range_end: 取得範囲の終了位置（OPSの1回あたり上限に注意）
    """
    try:
        client = _get_client()
    except ConfigError as exc:
        return f"[MCP未接続] {exc}"

    try:
        result = await client.search_published_data(
            query, range_begin=range_begin, range_end=range_end
        )
    except OPSError as exc:
        return f"[OPSエラー] {exc}"

    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_bibliographic_data(
    patent_number: str,
    input_format: str = "docdb",
    constituents: str = "biblio,abstract",
) -> str:
    """特許番号から書誌情報・要約を取得し、JSON文字列で返す。

    Args:
        patent_number: 特許番号。
            docdb形式（推奨）の例: 'EP.4803425.A1'（search_patentsの結果に含まれる
            country/doc-number/kindを'.'で連結するだけでよい）
            epodoc形式の例: 'EP4803425'（kindコードを付けると見つからない場合がある）
        input_format: 'docdb'（推奨） または 'epodoc'
        constituents: 取得する構成要素（カンマ区切り）。デフォルトは 'biblio,abstract'
    """
    try:
        client = _get_client()
    except ConfigError as exc:
        return f"[MCP未接続] {exc}"

    try:
        result = await client.get_bibliographic_data(
            patent_number, input_format=input_format, constituents=constituents
        )
    except OPSError as exc:
        return f"[OPSエラー] {exc}"

    return json.dumps(result, ensure_ascii=False, indent=2)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
