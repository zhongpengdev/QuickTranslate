import sys
import os
import unittest

# Add project root to sys.path
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

    def test_translation_engine(self):
        # 1. Test word lookup
        res = self.engine.translate("apple")
        self.assertIsNotNone(res)
        self.assertTrue(len(res.common_meanings) > 0 or len(res.pos_meanings) > 0)
        self.assertIn("UK", res.phonetics)
        self.assertTrue(len(res.examples) > 0)
        print("Apple result verified:", res.translation, res.phonetics)

        # 2. Test Chinese lookup
        res_cn = self.engine.translate("努力")
        self.assertIsNotNone(res_cn)
        self.assertTrue(res_cn.has_content())
        print("努力 result verified:", res_cn.translation, res_cn.common_meanings[:2])

        # 3. Test sentence lookup
        res_sent = self.engine.translate("Knowledge is power.")
        self.assertIsNotNone(res_sent)
        self.assertTrue(res_sent.has_content())
        print("Sentence result verified:", res_sent.translation)

    def test_ui_components(self):
        window = MainWindow(self.config, self.engine)
        self.assertIsNotNone(window)
        # Test loading state
        window.result_view.show_loading_state("test")
        # Test render
        res = self.engine.translate("hello")
        window.result_view.render_result(res)
        self.assertTrue(window.result_view.container_layout.count() > 0)
        print("UI components verified successfully!")

if __name__ == "__main__":
    unittest.main()
