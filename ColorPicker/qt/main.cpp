#include <stdio.h>

#include <QApplication>
#include <QMainWindow>
#include <QColorDialog>

int main(int argc, char *argv[]) {
    QApplication a(argc, argv);

    QMainWindow app;
    app.setGeometry(250, 250, 600, 400);
    QString input(argc > 1 ? QString("#") + argv[1] : QString("#000000"));
    QString res = QColorDialog::getColor(QColor(input), &app, "Color Picker").name().toUpper();
    if(res == "#000000")
        printf("%sFF", input.toUtf8().constData());
    else
        printf("%sFF", res.toUtf8().constData());

    return 0;
}
