#ifndef ROADIMAGEPLAYER_H
#define ROADIMAGEPLAYER_H

#include <QtGui/QMainWindow>
#include "ui_roadimageplayer.h"

class RoadImagePlayer : public QMainWindow
{
	Q_OBJECT

public:
	RoadImagePlayer(QWidget *parent = 0, Qt::WFlags flags = 0);
	~RoadImagePlayer();

private:
	Ui::RoadImagePlayerClass ui;
};

#endif // ROADIMAGEPLAYER_H
