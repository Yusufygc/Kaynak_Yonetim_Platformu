from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontMetrics


def elide_to_lines(text: str, font: QFont, width: int, max_lines: int) -> str:
    """Metni verilen genislik/font icin en fazla max_lines satira sigacak sekilde
    diziler; sigmayan kisim varsa son satir '...' ile kesilir.

    text.split() bosluk/satir-sonu ayirt etmez -- kaynak metindeki gelisigüzel
    \\n'leri de duz akan tek metne normalize eder (scrape edilmis ham baslik/
    aciklamalarda sik gorulen bir durum).
    """
    metrics = QFontMetrics(font)
    words = text.split()
    if not words:
        return ""

    lines: list[str] = []
    idx = 0
    total = len(words)
    while idx < total and len(lines) < max_lines:
        line = words[idx]
        idx += 1
        while idx < total:
            candidate = f"{line} {words[idx]}"
            if metrics.horizontalAdvance(candidate) <= width:
                line = candidate
                idx += 1
            else:
                break
        lines.append(line)

    fully_consumed = idx >= total
    if fully_consumed and "\n" not in text:
        # Hicbir sey kirpilmedi ve kaynakta zorlanmis satir sonu yok --
        # orijinal metni degistirmeden dondur (QLabel kendi wordWrap'iyle
        # akitir, string kimligi korunur).
        return text

    if not fully_consumed:
        # Son satir tek basina genisliğe sigiyor olabilir (elidedText o zaman
        # dokunmaz) -- kalan kelimeleri ekleyip tasmayi garanti ederek '...'
        # gercekten gorunmesini sagliyoruz.
        overflow_sample = lines[-1] + " " + " ".join(words[idx:])
        lines[-1] = metrics.elidedText(overflow_sample, Qt.TextElideMode.ElideRight, width)

    return "\n".join(lines)
