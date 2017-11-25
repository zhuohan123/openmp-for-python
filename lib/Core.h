#ifndef CORE_H
#define CORE_H

#include <vector>
#include <map>

#include "Toolkit.h"
#include "OMP.h"
#include "PY.h"

void changeVariable(Node_t*);
Node_t *findBelong(Node_t*, int);
void AddThreading(int, string, string, int);
void OpenMPforPython();

extern map<int, paraFor_t*> line2For;
extern vector< vector<pair<int, string> > > addCode;
extern vector<Block_t*> Block;
extern int NofBlock;

#endif