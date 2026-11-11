# SPDX-License-Identifier: AGPL-3.0-only
import sys
import unittest
from unittest.mock import patch

import server
from cli_support import run_json

class ProviderTest(unittest.TestCase):
    def test_business_error_on_successful_process(self):
        with self.assertRaisesRegex(ValueError,"rejected"):
            run_json([sys.executable,"-c","print('{\u0022success\u0022:false}')"])

    def test_projection_removes_credentials(self):
        result = run_json([sys.executable,"-c","import json; print(json.dumps({'token':'fixture','song':'example'}))"])
        self.assertEqual(result,{"song":"example"})

    def test_podcast_cursor_and_single_object_profile(self):
        from router import account_arguments
        with patch.object(server,"command",return_value={}) as run:
            server.music_collected_podcasts()
            self.assertEqual(run.call_args.args[0][-2:],["--cursor","0"])
            server.music_collected_podcasts(cursor="next")
            self.assertEqual(run.call_args.args[0][-2:],["--cursor","next"])
        self.assertEqual(account_arguments("netease_podcast_read",{"action":"collected"}),{"action":"collected","cursor":"0"})
        self.assertEqual(account_arguments("netease_user_library",{"action":"profile","limit":1}),{"action":"profile"})
        self.assertEqual(account_arguments("netease_user_library",{"action":"created_playlists","limit":3})["limit"],3)

    def test_playlist_keeps_ids_in_one_argument(self):
        with patch.object(server,"command",return_value={}) as run:
            server.music_edit_tracks("playlist","add",["alpha","alpha","beta"])
            self.assertEqual(run.call_args.args[0][-2:],["--songIdList",'["alpha","beta"]'])
