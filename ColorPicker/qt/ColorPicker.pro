#-------------------------------------------------
#
# Qt Creator / qmake Project
# Compiled 2014-10-05T12:05:00
#
#-------------------------------------------------

TARGET   = ColorPicker
TEMPLATE = app
LANGUAGE = c++

SOURCES += main.cpp
HEADERS +=
FORMS   +=

CONFIG  += static c++11 warn_on

QT      += core gui
greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

QMAKE_CXXFLAGS += -s -fvisibility=hidden -fomit-frame-pointer -march=nocona -Os
QMAKE_LFLAGS   += -s -fvisibility=hidden -dead_strip

macx {
    CONFIG -= app_bundle
    CONFIG += x86_64

    QMAKE_MAC_PLATFORM_NAME        = macosx
    QMAKE_MAC_SDK                  = macosx
    QMAKE_MACOSX_DEPLOYMENT_TARGET = 10.6

    greaterThan(QT_VERSION, 5.3.0) {
        message("Remove new default plugins in QT>5.3.0: 'imageformats', 'accessible', and only 'cocoa' portion of 'platforms'.")
        QTPLUGIN.platforms    = qcocoa
        QTPLUGIN.accessible   = -
        QTPLUGIN.imageformats = -
    }

    system(which g++-4.9) {
        message("Compiling with Homebrew-built GCC 4.9 instead of Apple-built Clang.")
        QMAKE_PLATFORM       = macx-g++
        QMAKE_COMPILER       = g++-4.9
        QMAKE_CXX            = g++-4.9
        QMAKE_CXXFLAGS      += -mmacosx-version-min=$$QMAKE_MACOSX_DEPLOYMENT_TARGET
        QMAKE_CXXFLAGS_CXX11 = -std=c++11

        message("Linking with Apple-built Clang.")
        QMAKE_LINK           = g++
        QMAKE_LFLAGS        += -mmacosx-version-min=$$QMAKE_MACOSX_DEPLOYMENT_TARGET
        QMAKE_LFLAGS_CXX11   = -lc++
    } else {
        message("Compiling with Apple-built GCC or Clang, depending on your OS version.")
    }
}