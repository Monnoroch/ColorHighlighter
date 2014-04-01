#include <stdio.h>

#include <QApplication>
#include <QMainWindow>
#include <QColorDialog>

int main(int argc, char *argv[]) {
    QApplication a(argc, argv);

    QMainWindow app;
    app.setGeometry(250, 250, 600, 400);
    printf("%sFF", QColorDialog::getColor(QColor(QString("#") + argv[1]), &app, "Color Picker", QColorDialog::DontUseNativeDialog).name().toUpper().toUtf8().constData());

    return 0;
}
