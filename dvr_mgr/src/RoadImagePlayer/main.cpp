#include "roadimageplayer.h"
#include <QtGui/QApplication>

int main(int argc, char *argv[])
{
	QApplication a(argc, argv);
	RoadImagePlayer w;
	w.show();
	return a.exec();
}
