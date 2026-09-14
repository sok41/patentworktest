"""EPO Open Patent Services (OPS) APIクライアント。

OPS: https://www.epo.org/ja/searching-for-patents/data/web-services/ops
API仕様書: https://www.epo.org/en/searching-for-patents/data/web-services/ops/documentation

認証は OAuth2 client_credentials グラント（Consumer Key/Secretを使ったBasic認証で
アクセストークンを取得し、以後 Bearer トークンとしてAPIを呼び出す）。
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import httpx

from .config import Settings

_TOKEN_PATH = "/auth/accesstoken"
_SEARCH_PATH = "/rest-services/published-data/search"
_BIBLIO_PATH = "/rest-services/published-data/{reference_type}/{input_format}/{number}/{constituents}"

# トークンの有効期限ギリギリで使ってエラーになるのを避けるための安全マージン
_TOKEN_SAFETY_MARGIN_SECONDS = 30


@dataclass
class _CachedToken:
    access_token: str
    expires_at: float  # time.monotonic() 基準


class OPSError(RuntimeError):
    """OPS APIがエラーレスポンスを返した場合に送出する。"""


class OPSClient:
    """EPO OPS APIへの薄いラッパー。アクセストークンの取得・キャッシュ・更新も担う。"""

    def __init__(self, settings: Settings, *, timeout: float = 30.0) -> None:
        self._settings = settings
        self._client = httpx.AsyncClient(base_url=settings.ops_base_url, timeout=timeout)
        self._token: _CachedToken | None = None

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _get_access_token(self) -> str:
        now = time.monotonic()
        if self._token is not None and now < self._token.expires_at:
            return self._token.access_token

        try:
            response = await self._client.post(
                _TOKEN_PATH,
                data={"grant_type": "client_credentials"},
                auth=(self._settings.ops_consumer_key, self._settings.ops_consumer_secret),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise OPSError(
                f"OPSのアクセストークン取得に失敗しました（status={exc.response.status_code}）。"
                " Consumer Key/Secretが正しいか、developers.epo.orgでアプリが有効になっているか確認してください。"
                f" 詳細: {exc.response.text[:500]}"
            ) from exc

        payload = response.json()
        access_token = payload["access_token"]
        expires_in = float(payload.get("expires_in", 1200))
        self._token = _CachedToken(
            access_token=access_token,
            expires_at=now + expires_in - _TOKEN_SAFETY_MARGIN_SECONDS,
        )
        return access_token

    async def _authed_get(self, path: str, *, params: dict[str, str] | None = None) -> httpx.Response:
        token = await self._get_access_token()
        try:
            response = await self._client.get(
                path,
                params=params,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise OPSError(
                f"OPS APIがエラーを返しました（status={exc.response.status_code}, path={path}）。"
                f" 詳細: {exc.response.text[:500]}"
            ) from exc
        return response

    async def search_published_data(
        self, cql_query: str, *, range_begin: int = 1, range_end: int = 25
    ) -> dict:
        """published-data search（書誌検索）を実行する。

        Args:
            cql_query: OPSのCQL検索式。例: 'ti=drone AND pd within "2020-2026"'
            range_begin: 取得範囲の開始位置（1始まり）
            range_end: 取得範囲の終了位置（最大でrange_begin+99程度、OPSの上限に従う）
        """
        response = await self._authed_get(
            _SEARCH_PATH,
            params={"q": cql_query, "Range": f"{range_begin}-{range_end}"},
        )
        return response.json()

    async def get_bibliographic_data(
        self,
        patent_number: str,
        *,
        input_format: str = "docdb",
        reference_type: str = "publication",
        constituents: str = "biblio,abstract",
    ) -> dict:
        """特許番号から書誌情報・要約（abstract）を取得する。

        Args:
            patent_number: 特許番号。
                docdb形式（推奨。search_patentsの結果のcountry/doc-number/kindを
                '.'で連結するだけでよい）の例: 'EP.4803425.A1'
                epodoc形式の例: 'EP4803425'（末尾にkindコードを付けると
                SERVER.EntityNotFoundになる場合があるため付けないこと）
            input_format: 'docdb'（推奨） または 'epodoc'
            reference_type: 通常は 'publication'
            constituents: 取得する構成要素。'biblio' 'abstract' をカンマ区切りで指定
        """
        path = _BIBLIO_PATH.format(
            reference_type=reference_type,
            input_format=input_format,
            number=patent_number,
            constituents=constituents,
        )
        response = await self._authed_get(path)
        return response.json()
