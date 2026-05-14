from PySide6.QtGui import QFont


class Fonts:
    FAMILY_PRIMARY = "Inter"
    FAMILY_MONO = "JetBrains Mono"

    @staticmethod
    def h1() -> QFont:
        return QFont(Fonts.FAMILY_PRIMARY, 24, QFont.Weight.Bold)

    @staticmethod
    def h2() -> QFont:
        return QFont(Fonts.FAMILY_PRIMARY, 18, QFont.Weight.Bold)

    @staticmethod
    def h3() -> QFont:
        return QFont(Fonts.FAMILY_PRIMARY, 14, QFont.Weight.DemiBold)

    @staticmethod
    def body() -> QFont:
        return QFont(Fonts.FAMILY_PRIMARY, 12, QFont.Weight.Normal)

    @staticmethod
    def caption() -> QFont:
        return QFont(Fonts.FAMILY_PRIMARY, 10, QFont.Weight.Normal)

    @staticmethod
    def mono() -> QFont:
        return QFont(Fonts.FAMILY_MONO, 12, QFont.Weight.Normal)
