#include <QApplication>
#include <QMainWindow>
#include <QColorDialog>

#include <QtCore/QtCore>

#include <stdio.h>


int main(int argc, char *argv[]) {
    QString input(argc > 1 ? QString("#") + argv[1] : QString("#000000FF"));

    QString col = input.left(7);
    QString al = input.right(2);

    bool ok = false;
    uint alpha = ("0x" + al).toUInt(&ok, 16);
    if(!ok)
        return 1;

    QColor color(col);
    color.setAlpha(alpha);

    QApplication a(argc, argv);

    bool selected = false;
    QColor result;
    QColorDialog colorDialog(color);
    colorDialog.setOptions(QColorDialog::ShowAlphaChannel);
    QObject::connect(&colorDialog, &QColorDialog::colorSelected, [&] (const QColor& col) {
        selected = true;
        result = col;
    });
    colorDialog.show();

    const int rc = a.exec();

    if(!selected)
        printf("CANCEL");
    else {
        QString hexAlpha;
        hexAlpha.setNum(result.alpha(), 16);
        if(hexAlpha.length() == 1)
            hexAlpha = "0" + hexAlpha;
        printf("%s%s", result.name().toUpper().toUtf8().constData(), hexAlpha.toUpper().toUtf8().constData());
    }

    return rc;
}
