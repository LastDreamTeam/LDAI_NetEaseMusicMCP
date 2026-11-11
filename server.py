# SPDX-License-Identifier: AGPL-3.0-only
"""MCP tools backed by the official NetEase Cloud Music CLI."""
import json
import os
from pathlib import Path
import shutil
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field
from cli_support import run_json

mcp = FastMCP("netease-music")
Id = Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]{1,128}$")]
Page = Annotated[int, Field(ge=1, le=50)]
Offset = Annotated[int, Field(ge=0, le=100000)]
Text = Annotated[str, Field(min_length=1, max_length=200)]

def executable():
    entry = os.getenv("NCM_CLI_JS")
    node = os.getenv("NCM_NODE") or shutil.which("node")
    if entry and node:
        return [node, str(Path(entry).expanduser().resolve(strict=True))]
    installed = shutil.which("ncm-cli")
    if installed and os.name != "nt":
        return [installed]
    if installed and node:
        package = Path(installed).parent / "node_modules" / "@music163" / "ncm-cli"
        manifest = package / "package.json"
        if manifest.is_file():
            bins = json.loads(manifest.read_text(encoding="utf-8"))["bin"]
            js = bins["ncm-cli"] if isinstance(bins, dict) else bins
            return [node, str((package / js).resolve(strict=True))]
    raise ValueError("Install @music163/ncm-cli or configure NCM_NODE and NCM_CLI_JS.")

def command(args, intent):
    return run_json([*executable(), *args, "--output", "json", "--userInput", intent])

@mcp.tool()
def music_status():
    """Read login status for the current operating-system user's CLI profile."""
    return run_json([*executable(), "login", "--check", "--output", "json"])

@mcp.tool()
def music_search(keyword: Text, kind: Literal["song","playlist","album","mv","voice","podcast","all"] = "song",
                 limit: Page = 20, offset: Offset = 0):
    """Search the catalog. Retain provider IDs for subsequent operations."""
    args = ["search", kind, "--keyword", keyword]
    if kind != "all":
        args.extend(["--limit", str(limit), "--offset", str(offset)])
    return command(args, "搜索音乐目录")

@mcp.tool()
def music_library(collection: Literal["profile","favorites","created_playlists","collected_playlists","collected_albums"],
                  limit: Page = 20, offset: Offset = 0):
    """Read the signed-in user's profile or a page from a library collection."""
    commands = {"profile":["user","info"],"favorites":["user","favorite"],"created_playlists":["playlist","created"],
                "collected_playlists":["playlist","collected"],"collected_albums":["album","collected"]}
    args = commands[collection]
    if collection not in ("profile","favorites"):
        args += ["--limit", str(limit), "--offset", str(offset)]
    return command(args, "读取个人音乐库")

@mcp.tool()
def music_playlist(playlist_id: Id, tracks: bool = False, limit: Page = 20, offset: Offset = 0):
    """Read playlist metadata or a page of tracks."""
    args = ["playlist", "tracks" if tracks else "get", "--playlistId", playlist_id]
    if tracks:
        args += ["--limit", str(limit), "--offset", str(offset)]
    return command(args, "查看歌单")

@mcp.tool()
def music_daily(limit: Page = 20):
    """Read daily recommendations for this user."""
    return command(["recommend","daily","--limit",str(limit)], "查看每日推荐")

@mcp.tool()
def music_lyric(song_id: Id):
    """Read lyrics available to the current account."""
    return command(["song","lyric","--songId",song_id], "查看歌词")

@mcp.tool()
def music_like(song_id: Id, liked: bool):
    """Set or remove a favorite for one song."""
    return command(["song","like" if liked else "dislike","--songId",song_id], "更新红心歌曲")

@mcp.tool()
def music_create_playlist(name: Text):
    """Create a playlist in the current account."""
    return command(["playlist","create","--playlistName",name], "创建歌单")

@mcp.tool()
def music_rename_playlist(playlist_id: Id, name: Text):
    """Change the displayed name of an owned playlist."""
    return command(["playlist","updateName","--playlistId",playlist_id,"--name",name], "修改歌单名称")

@mcp.tool()
def music_edit_tracks(playlist_id: Id, action: Literal["add","remove"],
                      song_ids: Annotated[list[Id],Field(min_length=1,max_length=50)]):
    """Add or remove the specified tracks. Inspect playlist membership before retrying."""
    return command(["playlist",action,"--playlistId",playlist_id,"--songIdList",
                    json.dumps(list(dict.fromkeys(song_ids)),separators=(",",":"))], "更新歌单曲目")

@mcp.tool()
def music_cloud(limit: Page = 20, cursor: str = ""):
    """Read a page from the account's music cloud library."""
    options = ["--limit",str(limit),"--sortType","ADD_TIME_DESC"]
    if cursor:
        options += ["--cursor",cursor]
    return command(["cloud","list",*options], "读取云盘歌曲")

@mcp.tool()
def music_podcast_categories():
    """Read the provider's podcast categories."""
    return command(["podcast","categories"], "读取播客分类")

@mcp.tool()
def music_ai_balance():
    """Read the account's AI songwriting credit balance."""
    return command(["aisong","pointBalance"], "读取音乐创作积分")

@mcp.tool()
def music_album(album_id: Id):
    """Read metadata for a catalog album."""
    return command(["album","get","--albumId",album_id], "读取专辑")


@mcp.tool()
def music_podcast(podcast_id:Annotated[str,Field(pattern=r"^\d{1,24}$")],episodes:bool=False,limit:Page=20,offset:Offset=0):
    """Read a podcast/radio channel or a page of its episodes."""
    if episodes:
        return command(["podcast","voices","--id",podcast_id,"--limit",str(limit),"--offset",str(offset),
                        "--filterCtrl","true","--needPlayRecord","true","--asc","false"],"读取电台节目")
    return command(["podcast","get","--ids",json.dumps([podcast_id])],"读取电台详情")

@mcp.tool()
def music_collected_podcasts(limit:Page=20,cursor:str=""):
    """Read radio channels subscribed to by the selected user."""
    args=["podcast","collected","--limit",str(limit),"--cursor",cursor or "0"]
    return command(args,"读取收藏电台")

if __name__ == "__main__":
    mcp.run(transport="stdio")
