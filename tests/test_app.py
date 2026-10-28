import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from quick_translate.config import ConfigManager
from quick_translate.translator.engine import TranslationEngine
from quick_translate.ui.main_window import MainWindow

class TestQuickTranslate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.config = ConfigManager()
        cls.engine = TranslationEngine()

    def test_translation_engine_rich(self):
        # 1. Test word lookup with rich dictionary data
        res = self.engine.translate("run")
        self.assertIsNotNone(res)
        self.assertTrue(len(res.common_meanings) > 0 or len(res.pos_meanings) > 0)
        self.assertIn("UK", res.phonetics)
        self.assertTrue(len(res.examples) > 0)
        self.assertTrue(len(res.word_forms) > 0)
        self.assertTrue(len(res.exam_tags) > 0)
        print("Run word forms verified:", [(wf.name, wf.value) for wf in res.word_forms[:3]])
        print("Run exam tags verified:", res.exam_tags)
        print("Run collins star:", res.collins_star)

        # 2. Test Chinese lookup
        res_cn = self.engine.translate("努力")
        self.assertIsNotNone(res_cn)
        self.assertTrue(res_cn.has_content())
        print("努力 result verified:", res_cn.translation)

        # 3. Test favorites & history
        self.engine.toggle_favorite("run", res.translation)
        favs = self.engine.get_favorites()
        self.assertTrue(any(f["query"] == "run" for f in favs))
        history = self.engine.get_recent_history(5)
        self.assertTrue(len(history) > 0)
        print("History & Favorites verified successfully!")

    def test_ui_slide_and_theme(self):
        window = MainWindow(self.config, self.engine)
        self.assertIsNotNone(window)

        # Test empty launchpad state
        window._refresh_empty_state()

        # Test slide down
        window.slide_down()
        self.assertTrue(window.isVisible())

        # Test theme switching
        window.apply_theme("light")
        self.assertIn("f8fafc", window.styleSheet())
        window.apply_theme("dark")
        self.assertIn("18181c", window.styleSheet())

        # Test render result
        res = self.engine.translate("run")
        window.result_view.render_result(res)
        self.assertTrue(window.result_view.container_layout.count() > 0)
        print("UI slide and theme verified successfully!")

if __name__ == "__main__":
    unittest.main()
